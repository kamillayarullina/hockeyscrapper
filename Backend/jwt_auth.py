import logging
import os
import warnings
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
if not SECRET_KEY:
    SECRET_KEY = "hockeyscrapper-secret-change-in-production"
    warnings.warn("JWT_SECRET_KEY is not set! Using insecure default key.")
    logging.getLogger(__name__).warning("JWT_SECRET_KEY is not set! Using insecure default key.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30

security = HTTPBearer()


def create_token(chat_id: int, email: str) -> str:
    payload = {
        "sub": str(chat_id),
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    # With auto_error=True (the default for HTTPBearer), this dependency will
    # automatically raise a 401 HTTPException if the Authorization header is missing.
    # However, for direct unit testing and to handle edge cases in integration tests,
    # we add a manual check to ensure credentials are not None.
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return verify_token(credentials.credentials)
