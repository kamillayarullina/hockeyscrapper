#!/usr/bin/env python3
"""
Точка входа: запускает Telegram-бота и парсер-мониторинг параллельно.
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

from bot import TelegramBot
from services.parser_runner import ParserRunner


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    fmt = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    logging.basicConfig(
        level=level,
        format=fmt,
        datefmt=datefmt,
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("playwright").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.WARNING)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Мониторинг хоккейных билетов + Telegram-бот")
    parser.add_argument("--once", action="store_true", help="Один цикл парсинга и выход (бот продолжит работать)")
    parser.add_argument("--site", type=str, default=None, help="Только указанный сайт")
    parser.add_argument("--config", type=str, default="config/sites.yaml", help="Путь к конфигу")
    parser.add_argument("--verbose", "-v", action="store_true", help="Подробные логи")
    parser.add_argument("--parser-only", action="store_true", help="Запустить только парсер (без бота)")
    parser.add_argument("--bot-only", action="store_true", help="Запустить только бота (без парсера)")
    return parser.parse_args()


def load_env() -> None:
    """Загружает переменные из .env."""
    env_path = Path(".env")
    dotenv_path = Path(__file__).parent / ".env"
    if dotenv_path.exists():
        env_path = dotenv_path
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
            return
        except ImportError:
            pass
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                os.environ[key.strip()] = val.strip()


async def run_all(args: argparse.Namespace) -> int:
    """Запускает бота и парсер параллельно."""
    logger = logging.getLogger("main")
    load_env()

    # Загружаем конфиг
    import yaml
    config_path = Path(args.config)
    if not config_path.exists():
        logger.error(f"Конфиг не найден: {args.config}")
        return 1

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Токен бота из .env (приоритет) или из config/sites.yaml
    bot_token = os.environ.get("BOT_TOKEN", "")

    # Инициализируем БД
    from services.database import get_db
    db = get_db()
    await db.init()

    telegram_bot = None
    bot_task = None

    # Запускаем Telegram-бота (если не режим parser-only)
    if not args.parser_only:
        if not bot_token:
            logger.error("❌ Не указан токен Telegram-бота!")
            logger.error("Создайте файл .env (по образцу .env.example) и укажите BOT_TOKEN.")
            logger.error("Получить токен: @BotFather")
            if args.bot_only:
                return 1
            logger.warning("⚠️ Продолжаю без бота (режим parser-only)")
        else:
            try:
                telegram_bot = TelegramBot(bot_token)
                # Запускаем бота в отдельной задаче
                bot_task = asyncio.create_task(telegram_bot.start())
                logger.info("🤖 Telegram-бот запущен")
            except Exception as e:
                logger.error(f"❌ Ошибка запуска бота: {e}")
                if args.bot_only:
                    return 1

    # Запускаем парсер (если не режим bot-only)
    parser_task = None
    if not args.bot_only:
        runner = ParserRunner(
            config_path=args.config,
            site_filter=args.site,
            once=args.once,
            telegram_bot=telegram_bot,
        )
        parser_task = asyncio.create_task(runner.run_forever())

    # Ждём завершения
    try:
        tasks = []
        if bot_task:
            tasks.append(bot_task)
        if parser_task:
            tasks.append(parser_task)

        if not tasks:
            logger.warning("Нет задач для выполнения")
            return 0

        # Если есть парсер — ждём его, бот работает в фоне
        if parser_task:
            await parser_task

        # Если только бот — ждём бесконечно
        if bot_task and not parser_task:
            await bot_task

    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        logger.info("Получен Ctrl+C")
    finally:
        if telegram_bot:
            await telegram_bot.stop()
        logger.info("✅ Работа завершена")

    return 0


def main() -> int:
    args = parse_args()
    setup_logging(verbose=args.verbose)

    logger = logging.getLogger("main")
    logger.info("=" * 60)
    logger.info("🏒 ХОККЕЙНЫЙ МОНИТОРИНГ + TELEGRAM-БОТ")
    logger.info("=" * 60)

    try:
        return asyncio.run(run_all(args))
    except KeyboardInterrupt:
        logger.info("Остановлено пользователем")
        return 0
    except Exception as e:
        logger.exception(f"Критическая ошибка: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())