import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend import database as _db

_db.engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_db.SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=_db.engine
)

from Backend.database import Base, get_db  # noqa: E402
from Backend.main import app  # noqa: E402


@pytest.fixture(scope="function", autouse=True)
def _setup_db():
    Base.metadata.drop_all(bind=_db.engine)
    Base.metadata.create_all(bind=_db.engine)
    yield


@pytest.fixture(scope="function")
def db_session(_setup_db):
    session = _db.SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
