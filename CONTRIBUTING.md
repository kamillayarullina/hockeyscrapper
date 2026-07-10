# Contributing to HockeyScrapper

## Setup and Verification

Before submitting changes, ensure your environment is set up and all checks pass:

```bash
# Set up
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env              # fill in BOT_TOKEN

# Lint
ruff check .

# Run all tests
pytest -v

# Run with coverage
pytest --cov=Backend --cov=services --cov-fail-under=30

# Security audit (if pip-audit is installed)
pip-audit -r requirements.txt

# Security linter
bandit -r Backend services -ll -ii

# Link check
lychee .
```

## Branch and PR Workflow

1. Create a feature branch from `main`: `<issue-number>-<short-description>`
2. Make commits with clear messages (`feat:`, `fix:`, `test:`, `docs:`, `chore:`)
3. Open a pull request targeting `main` when ready
4. Ensure all CI checks pass (ruff, pytest, pip-audit, bandit, lychee)
5. Request review from at least one team member
6. Address review feedback; keep the branch up to date with `main`
7. Merge via merge commit after approval and passing CI

## Review Expectations

- At least one approval is required before merging
- Reviews check: code quality, test coverage, adherence to architecture, no secrets committed
- All CI workflows must pass (ci.yml, tests.yml, lychee.yml)
- Changes should be focused on a single concern

## Maintained Documentation

- [Development Process](docs/development-process.md) — full workflow, CI/CD, config management
- [Architecture](docs/architecture/README.md) — system design, ADRs
- [Testing Strategy](docs/testing.md) — test locations, coverage targets
- [Definition of Done](docs/definition-of-done.md) — completion standard
- [Quality Requirements](docs/quality-requirements.md) — quality attributes
