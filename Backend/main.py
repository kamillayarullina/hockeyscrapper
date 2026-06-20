import sys
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Backend import models
from Backend.database import engine, get_db
from Backend.security import get_password_hash, verify_password
from Backend.jwt_auth import create_token, get_current_user
from services.team_matcher import get_team_info, normalize_team_name

import random

test_code = {}
_code_created_at = {}
_last_forgot_request = {}
CODE_TTL_SECONDS = 300

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="HockeyScrapper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conf_email = ConnectionConfig(
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "hqbo bhdk cxfg gabq"),
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "sakirovsamir401@gmail.com"),
    MAIL_FROM = os.getenv("MAIL_USERNAME", "sakirovsamir401@gmail.com"),
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "True") == "True",
    MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", "False") == "True",
) 

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    telegram: str
    password: str

    @field_validator("password")
    def password_valid(cls, v):
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

class NewPasswordRequest(BaseModel):
    email: EmailStr
    code: int
    new_password: str

    @field_validator("new_password")
    def password_valid(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v

class LinkCodeRequest(BaseModel):
    chat_id: int

@app.post("/register")
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.UserModel).filter(models.UserModel.email == user_data.email).first()
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
                email=user_data.email,
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
async def forgot_password(request: dict, db: Session = Depends(get_db)):
    email = request.get("email", "")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    user = db.query(models.UserModel).filter(models.UserModel.email == email).first()
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
    user = db.query(models.UserModel).filter(models.UserModel.email == request.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Пользователь не найден")

    user_code = test_code.get(request.email)
    if not user_code:
        raise HTTPException(status_code=400, detail="Код не запрашивался")

    created = _code_created_at.get(request.email, 0)
    if time.time() - created > CODE_TTL_SECONDS:
        test_code.pop(request.email, None)
        _code_created_at.pop(request.email, None)
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
    user = db.query(models.UserModel).filter(models.UserModel.chat_id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "chat_id": user.chat_id,
        "username": user.username,
        "email": user.email,
        "telegram": user.telegram
    }

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
    return {"code": code, "link": f"https://t.me/HockeyScrAppeer_bot?start={code}"}

@app.post("/subscription/toggle")
def toggle_subscription(sub_data: SubscriptionToggle, db: Session = Depends(get_db)):
    existing = db.query(models.SubscriptionModel).filter(
        models.SubscriptionModel.chat_id == sub_data.chat_id,
        models.SubscriptionModel.type == "team",
        models.SubscriptionModel.value == sub_data.team_name.lower()
    ).first()

    if existing:
        db.delete(existing)
        team_info = get_team_info(sub_data.team_name)
        if team_info:
            venue_value = f"{team_info['city']}, {team_info['venue']}".lower()
            db.query(models.SubscriptionModel).filter(
                models.SubscriptionModel.chat_id == sub_data.chat_id,
                models.SubscriptionModel.type == "venue",
                models.SubscriptionModel.value == venue_value
            ).delete()
        db.commit()
        return {"status": "removed", "message": f"Unsubscribed from {sub_data.team_name}"}
    else:
        new_sub = models.SubscriptionModel(
            chat_id=sub_data.chat_id,
            type="team",
            value=sub_data.team_name.lower()
        )
        db.add(new_sub)
        db.commit()
        team_info = get_team_info(sub_data.team_name)
        if team_info:
            venue_value = f"{team_info['city']}, {team_info['venue']}".lower()
            existing_venue = db.query(models.SubscriptionModel).filter(
                models.SubscriptionModel.chat_id == sub_data.chat_id,
                models.SubscriptionModel.type == "venue",
                models.SubscriptionModel.value == venue_value
            ).first()
            if not existing_venue:
                venue_sub = models.SubscriptionModel(
                    chat_id=sub_data.chat_id,
                    type="venue",
                    value=venue_value
                )
                db.add(venue_sub)
                db.commit()
        return {"status": "added", "message": f"Subscribed to {sub_data.team_name}"}

@app.get("/subscriptions/{chat_id}")
def get_user_subscriptions(chat_id: int, db: Session = Depends(get_db)):
    subs = db.query(models.SubscriptionModel).filter(
        models.SubscriptionModel.chat_id == chat_id
    ).all()
    teams = [s.value for s in subs if s.type == "team"]
    return {"chat_id": chat_id, "subscriptions": teams}

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
