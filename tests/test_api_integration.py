import time
from unittest.mock import patch
import pytest


@pytest.fixture(autouse=True)
def clear_rate_limits():
    from Backend import main as api_module
    api_module._last_forgot_request.clear()
    api_module.test_code.clear()
    api_module._code_created_at.clear()
    yield


class TestRegister:

    def test_register_success(self, client):
        response = client.post("/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "telegram": "@testuser",
            "password": "testpassword123",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "access_token" in data
        assert data["chat_id"] < 0

    def test_register_duplicate_email(self, client):
        client.post("/register", json={
            "username": "user1",
            "email": "dup@example.com",
            "telegram": "@user1",
            "password": "testpassword123",
        })
        response = client.post("/register", json={
            "username": "user2",
            "email": "dup@example.com",
            "telegram": "@user2",
            "password": "testpassword456",
        })
        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()

    def test_register_short_password(self, client):
        response = client.post("/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "telegram": "@testuser",
            "password": "short1",
        })
        assert response.status_code == 422

    def test_register_no_letter_password(self, client):
        response = client.post("/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "telegram": "@testuser",
            "password": "1234567890",
        })
        assert response.status_code == 422

    def test_register_invalid_email(self, client):
        response = client.post("/register", json={
            "username": "testuser",
            "email": "notanemail",
            "telegram": "@testuser",
            "password": "testpassword123",
        })
        assert response.status_code == 422


class TestLogin:

    def test_login_success(self, client):
        client.post("/register", json={
            "username": "loginuser",
            "email": "login@example.com",
            "telegram": "@loginuser",
            "password": "testpassword123",
        })
        response = client.post("/login", json={
            "email": "login@example.com",
            "password": "testpassword123",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "access_token" in data
        assert data["user"]["email"] == "login@example.com"

    def test_login_wrong_password(self, client):
        client.post("/register", json={
            "username": "loginuser2",
            "email": "login2@example.com",
            "telegram": "@loginuser2",
            "password": "testpassword123",
        })
        response = client.post("/login", json={
            "email": "login2@example.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 400

    def test_login_nonexistent_user(self, client):
        response = client.post("/login", json={
            "email": "nobody@example.com",
            "password": "anything",
        })
        assert response.status_code == 400

    def test_login_invalid_email(self, client):
        response = client.post("/login", json={
            "email": "notanemail",
            "password": "testpassword123",
        })
        assert response.status_code == 422


class TestForgotPassword:

    def _register_user(self, client, email="forgot@example.com"):
        client.post("/register", json={
            "username": "forgotuser",
            "email": email,
            "telegram": "@forgotuser",
            "password": "testpassword123",
        })

    def test_forgot_password_success(self, client):
        self._register_user(client)
        with patch("Backend.main.FastMail") as mock_fastmail:
            mock_fastmail.return_value.send_message = _AsyncMock()
            response = client.post("/forgot_password", json={
                "email": "forgot@example.com",
            })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_forgot_password_no_email(self, client):
        response = client.post("/forgot_password", json={})
        assert response.status_code == 400
        assert "required" in response.json()["detail"].lower()

    def test_forgot_password_nonexistent_user(self, client):
        response = client.post("/forgot_password", json={
            "email": "nobody@example.com",
        })
        assert response.status_code == 400

    def test_forgot_password_rate_limit(self, client):
        self._register_user(client, email="ratelimit@example.com")
        with patch("Backend.main.FastMail"):
            client.post("/forgot_password", json={"email": "ratelimit@example.com"})
            response = client.post("/forgot_password", json={"email": "ratelimit@example.com"})
        assert response.status_code == 429


class TestNewPassword:

    def _register_and_request_code(self, client, email="newpwd@example.com"):
        client.post("/register", json={
            "username": "newpwduser",
            "email": email,
            "telegram": "@newpwduser",
            "password": "testpassword123",
        })
        with patch("Backend.main.FastMail") as mock_fastmail:
            mock_fastmail.return_value.send_message = _AsyncMock()
            client.post("/forgot_password", json={"email": email})

    def test_new_password_success(self, client):
        email = "newpwd@example.com"
        self._register_and_request_code(client, email)

        from Backend.main import test_code
        code = test_code[email]["code"]

        response = client.post("/new_password", json={
            "email": email,
            "code": code,
            "new_password": "newsecurepassword1",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Password changed" in data["message"]

    def test_new_password_wrong_code(self, client):
        email = "wrongcode@example.com"
        self._register_and_request_code(client, email)

        response = client.post("/new_password", json={
            "email": email,
            "code": 999999,
            "new_password": "newsecurepassword1",
        })
        assert response.status_code == 400

    def test_new_password_expired_code(self, client):
        email = "expired@example.com"
        self._register_and_request_code(client, email)

        from Backend.main import _code_created_at
        _code_created_at[email] = time.time() - 9999

        from Backend.main import test_code
        code = test_code[email]["code"]

        response = client.post("/new_password", json={
            "email": email,
            "code": code,
            "new_password": "newsecurepassword1",
        })
        assert response.status_code == 400
        assert "истёк" in response.json()["detail"].lower()

    def test_new_password_no_code_requested(self, client):
        response = client.post("/new_password", json={
            "email": "neverrequested@example.com",
            "code": 123456,
            "new_password": "newsecurepassword1",
        })
        assert response.status_code == 400

    def test_new_password_short_password(self, client):
        email = "shortpwd@example.com"
        self._register_and_request_code(client, email)

        from Backend.main import test_code
        code = test_code[email]["code"]

        response = client.post("/new_password", json={
            "email": email,
            "code": code,
            "new_password": "short1",
        })
        assert response.status_code == 422


class TestMe:

    def test_get_me_authenticated(self, client):
        reg_resp = client.post("/register", json={
            "username": "meuser",
            "email": "me@example.com",
            "telegram": "@meuser",
            "password": "testpassword123",
        })
        token = reg_resp.json()["access_token"]
        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"

    def test_get_me_unauthenticated(self, client):
        response = client.get("/me")
        assert response.status_code == 401

    def test_get_me_invalid_token(self, client):
        response = client.get(
            "/me", headers={"Authorization": "Bearer invalidtoken"}
        )
        assert response.status_code == 401


class TestStats:

    def test_stats_returns_counts(self, client):
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        for key in ("users", "team_subs", "venue_subs", "matches"):
            assert key in data


class _AsyncMock:
    def __init__(self):
        self._call_count = 0

    async def __call__(self, *args, **kwargs):
        self._call_count += 1
