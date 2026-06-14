from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session



models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="HockeyScrapper API")


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    telegram: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class SubscriptionToggle(BaseModel):
    chat_id: int
    team_name: str



        username=user_data.username,
        email=user_data.email,
        telegram=user_data.telegram,
        password_hash=hashed,
        is_active=1
    )

        "user": {
            "chat_id": user.chat_id,
            "username": user.username,
            "email": user.email,
            "telegram": user.telegram
        }
    }


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
    return {"code": code, "link": f"https://t.me/HockeyScrapper_bot?start={code}"}


@app.post("/subscription/toggle")
def toggle_subscription(sub_data: SubscriptionToggle, db: Session = Depends(get_db)):
    existing = db.query(models.SubscriptionModel).filter(
        models.SubscriptionModel.chat_id == sub_data.chat_id,
        models.SubscriptionModel.type == "team",
        models.SubscriptionModel.value == sub_data.team_name.lower()
    ).first()

    if existing:
        db.delete(existing)
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
    from fastapi.responses import FileResponse, HTMLResponse
    import mimetypes

    file = frontend_path / full_path if full_path else frontend_path / "index.html"

    if not file.exists() or not file.is_file():
        if not full_path or full_path.endswith("/"):
            file = frontend_path / "index.html"
        else:
            file = frontend_path / full_path
            if not file.exists():
                file = frontend_path / "index.html"

    if not file.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")

    media_type, _ = mimetypes.guess_type(str(file))
    return FileResponse(str(file), media_type=media_type or "text/html")
