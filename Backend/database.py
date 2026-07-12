import os
import logging
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///data/tickets.db"
)

logger.info("DATABASE_URL = %s", DATABASE_URL)

if DATABASE_URL.startswith("sqlite"):
    db_path = DATABASE_URL.replace("sqlite:///", "", 1)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

    logger.info("Using SQLite at %s", db_path)
else:
    engine = create_engine(DATABASE_URL)
    logger.info("Using PostgreSQL")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_schema() -> None:
    """Apply additive billing fields to installations created before billing."""
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("users")}
    additions = {
        "premium_plan": "VARCHAR DEFAULT 'free'",
        "premium_until": "TIMESTAMP",
    }
    with engine.begin() as connection:
        for column, definition in additions.items():
            if column not in existing_columns:
                connection.execute(text(f"ALTER TABLE users ADD COLUMN {column} {definition}"))

    if "payments" in inspector.get_table_names():
        payment_columns = {column["name"] for column in inspector.get_columns("payments")}
    else:
        payment_columns = set()
    payment_additions = {
        "team_name": "VARCHAR",
        "auto_renew_requested": "BOOLEAN DEFAULT 0",
    }
    if "payments" in inspector.get_table_names():
        with engine.begin() as connection:
            for column, definition in payment_additions.items():
                if column not in payment_columns:
                    connection.execute(text(f"ALTER TABLE payments ADD COLUMN {column} {definition}"))

    if "paid_team_subscriptions" in inspector.get_table_names():
        subscription_columns = {
            column["name"] for column in inspector.get_columns("paid_team_subscriptions")
        }
        if "plan_code" not in subscription_columns:
            with engine.begin() as connection:
                connection.execute(text(
                    "ALTER TABLE paid_team_subscriptions "
                    "ADD COLUMN plan_code VARCHAR DEFAULT 'team_monthly'"
                ))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
