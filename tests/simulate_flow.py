"""Симуляция с реальным Telegram-ботом: отправляем уведомления на телефон."""

import sys
import os
import asyncio
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logging.getLogger("services").setLevel(logging.WARNING)
logging.getLogger("aiogram").setLevel(logging.WARNING)


async def simulate():
    from services.database import Database
    from services.notifier import Notifier
    from services.team_matcher import extract_teams_from_title
    from bot import TelegramBot
    import yaml

    # ── Читаем конфиг ──
    config_path = Path("config/sites.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    bot_token = os.environ.get("BOT_TOKEN", "")
    YOUR_CHAT_ID = config.get("settings", {}).get("telegram", {}).get("admin_chat_id", 8061310741)

    print(f"Токен бота: {'✅' if bot_token and len(bot_token) > 20 else '❌'}")
    print(f"Твой Chat ID: {YOUR_CHAT_ID}")

    # ── Запускаем бота в отдельной задаче ──
    bot = TelegramBot(bot_token)
    bot_task = asyncio.create_task(bot.start())
    await asyncio.sleep(2)
    print("✅ Бот запущен")

    # ── Временная БД ──
    import tempfile
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db = Database(tmp.name)
    await db.init()

    # ── Регистрируем и подписываем ──
    await db.add_user(YOUR_CHAT_ID, "testuser", "Test")
    await db.subscribe(YOUR_CHAT_ID, "team", "ска")
    subs = await db.get_user_subscriptions(YOUR_CHAT_ID)
    print(f"✅ Подписки: {subs}")

    # ── Нотификатор с реальным ботом ──
    notifier = Notifier(bot.get_bot(), admin_chat_id=YOUR_CHAT_ID)

    # ── Мок-матч ──
    match_title = "СКА — Ак Барс • Кубок Открытия"
    match_id = f"{match_title}|2026-09-16|test"

    async def process_match(availability: str):
        event = {
            "title": match_title,
            "date": "16 сентября 2026",
            "place": "Санкт-Петербург, СКА Арена",
            "price_min": "1 500 ₽",
            "price_max": "7 500 ₽",
            "availability": availability,
            "link": "https://ticket-hockey.ru/event/ska-akbars",
        }
        teams = extract_teams_from_title(event["title"])
        match_data = {
            "match_id": match_id,
            "title": event["title"],
            "date": event["date"],
            "place": event["place"],
            "venue": "СКА Арена",
            "city": "санкт-петербург",
            "teams": ", ".join(teams),
            "price_min": event["price_min"],
            "price_max": event["price_max"],
            "availability": event["availability"],
            "link": event["link"],
            "source": "test",
        }

        old = await db.get_match_by_id(match_id)
        old_avail = old.get("availability") if old else None
        print(f"\n  Старый: {old_avail or 'нет'} → Новый: {availability}")

        await db.save_match(match_data)

        should_notify = False
        reason = "new"
        if old is None:
            should_notify = True
            reason = "new"
        elif old_avail != availability:
            should_notify = True
            if old_avail == "Нет" and availability == "Да":
                reason = "available"
            elif old_avail == "Да" and availability == "Нет":
                reason = "sold_out"
            else:
                reason = "changed"

        if should_notify:
            subscriber_ids = await db.get_subscribers_for_teams(teams)
            print(f"  Подписчиков: {len(subscriber_ids)}, отправляю...")
            sent = await notifier.notify_subscribers(
                event=event,
                subscriber_chat_ids=subscriber_ids,
                db=db,
                reason=reason,
            )
            print(f"  Отправлено: {sent}")
        else:
            print("  Уведомление не нужно (статус не изменился)")

    # ════════════════════════
    print("\n" + "=" * 60)
    print("ШАГ 1: Матч БЕЗ билетов — идёт уведомление")
    print("=" * 60)
    await process_match("Нет")

    await asyncio.sleep(2)

    print("\n" + "=" * 60)
    print("ШАГ 2: Появились билеты — идёт уведомление")
    print("=" * 60)
    await process_match("Да")

    await asyncio.sleep(2)

    print("\n" + "=" * 60)
    print("ШАГ 3: Повтор (ничего не изменилось) — тишина")
    print("=" * 60)
    await process_match("Да")

    # ── Остановка ──
    await bot.stop()
    try:
        bot_task.cancel()
        await bot_task
    except asyncio.CancelledError:
        pass
    os.unlink(tmp.name)
    print("\n✅ Готово! Проверь Telegram.")


if __name__ == "__main__":
    asyncio.run(simulate())
