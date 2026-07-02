import os
import logging
from typing import Optional
from pathlib import Path
from databases import Database as DatabaseCore

logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("DB_PATH", "data/tickets.db")
DATABASE_URL = os.environ.get("DATABASE_URL", "")


def _build_url() -> str:
    if DATABASE_URL:
        url = DATABASE_URL
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        return url
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{DB_PATH}"


class Database:

    def __init__(self):
        self.db = DatabaseCore(_build_url())

    async def init(self) -> None:
        await self.db.connect()
        db_url = _build_url()
        if db_url.startswith("sqlite"):
            await self.db.execute("PRAGMA journal_mode=WAL")
            await self.db.execute("PRAGMA busy_timeout=5000")
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                email TEXT,
                telegram TEXT,
                password_hash TEXT,
                link_code TEXT,
                avatar_url TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        """)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                chat_id INTEGER,
                type TEXT,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (chat_id, type, value),
                FOREIGN KEY (chat_id) REFERENCES users(chat_id)
            )
        """)
        await self.db.execute("""
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
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(date)
        """)
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_matches_teams ON matches(teams)
        """)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS notified_events (
                event_id TEXT,
                chat_id INTEGER,
                notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (event_id, chat_id),
                FOREIGN KEY (chat_id) REFERENCES users(chat_id)
            )
        """)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        is_pg = "postgresql" in str(self.db.url)
        if is_pg:
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS proxies (
                    id SERIAL PRIMARY KEY,
                    url TEXT NOT NULL,
                    proxy_type TEXT DEFAULT 'http',
                    country TEXT DEFAULT '',
                    enabled INTEGER DEFAULT 1,
                    note TEXT DEFAULT ''
                )
            """)
        else:
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS proxies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    proxy_type TEXT DEFAULT 'http',
                    country TEXT DEFAULT '',
                    enabled INTEGER DEFAULT 1,
                    note TEXT DEFAULT ''
                )
            """)
        logger.info("database initialized")

    async def close(self) -> None:
        await self.db.disconnect()

    async def add_user(self, chat_id: int, username: Optional[str], first_name: Optional[str]) -> None:
        await self.db.execute("""
            INSERT INTO users (chat_id, username, first_name, is_active)
            VALUES (:chat_id, :username, :first_name, 1)
            ON CONFLICT(chat_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                is_active = 1
        """, {"chat_id": chat_id, "username": username, "first_name": first_name})

    async def get_all_users(self) -> list[dict]:
        rows = await self.db.fetch_all("SELECT * FROM users WHERE is_active = 1")
        return [dict(row) for row in rows]

    async def find_user_by_email(self, email: str) -> Optional[dict]:
        row = await self.db.fetch_one(
            "SELECT * FROM users WHERE email = :email",
            {"email": email.strip().lower()},
        )
        return dict(row) if row else None

    async def find_user_by_link_code(self, code: str) -> Optional[dict]:
        row = await self.db.fetch_one(
            "SELECT * FROM users WHERE link_code = :code",
            {"code": code},
        )
        return dict(row) if row else None

    async def set_link_code(self, chat_id: int, code: str) -> None:
        await self.db.execute(
            "UPDATE users SET link_code = :code WHERE chat_id = :chat_id",
            {"code": code, "chat_id": chat_id},
        )

    async def clear_link_code(self, chat_id: int) -> None:
        await self.db.execute(
            "UPDATE users SET link_code = NULL WHERE chat_id = :chat_id",
            {"chat_id": chat_id},
        )

    async def link_account(self, old_chat_id: int, new_chat_id: int) -> bool:
        async with self.db.transaction():
            old_user = await self.db.fetch_one(
                "SELECT * FROM users WHERE chat_id = :chat_id",
                {"chat_id": old_chat_id},
            )
            if not old_user:
                return False

            exists = await self.db.fetch_val(
                "SELECT 1 FROM users WHERE chat_id = :chat_id",
                {"chat_id": new_chat_id},
            )
            if not exists:
                await self.db.execute(
                    "INSERT INTO users (chat_id, is_active) VALUES (:chat_id, 1)",
                    {"chat_id": new_chat_id},
                )

            rows = await self.db.fetch_all(
                "SELECT type, value FROM subscriptions WHERE chat_id = :chat_id",
                {"chat_id": old_chat_id},
            )
            for row in rows:
                await self.db.execute(
                    "INSERT INTO subscriptions (chat_id, type, value) VALUES (:chat_id, :type, :value) ON CONFLICT(chat_id, type, value) DO NOTHING",
                    {"chat_id": new_chat_id, "type": row["type"], "value": row["value"]},
                )

            await self.db.execute(
                "DELETE FROM subscriptions WHERE chat_id = :chat_id",
                {"chat_id": old_chat_id},
            )

            await self.db.execute("""
                UPDATE users SET
                    email = COALESCE(NULLIF(:email, ''), email),
                    telegram = COALESCE(NULLIF(:telegram, ''), telegram),
                    password_hash = COALESCE(NULLIF(:password_hash, ''), password_hash),
                    is_active = 1
                WHERE chat_id = :chat_id
            """, {
                "email": old_user["email"] or "",
                "telegram": old_user["telegram"] or "",
                "password_hash": old_user["password_hash"] or "",
                "chat_id": new_chat_id,
            })

            await self.db.execute(
                "DELETE FROM users WHERE chat_id = :chat_id",
                {"chat_id": old_chat_id},
            )
        return True

    async def subscribe(self, chat_id: int, sub_type: str, value: str) -> bool:
        value = value.lower().strip()
        try:
            await self.db.execute(
                "INSERT INTO subscriptions (chat_id, type, value) VALUES (:chat_id, :type, :value)",
                {"chat_id": chat_id, "type": sub_type, "value": value},
            )
            return True
        except Exception:
            return False

    async def unsubscribe(self, chat_id: int, sub_type: str, value: str) -> bool:
        value = value.lower().strip()
        exists = await self.db.fetch_val(
            "SELECT 1 FROM subscriptions WHERE chat_id = :chat_id AND type = :type AND value = :value",
            {"chat_id": chat_id, "type": sub_type, "value": value},
        )
        if not exists:
            return False
        await self.db.execute(
            "DELETE FROM subscriptions WHERE chat_id = :chat_id AND type = :type AND value = :value",
            {"chat_id": chat_id, "type": sub_type, "value": value},
        )
        return True

    async def get_user_subscriptions(self, chat_id: int) -> dict[str, list[str]]:
        rows = await self.db.fetch_all(
            "SELECT type, value FROM subscriptions WHERE chat_id = :chat_id ORDER BY type, value",
            {"chat_id": chat_id},
        )
        result = {"team": [], "venue": []}
        for row in rows:
            result[row["type"]].append(row["value"])
        return result

    async def get_subscribers_for_teams(self, teams: list[str]) -> list[int]:
        if not teams:
            return []
        teams_lower = [t.lower().strip() for t in teams]
        placeholders = ", ".join(f":t{i}" for i in range(len(teams_lower)))
        values = {f"t{i}": t for i, t in enumerate(teams_lower)}
        query = (
            "SELECT DISTINCT u.chat_id FROM users u "
            "JOIN subscriptions s ON u.chat_id = s.chat_id "
            "WHERE s.type = 'team' AND s.value IN ({}) AND u.is_active = 1"
        ).format(placeholders)
        rows = await self.db.fetch_all(query, values)
        return [row[0] for row in rows]

    async def get_subscribers_for_venues(self, venues: list[str]) -> list[int]:
        if not venues:
            return []
        venues_lower = [v.lower().strip() for v in venues]
        placeholders = ", ".join(f":v{i}" for i in range(len(venues_lower)))
        values = {f"v{i}": t for i, t in enumerate(venues_lower)}
        query = (
            "SELECT DISTINCT u.chat_id FROM users u "
            "JOIN subscriptions s ON u.chat_id = s.chat_id "
            "WHERE s.type = 'venue' AND s.value IN ({}) AND u.is_active = 1"
        ).format(placeholders)
        rows = await self.db.fetch_all(query, values)
        return [row[0] for row in rows]

    async def save_match(self, match: dict, source_name: str = "") -> None:
        match_id = match.get("match_id", "")
        existing = await self.get_match_by_id(match_id)
        if existing:
            existing_sources = existing.get("sources", "")
            if source_name and source_name not in existing_sources:
                new_sources = f"{existing_sources},{source_name}" if existing_sources else source_name
            else:
                new_sources = existing_sources
            await self.db.execute("""
                UPDATE matches SET
                    place = :place,
                    venue = :venue,
                    city = :city,
                    teams = :teams,
                    price_min = :price_min,
                    price_max = :price_max,
                    availability = :availability,
                    source = :source,
                    sources = :sources,
                    updated_at = CURRENT_TIMESTAMP
                WHERE match_id = :match_id
            """, {
                "place": match.get("place", existing["place"]),
                "venue": match.get("venue", existing["venue"]),
                "city": match.get("city", existing["city"]),
                "teams": match.get("teams", existing["teams"]),
                "price_min": match.get("price_min", existing["price_min"]),
                "price_max": match.get("price_max", existing["price_max"]),
                "availability": match.get("availability", existing["availability"]),
                "source": source_name or existing["source"],
                "sources": new_sources,
                "match_id": match_id,
            })
        else:
            await self.db.execute("""
                INSERT INTO matches
                (match_id, title, date, place, venue, city, teams,
                 price_min, price_max, availability, link, source, sources)
                VALUES (:match_id, :title, :date, :place, :venue, :city, :teams,
                        :price_min, :price_max, :availability, :link, :source, :sources)
            """, {
                "match_id": match_id,
                "title": match.get("title"),
                "date": match.get("date"),
                "place": match.get("place"),
                "venue": match.get("venue"),
                "city": match.get("city"),
                "teams": match.get("teams"),
                "price_min": match.get("price_min"),
                "price_max": match.get("price_max"),
                "availability": match.get("availability"),
                "link": match.get("link"),
                "source": source_name or match.get("source", ""),
                "sources": source_name or "",
            })

    async def get_all_matches(self) -> list[dict]:
        rows = await self.db.fetch_all("SELECT * FROM matches ORDER BY date")
        return [dict(row) for row in rows]

    async def get_match_by_id(self, match_id: str) -> Optional[dict]:
        row = await self.db.fetch_one(
            "SELECT * FROM matches WHERE match_id = :match_id",
            {"match_id": match_id},
        )
        return dict(row) if row else None

    async def mark_event_notified(self, event_id: str, chat_id: int) -> None:
        try:
            await self.db.execute(
                "INSERT INTO notified_events (event_id, chat_id) VALUES (:event_id, :chat_id) ON CONFLICT(event_id, chat_id) DO NOTHING",
                {"event_id": event_id, "chat_id": chat_id},
            )
        except Exception as e:
            logger.warning(f"mark_event_notified failed: {e}")

    async def was_event_notified(self, event_id: str, chat_id: int) -> bool:
        result = await self.db.fetch_val(
            "SELECT 1 FROM notified_events WHERE event_id = :event_id AND chat_id = :chat_id",
            {"event_id": event_id, "chat_id": chat_id},
        )
        return result is not None

    async def get_stats(self) -> dict[str, int]:
        users = await self.db.fetch_val("SELECT COUNT(*) FROM users WHERE is_active = 1") or 0
        team_subs = await self.db.fetch_val("SELECT COUNT(*) FROM subscriptions WHERE type = 'team'") or 0
        venue_subs = await self.db.fetch_val("SELECT COUNT(*) FROM subscriptions WHERE type = 'venue'") or 0
        matches = await self.db.fetch_val("SELECT COUNT(*) FROM matches") or 0
        return {"users": users, "team_subs": team_subs, "venue_subs": venue_subs, "matches": matches}

    async def get_setting(self, key: str, default: str = "") -> str:
        row = await self.db.fetch_one(
            "SELECT value FROM settings WHERE key = :key",
            {"key": key},
        )
        return row[0] if row else default

    async def set_setting(self, key: str, value: str) -> None:
        await self.db.execute(
            "INSERT INTO settings (key, value) VALUES (:key, :value) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            {"key": key, "value": value},
        )

    async def get_all_settings(self) -> dict[str, str]:
        rows = await self.db.fetch_all("SELECT key, value FROM settings")
        return {row["key"]: row["value"] for row in rows}

    async def add_proxy(self, url: str, proxy_type: str = "http", country: str = "", note: str = "") -> int:
        return await self.db.execute(
            "INSERT INTO proxies (url, proxy_type, country, note) VALUES (:url, :proxy_type, :country, :note)",
            {"url": url, "proxy_type": proxy_type, "country": country, "note": note},
        )

    async def remove_proxy(self, proxy_id: int) -> bool:
        exists = await self.db.fetch_val(
            "SELECT 1 FROM proxies WHERE id = :id",
            {"id": proxy_id},
        )
        if not exists:
            return False
        await self.db.execute(
            "DELETE FROM proxies WHERE id = :id",
            {"id": proxy_id},
        )
        return True

    async def get_all_proxies(self) -> list[dict]:
        rows = await self.db.fetch_all("SELECT * FROM proxies ORDER BY id")
        return [dict(row) for row in rows]

    async def toggle_proxy(self, proxy_id: int) -> bool:
        enabled = await self.db.fetch_val(
            "SELECT enabled FROM proxies WHERE id = :id",
            {"id": proxy_id},
        )
        if enabled is None:
            return False
        new_val = 0 if enabled else 1
        await self.db.execute(
            "UPDATE proxies SET enabled = :enabled WHERE id = :id",
            {"enabled": new_val, "id": proxy_id},
        )
        return True


_db_instance: Optional[Database] = None


def get_db() -> Database:
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
