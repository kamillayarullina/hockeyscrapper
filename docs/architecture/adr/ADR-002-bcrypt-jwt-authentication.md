# ADR-002: Layered Authentication with bcrypt Password Hashing and JWT Token Management

**Status:** Accepted

**Context:** The system provides user registration, login, and password recovery through a REST API (FastAPI). These operations require secure credential storage and stateless session management. The deployment includes a web API (Render web / Docker) and a separate Telegram bot that needs to verify user identity when linking accounts.

**Decision:**

1. **Password hashing** (`Backend/security.py`): Use bcrypt via the `bcrypt` Python library with a unique salt per password (`bcrypt.gensalt()`). Store only the hash (prefixed `$2b$`), never plaintext.
2. **Token-based sessions** (`Backend/jwt_auth.py`): Use JWT (HS256, python-jose) with a 30-day expiry for API authentication. Tokens encode `sub` (chat_id) and `email` and are verified via a Bearer-token dependency (`get_current_user`).
3. **Separation of concerns**: Hashing logic is isolated in `security.py`, token logic in `jwt_auth.py`, and FastAPI route integration in `Backend/main.py`, so each component is independently testable.

**Consequences and tradeoffs:**

- Positive: bcrypt's adaptive cost factor resists brute-force attacks even if the database is compromised, directly addressing QR-003.
- Positive: JWT enables stateless authentication — no server-side session store is needed, simplifying horizontal scaling.
- Positive: Clear separation into three files (`security.py`, `jwt_auth.py`, `Backend/main.py`) with distinct responsibilities makes each unit independently testable and auditable.
- Negative: JWT secret key (`SECRET_KEY`) is hardcoded with a default fallback in `jwt_auth.py:7`; if not overridden via `JWT_SECRET_KEY` environment variable in production, tokens are forgeable.
- Negative: Token revocation requires short expiry times or a blocklist — the current 30-day expiry trades security for UX convenience and means leaked tokens are valid until expiry.
- Negative: Password recovery uses in-memory dicts (`test_code`, `_code_created_at`) which do not survive process restarts, limiting reliability.

**Quality requirements addressed:** QR-003 (Password storage confidentiality) — bcrypt hashing ensures passwords are never stored as plaintext.
