# HockeyScrapper 🏒

Track KHL hockey tickets. Web dashboard + Telegram bot in one project.

## Features

- **Ticket search** — scrapes ticket-hockey.ru, khl.ru, yandex.afisha
- **Notifications** — Telegram bot sends alerts on new tickets
- **Auth** — register / login with JWT
- **Subscriptions** — follow teams and venues
- **Telegram linking** — auto-link web account via one-time code

## Quick Start

```bash
git clone https://github.com/kamillayarullina/hockeyscrapper.git
cd hockeyscrapper

python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
playwright install

cp .env.example .env
# Set BOT_TOKEN and ADMIN_CHAT_ID in .env
```

## Run

```bash
# Everything (site + bot + parser)
python -m main --all

# Site only (http://localhost:8000)
python -m main --api-only

# Bot only
python -m main --bot-only
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
