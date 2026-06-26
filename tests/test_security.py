import pytest
from Backend.security import get_password_hash, verify_password


class TestGetPasswordHash:

    def test_returns_string(self):
        result = get_password_hash("testpassword")
        assert isinstance(result, str)

    def test_starts_with_bcrypt_prefix(self):
        result = get_password_hash("testpassword")
        assert result.startswith("$2b$")

    def test_different_salts(self):
        h1 = get_password_hash("testpassword")
        h2 = get_password_hash("testpassword")
        assert h1 != h2

    def test_handles_special_characters(self):
        result = get_password_hash("p@ss!0#")
        assert result.startswith("$2b$")

    def test_handles_empty_string(self):
        result = get_password_hash("")
        assert isinstance(result, str)

    def test_handles_unicode(self):
        result = get_password_hash("пароль")
        assert isinstance(result, str)


class TestVerifyPassword:

    def test_correct_password(self):
        hashed = get_password_hash("testpassword")
        assert verify_password("testpassword", hashed) is True

    def test_incorrect_password(self):
        hashed = get_password_hash("testpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_empty_password(self):
        hashed = get_password_hash("testpassword")
        assert verify_password("", hashed) is False

    def test_wrong_password_empty_hash(self):
        assert verify_password("test", "") is False
