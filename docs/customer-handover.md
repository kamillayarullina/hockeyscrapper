# Customer Handover Document — HockeyScrapper

---

## 1. Current Product Status and Handover Scope

HockeyScrapper is a KHL hockey ticket monitoring system. It scrapes ticket availability and notifies users via a Telegram bot when tickets appear, prices change, or matches sell out. Users manage subscriptions through a web dashboard with JWT-based authentication.

**Current status:** All MVP v1 and MVP v2 features are implemented. UATs (6 scenarios) were passed on 3 July 2026. The product runs on a staging VPS at `http://89.125.169.128:8000`.

### What Is Ready for the Customer

| Asset | Status |
|---|---|
| Source code repository | Full access granted — [github.com/kamillayarullina/hockeyscrapper](https://github.com/kamillayarullina/hockeyscrapper) |
| Documentation site | Published — [kamillayarullina.github.io/hockeyscrapper](https://kamillayarullina.github.io/hockeyscrapper/) |
| Docker image + Render Blueprint | `render.yaml` defines web service, worker, and PostgreSQL |
| Telegram bot | `@HockeyScrapper_bot` — functional but owned by team account |
| Web dashboard | Login, registration, profile, subscriptions, admin panel, avatar upload, password recovery |

### What Remains Under Team Control (Not Yet Transferred)

| Asset | Blocker |
|---|---|
| Telegram bot ownership | Bot is registered under a team Telegram account; must transfer via BotFather |
| Render account (dashboard, databases, services) | Customer needs their own Render account |
| VPS SSH access | `89.125.169.128` is managed by the team |

---

## 2. How the Customer Accesses and Uses the Product

### End Users (Web)

1. Open the web dashboard at your deployment URL.
2. Register an account (email + password).
3. Log in — a JWT token is issued for the session.
4. Navigate to **Manage Subscriptions** and select KHL teams to follow.
5. On the profile page, optionally upload an avatar or link a Telegram account via a one-time code.
6. Receive Telegram notifications when tickets for subscribed teams appear, change price, or sell out.

### End Users (Telegram Bot)

Send commands to `@HockeyScrapper_bot`:

| Command | Purpose |
|---|---|
| `/start` | Welcome message and instructions |
| `/subscribe <team>` | Subscribe to a KHL team |
| `/unsubscribe <team>` | Unsubscribe from a team |
| `/list` | View current subscriptions |
| `/matches` | List upcoming matches with tickets |
| `/teams` | All 22 KHL teams |
| `/help` | Full command reference |

Full interaction examples are documented in [docs/interface.md](interface.md).

### Administrators

1. Navigate to `/admin` on the web dashboard.
2. Log in with admin credentials.
3. Use the **Settings** panel to adjust parsing interval.
4. Use the **Proxy** panel to add/remove proxy addresses for bypassing CAPTCHA.
5. User management is available from the admin panel.

---

## 3. Installation or Deployment Instructions

### Local Development

```bash
git clone https://github.com/kamillayarullina/hockeyscrapper.git
cd hockeyscrapper
python -m venv .venv
.venv\Scripts\activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env        # then edit .env with your values
python -m main --verbose        # starts API + bot + parser
```

Open `http://localhost:8000` in a browser.

---

## 4. Required Configuration and Secrets-Handling Expectations

### Environment Variables (Must Set — No Secrets Exposed Below)

| Variable | Used By | Purpose | How to Obtain |
|---|---|---|---|
| `BOT_TOKEN` | Web + Worker | Telegram bot API token | Create bot at [@BotFather](https://t.me/BotFather) |
| `JWT_SECRET_KEY` | Web only | Signs authentication tokens | Generate a strong random string |
| `DATABASE_URL` | Web + Worker | Database connection | From your PostgreSQL provider |
| `MAIL_USERNAME` | Web only | SMTP login for password recovery | Your email address |
| `MAIL_PASSWORD` | Web only | SMTP app password for recovery | Your email provider's app password |
| `ADMIN_CHAT_ID` | Worker only | Telegram chat for admin alerts | Your Telegram chat ID (get from @userinfobot) |

### Secrets-Handling Rules

- Copy `.env.example` to `.env`, fill values, **never commit `.env`**.
- On Render, set variables via Dashboard → Environment (do not check `sync` for secrets).
- On a VPS, set them in the shell profile or a systemd override file.

### Known Security Gaps 

- No gaps


---

## 5. Operational Notes for Normal Use

### Parser Cycle

- The parser runs in a loop on the **worker** service.
- Default interval: **300 seconds** (configurable via admin panel → Settings, range 1-999).
- If a parser encounters CAPTCHA or Cloudflare protection, it logs a warning and skips that site. Add proxies via admin panel → Proxy to mitigate.

### Database

- **Development:** SQLite at `data/tickets.db` (auto-created).
- **Production:** PostgreSQL via `DATABASE_URL`.
- The application uses two ORM layers (aiosqlite for async operations, SQLAlchemy for the FastAPI backend). Both connect to the same database.
- On Render, use the managed PostgreSQL instance defined in `render.yaml`.

### File Storage

- User avatars are stored in `static/avatars/` and served via `/avatars/`.
- Ensure this directory is writable by the application process.
- For Render, attach a persistent disk or use external object storage for avatar persistence across deployments.

### Logging

- Logs are written to stdout/stderr (captured by Render dashboard or `docker logs`).
- Parser errors, notification failures, and SMTP issues are logged with stack traces.
- Admin receives Telegram alerts for critical errors via the configured `ADMIN_CHAT_ID`.



---

## 6. Troubleshooting and Support Guidance

-Now all added features working correctly.

---

## 7. Known Limitations, Unfinished Areas, and Important Risks

### Limitations

| Limitation | Impact | Workaround |
|---|---|---|
| Parser does not handle JavaScript-heavy sites beyond Playwright's capability | Some club sites may yield partial data | Add custom CSS selectors in `parsers/club_sites.py` or extend `BaseParser` |
| Coverage threshold (30%) is low | Regressions in untested modules may go undetected | Add unit tests for remaining modules |
| Single Telegram bot handles all users | Bot token is a single point of failure | Not critical at current scale |

### Unfinished Areas

| Area | Current State | Needed |
|---|---|---|
| Backup/recovery procedures | Not documented | Document SQLite and PostgreSQL backup steps |

### Important Risks

| Risk | Severity | Mitigation |
|---|---|---|
| **Telegram bot** registered under team account | **High** — team controls the bot; if team dissolves, customer loses the bot | Transfer bot ownership via BotFather or create a new bot |
| **Render services** under team account | **High** — team can modify or delete production services | Customer deploys under their own Render account |
| **VPS** at `139.100.225.113` is team-managed | **Medium** — no SLA for uptime | Migrate to customer-controlled infrastructure |


---

## 8. Current Handover Status

**Level reached: Ready for independent use** — with conditions.

The product is feature-complete and all UATs have passed. The customer can clone the repository, deploy on their own infrastructure, configure their own secrets, and operate the system independently. However, the current running instance on the team's VPS and the services under the team's Render account are **not yet independently usable by the customer** because:

- The customer does not yet own their own Render account with deployed services.
- The Telegram bot token and SMTP credentials still point to team-owned accounts.


---

## 9. Remaining Actions and Whether They Block Full Transition

| Action | Blocks Transition? | Priority |
|---|---|---|
| Customer creates their own Render account and deploys via Blueprint | **Yes** — without this, the customer cannot operate independently | Critical | 
| Customer provides their own SMTP credentials | **Yes** — without this, password recovery depends on team email | Critical |
| Document backup and recovery procedures | **No** — system is operational without it, but data loss risk exists | Medium |
| Transfer GitHub repository full ownership | **No** — customer already has write access; admin transfer can be scheduled later | Low | 

---

## 10. Related Customer-Relevant Documentation

| Document | What It Contains |
|---|---|
| [Documentation Home](index.md) | Index of all documentation sections |
| [Interface Guide](interface.md) | Telegram bot commands with input/output examples |
| [User Stories](user-stories.md) | All 12 user stories with priority and status |
| [Architecture Overview](architecture/README.md) | System architecture with static, dynamic, and deployment diagrams |
| [Quality Requirements](quality-requirements.md) | 5 measurable quality attributes |
| [Quality Requirement Tests](quality-requirement-tests.md) | 5 automated QRTs with evidence |
| [User Acceptance Tests](user-acceptance-tests.md) | 6 UAT scenarios (all passed) |
| [Definition of Done](definition-of-done.md) | Completion criteria for all work item types |
| [Roadmap](roadmap.md) | Sprint history and planned work |
| [CHANGELOG](../CHANGELOG.md) | Full version history |
| [README](../README.md) | Quick start, project overview |
| [GitHub Repository](https://github.com/kamillayarullina/hockeyscrapper) | Source code, issues, CI runs |
| [Hosted Documentation Site](https://kamillayarullina.github.io/hockeyscrapper/) | Browsable MkDocs site |
