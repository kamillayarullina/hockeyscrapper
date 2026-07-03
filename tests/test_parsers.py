"""Тесты парсеров на мок-данных (без Playwright, без live-сайтов)."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

MOCK_DIR = Path(__file__).parent / "mock_data"


def make_config(name: str, parser_type: str) -> dict:
    return {
        "name": name,
        "parser": parser_type,
        "url": "https://example.com",
        "params": {
            "keywords": ["хоккей", "кхл", "цска", "спартак", "динамо", "ска",
                         "авангард", "ак барс", "металлург", "трактор",
                         "локомотив", "сибирь", "торпедо"],
            "timeout_ms": 30000,
        },
        "_retry_attempts": 1,
        "_min_delay": 0.01,
        "_max_delay": 0.01,
        "_headless": True,
    }


async def test_club_parser():
    """ClubParser: парсинг страницы с карточками событий."""
    from parsers.club_parser import ClubParser

    config = make_config("ticket_hockey", "club")
    parser = ClubParser(config)

    html = (MOCK_DIR / "club_parser_hockey.html").read_text(encoding="utf-8")
    events = await parser.parse(html)

    assert len(events) == 9, f"Ожидалось 9 событий, получено {len(events)}"

    event = events[0]
    assert "цска" in event["title"].lower()
    assert "спартак" in event["title"].lower()
    assert event["price_min"] != "Не указана"
    assert "ticket-hockey.ru" in event["link"]
    assert event["source"] == "ticket_hockey"

    sold_out = [e for e in events if "распродано" in e["availability"].lower()]
    print(f"  - Найдено матчей: {len(events)}")
    print(f"  - Распродано: {len(sold_out)}")
    for e in events:
        print(f"    • {e['title']} | {e['date']} | {e['place']} | {e['price_min']}–{e['price_max']} | {e['availability']}")
    return events


async def test_club_parser_empty_html():
    """ClubParser: пустой HTML не ломается."""
    from parsers.club_parser import ClubParser

    parser = ClubParser(make_config("test", "club"))
    events = await parser.parse("<html></html>")
    assert events == [], f"Ожидался пустой список, получено {len(events)}"


async def test_club_parser_no_keywords():
    """ClubParser: события без ключевых слов отфильтровываются."""
    from parsers.club_parser import ClubParser

    config = make_config("test", "club")
    config["params"]["keywords"] = ["футбол"]
    parser = ClubParser(config)

    html = (MOCK_DIR / "club_parser_hockey.html").read_text(encoding="utf-8")
    events = await parser.parse(html)

    assert len(events) == 0, f"Хоккейные события не должны пройти с ключевым словом 'футбол'"


async def test_club_parser_extract_place():
    """ClubParser: парсинг места проведения."""
    from parsers.club_parser import ClubParser
    from bs4 import BeautifulSoup

    parser = ClubParser(make_config("test", "club"))
    html = '<div class="event-card"><h3>Тест</h3><div class="place">Москва, ЦСКА Арена</div><a href="/event/1">link</a></div>'
    soup = BeautifulSoup(html, "html.parser")
    card = soup.select_one(".event-card")
    place = parser._extract_place(card)
    assert place == "Москва, ЦСКА Арена", f"Ожидалось 'Москва, ЦСКА Арена', получено '{place}'"


async def test_club_parser_extract_prices():
    """ClubParser: парсинг цен."""
    from parsers.club_parser import ClubParser
    from bs4 import BeautifulSoup

    parser = ClubParser(make_config("test", "club"))
    html = '<div class="event-card"><h3>Тест</h3><div>от 800 ₽</div><a href="/event/1">link</a></div>'
    soup = BeautifulSoup(html, "html.parser")
    card = soup.select_one(".event-card")
    pmin, pmax = parser._extract_prices(card)
    assert "800" in pmin, f"Минимальная цена должна содержать 800, получено '{pmin}'"


async def test_yandex_parser_jsonld():
    """YandexParser: извлечение из JSON-LD."""
    from parsers.yandex_parser import YandexParser
    from bs4 import BeautifulSoup

    parser = YandexParser(make_config("yandex_test", "yandex"))

    html = (MOCK_DIR / "yandex_event_1.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    data = parser._extract_from_json_ld(soup)

    assert data is not None, "JSON-LD не извлечён"
    assert "ЦСКА" in data["title"]
    assert "Спартак" in data["title"]
    assert data["price_min"] != "Не указана"
    assert data["availability"] == "Да"
    print(f"  - JSON-LD: {data['title']} | {data['date']} | {data['place']} | {data['price_min']}–{data['price_max']}")


async def test_yandex_parser_jsonld_list():
    """YandexParser: JSON-LD в формате списка."""
    from parsers.yandex_parser import YandexParser
    from bs4 import BeautifulSoup

    parser = YandexParser(make_config("yandex_test", "yandex"))

    html = (MOCK_DIR / "yandex_event_3.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    data = parser._extract_from_json_ld(soup)

    assert data is not None, "JSON-LD (список) не извлечён"
    assert "СКА" in data["title"]
    assert "Ак Барс" in data["title"]
    assert data["price_min"] == "1500 ₽"


async def test_yandex_parser_html_fallback():
    """YandexParser: fallback на HTML-парсинг, если нет JSON-LD."""
    from parsers.yandex_parser import YandexParser
    from bs4 import BeautifulSoup

    parser = YandexParser(make_config("yandex_test", "yandex"))

    html = (MOCK_DIR / "yandex_event_4.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    data = parser._extract_from_html(soup)

    assert data is not None, "HTML-парсинг не сработал"
    assert "Локомотив" in data["title"]
    assert "Трактор" in data["title"]
    assert data["price_min"] != "Не указана"
    print(f"  - HTML fallback: {data['title']} | {data['date']} | {data['place']} | {data['price_min']}–{data['price_max']}")


async def test_yandex_parser_catalog_filter():
    """YandexParser: фильтрация URL каталога."""
    from parsers.yandex_parser import YandexParser
    from bs4 import BeautifulSoup

    parser = YandexParser(make_config("yandex_test", "yandex"))

    html = (MOCK_DIR / "yandex_catalog.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    urls = parser._find_event_urls(soup)

    assert len(urls) == 4, f"Ожидалось 4 URL событий, получено {len(urls)}: {urls}"

    for url in urls:
        assert "/places/" not in url, f"URL места не должен проходить фильтр: {url}"
        assert "afisha.yandex.ru" in url or url.startswith("/")

    print(f"  - Найдено URL событий: {len(urls)}")
    for u in urls:
        print(f"    • {u}")


async def test_yandex_parser_parse_event_page():
    """YandexParser: _parse_event_page с разными страницами."""
    from parsers.yandex_parser import YandexParser

    parser = YandexParser(make_config("yandex_test", "yandex"))

    test_pages = [
        ("yandex_event_1.html", "ЦСКА"),
        ("yandex_event_2.html", "Динамо"),
        ("yandex_event_3.html", "СКА"),
        ("yandex_event_4.html", "Локомотив"),
    ]

    for filename, expected_team in test_pages:
        html = (MOCK_DIR / filename).read_text(encoding="utf-8")
        data = parser._parse_event_page(html, f"https://afisha.yandex.ru/{filename}")
        assert data is not None, f"Не удалось распарсить {filename}"
        assert expected_team in data["title"], f"В {filename} ожидалась команда {expected_team}"
        print(f"  ✅ {filename}: {data['title']} | {data['price_min']} | {data['availability']}")


async def test_team_matcher():
    """Извлечение команд из названий матчей."""
    from services.team_matcher import extract_teams_from_title

    test_cases = [
        ("ЦСКА – Спартак • КХЛ 2026/2027", ["ЦСКА", "Спартак"]),
        ("СКА — Ак Барс • Кубок Открытия", ["СКА", "Ак Барс"]),
        ("Динамо Москва — Авангард • КХЛ", ["Авангард", "Динамо Москва"]),
        ("Металлург Мг – Локомотив • КХЛ", ["Металлург", "Локомотив"]),
        ("Торпедо – Сибирь", ["Торпедо", "Сибирь"]),
        ("Динамо – СКА", ["Динамо Москва", "СКА"]),
        ("ЦСКА — Динамо Москва", ["ЦСКА", "Динамо Москва"]),
        ("Концерт группы", []),
    ]

    for title, expected in test_cases:
        teams = extract_teams_from_title(title)
        for t in expected:
            assert t in teams, f"'{title}': ожидалась команда '{t}', получено {teams}"
        print(f"  ✅ {title[:40]:40s} -> {teams}")


async def test_database():
    """Базовые операции с БД (временный файл)."""
    import tempfile, os
    from services.database import Database

    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db = Database(tmp.name)
    await db.init()

    await db.add_user(12345, "testuser", "Test")
    await db.add_user(67890, "user2", "User2")

    subs = await db.get_user_subscriptions(12345)
    assert subs == {"team": [], "venue": []}

    ok = await db.subscribe(12345, "team", "цска")
    assert ok
    ok = await db.subscribe(12345, "venue", "москва, цска арена")
    assert ok

    subs = await db.get_user_subscriptions(12345)
    assert "цска" in subs["team"]
    assert "москва, цска арена" in subs["venue"]

    subscribers = await db.get_subscribers_for_teams(["цска"])
    assert 12345 in subscribers

    subscribers = await db.get_subscribers_for_venues(["москва, цска арена"])
    assert 12345 in subscribers

    ok = await db.unsubscribe(12345, "team", "цска")
    assert ok
    subs = await db.get_user_subscriptions(12345)
    assert "цска" not in subs["team"]

    await db.save_match({
        "match_id": "test|2026-09-12|test",
        "title": "Тестовый матч",
        "date": "2026-09-12",
        "place": "Москва",
        "venue": "ЦСКА Арена",
        "city": "москва",
        "teams": "ЦСКА, Спартак",
        "price_min": "800 ₽",
        "price_max": "5000 ₽",
        "availability": "Да",
        "link": "https://example.com",
        "source": "test",
    })

    match = await db.get_match_by_id("test|2026-09-12|test")
    assert match is not None
    assert match["title"] == "Тестовый матч"

    stats = await db.get_stats()
    assert stats["users"] == 2
    assert stats["matches"] == 1

    print(f"  ✅ Все операции с БД прошли успешно")
    print(f"  - Пользователей: {stats['users']}")
    print(f"  - Подписок на команды: {stats['team_subs']}")
    print(f"  - Подписок на стадионы: {stats['venue_subs']}")
    print(f"  - Матчей: {stats['matches']}")

    os.unlink(tmp.name)


async def test_notifier_format():
    """Notifier: форматирование сообщений."""
    from services.notifier import Notifier

    notifier = Notifier(None, admin_chat_id=0)

    event = {
        "title": "ЦСКА — Спартак",
        "date": "12 сентября 2026",
        "place": "Москва, ЦСКА Арена",
        "price_min": "800 ₽",
        "price_max": "5 000 ₽",
        "availability": "Да",
        "link": "https://example.com",
    }

    msg = notifier._format_message(event, "ЦСКА, Спартак", "new")
    assert "ЦСКА" in msg
    assert "Спартак" in msg
    assert "800" in msg
    assert "5 000" in msg
    assert "example.com" in msg

    msg_avail = notifier._format_message(event, "ЦСКА", "available")
    assert "БИЛЕТЫ ПОЯВИЛИСЬ" in msg_avail

    print(f"  ✅ Форматирование сообщений работает")


async def test_protection_detector():
    """ProtectionDetector: базовая проверка."""
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from parsers.protection_detector import ProtectionDetector

    clean = "<html><body><div>нормальная страница</div></body></html>"
    assert not ProtectionDetector.detect_captcha(clean)
    assert not ProtectionDetector.detect_cloudflare(clean)
    assert ProtectionDetector.get_protection_level(clean, "") == "none"

    protected_1 = '<html><body><div>g-recaptcha</div></body></html>'
    assert ProtectionDetector.detect_captcha(protected_1)

    protected_2 = '<html><body><script>_cf_chl_opt</script></body></html>'
    assert ProtectionDetector.detect_cloudflare(protected_2)

    assert ProtectionDetector.get_protection_level(protected_2, "") == "cloudflare"
    assert ProtectionDetector.get_protection_level("", "") == "unknown"

    print(f"  ✅ ProtectionDetector работает")


async def test_khl_parser():
    """KHLParser: парсинг страницы билетов КХЛ."""
    from parsers.khl_parser import KHLParser

    config = {
        "name": "khl_ru",
        "parser": "khl",
        "url": "https://www.khl.ru/tickets/",
        "params": {"keywords": ["кхл"], "timeout_ms": 30000},
        "_retry_attempts": 1, "_min_delay": 0.01, "_max_delay": 0.01, "_headless": True,
    }
    parser = KHLParser(config)

    html = (MOCK_DIR / "khl_tickets_page.html").read_text(encoding="utf-8")
    events = await parser.parse(html)

    assert len(events) == 5, f"Ожидалось 5 матчей, получено {len(events)}"

    match_cska = [e for e in events if "ЦСКА" in e["title"]][0]
    assert "Спартак" in match_cska["title"]
    assert match_cska["price_min"] != "Не указана"
    assert "khl.ru" in match_cska["link"]

    sold_out = [e for e in events if "Нет" in e["availability"]]
    assert len(sold_out) == 1, f"Ожидался 1 распроданный, получено {len(sold_out)}"

    print(f"  - Всего матчей: {len(events)}")
    for e in events:
        avail = "распродано" if e["availability"] == "Нет" else "есть билеты"
        print(f"    • {e['title']} | {e['date']} | {e['place']} | {e['price_min']} | {avail}")


async def test_match_dedup_cross_source():
    """Проверка кросс- source дедупликации матчей в БД."""
    import tempfile, os
    from services.database import Database

    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db = Database(tmp.name)
    await db.init()

    match_data = {
        "match_id": "СКА — Ак Барс|2026-09-16",
        "title": "СКА — Ак Барс",
        "date": "2026-09-16",
        "place": "Санкт-Петербург, СКА Арена",
        "venue": "СКА Арена",
        "city": "санкт-петербург",
        "teams": "СКА, Ак Барс",
        "price_min": "1500 ₽",
        "price_max": "7500 ₽",
        "availability": "Да",
        "link": "https://site-a.ru/match",
    }
    await db.save_match(match_data, source_name="site_a")
    assert await db.get_match_by_id(match_data["match_id"]) is not None

    existing = await db.get_match_by_id(match_data["match_id"])
    assert "site_a" in existing["sources"]
    assert existing["availability"] == "Да"

    await db.save_match(match_data, source_name="site_b")
    updated = await db.get_match_by_id(match_data["match_id"])
    assert "site_b" in updated["sources"]
    assert "site_a" in updated["sources"]

    os.unlink(tmp.name)
    print(f"  ✅ Кросс- source дедупликация работает")


if __name__ == "__main__":
    import asyncio

    tests = [
        ("ClubParser: парсинг страницы", test_club_parser),
        ("ClubParser: пустой HTML", test_club_parser_empty_html),
        ("ClubParser: фильтр по ключевым словам", test_club_parser_no_keywords),
        ("ClubParser: извлечение места", test_club_parser_extract_place),
        ("ClubParser: извлечение цен", test_club_parser_extract_prices),
        ("YandexParser: JSON-LD", test_yandex_parser_jsonld),
        ("YandexParser: JSON-LD список", test_yandex_parser_jsonld_list),
        ("YandexParser: HTML fallback", test_yandex_parser_html_fallback),
        ("YandexParser: фильтрация каталога", test_yandex_parser_catalog_filter),
        ("YandexParser: _parse_event_page", test_yandex_parser_parse_event_page),
        ("TeamMatcher: извлечение команд", test_team_matcher),
        ("База данных: операции", test_database),
        ("Notifier: форматирование", test_notifier_format),
        ("ProtectionDetector: проверка", test_protection_detector),
        ("KHLParser: парсинг страницы", test_khl_parser),
        ("MatchDedup: кросс- source", test_match_dedup_cross_source),
    ]

    passed = 0
    failed = 0

    print("=" * 60)
    print("🏒 ТЕСТЫ ПАРСЕРА (МОК-ДАННЫЕ)")
    print("=" * 60)

    for name, test_fn in tests:
        try:
            asyncio.run(test_fn())
            print(f"  ✅ {name}")
            passed += 1
        except Exception as e:
            import traceback
            print(f"  ❌ {name}: {e}")
            traceback.print_exc()
            failed += 1
        print()

    print("=" * 60)
    print(f"🎯 Результат: {passed} пройдено, {failed} провалено")
    print("=" * 60)

    sys.exit(1 if failed > 0 else 0)
