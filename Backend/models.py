from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    telegram: Mapped[str] = mapped_column(nullable=False)

    password_hash: Mapped[str] = mapped_column(nullable=False)

    # Связь: один пользователь может иметь много подписок
    subscriptions = relationship("SubscriptionModel", back_populates="user")

class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    team_name: Mapped[str] = mapped_column(nullable=False, index=True)
    user = relationship("UserModel", back_populates="subscriptions")