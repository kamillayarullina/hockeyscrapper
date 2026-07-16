import time
import pytest
from unittest.mock import patch, MagicMock

from jose import jwt
from fastapi import HTTPException


from Backend.jwt_auth import (
    create_token,
    verify_token,
    get_current_user,
    SECRET_KEY,
    ALGORITHM,
)


class TestCreateToken:

    def test_returns_string(self):
        token = create_token(chat_id=12345, email="test@example.com")
        assert isinstance(token, str)

    def test_contains_expected_fields(self):
        token = create_token(chat_id=12345, email="test@example.com")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "12345"
        assert payload["email"] == "test@example.com"
        assert "exp" in payload

    def test_negative_chat_id(self):
        token = create_token(chat_id=-1, email="test@example.com")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "-1"

    def test_expiration_is_future(self):
        token = create_token(chat_id=123, email="test@example.com")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["exp"] > time.time()


class TestVerifyToken:

    def test_valid_token(self):
        token = create_token(chat_id=123, email="test@example.com")
        payload = verify_token(token)
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"

    def test_expired_token(self):
        with patch("Backend.jwt_auth.datetime") as mock_datetime:
            mock_datetime.now.return_value = __import__("datetime").datetime(
                2020, 1, 1, tzinfo=__import__("datetime").timezone.utc
            )
            token = create_token(chat_id=123, email="test@example.com")

        with pytest.raises(HTTPException) as exc:
            verify_token(token)
        assert exc.value.status_code == 401

    def test_invalid_signature(self):
        token = create_token(chat_id=123, email="test@example.com")
        parts = token.split(".")
        tampered = parts[0] + "." + parts[1] + ".invalidsignature"
        with pytest.raises(HTTPException) as exc:
            verify_token(tampered)
        assert exc.value.status_code == 401

    def test_malformed_token(self):
        with pytest.raises(HTTPException) as exc:
            verify_token("not-a-token")
        assert exc.value.status_code == 401

    def test_empty_token(self):
        with pytest.raises(HTTPException) as exc:
            verify_token("")
        assert exc.value.status_code == 401


class TestGetCurrentUser:

    def test_with_valid_credentials(self):
        token = create_token(chat_id=123, email="test@example.com")
        mock_credentials = MagicMock()
        mock_credentials.credentials = token
        result = get_current_user(credentials=mock_credentials)
        assert result["sub"] == "123"

    def test_with_none_credentials(self):
        with pytest.raises(HTTPException) as exc:
            get_current_user(credentials=None)
        assert exc.value.status_code == 401
        assert "Not authenticated" in str(exc.value.detail)

    def test_with_expired_token(self):
        with patch("Backend.jwt_auth.datetime") as mock_datetime:
            mock_datetime.now.return_value = __import__("datetime").datetime(
                2020, 1, 1, tzinfo=__import__("datetime").timezone.utc
            )
            token = create_token(chat_id=123, email="test@example.com")

        mock_credentials = MagicMock()
        mock_credentials.credentials = token
        with pytest.raises(HTTPException) as exc:
            get_current_user(credentials=mock_credentials)
        assert exc.value.status_code == 401
