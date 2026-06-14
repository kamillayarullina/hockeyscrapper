# HockeyScrapper 🏒

Track KHL hockey tickets. Web dashboard + Telegram bot in one project.

## Features

- **Ticket search** — scrapes ticket-hockey.ru, khl.ru, yandex.afisha
- **Notifications** — Telegram bot sends alerts on new tickets
- **Auth** — register / login with JWT
- **Subscriptions** — follow teams and venues
- **Telegram linking** — auto-link web account via one-time code

## Reports

- [Week 2 report](reports/week2/README.md) — user stories, prototype, MVP v0, customer meeting
- [MVP v0 report](reports/week2/mvp-v0-report.md) — foundation details, smoke-check scenario

## Local Setup

### Requirements
- Python 3.10 or higher
- Git

### Steps

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
# Edit .env — set BOT_TOKEN and ADMIN_CHAT_ID (get token from @BotFather)
```

### Run

```bash
# Everything (API + frontend + bot + parser)
python -m main --all

# Open in browser
start http://localhost:8000
```

### Options

| Command | Starts |
|---------|--------|
| `python -m main --all` | API + bot + parser |
| `python -m main --api-only` | API + frontend only |
| `python -m main --bot-only` | Telegram bot only |

### Public access (optional)

```bash
# Cloudflare Tunnel — exposes localhost to the internet
cloudflared tunnel --url http://localhost:8000
```

## Stack

- **Backend:** FastAPI, SQLAlchemy, JWT (python-jose)
- **Frontend:** HTML + CSS (vanilla)
- **Bot:** aiogram 3.x
- **Parsers:** Playwright, BeautifulSoup, aiohttp
- **Database:** SQLite (dev) / PostgreSQL (prod) via `databases` library
- **Hosting:** Render / Docker / Fly.io

## Project Structure

```
Backend/       — API endpoints, JWT, ORM models
bot/           — Telegram bot (aiogram)
parsers/       — KHL, Yandex Afisha, club sites
services/      — DB, notifications, proxy rotation, team matching
Frontend/      — HTML pages (index, profile, subscriptions, login)
config/        — parser config (sites.yaml)
```
## links to week2

[`reports/week2/mvp-v0-report.md`](reports/week2/mvp-v0-report.md)
[`reports/week2/README.md`](reports/week2/README.md)

## License
