from datetime import datetime

from sqlalchemy import Column, DateTime, func, text
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
    is_active: Mapped[int] = mapped_column(default=1, server_default=text("1"))
    avatar_url: Mapped[str] = mapped_column(nullable=True)
    premium_plan: Mapped[str] = mapped_column(default="free")
    premium_until: Mapped[datetime] = mapped_column(nullable=True)
    registered_at = Column(DateTime, server_default=func.now())


class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    chat_id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(primary_key=True)
    created_at = Column(DateTime, server_default=func.now())


class PaidTeamSubscriptionModel(Base):
    """Monthly access and renewal settings for a paid team subscription."""

    __tablename__ = "paid_team_subscriptions"

    chat_id: Mapped[int] = mapped_column(primary_key=True)
    team_name: Mapped[str] = mapped_column(primary_key=True)
    expires_at: Mapped[datetime] = mapped_column(nullable=False, index=True)
    auto_renew: Mapped[bool] = mapped_column(default=False)
    payment_method_id: Mapped[str] = mapped_column(nullable=True)
    auto_renew_consented_at: Mapped[datetime] = mapped_column(nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class BillingProfileModel(Base):
    """A YooKassa payment method saved once for all of a user's paid teams."""

    __tablename__ = "billing_profiles"

    chat_id: Mapped[int] = mapped_column(primary_key=True)
    payment_method_id: Mapped[str] = mapped_column(nullable=False)
    consented_at: Mapped[datetime] = mapped_column(nullable=False)
    saved_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


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
    updated_at = Column(DateTime, server_default=func.now())


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


class PaymentModel(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(index=True)
    plan_code: Mapped[str] = mapped_column(nullable=False)
    provider: Mapped[str] = mapped_column(nullable=False)
    provider_payment_id: Mapped[str] = mapped_column(nullable=True, unique=True)
    amount_kopeks: Mapped[int] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(default="RUB")
    status: Mapped[str] = mapped_column(default="pending", index=True)
    idempotency_key: Mapped[str] = mapped_column(nullable=False, unique=True)
    # The team unlocked by this payment. Nullable for payment rows created before this feature.
    team_name: Mapped[str] = mapped_column(nullable=True)
    auto_renew_requested: Mapped[bool] = mapped_column(default=False)
    save_payment_method_requested: Mapped[bool] = mapped_column(default=False)
    created_at = Column(DateTime, server_default=func.now())
    paid_at = Column(DateTime, nullable=True)
