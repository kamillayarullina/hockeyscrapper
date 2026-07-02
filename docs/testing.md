# Testing Strategy and QA Report — HockeyScrapper 🏒

This document outlines the testing architecture, module coverage targets, automated quality gates, and Continuous Integration (CI) checks for the HockeyScrapper application.

## 1. Testing Infrastructure & Environment

We utilize **Pytest** as our primary test runner due to its native support for asynchronous execution via `pytest-asyncio` (required for `FastAPI` and `aiogram` bots).

### Test Databases & Mocking

* **Database Isolation:** To avoid state pollution, all backend integration tests run against an in-memory **SQLite database** (`sqlite:///:memory:`). The DB schema is rebuilt from scratch for every single test case using the `_setup_db` fixture in `tests/conftest.py`.

* **FastAPI Client:** Fast and isolated API endpoint testing is handled by standard FastAPI `TestClient` injection.

* **Network Mocking:** For Playwright-based web parsers, we mock outgoing HTTP requests and DOM structures to prevent network variance and rate-limiting from causing flaky builds in CI.

## 2. Test Locations & Modules

All test assets are maintained in the `tests/` directory:

* `tests/conftest.py` — Database session overrides and global pytest fixtures.
* `tests/test_jwt_auth.py` — Unit tests for token creation, encoding, expiration, and invalid signatures.
* `tests/test_security.py` — Unit tests for password hashing correctness and hash matching (`bcrypt`).
* `tests/test_team_matcher.py` — Unit tests for team name normalization and extraction logic.
* `tests/test_api_integration.py` — Integration tests for authentication flow and profile endpoints.
* `tests/test_fault_tolerance.py` — **[QRT-01]** Verifies the parser's retry mechanisms and isolation under network downtime (5xx errors).
* `tests/test_auth_confidentiality.py` — **[QRT-02]** Verifies that secure API endpoints block unauthorized actors without JWT credentials.
* `tests/test_notification_performance.py` — **[QRT-03]** Measures the speed of the notification matching service under load (50 matches simultaneously).

## 3. Coverage Analysis & Targets

We enforce a strict quality minimum of **at least 30% line coverage** for all critical backend and service modules.

### Target Modules vs Coverage Targets

| Module File | Critical Logic | Expected Target Coverage | Actual Status |
| ----- | ----- | ----- | ----- |
| `Backend/security.py` | Password encryption & verification | $\ge 80\%$ | Fully Covered |
| `Backend/jwt_auth.py` | Token signature, expiration checks, and Dependency-injection | $\ge 80\%$ | Fully Covered |
| `services/team_matcher.py` | Normalizing KHL and club naming conventions | $\ge 90\%$ | Fully Covered |
| `parsers/base_parser.py` | Playwright loader, user-agent generation, and retry logic | $\ge 40\%$ | Covered via Mock integration |
| `services/notifications` | Matching ticket updates to bot subscription models | $\ge 30\%$ | Covered via performance benchmark |

## 4. Additional QA Check — Dependency Vulnerability Audit

To secure the HockeyScrapper application against supply-chain attacks, we have introduced an automatic **dependency vulnerability audit** step utilizing **`pip-audit`**.

### 1. Options Considered

* **Safety:** Very popular tool for checking python packages, but its public database is often delayed unless a paid API key is supplied.
* **Pip-audit (Selected):** Backed by the PyPI advisory database, runs natively without keys, and scans local packages against active OSV (Open Source Vulnerabilities) databases.

### 2. QA Objective & Risk Addressed

* **Objective:** Ensure no third-party libraries listed in `requirements.txt` contain known, unpatched security vulnerabilities (CVEs).
* **Why it matters:** Web scraping frequently pulls packages that handle raw HTML, network sockets, and browser drivers (`playwright`, `aiohttp`, `beautifulsoup4`). A vulnerability in those libraries could lead to Remote Code Execution (RCE) or arbitrary file read on the deployed crawler server.

### 3. CI Integration & Limitations

* **CI Stage:** This check runs inside the main `test` job of the `Tests & QA` workflow (`.github/workflows/tests.yml`) right before the test suite. If any vulnerability is detected, **the build fails immediately**, preventing deployment.
* **Limitations:** It only scans packages listed in `requirements.txt`. Native system dependencies (such as Chromium library updates or host OS CVEs) are outside its scope and must be scanned at the Docker base-image level.
