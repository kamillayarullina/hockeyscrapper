# MVP v0 Report — HockeyScrapper

## What it is

HockeyScrapper MVP v0 is a working local project that connects a website, a Telegram bot, and a database. You can register on the site, subscribe to KHL teams, and get match notifications in Telegram. The parsers scrape ticket data from multiple sources in the background.

It's not deployed anywhere public (no server with a card), but you can run it locally and expose it via Cloudflare Tunnel if needed.

## Deployment

- **Run:** `python -m main --all` → `http://localhost:8000`
- **Tunnel:** `cloudflared tunnel --url http://localhost:8000`

## Video

<!-- Add link < 2 min -->

## Prototype vs MVP v0

| Что | Figma | Сейчас |
|-----|-------|--------|
| Профиль | Картинка | Живой `/me` |
| Подписки | Макет | Работают через API + бот |
| Логин/рег | Нет | Есть, с JWT |
| Уведомления | Нет | Telegram push |
| Парсер | Нет | Работает (кроме Яндекс.Афиши) |

## Что не работает / заглушки

- Публичный хостинг — только локально (карта нужна)
- Яндекс.Афиша — парсер находит 0 событий
- Подписки на арены — бэкенд есть, фронтенда нет
- Бот падает с `Conflict`, если запущен второй экземпляр
- Ошибки на фронтенде — показывают "Ошибка регистрации" без деталей

## Smoke-check

1. `python -m main --all` — сервер запущен, бот ответил
2. Открыть `http://localhost:8000` — видно кнопки входа/регистрации
3. Зарегистрироваться — редирект на профиль
4. Зайти в "Управление подписками" → подписаться на команду → кнопка стала "Отписаться"
5. `curl /subscriptions/{chat_id}` — в JSON видна подписка
6. `curl /matches` — JSON (может быть пустым)
7. `curl /stats` — JSON со счётчиками

Всё должно работать без ошибок.

## Запуск локально

```bash
git clone https://github.com/kamillayarullina/hockeyscrapper.git
cd hockeyscrapper
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install
# BOT_TOKEN в .env
python -m main --all
```

Подробнее — [README.md](../../README.md).
