"""Personal notifications for subscribers."""

import asyncio
import logging
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

logger = logging.getLogger(__name__)


class Notifier:
    """Sends personal notifications to subscribers via Telegram bot."""

    def __init__(self, bot: Optional[Bot]):
        self.bot = bot

    async def notify_subscribers(
        self,
        event: dict,
        subscriber_chat_ids: list[int],
        db,
        reason: str = "new",
    ) -> int:
        """
        Sends personal notifications to all subscribers.
        Returns the number of successfully sent.
        """
        if not self.bot or not subscriber_chat_ids:
            return 0

        event_id = f"{event.get('title')}|{event.get('date')}|{reason}"
        sent_count = 0


        from services.team_matcher import extract_teams_from_title
        teams = extract_teams_from_title(event.get("title", ""))
        teams_str = ", ".join(teams) if teams else "матч"

        for chat_id in subscriber_chat_ids:

            if await db.was_event_notified(event_id, chat_id):
                continue

            try:
                text = self._format_message(event, teams_str, reason)
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                )
                await db.mark_event_notified(event_id, chat_id)
                sent_count += 1
                logger.info(f"📨 Уведомление отправлено пользователю {chat_id}")
            except TelegramAPIError as e:
                if "bot was blocked" in str(e).lower() or "chat not found" in str(e).lower():
                    logger.warning(f"Пользователь {chat_id} заблокировал бота")

                else:
                    logger.error(f"Ошибка отправки {chat_id}: {e}")
            except Exception as e:
                logger.error(f"Ошибка отправки {chat_id}: {e}")

        return sent_count

    def _format_message(self, event: dict, teams_str: str, reason: str) -> str:
        """Format notification message."""
        if reason == "available":
            header = "🎟 <b>БИЛЕТЫ ПОЯВИЛИСЬ В ПРОДАЖЕ!</b>"
        elif reason == "sold_out":
            header = "❌ <b>БИЛЕТЫ ЗАКОНЧИЛИСЬ!</b>"
        elif reason == "changed":
            header = "🔄 <b>Изменение статуса матча</b>"
        else:
            header = "🏒 <b>Новый хоккейный матч!</b>"

        price_min = event.get("price_min", "Не указана")
        price_max = event.get("price_max", "Не указана")
        if price_min == price_max:
            price_block = f"💰 <b>Цена:</b> {price_min}"
        else:
            price_block = f"💰 <b>Цена:</b> {price_min} – {price_max}"

        return (
            f"{header}\n\n"
            f"🏟 <b>{event.get('title', '')}</b>\n"
            f"⚔️ <b>Команды:</b> {teams_str}\n"
            f"📅 <b>Дата:</b> {event.get('date', '')}\n"
            f"📍 <b>Место:</b> {event.get('place', '')}\n"
            f"{price_block}\n"
            f"✅ <b>Статус:</b> {event.get('availability', '')}\n\n"
            f"🔗 <a href=\"{event.get('link', '')}\">Купить билет</a>\n\n"
            f"<i>Вы получили это сообщение, т.к. подписаны на одну из команд.</i>\n"
            f"<i>Управление подписками: /list</i>"
        )