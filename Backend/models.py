# Database configuration and models definition
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

# --- User Model ---
# Represents users registered in the system
class UserModel(Base):
    __tablename__ = "users"

    # Primary key and user profile details
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    telegram: Mapped[str] = mapped_column(nullable=False)

    # Hashed password for secure authentication
    password_hash: Mapped[str] = mapped_column(nullable=False)

    # Relationship: One user can have multiple team subscriptions (One-to-Many)
    subscriptions = relationship("SubscriptionModel", back_populates="user")


# --- Subscription Model ---
# Represents the hockey teams that users subscribe to for notifications
class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign key linking the subscription to a specific user
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    team_name: Mapped[str] = mapped_column(nullable=False, index=True)
    
    # Relationship: Links the subscription back to its owner (UserModel)
    user = relationship("UserModel", back_populates="subscriptions")


# --- Match Model ---
# Represents the sports matches tracked by the system
class MatchModel(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Names of the competing teams
    home_team: Mapped[str] = mapped_column(nullable=True, index=True)
    away_team: Mapped[str] = mapped_column(nullable=True, index=True)

    # Boolean flag showing whether tickets are currently available for sale
    tickets_status: Mapped[bool] = mapped_column(default=False)