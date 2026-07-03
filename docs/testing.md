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
* `tests/test_notifier.py` — Unit tests for notification dispatch, deduplication (`was_event_notified` check), and message formatting per reason type (new, available, sold-out, changed).
* `tests/test_parser_runner.py` — Integration test for the full parser pipeline: config loading, parser creation via `ParserFactory`, match data flow, and `Notifier` invocation with correct reason and subscriber list.
* `tests/test_qrt_bandit.py` — **[QRT-002 companion]** Validates that `[tool.bandit]` is configured in `pyproject.toml` and the bandit security-lint command completes within 30 seconds.
* `tests/test_qrt_coverage.py` — **[QRT-001 companion]** Validates that `.coveragerc` exists, `fail_under` is set to at least 80, and `Backend` + `services` are in the source list.
* `tests/test_qrt_ruff.py` — **[QRT-004 companion]** Validates that `[tool.ruff]` is configured in `pyproject.toml` and `ruff check .` exits with code 0.
* `tests/test_qrt_startup.py` — **[QRT-005]** Verifies that all top-level module imports succeed without `ImportError`, the CLI argument parser responds within 10 seconds, and `load_env()` degrades gracefully when no `.env` file is present.

## 3. Coverage Analysis & Targets

We enforce a **global minimum of 30% line coverage** (`fail_under = 30` in `.coveragerc`) across `Backend/` and `services/` modules. The same threshold applies to every critical module listed below.

### Critical Modules

| Module File | Critical Logic | Target Coverage | Enforced Via |
| ----- | ----- | ----- | ----- |
| `Backend/security.py` | Password encryption & verification | ≥ 30% | `.coveragerc` (global `fail_under`) |
| `Backend/jwt_auth.py` | Token signature, expiration checks, and Dependency-injection | ≥ 30% | `.coveragerc` (global `fail_under`) |
| `services/team_matcher.py` | Normalizing KHL and club naming conventions | ≥ 30% | `.coveragerc` (global `fail_under`) |
| `parsers/base_parser.py` | Playwright loader, user-agent generation, and retry logic | ≥ 30% | `.coveragerc` (global `fail_under`) |
| `services/notifier.py` | Deduplication and dispatch of Telegram notifications | ≥ 30% | `.coveragerc` (global `fail_under`) |

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
