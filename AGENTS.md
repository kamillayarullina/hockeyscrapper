# HockeyScrapper — Agent Guidance

> **Project status:** Archived — all MVP milestones (v1, v2, v3) delivered. The repository is maintained for reference and customer handover. See [`docs/customer-handover.md`](docs/customer-handover.md) for deployment and operational instructions.

This file provides operating instructions for coding agents working in this repository. See [README.md](README.md) for a project overview and [CONTRIBUTING.md](CONTRIBUTING.md) for human contributor workflow.

## Setup and Verification Commands

```bash
# Environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env              # fill in BOT_TOKEN for bot-dependent work

# Lint
ruff check .

# Tests
pytest -v
pytest --cov=Backend --cov=services --cov-fail-under=30

# Security
pip-audit -r requirements.txt
bandit -r Backend services -ll -ii

# Links
lychee .

# Run
python -m main --api-only          # API + frontend on localhost:8000
python -m main --bot-only          # Telegram bot only
python -m main --all               # API + bot + parser
```

## Repository Workflow

- **Default branch:** `main`
- **Feature branches:** `<issue-number>-<short-description>` from `main`
- **PR target:** `main`
- **Merge method:** merge commit
- **Required CI:** ruff check + pytest + pip-audit + bandit + lychee must all pass
- **Review:** at least one approval required before merge
- **Commit style:** `feat:`, `fix:`, `test:`, `docs:`, `chore:`

## Safety Cautions

- **Do not commit real secrets.** The `.env` file is gitignored; never commit it or paste tokens into code.
- **Do not expose credentials** in logs, error messages, or test output.
- **Do not modify `.github/workflows/`** CI files without verifying the impact on pipeline security.
- **Do not commit large binary files** (e.g., Playwright browser binaries, database files).
- The `.env.example` contains placeholder values — use those, not real credentials.

## Maintained Documentation

- [Development Process](docs/development-process.md) — workflow, CI/CD, config, reproducible setup
- [Architecture](docs/architecture/README.md) — system design, ADRs, static/dynamic/deployment views
- [Testing Strategy](docs/testing.md) — test locations, coverage targets, QRTs
- [Quality Requirements](docs/quality-requirements.md) — QR-01 through QR-05
- [User Acceptance Tests](docs/user-acceptance-tests.md) — UAT scenarios
- [Customer Handover](docs/customer-handover.md) — deployment, configuration, troubleshooting, known limitations
