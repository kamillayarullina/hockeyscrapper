#!/usr/bin/env python3
import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("playwright").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("aiogram").setLevel(logging.WARNING)
logger = logging.getLogger("main")


def load_env():
    env_path = Path(".env")
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


async def run_bot():
    from bot.telegram_bot import TelegramBot

    token = os.environ.get("BOT_TOKEN", "")
    if not token:
        logger.error("BOT_TOKEN not set in .env")
        return

    from services.database import get_db
    db = get_db()
    await db.init()

    bot = TelegramBot(token)
    try:
        await bot.start()
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.stop()


def run_api():
    import Backend.main as api_app
    from Backend.database import engine
    import Backend.models

    Backend.models.Base.metadata.create_all(bind=engine)

    uvicorn.run("Backend.main:app", host="0.0.0.0", port=8000, reload=False)


async def main():
    load_env()

    parser = argparse.ArgumentParser(description="HockeyScrapper — API + Bot + Parser")
    parser.add_argument("--bot-only", action="store_true", help="Only Telegram bot")
    parser.add_argument("--api-only", action="store_true", help="Only FastAPI backend")
    parser.add_argument("--all", action="store_true", help="API + Bot + Parser")
    args = parser.parse_args()

    if not any([args.bot_only, args.api_only, args.all]):
        args.all = True

    tasks = []

    if args.api_only or args.all:
        logger.info("Starting FastAPI on http://localhost:8000")
        import threading
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        tasks.append(api_thread)

    if args.bot_only or args.all:
        logger.info("Starting Telegram bot")
        bot_task = asyncio.create_task(run_bot())
        tasks.append(bot_task)

    if args.all:
        logger.info("Starting parser...")
        from services.parser_runner import ParserRunner
        runner = ParserRunner(config_path="config/sites.yaml")
        parser_task = asyncio.create_task(runner.run_forever())
        tasks.append(parser_task)

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
