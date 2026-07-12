import sys
import os
import time
import logging
import random
from datetime import datetime, timedelta
from collections import deque
from pathlib import Path
import shutil
import uuid
from urllib.parse import urlencode, urlparse

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Backend import models
from Backend.database import engine, ensure_schema, get_db
from Backend.security import get_password_hash, verify_password
from Backend.jwt_auth import create_token, get_current_user
from Backend import payments
from services.team_matcher import get_team_info

test_code = {}
_code_created_at = {}
_last_forgot_request = {}
CODE_TTL_SECONDS = 300

models.Base.metadata.create_all(bind=engine)
ensure_schema()

app = FastAPI(title="HockeyScrapper API")

# Создаем папку для аватарок и делаем ее статической
Path("static/avatars").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conf_email = ConnectionConfig(
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", os.getenv("EMAIL_PASSWORD", "")),
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", os.getenv("EMAIL_LOGIN", "")),
    MAIL_FROM = os.getenv("MAIL_FROM", os.getenv("EMAIL_LOGIN", "noreply@example.com")),
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER = os.getenv("MAIL_SERVER", os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")),
    MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "True") == "True",
    MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", "False") == "True",
) 

def _validate_password(v: str) -> str:
    if len(v) < 8:
        raise ValueError("Пароль должен быть минимум 8 символов")
    if len(v) > 128:
        raise ValueError("Пароль должен быть максимум 128 символов")
    if not any(c.isalpha() for c in v):
        raise ValueError("Пароль должен содержать хотя бы одну букву")
    if not any(c.isdigit() for c in v):
        raise ValueError("Пароль должен содержать хотя бы одну цифру")
    return v

def _validate_username(v: str) -> str:
    if len(v) < 3:
        raise ValueError("Имя пользователя должно быть минимум 3 символа")
    if len(v) > 30:
        raise ValueError("Имя пользователя должно быть максимум 30 символов")
    if not all(c.isalnum() or c == "_" for c in v):
        raise ValueError("Имя пользователя может содержать только буквы, цифры и подчёркивания")
    return v

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    telegram: str
    password: str

    @field_validator("telegram")
    def telegram_valid(cls, v):
        if not v.startswith("@"):
            v = "@" + v
        return v

    @field_validator("password")
    def password_valid(cls, v):
        return _validate_password(v)

    @field_validator("username")
    def username_valid(cls, v):
        return _validate_username(v)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SubscriptionToggle(BaseModel):
    chat_id: int
    team_name: str

class NewPasswordRequest(BaseModel):
    email: EmailStr
    code: int
    new_password: str

    @field_validator("new_password")
    def password_valid(cls, v):
        return _validate_password(v)

class LinkCodeRequest(BaseModel):
    chat_id: int


class CheckoutRequest(BaseModel):
    team_name: str
    enable_auto_renew: bool = False
    save_payment_method_consent: bool = False


class AutoRenewRequest(BaseModel):
    enabled: bool


FREE_TEAM_LIMIT = 3
PAID_TEAM_PRICE_KOPEKS = 3900
PAID_TEAM_PRICE_RUB = PAID_TEAM_PRICE_KOPEKS // 100
TEAM_SUBSCRIPTION_PAYMENT = "team_subscription"
TEAM_SUBSCRIPTION_RENEWAL = "team_subscription_renewal"
TEAM_SUBSCRIPTION_DAYS = 30


def _get_authenticated_user(payload: dict, db: Session) -> models.UserModel:
    user = db.query(models.UserModel).filter(models.UserModel.chat_id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    return user


def _is_local_billing_demo() -> bool:
    """Allow fake payments only on a loopback address explicitly marked as demo."""
    if os.getenv("BILLING_DEMO_MODE", "").lower() not in {"1", "true", "yes"}:
        return False
    host = urlparse(os.getenv("APP_BASE_URL", "")).hostname
    return host in {"127.0.0.1", "localhost"}


def _membership(user: models.UserModel, db: Session) -> dict:
    team_count = db.query(models.SubscriptionModel).filter(
        models.SubscriptionModel.chat_id == user.chat_id,
        models.SubscriptionModel.type == "team",
    ).count()
    free_team_count = _free_team_subscription_count(db, user.chat_id)
    return {
        "pricing_model": "per_team",
        "free_team_limit": FREE_TEAM_LIMIT,
        "free_team_slots_remaining": max(FREE_TEAM_LIMIT - free_team_count, 0),
        "paid_team_price_rub": PAID_TEAM_PRICE_RUB,
        "team_subscription_count": team_count,
        "payment_method_saved": bool(_get_or_migrate_billing_profile(db, user.chat_id)),
    }


def _get_or_migrate_billing_profile(db: Session, chat_id: int) -> models.BillingProfileModel | None:
    """Return the user's shared payment method, migrating an older per-team method."""
    profile = db.query(models.BillingProfileModel).filter(
        models.BillingProfileModel.chat_id == chat_id,
    ).first()
    if profile:
        return profile

    legacy_subscription = db.query(models.PaidTeamSubscriptionModel).filter(
        models.PaidTeamSubscriptionModel.chat_id == chat_id,
        models.PaidTeamSubscriptionModel.payment_method_id.isnot(None),
    ).first()
    if not legacy_subscription:
        return None

    now = datetime.utcnow()
    profile = models.BillingProfileModel(
        chat_id=chat_id,
        payment_method_id=legacy_subscription.payment_method_id,
        consented_at=legacy_subscription.auto_renew_consented_at or now,
        saved_at=now,
    )
    db.add(profile)
    db.flush()
    return profile


def _active_paid_team_values(db: Session, chat_id: int) -> set[str]:
    """Return teams with an unexpired monthly paid subscription."""
    rows = db.query(models.PaidTeamSubscriptionModel.team_name).filter(
        models.PaidTeamSubscriptionModel.chat_id == chat_id,
        models.PaidTeamSubscriptionModel.expires_at > datetime.utcnow(),
    ).all()
    return {team_name for (team_name,) in rows}


def _free_team_subscription_count(db: Session, chat_id: int) -> int:
    paid_teams = _active_paid_team_values(db, chat_id)
    teams = db.query(models.SubscriptionModel.value).filter(
        models.SubscriptionModel.chat_id == chat_id,
        models.SubscriptionModel.type == "team",
    ).all()
    return sum(team_name not in paid_teams for (team_name,) in teams)


def _add_team_subscription(db: Session, chat_id: int, team_name: str) -> None:
    """Add the paid or free team and its venue subscription without committing."""
    team_value = team_name.strip().lower()
    db.add(models.SubscriptionModel(chat_id=chat_id, type="team", value=team_value))
    team_info = get_team_info(team_name)
    if not team_info:
        return

    venue_value = f"{team_info['city']}, {team_info['venue']}".lower()
    existing_venue = db.query(models.SubscriptionModel).filter(
        models.SubscriptionModel.chat_id == chat_id,
        models.SubscriptionModel.type == "venue",
        models.SubscriptionModel.value == venue_value,
    ).first()
    if not existing_venue:
        db.add(models.SubscriptionModel(chat_id=chat_id, type="venue", value=venue_value))


def _remove_team_subscription(db: Session, chat_id: int, team_name: str) -> None:
    """Remove a team from notifications without deleting its payment history."""
    team_value = team_name.strip().lower()
    db.query(models.SubscriptionModel).filter(
        models.SubscriptionModel.chat_id == chat_id,
        models.SubscriptionModel.type == "team",
        models.SubscriptionModel.value == team_value,
    ).delete()
    team_info = get_team_info(team_name)
    if team_info:
        venue_value = f"{team_info['city']}, {team_info['venue']}".lower()
        db.query(models.SubscriptionModel).filter(
            models.SubscriptionModel.chat_id == chat_id,
            models.SubscriptionModel.type == "venue",
            models.SubscriptionModel.value == venue_value,
        ).delete()


def _disable_expired_nonrenewing_subscriptions(db: Session) -> int:
    """Stop notifications for monthly subscriptions that ended without auto-renewal."""
    expired = db.query(models.PaidTeamSubscriptionModel).filter(
        models.PaidTeamSubscriptionModel.expires_at <= datetime.utcnow(),
        models.PaidTeamSubscriptionModel.auto_renew.is_(False),
    ).all()
    for subscription in expired:
        _remove_team_subscription(db, subscription.chat_id, subscription.team_name)
    return len(expired)


def _activate_monthly_team_subscription(
    db: Session,
    payment: models.PaymentModel,
    verified_payment: dict,
) -> None:
    if not payment.team_name:
        raise HTTPException(status_code=400, detail="Team name is required")

    now = datetime.utcnow()
    subscription = db.query(models.PaidTeamSubscriptionModel).filter(
        models.PaidTeamSubscriptionModel.chat_id == payment.chat_id,
        models.PaidTeamSubscriptionModel.team_name == payment.team_name,
    ).first()
    starts_at = now
    if subscription and subscription.expires_at > now:
        starts_at = subscription.expires_at

    payment_method = verified_payment.get("payment_method", {})
    saved_payment_method_id = payment_method.get("id") if payment_method.get("saved") else None
    if saved_payment_method_id and payment.save_payment_method_requested:
        billing_profile = db.query(models.BillingProfileModel).filter(
            models.BillingProfileModel.chat_id == payment.chat_id,
        ).first()
        if billing_profile:
            billing_profile.payment_method_id = saved_payment_method_id
            billing_profile.saved_at = now
        else:
            billing_profile = models.BillingProfileModel(
                chat_id=payment.chat_id,
                payment_method_id=saved_payment_method_id,
                consented_at=now,
                saved_at=now,
            )
            db.add(billing_profile)
        db.flush()
    else:
        billing_profile = _get_or_migrate_billing_profile(db, payment.chat_id)

    can_auto_renew = bool(billing_profile)
    if not subscription:
        subscription = models.PaidTeamSubscriptionModel(
            chat_id=payment.chat_id,
            team_name=payment.team_name,
            expires_at=starts_at + timedelta(days=TEAM_SUBSCRIPTION_DAYS),
            auto_renew=bool(payment.auto_renew_requested and can_auto_renew),
            auto_renew_consented_at=now if payment.auto_renew_requested and can_auto_renew else None,
        )
        db.add(subscription)
    else:
        subscription.expires_at = starts_at + timedelta(days=TEAM_SUBSCRIPTION_DAYS)
        if payment.plan_code == TEAM_SUBSCRIPTION_RENEWAL:
            subscription.auto_renew = True
        elif payment.auto_renew_requested and can_auto_renew:
            subscription.auto_renew = True
            subscription.auto_renew_consented_at = now

    existing = db.query(models.SubscriptionModel).filter(
        models.SubscriptionModel.chat_id == payment.chat_id,
        models.SubscriptionModel.type == "team",
        models.SubscriptionModel.value == payment.team_name,
    ).first()
    if not existing:
        _add_team_subscription(db, payment.chat_id, payment.team_name)


def process_due_renewals(db: Session) -> dict[str, int]:
    """Create YooKassa renewal payments and stop expired subscriptions without renewal."""
    now = datetime.utcnow()
    result = {"renewals_started": 0, "expired_disabled": 0, "skipped": 0}

    result["expired_disabled"] = _disable_expired_nonrenewing_subscriptions(db)
    db.commit()

    due_subscriptions = db.query(models.PaidTeamSubscriptionModel).filter(
        models.PaidTeamSubscriptionModel.expires_at <= now,
        models.PaidTeamSubscriptionModel.auto_renew.is_(True),
    ).all()
    for subscription in due_subscriptions:
        billing_profile = _get_or_migrate_billing_profile(db, subscription.chat_id)
        if not billing_profile:
            subscription.auto_renew = False
            _remove_team_subscription(db, subscription.chat_id, subscription.team_name)
            db.commit()
            result["expired_disabled"] += 1
            continue

        pending = db.query(models.PaymentModel).filter(
            models.PaymentModel.chat_id == subscription.chat_id,
            models.PaymentModel.team_name == subscription.team_name,
            models.PaymentModel.plan_code == TEAM_SUBSCRIPTION_RENEWAL,
            models.PaymentModel.status == "pending",
        ).first()
        if pending:
            result["skipped"] += 1
            continue

        payment = models.PaymentModel(
            id=str(uuid.uuid4()),
            chat_id=subscription.chat_id,
            plan_code=TEAM_SUBSCRIPTION_RENEWAL,
            provider="yookassa",
            amount_kopeks=PAID_TEAM_PRICE_KOPEKS,
            currency="RUB",
            status="pending",
            idempotency_key=str(uuid.uuid4()),
            team_name=subscription.team_name,
            auto_renew_requested=True,
        )
        db.add(payment)
        db.commit()
        try:
            provider_payment = payments.create_recurring_payment(
                amount=f"{PAID_TEAM_PRICE_KOPEKS / 100:.2f}",
                description=f"HockeyScrapper: продление подписки на {subscription.team_name}",
                order_id=payment.id,
                idempotency_key=payment.idempotency_key,
                payment_method_id=billing_profile.payment_method_id,
            )
            provider_payment_id = provider_payment.get("id")
            if not provider_payment_id:
                raise payments.PaymentProviderError("YooKassa returned an incomplete renewal payment")
            payment.provider_payment_id = provider_payment_id
            db.commit()
            result["renewals_started"] += 1
        except payments.PaymentProviderError:
            payment.status = "failed"
            subscription.auto_renew = False
            _remove_team_subscription(db, subscription.chat_id, subscription.team_name)
            db.commit()
            result["expired_disabled"] += 1

    return result

@app.post("/register")
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    email_norm = user_data.email.lower().strip()
    existing = db.query(models.UserModel).filter(
        func.lower(models.UserModel.email) == email_norm
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = get_password_hash(user_data.password)
    for attempt in range(3):
        try:
            min_chat = db.query(models.UserModel.chat_id).order_by(models.UserModel.chat_id.asc()).first()
            new_chat_id = (min_chat[0] - 1) if (min_chat and min_chat[0] < 0) else -1

            user = models.UserModel(
                chat_id=new_chat_id,
                username=user_data.username,
                email=email_norm,
                telegram=user_data.telegram,
                password_hash=hashed,
                is_active=1
            )
            db.add(user)
            db.commit()
            break
        except IntegrityError:
            db.rollback()
            if attempt == 2:
                raise HTTPException(status_code=500, detail="Registration failed, try again")
            continue

    token = create_token(new_chat_id, user_data.email)
    return {
        "status": "success",
        "message": "Registered!",
        "chat_id": new_chat_id,
        "access_token": token,
        "token_type": "bearer"
    }

@app.post("/login")
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    email_norm = login_data.email.lower().strip()
    user = db.query(models.UserModel).filter(
        func.lower(models.UserModel.email) == email_norm
    ).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    token = create_token(user.chat_id, user.email)
    return {
        "status": "success",
        "message": "Login successful!",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "chat_id": user.chat_id,
            "username": user.username,
            "email": user.email,
            "telegram": user.telegram
        }
    }

@app.post("/forgot_password")
async def forgot_password(request: dict, db: Session = Depends(get_db)):
    email = request.get("email", "").lower().strip()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    user = db.query(models.UserModel).filter(
        func.lower(models.UserModel.email) == email
    ).first()
    if not user:
        raise HTTPException(status_code=400, detail="Такого пользователя не существует")

    now = time.time()
    last_req = _last_forgot_request.get(email, 0)
    if now - last_req < 60:
        raise HTTPException(status_code=429, detail="Повторите через минуту")

    random_code = random.randint(100000, 999999)
    test_code[email] = {"code": random_code}
    _code_created_at[email] = now
    _last_forgot_request[email] = now

    try:
        fm = FastMail(conf_email)
        msg = MessageSchema(
            subject="Код подтверждения",
            recipients=[email],
            body=str(random_code),
            subtype=MessageType.plain
        ) #sending msg 
        await fm.send_message(msg)
    except Exception as e:
        print(f"[EMAIL FAILED] Code for {email}: {random_code} (SMTP error: {e})")
    return {"status": "success", "message": "Email sent!"}

@app.post("/new_password")
async def new_password(request: NewPasswordRequest, db: Session = Depends(get_db)):
    email_norm = request.email.lower().strip()
    user = db.query(models.UserModel).filter(
        func.lower(models.UserModel.email) == email_norm
    ).first()
    if not user:
        raise HTTPException(status_code=400, detail="Пользователь не найден")

    user_code = test_code.get(email_norm)
    if not user_code:
        raise HTTPException(status_code=400, detail="Код не запрашивался")

    created = _code_created_at.get(email_norm, 0)
    if time.time() - created > CODE_TTL_SECONDS:
        test_code.pop(email_norm, None)
        _code_created_at.pop(email_norm, None)
        raise HTTPException(status_code=400, detail="Код истёк, запросите новый")

    if user_code["code"] != request.code:
        raise HTTPException(status_code=400, detail="Неверный код")

    hashed_password = get_password_hash(request.new_password)
    user.password_hash = hashed_password
    db.commit()
    test_code.pop(request.email, None)
    _code_created_at.pop(request.email, None)
    return {"status": "success", "message": "Password changed!"}

@app.get("/me")
def get_me(payload: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = _get_authenticated_user(payload, db)
    return {
        "chat_id": user.chat_id,
        "username": user.username,
        "email": user.email,
        "telegram": user.telegram,
        "avatar_url": user.avatar_url,
        "membership": _membership(user, db),
    }

@app.put("/me/avatar")
def upload_avatar(
    payload: dict = Depends(get_current_user),
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.UserModel).filter(models.UserModel.chat_id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверяем тип файла
    if avatar.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, PNG, GIF are allowed.")

    # Удаляем старый файл, если он есть
    if user.avatar_url:
        old_path = user.avatar_url.lstrip("/")
        if os.path.exists(old_path):
            os.remove(old_path)

    # Генерируем уникальное имя файла
    file_extension = avatar.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"static/avatars/{unique_filename}"

    # Сохраняем файл на диск
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(avatar.file, buffer)

    # Обновляем путь в базе данных
    user.avatar_url = f"/{file_path}"
    db.commit()

    return {"status": "success", "avatar_url": user.avatar_url}

@app.post("/link-code")
def generate_link_code(req: LinkCodeRequest, db: Session = Depends(get_db)):
    import secrets
    user = db.query(models.UserModel).filter(models.UserModel.chat_id == req.chat_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.chat_id > 0:
        raise HTTPException(status_code=400, detail="Account already linked")
    code = secrets.token_hex(4)
    user.link_code = code
    db.commit()
    bot_username = os.environ.get("BOT_USERNAME", "HockeyScrAppeer_bot")
    return {"code": code, "link": f"https://t.me/{bot_username}?start={code}"}

@app.post("/subscription/toggle")
def toggle_subscription(
    sub_data: SubscriptionToggle,
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = _get_authenticated_user(payload, db)
    if _disable_expired_nonrenewing_subscriptions(db):
        db.commit()
    if sub_data.chat_id != user.chat_id:
        raise HTTPException(status_code=403, detail="You can only manage your own subscriptions")

    team_name = sub_data.team_name.strip()
    team_value = team_name.lower()
    existing = db.query(models.SubscriptionModel).filter(
        models.SubscriptionModel.chat_id == user.chat_id,
        models.SubscriptionModel.type == "team",
        models.SubscriptionModel.value == team_value,
    ).first()

    if existing:
        _remove_team_subscription(db, user.chat_id, team_name)
        db.commit()
        return {"status": "removed", "message": f"Unsubscribed from {sub_data.team_name}"}
    else:
        paid_teams = _active_paid_team_values(db, user.chat_id)
        if team_value not in paid_teams and _free_team_subscription_count(db, user.chat_id) >= FREE_TEAM_LIMIT:
            raise HTTPException(
                status_code=402,
                detail={
                    "code": "payment_required",
                    "message": f"Первые {FREE_TEAM_LIMIT} команды бесплатны. Подписка на следующую команду стоит {PAID_TEAM_PRICE_RUB} ₽.",
                    "team_name": team_name,
                    "price_rub": PAID_TEAM_PRICE_RUB,
                },
            )
        _add_team_subscription(db, user.chat_id, team_name)
        db.commit()
        return {"status": "added", "message": f"Subscribed to {team_name}"}

@app.get("/subscriptions/{chat_id}")
def get_user_subscriptions(
    chat_id: int,
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = _get_authenticated_user(payload, db)
    if _disable_expired_nonrenewing_subscriptions(db):
        db.commit()
    if chat_id != user.chat_id:
        raise HTTPException(status_code=403, detail="You can only view your own subscriptions")
    subs = db.query(models.SubscriptionModel).filter(
        models.SubscriptionModel.chat_id == user.chat_id
    ).all()
    teams = [s.value for s in subs if s.type == "team"]
    return {"chat_id": user.chat_id, "subscriptions": teams, "membership": _membership(user, db)}


@app.get("/billing/plans")
def get_billing_plans():
    return {
        "plans": [{
            "code": TEAM_SUBSCRIPTION_PAYMENT,
            "name": "Подписка на команду на месяц",
            "amount_rub": PAID_TEAM_PRICE_RUB,
            "duration_days": TEAM_SUBSCRIPTION_DAYS,
        }],
        "free_team_limit": FREE_TEAM_LIMIT,
        "demo_mode": _is_local_billing_demo(),
    }


@app.get("/billing/me")
def get_billing_membership(payload: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return _membership(_get_authenticated_user(payload, db), db)


@app.get("/billing/subscriptions")
def get_paid_team_subscriptions(payload: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = _get_authenticated_user(payload, db)
    now = datetime.utcnow()
    billing_profile = _get_or_migrate_billing_profile(db, user.chat_id)
    if billing_profile:
        db.commit()
    subscriptions = db.query(models.PaidTeamSubscriptionModel).filter(
        models.PaidTeamSubscriptionModel.chat_id == user.chat_id,
    ).order_by(models.PaidTeamSubscriptionModel.expires_at.desc()).all()
    return {
        "monthly_price_rub": PAID_TEAM_PRICE_RUB,
        "subscriptions": [
            {
                "team_name": subscription.team_name,
                "expires_at": subscription.expires_at.isoformat(),
                "is_active": subscription.expires_at > now,
                "auto_renew": subscription.auto_renew,
                "can_enable_auto_renew": bool(billing_profile),
            }
            for subscription in subscriptions
        ],
    }


@app.patch("/billing/subscriptions/{team_name}/auto-renew")
def update_auto_renew(
    team_name: str,
    request: AutoRenewRequest,
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = _get_authenticated_user(payload, db)
    subscription = db.query(models.PaidTeamSubscriptionModel).filter(
        models.PaidTeamSubscriptionModel.chat_id == user.chat_id,
        models.PaidTeamSubscriptionModel.team_name == team_name.strip().lower(),
    ).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Paid subscription not found")
    if request.enabled:
        if subscription.expires_at <= datetime.utcnow():
            raise HTTPException(status_code=400, detail="Renew this subscription before enabling auto-renewal")
        billing_profile = _get_or_migrate_billing_profile(db, user.chat_id)
        if not billing_profile:
            if _is_local_billing_demo():
                now = datetime.utcnow()
                billing_profile = models.BillingProfileModel(
                    chat_id=user.chat_id,
                    payment_method_id="demo-payment-method",
                    consented_at=now,
                    saved_at=now,
                )
                db.add(billing_profile)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Для автопродления нужно привязать способ оплаты в YooKassa.",
                )
        subscription.auto_renew = True
        subscription.auto_renew_consented_at = datetime.utcnow()
    else:
        subscription.auto_renew = False
    db.commit()
    return {"team_name": subscription.team_name, "auto_renew": subscription.auto_renew}


@app.post("/billing/checkout")
def create_checkout(
    request: CheckoutRequest,
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = _get_authenticated_user(payload, db)
    if _disable_expired_nonrenewing_subscriptions(db):
        db.commit()
    team_name = request.team_name.strip()
    if not team_name:
        raise HTTPException(status_code=400, detail="Team name is required")

    team_value = team_name.lower()
    existing = db.query(models.SubscriptionModel).filter(
        models.SubscriptionModel.chat_id == user.chat_id,
        models.SubscriptionModel.type == "team",
        models.SubscriptionModel.value == team_value,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="You are already subscribed to this team")

    if team_value in _active_paid_team_values(db, user.chat_id):
        raise HTTPException(status_code=409, detail="This paid subscription is already active")

    if _free_team_subscription_count(db, user.chat_id) < FREE_TEAM_LIMIT:
        raise HTTPException(status_code=400, detail="The first three team subscriptions are free")

    billing_profile = _get_or_migrate_billing_profile(db, user.chat_id)
    if billing_profile:
        db.commit()
    elif not request.save_payment_method_consent:
        raise HTTPException(
            status_code=400,
            detail="Подтвердите сохранение способа оплаты в YooKassa для первой платной покупки.",
        )

    pending = db.query(models.PaymentModel).filter(
        models.PaymentModel.chat_id == user.chat_id,
        models.PaymentModel.team_name == team_value,
        models.PaymentModel.status == "pending",
    ).first()
    if pending:
        raise HTTPException(status_code=409, detail="Payment for this team is already pending")

    payment = models.PaymentModel(
        id=str(uuid.uuid4()),
        chat_id=user.chat_id,
        plan_code=TEAM_SUBSCRIPTION_PAYMENT,
        provider="yookassa",
        amount_kopeks=PAID_TEAM_PRICE_KOPEKS,
        currency="RUB",
        status="pending",
        idempotency_key=str(uuid.uuid4()),
        team_name=team_value,
        auto_renew_requested=request.enable_auto_renew,
        save_payment_method_requested=not bool(billing_profile),
    )
    db.add(payment)
    db.commit()

    app_base_url = os.getenv("APP_BASE_URL", "").rstrip("/")
    if _is_local_billing_demo():
        app_base_url = app_base_url or "http://127.0.0.1:8000"
        payment.provider_payment_id = f"demo-{payment.id}"
        _activate_monthly_team_subscription(
            db,
            payment,
            {
                "payment_method": {
                    "id": billing_profile.payment_method_id if billing_profile else "demo-payment-method",
                    "saved": True,
                }
            },
        )
        payment.status = "succeeded"
        payment.paid_at = datetime.utcnow()
        db.commit()
        return {
            "payment_id": payment.id,
            "checkout_url": f"{app_base_url}/billing.html?{urlencode({'payment': 'success', 'team': team_name})}",
        }

    if not app_base_url:
        payment.status = "failed"
        db.commit()
        raise HTTPException(status_code=503, detail="Billing is not configured")

    return_url = f"{app_base_url}/billing.html?{urlencode({'payment': 'success', 'team': team_name})}"
    try:
        if billing_profile:
            provider_payment = payments.create_recurring_payment(
                amount=f"{PAID_TEAM_PRICE_KOPEKS / 100:.2f}",
                description=f"HockeyScrapper: подписка на {team_name}",
                order_id=payment.id,
                idempotency_key=payment.idempotency_key,
                payment_method_id=billing_profile.payment_method_id,
            )
            checkout_url = return_url
        else:
            provider_payment = payments.create_payment(
                amount=f"{PAID_TEAM_PRICE_KOPEKS / 100:.2f}",
                description=f"HockeyScrapper: подписка на {team_name}",
                return_url=return_url,
                order_id=payment.id,
                idempotency_key=payment.idempotency_key,
                save_payment_method=True,
            )
            checkout_url = provider_payment.get("confirmation", {}).get("confirmation_url")
        provider_payment_id = provider_payment.get("id")
        if not checkout_url or not provider_payment_id:
            raise payments.PaymentProviderError("YooKassa returned an incomplete payment")
    except payments.PaymentProviderError as error:
        payment.status = "failed"
        db.commit()
        raise HTTPException(status_code=503, detail=str(error)) from error

    payment.provider_payment_id = provider_payment_id
    # The webhook performs the authoritative verification and activation.
    payment.status = "pending"
    db.commit()
    return {"payment_id": payment.id, "checkout_url": checkout_url}


@app.get("/billing/payments/{payment_id}")
def get_payment_status(
    payment_id: str,
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = _get_authenticated_user(payload, db)
    payment = db.query(models.PaymentModel).filter(models.PaymentModel.id == payment_id).first()
    if not payment or payment.chat_id != user.chat_id:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {
        "id": payment.id,
        "team_name": payment.team_name,
        "status": payment.status,
        "amount_rub": payment.amount_kopeks / 100,
        "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
    }


@app.post("/payments/yookassa/webhook")
def yookassa_webhook(notification: dict, db: Session = Depends(get_db)):
    provider_payment_id = notification.get("object", {}).get("id")
    if not provider_payment_id:
        raise HTTPException(status_code=400, detail="Payment id is required")

    payment = db.query(models.PaymentModel).filter(
        models.PaymentModel.provider_payment_id == provider_payment_id
    ).first()
    if not payment:
        return {"status": "ignored"}

    try:
        verified_payment = payments.get_payment(provider_payment_id)
    except payments.PaymentProviderError as error:
        raise HTTPException(status_code=503, detail="Payment verification is unavailable") from error

    expected_amount = f"{payment.amount_kopeks / 100:.2f}"
    verified_amount = verified_payment.get("amount", {})
    if (
        verified_payment.get("metadata", {}).get("order_id") != payment.id
        or verified_amount.get("currency") != payment.currency
        or verified_amount.get("value") != expected_amount
    ):
        raise HTTPException(status_code=400, detail="Payment verification failed")

    provider_status = verified_payment.get("status", "pending")
    if provider_status == "succeeded" and payment.status != "succeeded":
        user = db.query(models.UserModel).filter(models.UserModel.chat_id == payment.chat_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if payment.plan_code not in {TEAM_SUBSCRIPTION_PAYMENT, TEAM_SUBSCRIPTION_RENEWAL} or not payment.team_name:
            raise HTTPException(status_code=400, detail="Unsupported payment type")
        _activate_monthly_team_subscription(db, payment, verified_payment)
        payment.status = "succeeded"
        payment.paid_at = datetime.utcnow()
        db.commit()
    elif provider_status == "canceled" and payment.status == "pending":
        payment.status = "canceled"
        if payment.plan_code == TEAM_SUBSCRIPTION_RENEWAL and payment.team_name:
            subscription = db.query(models.PaidTeamSubscriptionModel).filter(
                models.PaidTeamSubscriptionModel.chat_id == payment.chat_id,
                models.PaidTeamSubscriptionModel.team_name == payment.team_name,
            ).first()
            if subscription:
                subscription.auto_renew = False
                if subscription.expires_at <= datetime.utcnow():
                    _remove_team_subscription(db, payment.chat_id, payment.team_name)
        db.commit()

    return {"status": "ok"}


@app.get("/matches")
def get_all_matches(db: Session = Depends(get_db)):
    matches = db.query(models.MatchModel).order_by(models.MatchModel.date).all()
    return [
        {
            "match_id": m.match_id,
            "title": m.title,
            "date": m.date,
            "place": m.place,
            "venue": m.venue,
            "city": m.city,
            "teams": m.teams,
            "price_min": m.price_min,
            "price_max": m.price_max,
            "availability": m.availability,
            "link": m.link,
        }
        for m in matches
    ]

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    users = db.query(models.UserModel).filter(models.UserModel.is_active == 1).count()
    team_subs = db.query(models.SubscriptionModel).filter(models.SubscriptionModel.type == "team").count()
    venue_subs = db.query(models.SubscriptionModel).filter(models.SubscriptionModel.type == "venue").count()
    matches = db.query(models.MatchModel).count()
    return {"users": users, "team_subs": team_subs, "venue_subs": venue_subs, "matches": matches}

# ─── Admin panel ────────────────────────────────────────────────────────────

ADMIN_EMAILS = [e.strip() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()]

class _LogBuffer(logging.Handler):
    def __init__(self, maxlen=500):
        super().__init__()
        self.buffer = deque(maxlen=maxlen)
    def emit(self, record):
        self.buffer.append(self.format(record))

_log_buffer = _LogBuffer()
_log_buffer.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
logging.getLogger().addHandler(_log_buffer)

async def _require_admin(current_user=Depends(get_current_user)):
    if current_user.get("email") not in ADMIN_EMAILS:
        raise HTTPException(status_code=404, detail="Not found")
    return current_user

# ── Settings ─────────────────────────────────────────────────────────────────

class ParseIntervalSchema(BaseModel):
    minutes: int

class BotProxySchema(BaseModel):
    proxy_url: str

    @field_validator("proxy_url")
    def proxy_url_valid(cls, v):
        v = v.strip()
        if v and not any(v.startswith(p) for p in ("http://", "https://", "socks4://", "socks5://")):
            raise ValueError("URL должен начинаться с http://, https://, socks4:// или socks5://")
        return v

class NotifySchema(BaseModel):
    title: str = "Тестовое уведомление"
    date: str = ""
    place: str = "Админ-панель"
    price_min: str = "—"
    price_max: str = "—"
    availability: str = "—"
    link: str = ""

    @field_validator("title")
    def title_valid(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Заголовок не может быть пустым")
        if len(v) > 200:
            raise ValueError("Заголовок слишком длинный (макс. 200 символов)")
        return v

class AddSubscriptionSchema(BaseModel):
    type: str
    value: str

    @field_validator("type")
    def type_valid(cls, v):
        if v not in ("team", "venue"):
            raise ValueError("Тип подписки должен быть 'team' или 'venue'")
        return v

    @field_validator("value")
    def value_valid(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Название не может быть пустым")
        if len(v) > 100:
            raise ValueError("Название слишком длинное (макс. 100 символов)")
        return v

class AddProxySchema(BaseModel):
    url: str
    proxy_type: str = "http"
    country: str = ""
    note: str = ""

    @field_validator("url")
    def url_valid(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("URL прокси не может быть пустым")
        if not any(v.startswith(p) for p in ("http://", "https://", "socks4://", "socks5://")):
            raise ValueError("URL должен начинаться с http://, https://, socks4:// или socks5://")
        return v

    @field_validator("proxy_type")
    def proxy_type_valid(cls, v):
        if v not in ("http", "socks4", "socks5"):
            raise ValueError("Тип прокси должен быть http, socks4 или socks5")
        return v

# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/admin/check")
async def admin_check(admin=Depends(_require_admin)):
    return {"admin": True, "email": admin["email"]}

@app.get("/admin/stats")
async def admin_stats(db: Session = Depends(get_db), admin=Depends(_require_admin)):
    total_users = db.query(models.UserModel).count()
    active_users = db.query(models.UserModel).filter(models.UserModel.is_active == 1).count()
    banned_users = db.query(models.UserModel).filter(models.UserModel.is_active == 0).count()
    team_subs = db.query(models.SubscriptionModel).filter(models.SubscriptionModel.type == "team").count()
    venue_subs = db.query(models.SubscriptionModel).filter(models.SubscriptionModel.type == "venue").count()
    matches = db.query(models.MatchModel).count()
    proxies = db.query(models.ProxyModel).count()
    return {
        "total_users": total_users,
        "active_users": active_users,
        "banned_users": banned_users,
        "team_subs": team_subs,
        "venue_subs": venue_subs,
        "matches": matches,
        "proxies": proxies,
    }

@app.get("/admin/users")
def admin_users(db: Session = Depends(get_db), admin=Depends(_require_admin)):
    users = db.query(models.UserModel).order_by(models.UserModel.registered_at.desc()).all()
    result = []
    for u in users:
        subs = db.query(models.SubscriptionModel).filter(
            models.SubscriptionModel.chat_id == u.chat_id
        ).all()
        result.append({
            "chat_id": u.chat_id,
            "username": u.username,
            "email": u.email,
            "telegram": u.telegram,
            "is_active": u.is_active,
            "registered_at": str(u.registered_at) if u.registered_at else None,
            "subscriptions": [{"type": s.type, "value": s.value} for s in subs],
        })
    return result

@app.delete("/admin/users/{chat_id}")
def admin_delete_user(chat_id: int, db: Session = Depends(get_db), admin=Depends(_require_admin)):
    user = db.query(models.UserModel).filter(models.UserModel.chat_id == chat_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.query(models.SubscriptionModel).filter(models.SubscriptionModel.chat_id == chat_id).delete()
    db.query(models.NotifiedEventModel).filter(models.NotifiedEventModel.chat_id == chat_id).delete()
    db.delete(user)
    db.commit()
    return {"status": "deleted"}

@app.patch("/admin/users/{chat_id}/ban")
def admin_toggle_ban(chat_id: int, db: Session = Depends(get_db), admin=Depends(_require_admin)):
    user = db.query(models.UserModel).filter(models.UserModel.chat_id == chat_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = 0 if user.is_active else 1
    db.commit()
    return {"status": "updated", "is_active": user.is_active}

@app.post("/admin/users/{chat_id}/subscriptions")
def admin_add_subscription(chat_id: int, body: AddSubscriptionSchema,
                            db: Session = Depends(get_db), admin=Depends(_require_admin)):
    user = db.query(models.UserModel).filter(models.UserModel.chat_id == chat_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    normalized = body.value.lower().strip()
    existing = db.query(models.SubscriptionModel).filter(
        models.SubscriptionModel.chat_id == chat_id,
        models.SubscriptionModel.type == body.type,
        func.lower(models.SubscriptionModel.value) == normalized,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Подписка '{body.value}' уже существует")
    sub = models.SubscriptionModel(chat_id=chat_id, type=body.type, value=normalized)
    db.add(sub)
    db.commit()
    return {"status": "added", "value": normalized}

@app.delete("/admin/users/{chat_id}/subscriptions")
def admin_remove_subscription(chat_id: int, type: str = "team", value: str = "",
                               db: Session = Depends(get_db), admin=Depends(_require_admin)):
    normalized = value.lower().strip()
    sub = db.query(models.SubscriptionModel).filter(
        models.SubscriptionModel.chat_id == chat_id,
        models.SubscriptionModel.type == type,
        func.lower(models.SubscriptionModel.value) == normalized,
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    db.delete(sub)
    db.commit()
    return {"status": "deleted"}

@app.get("/admin/proxies")
def admin_proxies(db: Session = Depends(get_db), admin=Depends(_require_admin)):
    proxies = db.query(models.ProxyModel).order_by(models.ProxyModel.id).all()
    return [{"id": p.id, "url": p.url, "proxy_type": p.proxy_type,
             "country": p.country, "enabled": p.enabled, "note": p.note} for p in proxies]

@app.post("/admin/proxies")
def admin_add_proxy(body: AddProxySchema, db: Session = Depends(get_db), admin=Depends(_require_admin)):
    proxy = models.ProxyModel(url=body.url, proxy_type=body.proxy_type,
                               country=body.country, note=body.note)
    db.add(proxy)
    db.commit()
    return {"status": "added", "id": proxy.id}

@app.delete("/admin/proxies/{proxy_id}")
def admin_delete_proxy(proxy_id: int, db: Session = Depends(get_db), admin=Depends(_require_admin)):
    proxy = db.query(models.ProxyModel).filter(models.ProxyModel.id == proxy_id).first()
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")
    db.delete(proxy)
    db.commit()
    return {"status": "deleted"}

@app.patch("/admin/proxies/{proxy_id}/toggle")
def admin_toggle_proxy(proxy_id: int, db: Session = Depends(get_db), admin=Depends(_require_admin)):
    proxy = db.query(models.ProxyModel).filter(models.ProxyModel.id == proxy_id).first()
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")
    proxy.enabled = 0 if proxy.enabled else 1
    db.commit()
    return {"status": "updated", "enabled": proxy.enabled}

@app.get("/admin/settings")
def admin_settings(db: Session = Depends(get_db), admin=Depends(_require_admin)):
    rows = db.query(models.SettingModel).all()
    return {r.key: r.value for r in rows}

@app.put("/admin/settings/parse-interval")
def admin_set_parse_interval(body: ParseIntervalSchema,
                              db: Session = Depends(get_db), admin=Depends(_require_admin)):
    m = max(1, min(body.minutes, 999))
    setting = db.query(models.SettingModel).filter(models.SettingModel.key == "parse_interval_minutes").first()
    if setting:
        setting.value = str(m)
    else:
        db.add(models.SettingModel(key="parse_interval_minutes", value=str(m)))
    db.commit()
    return {"status": "updated", "value": m}

@app.put("/admin/settings/bot-proxy")
def admin_set_bot_proxy(body: BotProxySchema,
                         db: Session = Depends(get_db), admin=Depends(_require_admin)):
    setting = db.query(models.SettingModel).filter(models.SettingModel.key == "bot_proxy_url").first()
    if setting:
        setting.value = body.proxy_url
    else:
        db.add(models.SettingModel(key="bot_proxy_url", value=body.proxy_url))
    db.commit()
    return {"status": "updated"}

@app.get("/admin/sites")
def admin_sites(admin=Depends(_require_admin)):
    import yaml
    config_path = Path(__file__).resolve().parent.parent / "config" / "sites.yaml"
    if not config_path.exists():
        raise HTTPException(status_code=404, detail="Config not found")
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    sites = cfg.get("sites", [])
    return [{"name": s["name"], "parser": s.get("parser", ""),
             "enabled": s.get("enabled", True),
             "interval_minutes": s.get("interval_minutes", 30)} for s in sites]

@app.put("/admin/sites/{name}/toggle")
def admin_toggle_site(name: str, db: Session = Depends(get_db), admin=Depends(_require_admin)):
    key = f"site:{name}:enabled"
    import yaml
    config_path = Path(__file__).resolve().parent.parent / "config" / "sites.yaml"
    if not config_path.exists():
        raise HTTPException(status_code=404, detail="Config not found")
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    site = next((s for s in cfg.get("sites", []) if s["name"] == name), None)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    current = db.query(models.SettingModel).filter(models.SettingModel.key == key).first()
    if current:
        new_val = "false" if current.value == "true" else "true"
        current.value = new_val
    else:
        new_val = "false" if site.get("enabled", True) else "true"
        db.add(models.SettingModel(key=key, value=new_val))
    db.commit()
    return {"status": "updated", "enabled": new_val == "true"}

@app.post("/admin/trigger-parse")
def admin_trigger_parse(db: Session = Depends(get_db), admin=Depends(_require_admin)):
    from datetime import datetime
    setting = db.query(models.SettingModel).filter(models.SettingModel.key == "parse_trigger_requested_at").first()
    if setting:
        setting.value = str(datetime.now().timestamp())
    else:
        db.add(models.SettingModel(key="parse_trigger_requested_at", value=str(datetime.now().timestamp())))
    db.commit()
    return {"status": "parse_triggered", "message": "Парсер запустится в ближайшем цикле"}

@app.post("/admin/notify")
async def admin_notify_all(body: NotifySchema, admin=Depends(_require_admin)):
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    if not BOT_TOKEN:
        raise HTTPException(status_code=400, detail="BOT_TOKEN not configured")
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    from services.notifier import Notifier
    from services.database import get_db as get_async_db
    notifier = Notifier(bot)
    adb = get_async_db()
    await adb.init()
    users = await adb.get_all_users()
    chat_ids = [u["chat_id"] for u in users]
    event = {
        "title": body.title,
        "date": body.date or datetime.now().strftime("%d.%m.%Y"),
        "place": body.place,
        "price_min": body.price_min,
        "price_max": body.price_max,
        "availability": body.availability,
        "link": body.link,
    }
    sent = await notifier.notify_subscribers(
        event=event,
        subscriber_chat_ids=chat_ids,
        db=adb,
        reason="available",
    )
    await bot.session.close()
    return {"status": "notified", "sent": sent}

@app.get("/admin/logs")
def admin_logs(admin=Depends(_require_admin)):
    return {"logs": list(_log_buffer.buffer)}

@app.delete("/admin/matches")
def admin_clear_matches(db: Session = Depends(get_db), admin=Depends(_require_admin)):
    count = db.query(models.MatchModel).count()
    db.query(models.MatchModel).delete()
    db.query(models.NotifiedEventModel).delete()
    db.commit()
    return {"status": "cleared", "deleted": count}

frontend_path = Path(__file__).resolve().parent.parent / "Frontend"

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    from fastapi.responses import FileResponse
    import mimetypes
    from fastapi import HTTPException

    resolved = (frontend_path / full_path).resolve() if full_path else (frontend_path / "index.html").resolve()
    if not str(resolved).startswith(str(frontend_path.resolve())):
        raise HTTPException(status_code=404, detail="Not found")
    if not resolved.exists() or not resolved.is_file():
        resolved = frontend_path / "index.html"
    if not resolved.exists():
        raise HTTPException(status_code=404, detail="Not found")
    media_type, _ = mimetypes.guess_type(str(resolved))
    return FileResponse(str(resolved), media_type=media_type or "text/html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Backend.main:app", host="127.0.0.1", port=8000, reload=True)
