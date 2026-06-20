from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from Backend.database import Base


class UserModel(Base):
    __tablename__ = "users"

    chat_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=True)
    telegram: Mapped[str] = mapped_column(nullable=True)
    password_hash: Mapped[str] = mapped_column(nullable=True)
    link_code: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[int] = mapped_column(default=1)
    registered_at = Column(DateTime, server_default=func.now())


class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    chat_id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(primary_key=True)
    created_at = Column(DateTime, server_default=func.now())


class MatchModel(Base):
    __tablename__ = "matches"

    match_id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=True)
    date: Mapped[str] = mapped_column(nullable=True, index=True)
    place: Mapped[str] = mapped_column(nullable=True)
    venue: Mapped[str] = mapped_column(nullable=True)
    city: Mapped[str] = mapped_column(nullable=True)
    teams: Mapped[str] = mapped_column(nullable=True)
    price_min: Mapped[str] = mapped_column(nullable=True)
    price_max: Mapped[str] = mapped_column(nullable=True)
    availability: Mapped[str] = mapped_column(nullable=True)
    link: Mapped[str] = mapped_column(nullable=True)
    source: Mapped[str] = mapped_column(nullable=True)
    sources: Mapped[str] = mapped_column(default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class NotifiedEventModel(Base):
    __tablename__ = "notified_events"

    event_id: Mapped[str] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(primary_key=True)
    notified_at = Column(DateTime, server_default=func.now())


class SettingModel(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(nullable=True)


class ProxyModel(Base):
    __tablename__ = "proxies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    url: Mapped[str] = mapped_column(nullable=False)
    proxy_type: Mapped[str] = mapped_column(default="http")
    country: Mapped[str] = mapped_column(default="")
    enabled: Mapped[int] = mapped_column(default=1)
    note: Mapped[str] = mapped_column(default="")
