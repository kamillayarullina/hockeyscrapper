"""Работа с базой данных SQLite: пользователи, подписки, матчи."""

import aiosqlite
import logging
import os
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = os.environ.get("DB_PATH", str(_PROJECT_ROOT / "data" / "tickets.db"))


class Database:
    """Асинхронная работа с БД."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    async def init(self) -> None:
        """Создаёт таблицы."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    chat_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    chat_id INTEGER,
                    type TEXT,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (chat_id, type, value),
                    FOREIGN KEY (chat_id) REFERENCES users(chat_id)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    match_id TEXT PRIMARY KEY,
                    title TEXT,
                    date TEXT,
                    place TEXT,
                    venue TEXT,
                    city TEXT,
                    teams TEXT,
                    price_min TEXT,
                    price_max TEXT,
                    availability TEXT,
                    link TEXT,
                    source TEXT,
                    sources TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(date)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_matches_teams ON matches(teams)
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS notified_events (
                    event_id TEXT,
                    chat_id INTEGER,
                    notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (event_id, chat_id),
                    FOREIGN KEY (chat_id) REFERENCES users(chat_id)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS proxies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    proxy_type TEXT DEFAULT 'http',
                    country TEXT DEFAULT '',
                    enabled INTEGER DEFAULT 1,
                    note TEXT DEFAULT ''
                )
            """)
            try:
                await db.execute(
                    "ALTER TABLE users ADD COLUMN link_code TEXT"
                )
            except aiosqlite.OperationalError:
                pass
            await db.commit()
        logger.info(f"База данных инициализирована: {self.db_path}")

    # ─────────────────────────────────────────────
    # Пользователи
    # ─────────────────────────────────────────────
    async def add_user(self, chat_id: int, username: Optional[str], first_name: Optional[str]) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cols = ["chat_id", "username", "first_name", "is_active"]
            vals: list = [chat_id, username, first_name, 1]
            async with db.execute("PRAGMA table_info(users)") as c:
                existing = {r["name"] for r in await c.fetchall()}
            for extra, default in [("premium_plan", "free"), ("premium_until", None)]:
                if extra in existing:
                    cols.append(extra)
                    vals.append(default)
            await db.execute(
                f"INSERT INTO users ({', '.join(cols)}) "  # nosec B608
                f"VALUES ({', '.join('?' * len(cols))}) "
                f"ON CONFLICT(chat_id) DO UPDATE SET "
                f"username = excluded.username, first_name = excluded.first_name, is_active = 1",
                vals,
            )
            await db.commit()

    async def get_all_users(self) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users WHERE is_active = 1") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    # ─────────────────────────────────────────────
    # Подписки
    # ─────────────────────────────────────────────
    async def subscribe(self, chat_id: int, sub_type: str, value: str) -> bool:
        """Подписка (type: "team" или "venue")."""
        value = value.lower().strip()
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    "INSERT INTO subscriptions (chat_id, type, value) VALUES (?, ?, ?)",
                    (chat_id, sub_type, value),
                )
                await db.commit()
                return True
            except aiosqlite.IntegrityError:
                return False

    async def unsubscribe(self, chat_id: int, sub_type: str, value: str) -> bool:
        value = value.lower().strip()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM subscriptions WHERE chat_id = ? AND type = ? AND value = ?",
                (chat_id, sub_type, value),
            )
            await db.commit()
            return cursor.rowcount > 0

    async def get_user_subscriptions(self, chat_id: int) -> dict[str, list[str]]:
        """Возвращает подписки: {"team": [...], "venue": [...]}"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                    "SELECT type, value FROM subscriptions WHERE chat_id = ? ORDER BY type, value",
                    (chat_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                result = {"team": [], "venue": []}
                for row in rows:
                    result[row[0]].append(row[1])
                return result

    async def get_subscribers_for_teams(self, teams: list[str]) -> list[int]:
        """Находит подписчиков на команды."""
        if not teams:
            return []
        teams_lower = [t.lower().strip() for t in teams]
        placeholders = ",".join("?" for _ in teams_lower)

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                    f"""
                SELECT DISTINCT u.chat_id 
                FROM users u
                JOIN subscriptions s ON u.chat_id = s.chat_id
                WHERE s.type = 'team' AND s.value IN ({placeholders}) AND u.is_active = 1
                """,  # nosec B608
                    teams_lower,
            ) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def get_subscribers_for_venues(self, venues: list[str]) -> list[int]:
        """Находит подписчиков на стадионы."""
        if not venues:
            return []
        venues_lower = [v.lower().strip() for v in venues]
        placeholders = ",".join("?" for _ in venues_lower)

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                    f"""
                SELECT DISTINCT u.chat_id 
                FROM users u
                JOIN subscriptions s ON u.chat_id = s.chat_id
                WHERE s.type = 'venue' AND s.value IN ({placeholders}) AND u.is_active = 1
                """,  # nosec B608
                    venues_lower,
            ) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    # ─────────────────────────────────────────────
    # Матчи
    # ─────────────────────────────────────────────
    async def save_match(self, match: dict, source_name: str = "") -> None:
        """Сохраняет матч в БД с кросс- source дедупликацией.

        Если матч с таким match_id (title|date) уже существует:
        - Обновляет availability, цены, venue
        - Добавляет новый source к списку sources
        - Не затирает первый найденный link
        """
        match_id = match.get("match_id", "")
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM matches WHERE match_id = ?", (match_id,)) as cursor:
                existing_row = await cursor.fetchone()
                existing = dict(existing_row) if existing_row else None
            if existing:
                existing_sources = existing.get("sources", "")
                if source_name and source_name not in existing_sources:
                    new_sources = f"{existing_sources},{source_name}" if existing_sources else source_name
                else:
                    new_sources = existing_sources
                await db.execute("""
                    UPDATE matches SET
                        place = ?,
                        venue = ?,
                        city = ?,
                        teams = ?,
                        price_min = ?,
                        price_max = ?,
                        availability = ?,
                        source = ?,
                        sources = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE match_id = ?
                """, (
                    match.get("place", existing["place"]),
                    match.get("venue", existing["venue"]),
                    match.get("city", existing["city"]),
                    match.get("teams", existing["teams"]),
                    match.get("price_min", existing["price_min"]),
                    match.get("price_max", existing["price_max"]),
                    match.get("availability", existing["availability"]),
                    source_name or existing["source"],
                    new_sources,
                    match_id,
                ))
            else:
                await db.execute("""
                    INSERT INTO matches
                    (match_id, title, date, place, venue, city, teams,
                     price_min, price_max, availability, link, source, sources)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    match_id,
                    match.get("title"),
                    match.get("date"),
                    match.get("place"),
                    match.get("venue"),
                    match.get("city"),
                    match.get("teams"),
                    match.get("price_min"),
                    match.get("price_max"),
                    match.get("availability"),
                    match.get("link"),
                    source_name or match.get("source", ""),
                    source_name or "",
                ))
            await db.commit()

    async def get_all_matches(self) -> list[dict]:
        """Возвращает все актуальные матчи."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                    "SELECT * FROM matches ORDER BY date"
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_match_by_id(self, match_id: str) -> Optional[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                    "SELECT * FROM matches WHERE match_id = ?", (match_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    # ─────────────────────────────────────────────
    # Уведомления
    # ─────────────────────────────────────────────
    async def mark_event_notified(self, event_id: str, chat_id: int) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    "INSERT OR IGNORE INTO notified_events (event_id, chat_id) VALUES (?, ?)",
                    (event_id, chat_id),
                )
                await db.commit()
            except Exception as e:
                logger.warning(f"Не удалось пометить уведомление: {e}")

    async def was_event_notified(self, event_id: str, chat_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                    "SELECT 1 FROM notified_events WHERE event_id = ? AND chat_id = ?",
                    (event_id, chat_id),
            ) as cursor:
                return await cursor.fetchone() is not None

    async def get_stats(self) -> dict[str, int]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users WHERE is_active = 1") as cur:
                users = (await cur.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM subscriptions WHERE type = 'team'") as cur:
                team_subs = (await cur.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM subscriptions WHERE type = 'venue'") as cur:
                venue_subs = (await cur.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM matches") as cur:
                matches = (await cur.fetchone())[0]
        return {"users": users, "team_subs": team_subs, "venue_subs": venue_subs, "matches": matches}

    # ─────────────────────────────────────────────
    # Настройки (admin panel)
    # ─────────────────────────────────────────────
    async def get_setting(self, key: str, default: str = "") -> str:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cur:
                row = await cur.fetchone()
                return row[0] if row else default

    async def set_setting(self, key: str, value: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value)
            )
            await db.commit()

    async def get_all_settings(self) -> dict[str, str]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT key, value FROM settings") as cur:
                return {row[0]: row[1] for row in await cur.fetchall()}

    # ─────────────────────────────────────────────
    # Прокси (admin panel)
    # ─────────────────────────────────────────────
    async def add_proxy(self, url: str, proxy_type: str = "http", country: str = "", note: str = "") -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "INSERT INTO proxies (url, proxy_type, country, note) VALUES (?, ?, ?, ?)",
                (url, proxy_type, country, note),
            )
            await db.commit()
            return cur.lastrowid or 0

    async def remove_proxy(self, proxy_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute("DELETE FROM proxies WHERE id = ?", (proxy_id,))
            await db.commit()
            return cur.rowcount > 0

    async def get_all_proxies(self) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM proxies ORDER BY id") as cur:
                return [dict(row) for row in await cur.fetchall()]

    async def toggle_proxy(self, proxy_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute("SELECT enabled FROM proxies WHERE id = ?", (proxy_id,))
            row = await cur.fetchone()
            if not row:
                return False
            new_val = 0 if row[0] else 1
            await db.execute("UPDATE proxies SET enabled = ? WHERE id = ?", (new_val, proxy_id))
            await db.commit()
            return True


_db_instance: Optional[Database] = None


def get_db() -> Database:
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance