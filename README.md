# HockeyScrapper 🏒

Track KHL hockey tickets. Web dashboard + Telegram bot in one project.

## Features

- Ticket search — scrapes ticket-hockey.ru, khl.ru, yandex.afisha
- Notifications — Telegram bot sends alerts on new tickets
- Auth — register / login with JWT
- Subscriptions — follow teams and venues
- Telegram linking — auto-link web account via one-time code

## Quick Start
```bash
git clone https://github.com/kamillayarullina/hockeyscrapper.git
cd hockeyscrapper
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install
cp .env.example .env
```
## Run
```
Everything (site + bot + parser):   python -m main --all
Site only:                          python -m main --api-only
Bot only:                           python -m main --bot-only
```
## Stack
```bash
Backend: FastAPI, SQLAlchemy, JWT
Frontend: HTML + CSS (vanilla)
Bot: aiogram 3.x
Parsers: Playwright, BeautifulSoup, aiohttp
Database: SQLite (dev) / PostgreSQL (prod)
```
## License

![`MIT`](LICENSE)
