"""Тест полной интеграции: бот + парсер."""

import asyncio
import os
import yaml
from pathlib import Path
from bot import TelegramBot
from services.database import get_db
from services.parser_runner import ParserRunner


async def test_full():
    print("=" * 60)
    print("ТЕСТ ПОЛНОЙ ИНТЕГРАЦИИ")
    print("=" * 60)

    # 1. Загружаем конфиг
    config_path = Path("config/sites.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    token = os.environ.get("BOT_TOKEN", "")
    chat_id = config.get("settings", {}).get("telegram", {}).get("admin_chat_id", 0)

    print(f"1. Токен: {'✅' if token and len(token) > 20 else '❌'}")
    print(f"2. Chat ID: {'✅' if chat_id else '❌'} ({chat_id})")

    # 2. Инициализируем БД
    db = get_db()
    await db.init()
    print("3. База данных: ✅")

    # 3. Проверяем подписчиков
    subs = await db.get_user_subscriptions(chat_id)
    print(f"4. Ваши подписки: {subs if subs else '❌ НЕТ ПОДПИСОК!'}")

    if not subs:
        print("\n⚠️  У вас нет подписок! Добавьте:")
        print("   /subscribe ЦСКА")
        print("   /subscribe Спартак")
        return

    # 4. Запускаем бота
    try:
        bot = TelegramBot(token)
        await bot.start()
        print("5. Telegram-бот: ✅ запущен")
    except Exception as e:
        print(f"5. Telegram-бот: ❌ {e}")
        return

    # 5. Запускаем парсер на один цикл
    print("\n Запускаю парсер...")
    runner = ParserRunner(
        config_path="config/sites.yaml",
        once=True,
        telegram_bot=bot,
    )
    await runner.run_forever()

    await bot.stop()
    print("\n✅ Тест завершен!")


if __name__ == "__main__":
    asyncio.run(test_full())