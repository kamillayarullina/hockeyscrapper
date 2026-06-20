import sys
import os
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Backend import models
from Backend.database import engine, get_db
from Backend.security import get_password_hash, verify_password
from Backend.jwt_auth import create_token, get_current_user

import random
import time
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError

from services.team_matcher import get_team_info, normalize_team_name

test_code = {}
CODE_TTL_SECONDS = 300  # 5 minutes
_last_forgot_request = {}  # email -> timestamp for rate limiting

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="HockeyScrapper API")

_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conf_email = ConnectionConfig(
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "hqbo bhdk cxfg gabq"),
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "sakirovsamir401@gmail.com"),
    MAIL_FROM = os.getenv("MAIL_FROM", "sakirovsamir401@gmail.com"),
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "True") == "True",
    MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", "False") == "True"
)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class NewPasswordRequest(BaseModel):
    email: EmailStr
    code: int
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    telegram: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class SubscriptionToggle(BaseModel):
    chat_id: int
    team_name: str


@app.post("/register")
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.UserModel).filter(models.UserModel.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = get_password_hash(user_data.password)
    for attempt in range(3):
        min_chat = db.query(models.UserModel.chat_id).filter(models.UserModel.chat_id < 0).order_by(models.UserModel.chat_id.asc()).first()
        new_chat_id = (min_chat[0] - 1) if min_chat else -1
        user = models.UserModel(
            chat_id=new_chat_id,
            username=user_data.username,
            email=user_data.email,
            telegram=user_data.telegram,
            password_hash=hashed,
            is_active=1
        )
        db.add(user)
        try:
            db.commit()
            break
        except IntegrityError:
            db.rollback()
            continue
    else:
        raise HTTPException(status_code=500, detail="Registration error, try again")

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
    user = db.query(models.UserModel).filter(models.UserModel.email == login_data.email).first()
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
async def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email = req.email
    now = time.time()
    last = _last_forgot_request.get(email, 0)
    if now - last < 60:
        raise HTTPException(status_code=429, detail="Повторите попытку через минуту")
    user = db.query(models.UserModel).filter(models.UserModel.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такого пользователя не существует"
        )
    _last_forgot_request[email] = now
    random_code = random.randint(100000, 999999)
    test_code[email] = {"code": random_code, "created_at": time.time()}
    fm = FastMail(conf_email)
    msg = MessageSchema(
        subject = "Код подтверждения",
        recipients = [email],
        body=str(random_code),
        subtype="plain"
    )
    await fm.send_message(msg)
    return {"status": "success", "message": "Email sent!"}

@app.post("/new_password")
async def new_password(request: NewPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.UserModel).filter(models.UserModel.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такого пользователя не существует"
        )
    user_code = test_code.get(request.email)
    if not user_code or user_code["code"] != request.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный код"
        )
    if time.time() - user_code.get("created_at", 0) > CODE_TTL_SECONDS:
        test_code.pop(request.email, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Код истёк. Запросите новый."
        )
    hashed_password = get_password_hash(request.new_password)
    user.password_hash = hashed_password
    db.commit()
    test_code.pop(request.email, None)
    return {"status": "success","message": "Password changed!"}

@app.get("/me")
def get_me(payload: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.UserModel).filter(models.UserModel.chat_id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "chat_id": user.chat_id,
        "username": user.username,
        "email": user.email,
        "telegram": user.telegram
    }


class LinkCodeRequest(BaseModel):
    chat_id: int


@app.post("/link-code")
def generate_link_code(req: LinkCodeRequest, payload: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    import secrets
    if int(payload["sub"]) != req.chat_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    user = db.query(models.UserModel).filter(models.UserModel.chat_id == req.chat_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.chat_id > 0:
        raise HTTPException(status_code=400, detail="Account already linked")
    code = secrets.token_hex(4)
    user.link_code = code
    db.commit()
    return {"code": code, "link": f"https://t.me/HockeyScrapper_bot?start={code}"}


@app.post("/subscription/toggle")
def toggle_subscription(sub_data: SubscriptionToggle, payload: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if int(payload["sub"]) != sub_data.chat_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    team = normalize_team_name(sub_data.team_name)
    existing = db.query(models.SubscriptionModel).filter(
        models.SubscriptionModel.chat_id == sub_data.chat_id,
        models.SubscriptionModel.type == "team",
        models.SubscriptionModel.value == (team or sub_data.team_name).lower()
    ).first()

    if existing:
        db.delete(existing)
        team_info = get_team_info(team) if team else None
        if team_info:
            venue_key = f"{team_info['city']}, {team_info['venue']}".lower()
            venue_sub = db.query(models.SubscriptionModel).filter(
                models.SubscriptionModel.chat_id == sub_data.chat_id,
                models.SubscriptionModel.type == "venue",
                models.SubscriptionModel.value == venue_key
            ).first()
            if venue_sub:
                db.delete(venue_sub)
        db.commit()
        return {"status": "removed", "message": f"Unsubscribed from {team or sub_data.team_name}"}
    else:
        new_sub = models.SubscriptionModel(
            chat_id=sub_data.chat_id,
            type="team",
            value=(team or sub_data.team_name).lower()
        )
        db.add(new_sub)
        team_info = get_team_info(team) if team else None
        if team_info:
            venue_key = f"{team_info['city']}, {team_info['venue']}".lower()
            existing_venue = db.query(models.SubscriptionModel).filter(
                models.SubscriptionModel.chat_id == sub_data.chat_id,
                models.SubscriptionModel.type == "venue",
                models.SubscriptionModel.value == venue_key
            ).first()
            if not existing_venue:
                venue_sub = models.SubscriptionModel(
                    chat_id=sub_data.chat_id,
                    type="venue",
                    value=venue_key
                )
                db.add(venue_sub)
        db.commit()
        return {"status": "added", "message": f"Subscribed to {team or sub_data.team_name}"}


@app.get("/subscriptions/{chat_id}")
def get_user_subscriptions(chat_id: int, payload: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if int(payload["sub"]) != chat_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    subs = db.query(models.SubscriptionModel).filter(
        models.SubscriptionModel.chat_id == chat_id
    ).all()
    teams = [s.value for s in subs if s.type == "team"]
    venues = [s.value for s in subs if s.type == "venue"]
    return {"chat_id": chat_id, "subscriptions": teams, "venues": venues}


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

frontend_path = Path(__file__).resolve().parent.parent / "Frontend"


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    from fastapi.responses import FileResponse, HTMLResponse
    import mimetypes

    resolved = (frontend_path / full_path).resolve() if full_path else (frontend_path / "index.html").resolve()

    if not str(resolved).startswith(str(frontend_path.resolve())):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")

    if not resolved.exists() or not resolved.is_file():
        resolved = frontend_path / "index.html"

    if not resolved.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")

    media_type, _ = mimetypes.guess_type(str(resolved))
    return FileResponse(str(resolved), media_type=media_type or "text/html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
