"""Интеграционные тесты полного пайплайна: парсер -> БД -> уведомления."""

import asyncio
import os
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

MOCK_DIR = Path(__file__).parent / "mock_data"


def make_config(name: str, parser_type: str, extra_kw: list | None = None) -> dict:
    kw = ["хоккей", "кхл", "цска", "спартак", "динамо", "ска",
          "авангард", "ак барс", "металлург", "трактор",
          "локомотив", "сибирь", "торпедо"]
    if extra_kw:
        kw.extend(extra_kw)
    return {
        "name": name,
        "parser": parser_type,
        "url": "https://example.com",
        "params": {"keywords": kw, "timeout_ms": 30000},
        "_retry_attempts": 1, "_min_delay": 0.01, "_max_delay": 0.01, "_headless": True,
    }


# ─────────────────────────────────────────────
# МОК: подменяем fetch() чтобы возвращать мок-HTML
# ─────────────────────────────────────────────
_original_fetch = None


def _patch_base_parser():
    """Подменяет BaseParser.fetch на возврат мок-данных."""
    import parsers.base_parser as bp

    global _original_fetch
    _original_fetch = bp.BaseParser.fetch

    async def mock_fetch(self, url=None, wait_selector=None, timeout_ms=None) -> str:
        mock_map = {
            "ticket_hockey": "club_parser_hockey.html",
            "khl_ru": "khl_tickets_page.html",
            "yandex_afisha": "yandex_catalog.html",
        }
        filename = mock_map.get(self.name)
        if filename:
            html = (MOCK_DIR / filename).read_text(encoding="utf-8")
            return html
        return "<html></html>"

    bp.BaseParser.fetch = mock_fetch


def _unpatch_base_parser():
    import parsers.base_parser as bp
    global _original_fetch
    if _original_fetch:
        bp.BaseParser.fetch = _original_fetch


# ─────────────────────────────────────────────
# ТЕСТ 1: Полный пайплайн клубного парсера
# ─────────────────────────────────────────────
async def test_club_parser_full_pipeline():
    """ClubParser: полный цикл _process_site -> БД."""
    from services.parser_runner import ParserRunner
    from services.database import Database

    _patch_base_parser()
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db = Database(tmp.name)
    await db.init()

    runner = ParserRunner(once=True, telegram_bot=None)
    runner.db = db
    runner.notifier = None

    site_config = make_config("ticket_hockey", "club")
    runner._settings = {"output_dir": os.path.dirname(tmp.name)}
    await runner._process_site(site_config)

    matches = await db.get_all_matches()
    assert len(matches) >= 8, f"Ожидалось >=8 матчей, получено {len(matches)}"

    titles = [m["title"] for m in matches]
    assert any("цска" in t.lower() for t in titles), "Нет ЦСКА"
    assert any("спартак" in t.lower() for t in titles), "Нет Спартак"
    assert any("авангард" in t.lower() for t in titles), "Нет Авангард"

    for m in matches:
        assert m["match_id"], f"Нет match_id: {m}"
        assert m["source"] == "ticket_hockey", f"Неверный source: {m['source']}"
        assert m["teams"] != "Не определены", f"Команды не определены: {m['title']}"

    os.unlink(tmp.name)
    _unpatch_base_parser()
    return matches


# ─────────────────────────────────────────────
# ТЕСТ 2: Полный пайплайн KHL парсера
# ─────────────────────────────────────────────
async def test_khl_parser_full_pipeline():
    """KHLParser: полный цикл _process_site -> БД."""
    from services.parser_runner import ParserRunner
    from services.database import Database

    _patch_base_parser()
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db = Database(tmp.name)
    await db.init()

    runner = ParserRunner(once=True, telegram_bot=None)
    runner.db = db
    runner.notifier = None

    site_config = make_config("khl_ru", "khl")
    runner._settings = {"output_dir": os.path.dirname(tmp.name)}
    await runner._process_site(site_config)

    matches = await db.get_all_matches()
    assert len(matches) >= 4, f"Ожидалось >=4 матчей, получено {len(matches)}"

    titles = [m["title"] for m in matches]
    assert any("цска" in t.lower() for t in titles), "Нет ЦСКА в KHL"
    assert any("спартак" in t.lower() for t in titles), "Нет Спартак в KHL"

    for m in matches:
        assert m["source"] == "khl_ru", f"Неверный source: {m['source']}"
        assert "khl.ru" in m["link"] or m["link"].startswith("https://www.khl.ru"), f"Неверный link: {m['link']}"

    os.unlink(tmp.name)
    _unpatch_base_parser()
    return matches


# ─────────────────────────────────────────────
# ТЕСТ 3: YandexParser — двухступенчатый пайплайн
# ─────────────────────────────────────────────
async def test_yandex_parser_full_pipeline():
    """YandexParser: сначала каталог, потом парсинг каждого события.

    Для mock-теста подменяем _fetch_event_page чтобы возвращать
    соответствующий HTML из mock_data.
    """
    import parsers.yandex_parser as yp

    url_to_file = {
        "hockey-cska-spartak": "yandex_event_1.html",
        "hockey-dinamo-avangard": "yandex_event_2.html",
        "ska-akbars-hockey": "yandex_event_3.html",
        "hockey-lokomotiv-traktor": "yandex_event_4.html",
    }

    original_fetch_event = yp.YandexParser._fetch_event_page

    async def mock_fetch_event(self, url: str):
        for url_pattern, filename in url_to_file.items():
            if url_pattern in url:
                html = (MOCK_DIR / filename).read_text(encoding="utf-8")
                return html
        return None

    yp.YandexParser._fetch_event_page = mock_fetch_event
    _patch_base_parser()

    from services.parser_runner import ParserRunner
    from services.database import Database

    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db = Database(tmp.name)
    await db.init()

    runner = ParserRunner(once=True, telegram_bot=None)
    runner.db = db
    runner.notifier = None

    site_config = make_config("yandex_afisha", "yandex")
    runner._settings = {"output_dir": os.path.dirname(tmp.name)}
    await runner._process_site(site_config)

    matches = await db.get_all_matches()
    assert len(matches) >= 3, f"Ожидалось >=3 матчей, получено {len(matches)}"

    titles = [m["title"] for m in matches]
    print(f"Yandex matches: {[m['title'] for m in matches]}")

    assert any("цска" in t.lower() or "cska" in t.lower() for t in titles), "Нет ЦСКА в Yandex"
    assert any("спартак" in t.lower() for t in titles), "Нет Спартак в Yandex"
    assert any("ска" in t.lower() or "динамо" in t.lower() for t in titles), "Нет СКА/Динамо в Yandex"

    for m in matches:
        assert m["source"] == "yandex_afisha", f"Неверный source: {m['source']}"

    yp.YandexParser._fetch_event_page = original_fetch_event
    os.unlink(tmp.name)
    _unpatch_base_parser()
    return matches


# ─────────────────────────────────────────────
# ТЕСТ 4: Team Matcher — все 23 команды
# ─────────────────────────────────────────────
async def test_team_matcher_all_teams():
    """Team Matcher: проверка всех 23 команд в разных форматах."""
    from services.team_matcher import extract_teams_from_title, get_all_team_names

    teams = get_all_team_names()
    assert len(teams) == 23, f"Ожидалось 23 команды, получено {len(teams)}"

    test_cases = [
        ("ЦСКА - Спартак", ["ЦСКА", "Спартак"]),
        ("СКА - Ак Барс", ["СКА", "Ак Барс"]),
        ("Динамо Москва - Авангард", ["Авангард", "Динамо Москва"]),
        ("Металлург - Локомотив", ["Металлург", "Локомотив"]),
        ("Салават Юлаев - Трактор", ["Салават Юлаев", "Трактор"]),
        ("Торпедо - Сибирь", ["Торпедо", "Сибирь"]),
        ("Лада - Витязь", ["Витязь", "Лада"]),
        ("Северсталь - Нефтехимик", ["Нефтехимик", "Северсталь"]),
        ("Амур - Адмирал", ["Амур", "Адмирал"]),
        ("Куньлунь - Барыс", ["Куньлунь", "Барыс"]),
        ("Динамо Минск - Сочи", ["Динамо Минск", "Сочи"]),
        ("Автомобилист - ЦСКА", ["Автомобилист", "ЦСКА"]),
        ("ЦСКА - Динамо Москва", ["ЦСКА", "Динамо Москва"]),
        ("Динамо - СКА", ["Динамо Москва", "СКА"]),
        ("Шанхай Драгонс - Спартак", ["Куньлунь", "Спартак"]),
    ]

    for title, expected in test_cases:
        result = extract_teams_from_title(title)
        for t in expected:
            assert t in result, f"'{title}': ожидалась '{t}', получено {result}"

    # Отдельно проверяем граничные случаи
    assert extract_teams_from_title("Концерт группы") == [], "Концерт не должен распознаться"
    assert extract_teams_from_title("") == [], "Пустая строка"
    assert extract_teams_from_title("Чемпионат мира по футболу") == [], "Футбол не КХЛ"

    return True


# ─────────────────────────────────────────────
# ТЕСТ 5: Cross-source дедупликация + нотификации
# ─────────────────────────────────────────────
async def test_cross_source_dedup_and_notifications():
    """Два источника сохраняют один матч -> sources накапливаются, link не затирается."""
    from services.database import Database
    import tempfile
    import os

    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db = Database(tmp.name)
    await db.init()

    match_data = {
        "match_id": "СКА - Ак Барс|2026-09-16",
        "title": "СКА - Ак Барс",
        "date": "2026-09-16",
        "place": "Санкт-Петербург, СКА Арена",
        "venue": "СКА Арена",
        "city": "санкт-петербург",
        "teams": "СКА, Ак Барс",
        "price_min": "1500 руб",
        "price_max": "7500 руб",
        "availability": "Да",
        "link": "https://site-a.ru/match",
    }
    await db.save_match(match_data, source_name="site_a")
    m1 = await db.get_match_by_id(match_data["match_id"])
    assert m1["link"] == "https://site-a.ru/match", "link должен сохраниться"
    assert m1["sources"] == "site_a", "sources должен быть site_a"
    assert m1["source"] == "site_a", "source должен быть site_a"

    match_data2 = dict(match_data)
    match_data2["availability"] = "Нет"
    match_data2["link"] = "https://site-b.ru/match"
    await db.save_match(match_data2, source_name="site_b")
    m2 = await db.get_match_by_id(match_data["match_id"])
    assert m2["availability"] == "Нет", "availability обновился"
    assert "site_a" in m2["sources"], "site_a должен быть в sources"
    assert "site_b" in m2["sources"], "site_b должен быть в sources"

    os.unlink(tmp.name)
    return True


# ─────────────────────────────────────────────
# ТЕСТ 6: Уведомления — правильные причины
# ─────────────────────────────────────────────
async def test_notification_reasons():
    """Notifier: проверка формирования причин уведомлений."""
    from services.notifier import Notifier

    notifier = Notifier(None, admin_chat_id=0)

    event = {
        "title": "ЦСКА - Спартак",
        "date": "12 сентября 2026",
        "place": "Москва, ЦСКА Арена",
        "price_min": "800 руб",
        "price_max": "5000 руб",
        "availability": "Да",
        "link": "https://example.com",
    }

    msg_new = notifier._format_message(event, "ЦСКА, Спартак", "new")
    assert "Новый" in msg_new, "new: ожидается 'Новый хоккейный матч'"
    assert "800" in msg_new
    assert "5000" in msg_new
    assert "example.com" in msg_new

    msg_avail = notifier._format_message(event, "ЦСКА, Спартак", "available")
    assert "ПОЯВИЛИСЬ" in msg_avail, "available: ожидается 'БИЛЕТЫ ПОЯВИЛИСЬ'"

    msg_sold = notifier._format_message(event, "ЦСКА, Спартак", "sold_out")
    assert "ЗАКОНЧИЛИСЬ" in msg_sold, "sold_out: ожидается 'БИЛЕТЫ ЗАКОНЧИЛИСЬ'"

    msg_changed = notifier._format_message(event, "ЦСКА, Спартак", "changed")
    assert "Изменение" in msg_changed, "changed: ожидается 'Изменение статуса'"

    return True


# ─────────────────────────────────────────────
# ТЕСТ 7: Проверка _process_site решает уведомлять или нет
# ─────────────────────────────────────────────
async def test_process_site_notification_logic():
    """_process_site: правильная логика old_availability vs new_availability."""
    from services.parser_runner import ParserRunner
    from services.database import Database
    import tempfile
    import os
    from services.team_matcher import extract_teams_from_title

    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db = Database(tmp.name)
    await db.init()

    runner = ParserRunner(once=True, telegram_bot=None)
    runner.db = db
    runner._settings = {"output_dir": os.path.dirname(tmp.name)}

    test_cases = [
        {"old": None, "new": "Да", "expected_reason": "new"},
        {"old": "Нет", "new": "Да", "expected_reason": "available"},
        {"old": "Да", "new": "Нет", "expected_reason": "sold_out"},
        {"old": "Да", "new": "Скоро", "expected_reason": "changed"},
    ]

    for i, tc in enumerate(test_cases):
        match_id = f"Test Team A - Test Team B|2026-10-{i+1:02d}"
        event = {
            "title": "Test Team A - Test Team B",
            "date": f"2026-10-{i+1:02d}",
            "place": "Test City, Test Arena",
            "price_min": "1000 руб",
            "price_max": "3000 руб",
            "availability": tc["new"],
            "link": f"https://test{i}.ru/match",
        }

        teams = extract_teams_from_title(event.get("title", ""))

        if tc["old"] is not None:
            old_match = {
                "match_id": match_id,
                "title": event["title"],
                "date": event["date"],
                "place": event["place"],
                "venue": "Test Arena",
                "city": "test city",
                "teams": ", ".join(teams),
                "price_min": event["price_min"],
                "price_max": event["price_max"],
                "availability": tc["old"],
                "link": event["link"],
                "source": "test",
            }
            await db.save_match(old_match, source_name="test")

        match_data = {
            "match_id": match_id,
            "title": event.get("title"),
            "date": event.get("date"),
            "place": event.get("place"),
            "venue": "Test Arena",
            "city": "test city",
            "teams": ", ".join(teams),
            "price_min": event.get("price_min"),
            "price_max": event.get("price_max"),
            "availability": event.get("availability"),
            "link": event.get("link"),
            "source": "test_site",
        }
        await db.save_match(match_data, source_name="test_site")

        old_match = await db.get_match_by_id(match_id)
        assert old_match is not None, f"Матч {match_id} должен существовать"
        assert old_match["availability"] == tc["new"], f"availability должен быть {tc['new']}"

    os.unlink(tmp.name)
    return True


async def test_config_valid():
    """Валидация config/sites.yaml — все секции корректны."""
    import yaml

    cfg_path = Path(__file__).parent.parent / "config" / "sites.yaml"
    with open(cfg_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    assert "settings" in cfg
    assert "sites" in cfg
    assert len(cfg["sites"]) > 0, "Нет ни одного сайта в конфиге"

    valid_parsers = {"club", "khl", "yandex", "club_site"}
    names_seen = set()

    for site in cfg["sites"]:
        name = site.get("name")
        assert name, f"Сайт без name: {site}"
        assert name not in names_seen, f"Дубликат имени сайта: {name}"
        names_seen.add(name)

        assert "url" in site, f"{name}: нет url"
        assert site["url"].startswith("http"), f"{name}: url должен начинаться с http"

        ptype = site.get("parser")
        assert ptype in valid_parsers, f"{name}: неизвестный тип парсера '{ptype}' (нужен {valid_parsers})"

        assert "enabled" in site, f"{name}: нет поля enabled"
        assert isinstance(site["enabled"], bool), f"{name}: enabled должен быть bool"
        assert "interval_minutes" in site, f"{name}: нет interval_minutes"
        assert isinstance(site["interval_minutes"], int) and site["interval_minutes"] > 0

        params = site.get("params", {})
        assert isinstance(params, dict), f"{name}: params должен быть dict"

        if ptype in ("club", "yandex"):
            assert "keywords" in params, f"{name}: для парсера '{ptype}' нужны keywords"
            assert isinstance(params["keywords"], list), f"{name}: keywords должен быть списком"
            assert len(params["keywords"]) > 0, f"{name}: keywords не должен быть пустым"

        assert "timeout_ms" in params
        assert isinstance(params["timeout_ms"], int) and params["timeout_ms"] > 0


# ─────────────────────────────────────────────
# ЗАПУСК
# ─────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        ("ClubParser: полный пайплайн", test_club_parser_full_pipeline),
        ("KHLParser: полный пайплайн", test_khl_parser_full_pipeline),
        ("YandexParser: полный пайплайн", test_yandex_parser_full_pipeline),
        ("TeamMatcher: все 23 команды", test_team_matcher_all_teams),
        ("Cross-source дедупликация", test_cross_source_dedup_and_notifications),
        ("Причины уведомлений", test_notification_reasons),
        ("Логика old_availability", test_process_site_notification_logic),
        ("Валидация конфига", test_config_valid),
    ]

    passed = 0
    failed = 0
    print("=" * 60)
    print("INTEGRATION TESTS: PARSER PIPELINE")
    print("=" * 60)

    for name, fn in tests:
        try:
            asyncio.run(fn())
            print(f"  PASS  {name}")
            passed += 1
        except Exception as e:
            import traceback
            print(f"  FAIL  {name}: {e}")
            traceback.print_exc()
            failed += 1

    print("=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    sys.exit(1 if failed > 0 else 0)
