# MVP v0 Report — HockeyScrapper

## Purpose and Description

MVP v0 establishes a runnable technical foundation for HockeyScrapper — a platform that tracks KHL hockey tickets and notifies users via Telegram. It demonstrates:

- A working **FastAPI backend** serving REST endpoints (auth, subscriptions, matches, stats)
- A **vanilla HTML/CSS frontend** for registration, login, profile, and subscription management
- A **Telegram bot** (aiogram) for subscribing to teams and receiving notifications
- **Parser infrastructure** for scraping ticket data from multiple sources
- A **shared database** (SQLite/PostgreSQL) connecting all components

The foundation supports the eventual implementation of all proposed user stories (US-01 through US-11).

## Deployment / Runnable Artifact

- **Local run:** `python -m main --all` starts API + frontend + bot + parser
- **Access:** `http://localhost:8000`
- **Cloud exposure:** via Cloudflare Tunnel (`cloudflared tunnel --url http://localhost:8000`)

No public hosted deployment (requires paid service with card). The product is fully runnable locally with clear setup instructions.

## Video Demonstration

<!-- Add link to public video (YouTube/Google Drive) < 2 minutes -->

## Relationship to Prototype and MVP v1

| Aspect | Prototype (Figma) | MVP v0 |
|--------|-------------------|--------|
| Profile screen | Static mockup | Live `/me` endpoint + HTML page |
| Subscription list | Static mockup | Live `/subscriptions/{id}` + toggle via API |
| Team selection | Clickable prototype | Working subscribe/unsubscribe via bot and web |
| Match notifications | Not shown | Working Telegram push on new matches |
| Login/Register | Not in prototype | Working JWT-based auth |
| Parser | Not shown | Working Playwright-based scrapers |

MVP v0 reuses the visual design language from the Figma prototype and implements the core data flows. The main gap vs MVP v1 is: no hosted deployment, no payment integration, limited venue subscription support on the frontend.

## Current Limitations, Placeholders, and Mocks

| Area | Limitation | Status |
|------|-----------|--------|
| Deployment | No public hosting (Render/Fly.io require card) | Local-only; cloudflared as workaround |
| Yandex parser | Finds 0 events (site may have changed URL scheme) | Needs investigation |
| Venue subscriptions | Backend supports, frontend only shows teams | Placeholder |
| Bot conflict | `TelegramConflictError` if two instances run | Must ensure single instance |
| Error display | Frontend shows generic "Ошибка регистрации" instead of real error | Minor UX issue |
| Database | Two ORM layers (SQLAlchemy + `databases` lib) share same file | Works but not ideal |

## Smoke-Check Scenario

### Prerequisites
- Python 3.10+, `.venv` activated, `requirements.txt` installed, `.env` configured with `BOT_TOKEN`

### Steps

1. **Start the application**
   ```bash
   python -m main --all
   ```
   Expected: `Uvicorn running on http://localhost:8000`, bot shows "Telegram-бот запущен"

2. **Open the web app**
   - Navigate to `http://localhost:8000`
   - Expected: index page loads with "Войти" and "Зарегистрироваться" buttons

3. **Register a user**
   - Click "Зарегистрироваться" → fill form → submit
   - Expected: redirected to profile page with username and chat_id displayed

4. **Subscribe to a team**
   - Click "Управление подписками" → click "Подписаться" on any team
   - Expected: button changes to "Отписаться"

5. **Verify the subscription via API**
   ```bash
   curl http://localhost:8000/subscriptions/{chat_id}
   ```
   Expected: JSON with the subscribed team in the `subscriptions` array

6. **Check matches endpoint**
   ```bash
   curl http://localhost:8000/matches
   ```
   Expected: JSON array (may be empty if no matches have been parsed yet)

7. **Check stats**
   ```bash
   curl http://localhost:8000/stats
   ```
   Expected: JSON with user/subscription/match counts

8. **(Optional) Telegram bot**
   - Open Telegram → find `@HockeyScrapper_bot` → send `/start`
   - Expected: welcome message with instructions

### Expected Result
All steps complete without errors. The application is accessible at `localhost:8000`, user can register, log in, subscribe to teams, and see their subscriptions reflected in the UI.

## Local Setup Instructions

See [root README.md](../../README.md) for detailed local setup. Key commands:

```bash
git clone https://github.com/kamillayarullina/hockeyscrapper.git
cd hockeyscrapper
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install
# Set BOT_TOKEN and ADMIN_CHAT_ID in .env
python -m main --all
```
