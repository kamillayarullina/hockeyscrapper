# Development Process

This document describes the actual development process used by the HockeyScrapper team. It covers backlog management, git workflow, configuration management, CI/CD, and reproducible development environment setup.
---
## 1. Backlog Management

The team uses GitHub Projects to manage the Product Backlog and Sprint Backlogs.

### Boards and Views

- **Product Backlog** — contains all user stories, technical PBIs, and bug reports. Items are prioritized using MoSCoW Priorities.
- **Sprint Backlog** — contains items selected for the current sprint. Each sprint has its own milestone (for example "Sprint 2").
- **Sprint N Backlog** — dedicated boards for specific sprints (for example "Sprint 2 Backlog").

### Workflow States (Columns)

Issues move through the following states in the project boards:

| State | Entry Criteria |
|-------|----------------|
| **Todo** | Issue created with complete template (Type, Priority, Story Points, Acceptance Criteria). Assigned to a developer. |
| **In Progress** | Developer has started working on the issue. A feature branch has been created/PR created. |
| **Done** | PR merged to `main`. All acceptance criteria met. CI checks passed. Review completed. |

### Issue Template

All issues follow a standardized template with the following fields:
- **Type**: Infrastructure, Database, API, Frontend, Testing, Documentation, Deployment, Other
- **MoSCoW Priority**: Must Have, Should Have, Could Have, Won't Have
- **Story Points**: Estimate ( 1, 2, 3, 5, 8)
- **MVP Version**: MVP v1, MVP v2, MVP v3
- **Sprint**: Milestone assignment (e.g., Sprint 2)
- **Assignee**: Developer and Reviewer
- **Acceptance Criteria**: Clear, testable conditions for completion

---

## 2. Git Workflow

### Base Workflow

The team follows a feature branch workflow with pull requests:

```mermaid
gitGraph
  commit id: "Initial commit"
  branch main
  commit id: "main baseline"
  branch feature/issue-131
  checkout feature/issue-131
  commit id: "feat: add admin panel backend"
  commit id: "test: add admin panel tests"
  checkout main
  merge feature/issue-131 id: "Merge PR #131" tag: "v1.0"
  branch feature/issue-132
  checkout feature/issue-132
  commit id: "fix: resolve API error"
  checkout main
  merge feature/issue-132 id: "Merge PR #132"
```

### What the Diagram Shows

The diagram illustrates:
1. **`main` branch** is the stable baseline. All production-ready code lives here.
2. **Feature branches** are created from `main` for each issue (e.g., `153-avatar-feature`).
3. **Commits** are made on the feature branch with conventional commit messages (`feat:`, `fix:`, `test:`, `chore:`, `docs:` or just the action).
4. **Pull Request** is opened when the feature is ready for review.
5. **Merge** happens after approval and Lychee, CI checks pass. The feature branch is merged into `main`.

### How the Team Uses This Workflow

1. **Issue Creation**: A team member creates an issue using the template. The issue is added to the Product Backlog and assigned to a sprint milestone.
2. **Branch Creation**: The assignee creates a feature branch from `main` using the naming convention: `<issue-number>-<short-description>` (e.g., `131-admin-panel`).
3. **Development**: The developer works on the feature, making commits with clear messages. They regularly pull from `main` to stay up-to-date.
4. **Pull Request**: When the feature is complete, the developer opens a PR:
   - Links the issue (by creating a branch and link branch to issue)
   - Provides a summary of changes
   - Ensures CI checks pass
5. **Review**: At least one other team member reviews the PR:
   - Checks code quality, adherence to architecture, and test coverage
   - Provides feedback/approves
6. **Merge**: After approval and all CI checks pass, the PR is merged into `main` using a **merge commit**.
7. **Issue Closure**: The issue is automatically closed when the PR is merged (via linking the branch/PR). The issue moves to "Done" in the project board.

### Branch Naming Convention

- `<issue-naumber>-<description>` — for new features
- `<issue-number>-<description>` — for bug fixes
- `<description>` — for documentation updates
- `<description>` — for maintenance tasks

### Pull Request Requirements

- **Title**: Clear and descriptive (e.g., "feat: add admin panel backend (#131)")
- **Description**: Summary of changes, linked issue, testing notes
- **Review**: At least one approval required
- **CI Checks**: All workflows must pass (see Section 5)
- **Lychee Checks**: All workflows must pass (see Section 5)
- **Tests/QA Checks**: All workflows must pass (see Section 5)
- **No merge conflicts**: Branch must be up-to-date with `main`

---

## 3. Configuration and Secrets Management

### Secrets Storage

- **Production secrets** (BOT_TOKEN, JWT_SECRET_KEY, MAIL_PASSWORD, DATABASE_URL) are stored in **GitHub Secrets** for CI/CD and in environment variables on the deployment server (Render / Fly.io).
- **Local development** uses a `.env` file (gitignored) created from `.env.example`.

### Ignored Files

The `.gitignore` excludes:
- `.env` — environment variables with secrets
- `__pycache__/`, `*.py[cod]`, `*.pyc`, `*.egg-info/`, `dist/`, `build/` — Python cache, bytecode, and build artifacts
- `data/`, `hockey.db` — local SQLite database
- `*.log` — log files
- `.vscode/`, `.idea/`, `*.swp`, `*.swo` — IDE and editor configuration
- `node_modules/`, `.npm/` — Node.js dependencies (if any)
- `.DS_Store`, `Thumbs.db` — OS-specific metadata

### Runtime Configuration

- **Local**: `.env` file loaded via `python-dotenv` or similar
- **CI/CD**: GitHub Secrets injected as environment variables
- **Production**: Environment variables set in the hosting platform

### Example Configuration

The repository includes `.env.example` with placeholder values:

```env
# Telegram Bot
BOT_TOKEN=your_bot_token_here
ADMIN_CHAT_ID=your_chat_id_here

# Mail (Gmail app password) — для восстановления пароля
MAIL_USERNAME=sakirovsamir401@gmail.com
MAIL_PASSWORD=hqbo bhdk cxfg gabq
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_STARTTLS=True
MAIL_SSL_TLS=False

# JWT (подпись токенов) — смените на своё значение в production!
JWT_SECRET_KEY=hockeyscrapper-secret-change-in-production

# База данных (по умолчанию SQLite)
DATABASE_URL=sqlite:///data/tickets.db
DB_PATH=data/tickets.db

# Deployment
DEPLOY_URL=https://your-deployment.example.com
PORT=8000
```

**Note**: Developers must copy `.env.example` to `.env` and fill in real values. The `.env` file is never committed.

### CI/CD Configuration

- **GitHub Actions workflows** are stored in `.github/workflows/`:
  - `ci.yml` — linting (ruff) and unit tests with coverage
  - `tests.yml` — QA checks (pip-audit, bandit, pytest with coverage)
  - `lychee.yml` — link validation

---

## 4. Reproducible Development Environment

### Requirements

- **Python 3.10 or higher**
- **Git**
- **pip** (Python package manager)

### Setup Steps

```bash
# 1. Clone
git clone https://github.com/kamillayarullina/hockeyscrapper.git
cd hockeyscrapper

# 2. Virtual environment
python -m venv .venv
.venv\Scripts\activate    # Windows

# 3. Dependencies
pip install -r requirements.txt
playwright install         # for parsers

# 4. Environment
cp .env.example .env
# Edit .env — set BOT_TOKEN (get token from @BotFather)

# 5. Run 
# Everything (API + frontend + bot + parser)
python -m main --all
# Open in browser
start http://localhost:8000
```

### Running Components Separately

| Command | Starts |
|---------|--------|
| `python -m main --all` | API + bot + parser |
| `python -m main --api-only` | API + frontend only |
| `python -m main --bot-only` | Telegram bot only |

### Database

- **Development**: SQLite (local file `data/tickets.db`)
- **Production**: PostgreSQL (configured via `DATABASE_URL` in `.env`)

---

## 5. CI/CD Process

### Continuous Integration

The team uses **GitHub Actions** for CI. Three workflows run on every push and pull request to `main`:

#### 1. Python CI (`ci.yml`)
- **Triggers**: Push/PR to `main`
- **Steps**:
  - Set up Python 3.11
  - Install dependencies (including pytest, ruff)
  - Install Playwright browsers
  - Lint with `ruff check .`
  - Run tests with coverage (`pytest --cov=services --cov=bot --cov=parsers --cov-fail-under=20`)

#### 2. Tests & QA (`tests.yml`)
- **Triggers**: Push/PR to `main`
- **Steps**:
  - Set up Python 3.11
  - Install dependencies
  - Install Playwright browsers
  - Run security audit (`pip-audit`)
  - Run security linter (`bandit`)
  - Run tests with coverage (`pytest --cov=Backend --cov-report=xml`)
  - Upload coverage report as artifact

#### 3. Link Check (`lychee.yml`)
- **Triggers**: Push/PR to `main`
- **Steps**:
  - Run Lychee link checker on all markdown files
  - Fail if broken links are found

### Continuous Delivery

- **Deployment** is manual and performed via SSH:
  - After merging to `main`, a team member connects to the production server via SSH
  - The server pulls the latest changes from the `main` branch (`git pull origin main`)
  - Environment variables are set on the server (not in the repository)
  - Database migrations are run manually after the pull
- **No automated deployment** is currently configured. All deployments require manual SSH access and execution.

---

## 6. Definition of Done

All work items must satisfy the criteria defined in [`docs/definition-of-done.md`](definition-of-done.md):

- All acceptance criteria are satisfied
- Reviewed by another team member
- Required tests or checks pass
- Verification evidence preserved (CI logs, screenshots, test output)
- No secrets committed
- Code compiles/parses without errors
- Changes are focused on a single concern

---

## 7. Traceability

- **Issues → Branches → PRs → Commits**: Each issue has a corresponding feature branch. PRs link to issues via linkin the branch. Commits reference issues in messages.
- **Sprint Tracking**: Issues are assigned to milestones (e.g., "Sprint 2"). Project boards track progress through states (Todo → In Progress → Done).
- **Test Coverage**: Coverage reports are uploaded as CI artifacts and linked in PRs.
- **Documentation**: All architectural decisions are documented in `docs/architecture/adr/`. User stories are in `docs/user-stories.md`.

---

## 8. Related Documentation

- [Definition of Done](definition-of-done.md)
- [User Stories](user-stories.md)
- [Architecture ADR](architecture/adr/README.md)
- [Testing Strategy](testing.md)
- [Quality Requirements](quality-requirements.md)
- [Roadmap](roadmap.md)
