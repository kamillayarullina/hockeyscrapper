from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

import models
from database import engine, get_db
from security import get_password_hash, verify_password

# Автоматически создаем таблицы в PostgreSQL при старте
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="HockeyScrapper API")

# --- СХЕМЫ ДАННЫХ (Pydantic) ---
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    telegram: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SubscriptionToggle(BaseModel):
    user_id: int
    team_name: str

# --- ЭНДПОИНТЫ (Ручки API) ---

@app.get("/")
def home():
    return {"status": "norm", "message": "Бэкенд HockeyScrapper работает!"}

# 1. РЕГИСТРАЦИЯ (для register.html)
@app.post("/register")
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    # Проверяем, нет ли уже такого email в базе
    existing_user = db.query(models.UserModel).filter(models.UserModel.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже зарегистрирован"
        )
    
    # Хэшируем пароль и сохраняем в БД
    hashed_password = get_password_hash(user_data.password)
    new_user = models.UserModel(
        username=user_data.username,
        email=user_data.email,
        telegram=user_data.telegram,
        password_hash=hashed_password
    )
    
    db.add(new_user)
    db.commit()      # Фиксируем изменения в PostgreSQL
    db.refresh(new_user)
    
    return {
        "status": "success",
        "message": "Пользователь успешно зарегистрирован!",
        "user_id": new_user.id
    }

# 2. ВХОД (для vhod.html)
@app.post("/login")
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    # Ищем пользователя по email
    user = db.query(models.UserModel).filter(models.UserModel.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный email или пароль"
        )
    
    # Проверяем, совпадает ли пароль с хэшем из базы
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный email или пароль"
        )
    
    # Если всё ок, возвращаем данные пользователя для страницы профиля (main.html)
    return {
        "status": "success",
        "message": "Вход успешно выполнен!",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "telegram": user.telegram
        }
    }

@app.post("/subscription/toggle")
def toggle_subscription(sub_data: SubscriptionToggle, db: Session = Depends(get_db)):
    #Ищем в базе, есть ли уже у этого юзера подписка на эту команду
    existing_sub = db.query(models.SubscriptionModel).filter(
        models.SubscriptionModel.team_name == sub_data.team_name,
        models.SubscriptionModel.user_id == sub_data.user_id
        ).first()
    
    #Если подписка найдена — удаляем её (действие "Отписаться")
    if existing_sub:
        db.delete(existing_sub)
        db.commit()
        return {"status": "removed", "message": f"Вы отписались от команды {sub_data.team_name}"}
    
    else:
        new_sub = models.SubscriptionModel(
            user_id=sub_data.user_id,
            team_name=sub_data.team_name
        )

        db.add(new_sub)
        db.commit()

        return {"status": "added", "message": f"Вы успешно подписались на команду {sub_data.team_name}"}
    
@app.get("/subscriptions/{user_id}")
def get_user_subscriptions(user_id: int, db: Session=Depends(get_db)):
    subs = db.query(models.SubscriptionModel).filter(
        models.SubscriptionModel.user_id == user_id
    ).all()

    teams = [sub.team_name for sub in subs]

    return {"user_id": user_id, "subscriptions": teams}