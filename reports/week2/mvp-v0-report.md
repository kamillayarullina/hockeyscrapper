# MVP v0 Report — HockeyScrapper

## What it is

HockeyScrapper MVP v0 is a working local project that connects a website, a Telegram bot, and a database. You can register on the site, subscribe to KHL teams, and get match notifications in Telegram. The parsers scrape ticket data from multiple sources in the background.



## Deployment URL

[Deployment](http://139.100.225.113:8000/)

## Video

[Video demostration](https://drive.google.com/file/d/1F7rCt25XgOrvZRCbu4dqxDarWH1BV5li/view?usp=sharing)

## Prototype vs MVP v0

| Item | Figma | Current |
|------|-------|---------|
| Profile | Mockup | Live `/me` endpoint |
| Subscriptions | Mockup | Working via API + bot |
| Login/Register | Mockup | Working with JWT |
| Notifications | Not shown | Telegram push |
| Parser | Not shown | Works (except Yandex) |

## Prototype vs MVP v1

| MVP v1 user story | Prototype |
|------|-------|
| US-01 | Shown in prototype |
| US-02 | Shown in prototype | 
| US-04 | Shown in prototype |
| US-05 | Available in MVP v0 (only telegram notifications)|
| US-07 | Shown in prototype |
| US-10 | Not realised yet |

## What doesn't work / placeholders

- No public hosting (needs a card)
- Yandex parser finds 0 events
- Bot crashes with `Conflict` if a second instance runs
- Frontend shows generic error messages

## Smoke-check

1. `python -m main --all` — server starts, bot says it's running
2. Open `http://localhost:8000` — buttons for login/register visible
3. Register — redirect to profile page
4. Go to "Управление подписками" → subscribe to a team → button changes to "Отписаться"
5. `curl /subscriptions/{chat_id}` — JSON has the subscription
6. `curl /matches` — JSON array (may be empty)
7. `curl /stats` — JSON with counts

All steps should pass without errors.

## Local setup

```bash
git clone https://github.com/kamillayarullina/hockeyscrapper.git
cd hockeyscrapper
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install
# Set BOT_TOKEN in .env
python -m main --all
```

More details — [README.md](../../README.md).
