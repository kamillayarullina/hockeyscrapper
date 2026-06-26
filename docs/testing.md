# Testing Strategy

## Overview

This document describes the testing approach for the HockeyScrapper project.
Tests are located in `tests/` and run via pytest with coverage reporting.

## Test Types

### Unit Tests

| Module | File | Scope |
|---|---|---|
| `services/team_matcher.py` | `tests/test_team_matcher.py` | Team name extraction, normalization, team info lookup |
| `Backend/security.py` | `tests/test_security.py` | Password hashing and verification |
| `Backend/jwt_auth.py` | `tests/test_jwt_auth.py` | JWT token creation, verification, expiration |

### Integration Tests

| Endpoint | File | Scope |
|---|---|---|
| `POST /register` | `tests/test_api_integration.py` | User registration, duplicate emails, password validation |
| `POST /login` | `tests/test_api_integration.py` | Authentication, wrong credentials |
| `POST /forgot_password` | `tests/test_api_integration.py` | Password reset request, rate limiting |
| `POST /new_password` | `tests/test_api_integration.py` | Code verification, expiration, password update |
| `GET /me` | `tests/test_api_integration.py` | Authenticated profile access, invalid tokens |
| `GET /stats` | `tests/test_api_integration.py` | Statistics endpoint |

## Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ -v --cov=Backend --cov=services --cov-report=term

# With coverage report
python -m pytest tests/ -v --cov=Backend --cov=services --cov-report=html
```

## Coverage

Coverage is configured in `.coveragerc`. Critical modules:

| Module | Target coverage |
|---|---|
| `Backend/security.py` | >= 80% |
| `Backend/jwt_auth.py` | >= 80% |
| `services/team_matcher.py` | >= 90% |
| `Backend/main.py` (API endpoints) | >= 30% |

## CI

Tests and QA checks run automatically on push/PR to `main` via
`.github/workflows/tests.yml`.

## Additional QA Check

**Bandit** — Python security linter — runs as an additional QA step in CI.
It is distinct from unit tests, integration tests, coverage, and link checking.

## Quality Requirement Tests

Quality requirement tests (QRTs) are documented in
`docs/quality-requirement-tests.md` and linked to specific quality
requirements in `docs/quality-requirements.md`.
