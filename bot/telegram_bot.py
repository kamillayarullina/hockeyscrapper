"""Telegram bot with KHL team subscription system."""

import asyncio
import logging
import os
from html import escape
from typing import Optional

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, BotCommand
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from services.database import get_db
from services.team_matcher import get_all_team_names, normalize_team_name, get_team_info, _VARIANT_TO_TEAM

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Greeting and user registration with link code support."""
    db = get_db()
    chat_id = message.from_user.id
    await db.add_user(
        chat_id=chat_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

    args = message.text.split(maxsplit=1)
    code = args[1].strip() if len(args) > 1 else ""

    if code:
        user = await db.find_user_by_link_code(code)
        if user and user["chat_id"] < 0:
            await db.link_account(user["chat_id"], chat_id)
            await message.answer(
                f"✅ Аккаунт с email <b>{escape(user['email'] or '—')}</b> "
                f"успешно привязан к Telegram!\n\n"
                f"📋 Ваши подписки перенесены.\n"
                f"Теперь уведомления будут приходить сюда."
            )
            return

    teams_list = "\n".join(f"• <code>/{t.split()[0].lower()}</code> — {t}" for t in get_all_team_names()[:10])

    text = (
        f"👋 Привет, <b>{escape(message.from_user.first_name or 'друг')}</b>!\n\n"
        f"Я бот для отслеживания хоккейных билетов. "
        f"Подпишись на любимые команды КХЛ и получай уведомления, "
        f"как только появятся билеты на их матчи!\n\n"
        f"📋 <b>Команды для управления:</b>\n"
        f"• /subscribe <code>ЦСКА</code> — подписаться на команду\n"
        f"• /unsubscribe <code>ЦСКА</code> — отписаться\n"
        f"• /list — мои подписки\n"
        f"• /matches — все актуальные матчи\n"
        f"• /teams — все доступные команды\n"
        f"• /help — помощь\n\n"
        f"🔗 <b>Привязка аккаунта:</b>\n"
        f"Если вы зарегистрированы на сайте, нажмите «Привязать Telegram»\n"
        f"в личном кабинете — бот подхватит код автоматически.\n\n"
        f"🏒 <b>Популярные команды:</b>\n{teams_list}\n"
        f"...и ещё {len(get_all_team_names()) - 10} команд. Полный список: /teams"
    )
    await message.answer(text)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Help."""
    text = (
        "🤖 <b>Как пользоваться ботом:</b>\n\n"
        "1️⃣ Подпишитесь на команды: /subscribe <code>ЦСКА</code>\n"
        "2️⃣ Можете подписаться на несколько команд\n"
        "3️⃣ Как только появятся билеты на матч с вашей командой — "
        "я пришлю вам уведомление с ценой и ссылкой\n\n"
        "📋 <b>Команды:</b>\n"
        "• /subscribe <code>команда</code> — подписка\n"
        "• /unsubscribe <code>команда</code> — отписка\n"
        "• /list — посмотреть подписки\n"
        "• /matches — все актуальные матчи\n"
        "• /match <code>номер</code> — детали матча\n"
        "• /teams — все команды\n"
        "• /stats — статистика бота\n"
        "• /help — эта справка"
    )
    await message.answer(text)


@router.message(Command("link"))
async def cmd_link(message: Message):
    """Link Telegram to a website account."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "❗ Укажите email, который вы использовали при регистрации на сайте.\n"
            "Пример: /link <code>my@email.com</code>"
        )
        return

    email = args[1].strip().lower()
    db = get_db()
    user = await db.find_user_by_email(email)

    if not user:
        await message.answer(
            f"❌ Пользователь с email <b>{escape(email)}</b> не найден.\n"
            f"Сначала зарегистрируйтесь на сайте: http://localhost:8000"
        )
        return

    if user['chat_id'] == message.from_user.id:
        await message.answer("✅ Этот аккаунт уже привязан к вашему Telegram.")
        return

    if user['chat_id'] > 0:
        await message.answer(
            f"❌ Email <b>{escape(email)}</b> уже привязан к другому Telegram-аккаунту.\n"
            f"Если это вы — войдите на сайт и отвяжите старый аккаунт."
        )
        return

    old_chat_id = user['chat_id']
    new_chat_id = message.from_user.id
    await db.link_account(old_chat_id, new_chat_id)

    await message.answer(
        f"✅ Аккаунт с email <b>{escape(email)}</b> привязан к Telegram!\n\n"
        f"📋 Ваши подписки перенесены.\n"
        f"Теперь уведомления о билетах будут приходить сюда."
    )


@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message):
    """Subscribe to a team (auto-subscribe to venue)."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "❗ Укажите название команды.\n"
            "Пример: /subscribe <code>ЦСКА</code>\n"
            "Список команд: /teams",
        )
        return

    team_input = " ".join(args[1:]).strip()
    team_canonical = normalize_team_name(team_input)

    if not team_canonical:
        await message.answer(
            f"❌ Команда '<b>{escape(team_input)}</b>' не найдена.\n"
            f"Посмотрите список: /teams",
        )
        return

    db = get_db()

    is_new_team = await db.subscribe(message.from_user.id, "team", team_canonical.lower())

    team_info = get_team_info(team_canonical)
    venue_subscribed = False
    if team_info:
        venue = f"{team_info['city']}, {team_info['venue']}"
        is_new_venue = await db.subscribe(message.from_user.id, "venue", venue.lower())
        venue_subscribed = is_new_venue

    if is_new_team:
        text = f"✅ Вы подписались на <b>{escape(team_canonical)}</b>!\n"
        if venue_subscribed:
            text += f"🏟 Автоматически добавлена подписка на стадион: <b>{escape(team_info['venue'])}</b> ({escape(team_info['city'])})\n"
        text += "\nТеперь вы будете получать уведомления о билетах."
        await message.answer(text)
    else:
        await message.answer(f"ℹ️ Вы уже подписаны на <b>{escape(team_canonical)}</b>.")


@router.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: Message):
    """Unsubscribe from a team."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "❗ Укажите название команды.\n"
            "Пример: /unsubscribe <code>ЦСКА</code>",
        )
        return

    team_input = " ".join(args[1:]).strip()
    team_canonical = normalize_team_name(team_input)

    if not team_canonical:
        await message.answer(
            f"❌ Команда '<b>{escape(team_input)}</b>' не найдена.",
        )
        return

    db = get_db()
    removed = await db.unsubscribe(message.from_user.id, "team", team_canonical.lower())

    if removed:
        await message.answer(
            f"❌ Вы отписались от <b>{escape(team_canonical)}</b>.",
        )
    else:
        await message.answer(
            f"ℹ️ Вы не были подписаны на <b>{escape(team_canonical)}</b>.",
        )


@router.message(Command("list"))
async def cmd_list(message: Message):
    """Show user subscriptions."""
    db = get_db()
    subs = await db.get_user_subscriptions(message.from_user.id)

    teams = subs.get("team", [])
    venues = subs.get("venue", [])

    if not teams and not venues:
        await message.answer(
            "📭 У вас пока нет подписок.\n"
            "Подпишитесь: /subscribe <code>ЦСКА</code>",
        )
        return

    text = "📋 <b>Ваши подписки:</b>\n\n"

    if teams:
        text += f"<b>🏒 Команды ({len(teams)}):</b>\n"
        for t in teams:
            canonical = _VARIANT_TO_TEAM.get(t, t)
            text += f"• {escape(canonical)}\n"
        text += "\n"

    if venues:
        text += f"<b>🏟 Стадионы ({len(venues)}):</b>\n"
        for v in venues:
            text += f"• {escape(v.title())}\n"

    text += "\nЧтобы отписаться: /unsubscribe <code>ЦСКА</code>"

    await message.answer(text)


@router.message(Command("matches"))
async def cmd_matches(message: Message):
    """Show all current matches."""
    db = get_db()
    matches = await db.get_all_matches()

    if not matches:
        await message.answer("📭 Сейчас нет доступных матчей в базе.")
        return

    text = f"🏒 <b>Актуальные матчи ({len(matches)}):</b>\n\n"

    for i, match in enumerate(matches[:10], 1):
        title = escape(match['title'])
        date = escape(match['date'])
        place = escape(match['place'])

        text += f"<b>{i}. {title}</b>\n"
        text += f"   📅 {date}\n"
        text += f"   📍 {place}\n"
        text += f"   💰 {match['price_min']} – {match['price_max']}\n"
        text += f"   ✅ {match['availability']}\n\n"

    if len(matches) > 10:
        text += f"...и ещё {len(matches) - 10} матчей\n"

    text += "\nПодробности: /match " + escape("<номер>") + "\nНапример: /match 1"

    await message.answer(text)


@router.message(Command("match"))
async def cmd_match(message: Message):
    """Show match details."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❗ Укажите номер матча.\nПример: /match 1")
        return

    try:
        match_num = int(args[1])
    except ValueError:
        await message.answer("❗ Неверный номер. Пример: /match 1")
        return

    db = get_db()
    matches = await db.get_all_matches()

    if match_num < 1 or match_num > len(matches):
        await message.answer(f"❗ Матч #{match_num} не найден. Всего матчей: {len(matches)}")
        return

    match = matches[match_num - 1]

    title = escape(match['title'])
    date = escape(match['date'])
    place = escape(match['place'])
    venue = escape(match['venue'])
    city = escape(match['city'])
    teams = escape(match['teams'])

    text = (
        f"🏒 <b>{title}</b>\n\n"
        f"📅 <b>Дата:</b> {date}\n"
        f"📍 <b>Место:</b> {place}\n"
        f"🏟 <b>Арена:</b> {venue}\n"
        f"🌆 <b>Город:</b> {city}\n"
        f"⚔️ <b>Команды:</b> {teams}\n\n"
        f"💰 <b>Цена:</b> {match['price_min']} – {match['price_max']}\n"
        f"✅ <b>Наличие:</b> {match['availability']}\n\n"
        f"🔗 <a href=\"{match['link']}\">Купить билет</a>"
    )

    await message.answer(text)


@router.message(Command("teams"))
async def cmd_teams(message: Message):
    """Show all available teams."""
    teams = get_all_team_names()
    teams_list = "\n".join(f"• <code>{escape(t)}</code>" for t in teams)

    text = (
        f"🏒 <b>Доступные команды ({len(teams)}):</b>\n\n"
        f"{teams_list}\n\n"
        f"Подписаться: /subscribe <code>ЦСКА</code>"
    )
    await message.answer(text)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Bot statistics."""
    db = get_db()
    stats = await db.get_stats()
    text = (
        f"📊 <b>Статистика бота:</b>\n\n"
        f"👥 Пользователей: <b>{stats['users']}</b>\n"
        f"🏒 Подписок на команды: <b>{stats['team_subs']}</b>\n"
        f"🏟 Подписок на стадионы: <b>{stats['venue_subs']}</b>\n"
        f"🎟 Матчей в базе: <b>{stats['matches']}</b>"
    )
    await message.answer(text)



class TelegramBot:
    """Wrapper for starting the Telegram bot."""

    def __init__(self, token: str):
        if not token:
            raise ValueError("Не указан токен Telegram-бота. Укажите BOT_TOKEN в .env")

        proxy = os.environ.get("BOT_PROXY", "")
        if proxy:
            from aiogram.client.session.aiohttp import AiohttpSession
            session = AiohttpSession(proxy=proxy)
            self.bot = Bot(
                token=token,
                session=session,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
        else:
            self.bot = Bot(
                token=token,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
        self.dp = Dispatcher()
        self.dp.include_router(router)
        self._polling_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        """Start the bot and wait for stop signal."""
        await self.bot.set_my_commands([
            BotCommand(command="start", description="Приветствие"),
            BotCommand(command="subscribe", description="Подписаться на команду"),
            BotCommand(command="unsubscribe", description="Отписаться"),
            BotCommand(command="list", description="Мои подписки"),
            BotCommand(command="matches", description="Все матчи"),
            BotCommand(command="match", description="Детали матча"),
            BotCommand(command="teams", description="Все команды"),
            BotCommand(command="stats", description="Статистика"),
            BotCommand(command="help", description="Помощь"),
        ])

        logger.info("Telegram-бот запущен")

        async def _polling_forever():
            while not self._stop_event.is_set():
                try:
                    await self.dp.start_polling(self.bot, handle_signals=False)
                    logger.info("Polling завершился штатно, перезапуск...")
                    await asyncio.sleep(1)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.warning(f"Polling error: {e}, restarting in 3s...")
                    await asyncio.sleep(3)

        self._polling_task = asyncio.create_task(_polling_forever())
        await self._stop_event.wait()

    async def stop(self) -> None:
        """Stop the bot."""
        self._stop_event.set()
        if self._polling_task:
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
        await self.bot.session.close()
        logger.info("Telegram-бот остановлен")

    def get_bot(self) -> Bot:
        return self.bot