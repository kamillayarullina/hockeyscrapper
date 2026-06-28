import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.parser_runner import ParserRunner

@pytest.fixture
def mock_db():
    """Фикстура для мокирования объекта базы данных."""
    db = MagicMock()
    db.init = AsyncMock()
    db.get_all_proxies = AsyncMock(return_value=[])
    db.get_match_by_id = AsyncMock(return_value=None)  # Имитируем, что матч новый
    db.save_match = AsyncMock()
    db.get_subscribers_for_teams = AsyncMock(return_value=[12345]) # Возвращаем одного подписчика
    db.get_subscribers_for_venues = AsyncMock(return_value=[])
    db.get_all_users = AsyncMock(return_value=[{"chat_id": 12345}])
    db.get_setting = AsyncMock(return_value="30")
    return db

@pytest.fixture
def mock_notifier():
    """Фикстура для мокирования сервиса уведомлений."""
    notifier = MagicMock()
    notifier.notify_subscribers = AsyncMock(return_value=1)
    return notifier

@pytest.fixture
def mock_parser():
    """Фикстура для мокирования парсера, возвращающего один тестовый матч."""
    parser = MagicMock()
    parser.run = AsyncMock(return_value=[
        {
            "title": "ЦСКА - Спартак",
            "date": "2026-10-10",
            "place": "г. Москва, ЦСКА Арена",
            "availability": "Да",
            "price_min": "1000",
            "price_max": "5000",
            "link": "http://example.com/ticket"
        }
    ])
    return parser

@pytest.mark.asyncio
@patch('services.parser_runner.get_db')
@patch('services.parser_runner.ParserFactory.create')
@patch('services.parser_runner.Notifier')
@patch('services.parser_runner.ConfigLoader.load')
async def test_parser_runner_new_match_notification(
    mock_load_config, mock_Notifier, mock_create_parser, mock_get_db,
    mock_db, mock_notifier, mock_parser
):
    """
    Тест: ParserRunner должен отправлять уведомление о новом матче.
    Проверяет полный цикл: запуск парсера -> обработка данных -> вызов нотификатора.
    """
    # Настройка моков
    mock_get_db.return_value = mock_db
    mock_create_parser.return_value = mock_parser
    mock_Notifier.return_value = mock_notifier
    mock_load_config.return_value = {
        "settings": {"default_interval_minutes": 30},
        "sites": [{"name": "test_site", "parser": "club", "enabled": True}]
    }

    # Инициализация и запуск
    runner = ParserRunner(once=True)
    await runner.load_config()
    runner.notifier = mock_notifier  # Убедимся, что используется наш мок

    # Запускаем один цикл обработки
    await runner.run_cycle()

    # Проверки
    # 1. Был вызван метод сохранения матча в БД
    mock_db.save_match.assert_called_once()
    saved_data = mock_db.save_match.call_args[0][0]
    assert saved_data["title"] == "ЦСКА - Спартак"
    assert saved_data["teams"] == "Спартак, ЦСКА"

    # 2. Был вызван метод получения подписчиков для команд из матча
    mock_db.get_subscribers_for_teams.assert_called_once_with(['Спартак', 'ЦСКА'])

    # 3. Была вызвана отправка уведомлений с правильными параметрами
    mock_notifier.notify_subscribers.assert_called_once()
    notify_args = mock_notifier.notify_subscribers.call_args.kwargs
    assert notify_args['reason'] == 'new'
    assert notify_args['subscriber_chat_ids'] == [12345]