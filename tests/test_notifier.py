import pytest
from unittest.mock import AsyncMock, MagicMock
from services.notifier import Notifier

@pytest.fixture
def mock_bot():
    """Фикстура для мокирования Telegram-бота."""
    bot = MagicMock()
    bot.send_message = AsyncMock()
    return bot

@pytest.fixture
def mock_db():
    """Фикстура для мокирования БД с поведением для нотификатора."""
    db = MagicMock()
    # По умолчанию считаем, что уведомление еще не отправлялось
    db.was_event_notified = AsyncMock(return_value=False)
    db.mark_event_notified = AsyncMock()
    return db

@pytest.mark.asyncio
async def test_notify_subscribers_sends_message(mock_bot, mock_db):
    """Тест: Notifier успешно отправляет сообщение подписчику."""
    notifier = Notifier(mock_bot)
    event = {"title": "Test Event", "date": "2026-01-01", "link": "http://a.com"}
    subscribers = [12345]

    sent_count = await notifier.notify_subscribers(event, subscribers, mock_db, reason="new")

    assert sent_count == 1
    mock_bot.send_message.assert_called_once()
    mock_db.mark_event_notified.assert_called_once()

@pytest.mark.asyncio
async def test_notify_subscribers_skips_already_notified(mock_bot, mock_db):
    """Тест: Notifier не отправляет повторное уведомление, если оно уже было."""
    mock_db.was_event_notified.return_value = True  # Имитируем, что уже отправляли
    notifier = Notifier(mock_bot)
    event = {"title": "Test Event", "date": "2026-01-01", "link": "http://a.com"}
    subscribers = [12345]

    sent_count = await notifier.notify_subscribers(event, subscribers, mock_db, reason="new")

    assert sent_count == 0
    mock_bot.send_message.assert_not_called()

@pytest.mark.parametrize("reason, expected_header", [
    ("new", "🏒 <b>Новый хоккейный матч!</b>"),
    ("available", "🎟 <b>БИЛЕТЫ ПОЯВИЛИСЬ В ПРОДАЖЕ!</b>"),
    ("sold_out", "❌ <b>БИЛЕТЫ ЗАКОНЧИЛИСЬ!</b>"),
    ("changed", "🔄 <b>Изменение статуса матча</b>"),
])
def test_format_message_uses_correct_header(reason, expected_header):
    """Тест: _format_message использует правильный заголовок в зависимости от причины."""
    notifier = Notifier(bot=None)
    event = {
        "title": "Спартак - Динамо", "date": "01.01.2026",
        "place": "Арена-2000", "price_min": "500 ₽", "price_max": "1000 ₽",
        "availability": "Да", "link": "http://example.com"
    }
    message = notifier._format_message(event, "Спартак, Динамо", reason)
    assert message.startswith(expected_header)