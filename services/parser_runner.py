"""Раннер парсера с интеграцией уведомлений подписчикам."""

import asyncio
import csv
import logging
import os
import re
import signal
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Type

import yaml

from parsers.base_parser import BaseParser
from parsers.club_parser import ClubParser
from parsers.club_sites import ClubSiteParser
from parsers.yandex_parser import YandexParser
from parsers.khl_parser import KHLParser
from services.database import get_db
from services.notifier import Notifier
from services.email_sender import EmailSender
from services.proxy_rotator import ProxyRotator
from services.team_matcher import extract_teams_from_title

logger = logging.getLogger(__name__)

_ENV_VAR_RE = re.compile(r"\$\{([^}]+)\}")


def _resolve_env_vars(value: Any) -> Any:
    """Заменяет ${VAR} на значение из os.environ."""
    if isinstance(value, str):
        def replacer(m: re.Match) -> str:
            var_name = m.group(1)
            return os.environ.get(var_name, m.group(0))
        return _ENV_VAR_RE.sub(replacer, value)
    if isinstance(value, dict):
        return {k: _resolve_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env_vars(v) for v in value]
    return value


class ParserFactory:
    _registry: dict[str, Type[BaseParser]] = {}

    @classmethod
    def register(cls, name: str, parser_class: Type[BaseParser]) -> None:
        cls._registry[name.lower()] = parser_class

    @classmethod
    def create(cls, name: str, config: dict[str, Any], proxy_rotator=None) -> BaseParser:
        key = name.lower()
        if key not in cls._registry:
            raise KeyError(f"Парсер '{name}' не зарегистрирован. Доступные: {list(cls._registry.keys())}")
        return cls._registry[key](config, proxy_rotator=proxy_rotator)

    @classmethod
    def available(cls) -> list[str]:
        return list(cls._registry.keys())


ParserFactory.register("yandex", YandexParser)
ParserFactory.register("club", ClubParser)
ParserFactory.register("club_site", ClubSiteParser)
ParserFactory.register("khl", KHLParser)


class ConfigLoader:
    def __init__(self, config_path: str):
        self.config_path = config_path

    def load(self) -> dict[str, Any]:
        path = Path(self.config_path)
        if not path.exists():
            raise FileNotFoundError(f"Конфиг не найден: {self.config_path}")
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return _resolve_env_vars(config)


class ParserRunner:
    def __init__(
            self,
            config_path: str = "config/sites.yaml",
            site_filter: Optional[str] = None,
            once: bool = False,
            telegram_bot=None,
    ):
        self.config_path = config_path
        self.site_filter = site_filter
        self.once = once
        self.telegram_bot = telegram_bot
        self._shutdown_event = asyncio.Event()
        self._config: dict[str, Any] = {}
        self._settings: dict[str, Any] = {}
        self._sites: list[dict[str, Any]] = []
        self.notifier: Optional[Notifier] = None
        self.email_sender: Optional[EmailSender] = None
        self.proxy_rotator: Optional[ProxyRotator] = None
        self.db = get_db()

    async def load_config(self) -> None:
        loader = ConfigLoader(self.config_path)
        self._config = loader.load()
        self._settings = self._config.get("settings", {})
        self._sites = self._config.get("sites", [])

        if self.site_filter:
            self._sites = [s for s in self._sites if s["name"].lower() == self.site_filter.lower()]
        self._sites = [s for s in self._sites if s.get("enabled", True)]

        if self.telegram_bot:
            admin_id = self._settings.get("telegram", {}).get("admin_chat_id", 0)
            self.notifier = Notifier(self.telegram_bot.get_bot(), admin_id)
        else:
            self.notifier = Notifier(None, 0)

        email_cfg = self._settings.get("email", {})
        self.email_sender = EmailSender(email_cfg)
        if email_cfg.get("enabled"):
            logger.info(f"Email-уведомления включены: {email_cfg.get('to_email')}")

        logger.info(f"Загружено {len(self._sites)} активных сайтов")

    async def load_proxies_from_db(self) -> None:
        """Загружает прокси из БД и создаёт ProxyRotator."""
        try:
            db_proxies = await self.db.get_all_proxies()
            servers = []
            for p in db_proxies:
                if p.get("enabled"):
                    full_url = f"{p.get('proxy_type', 'http')}://{p['url']}"
                    servers.append({
                        "url": full_url,
                        "type": p.get("proxy_type", "http"),
                        "country": p.get("country", ""),
                        "note": p.get("note", ""),
                    })
            if servers:
                proxy_cfg = self._settings.get("proxy", {})
                config = {
                    "enabled": True,
                    "servers": servers,
                    "rotation_strategy": proxy_cfg.get("strategy", "round_robin"),
                    "health_check_interval_seconds": proxy_cfg.get("health_check_interval", 300),
                    "health_check_timeout_seconds": proxy_cfg.get("health_check_timeout", 10),
                    "max_failures_before_disable": proxy_cfg.get("max_failures", 3),
                    "reanimate_after_seconds": proxy_cfg.get("reanimate_after", 600),
                    "use_direct_as_fallback": proxy_cfg.get("direct_fallback", True),
                }
                self.proxy_rotator = ProxyRotator(config)
                logger.info(f"Загружено {len(servers)} прокси из БД")
            else:
                self.proxy_rotator = None
                logger.debug("Нет активных прокси в БД")
        except Exception as e:
            logger.warning(f"Не удалось загрузить прокси из БД: {e}")
            self.proxy_rotator = None

    def _apply_global_settings(self, site_config: dict) -> dict:
        site_config["_retry_attempts"] = self._settings.get("retry_attempts", 3)
        site_config["_retry_backoff_base"] = self._settings.get("retry_backoff_base", 2)
        site_config["_min_delay"] = self._settings.get("min_delay_seconds", 1.0)
        site_config["_max_delay"] = self._settings.get("max_delay_seconds", 3.0)
        site_config["_headless"] = self._settings.get("headless", True)
        return site_config

    async def _process_site(self, site_config: dict) -> None:
        name = site_config["name"]
        logger.info(f"=== Проверка: {name} ===")

        try:
            enriched_config = self._apply_global_settings(site_config.copy())
            parser = ParserFactory.create(site_config["parser"], enriched_config, self.proxy_rotator)
            events = await parser.run()

            if not events:
                logger.info(f"[{name}] Событий не найдено")
                return

            total_notified = 0

            for event in events:
                teams = extract_teams_from_title(event.get("title", ""))
                teams_str = ", ".join(teams) if teams else "Не определены"

                place = event.get("place", "")
                venue = ""
                city = ""

                if "," in place:
                    parts = place.split(",", 1)
                    city_raw = parts[0].strip()
                    venue = parts[1].strip() if len(parts) > 1 else ""
                    city = self._clean_city_name(city_raw)
                else:
                    venue = place

                logger.debug(f"Место: {place} -> город: '{city}', арена: '{venue}'")

                match_id = f"{event.get('title')}|{event.get('date')}"

                old_match = await self.db.get_match_by_id(match_id)
                old_availability = old_match.get("availability") if old_match else None
                new_availability = event.get("availability")

                match_data = {
                    "match_id": match_id,
                    "title": event.get("title"),
                    "date": event.get("date"),
                    "place": event.get("place"),
                    "venue": venue,
                    "city": city,
                    "teams": teams_str,
                    "price_min": event.get("price_min"),
                    "price_max": event.get("price_max"),
                    "availability": event.get("availability"),
                    "link": event.get("link"),
                    "source": name,
                }
                await self.db.save_match(match_data, source_name=name)

                should_notify = False
                notify_reason = "new"

                if old_match is None:
                    should_notify = True
                    notify_reason = "new"
                    logger.info(f"🆕 Новый матч: {event.get('title')}")
                elif old_availability != new_availability:
                    should_notify = True
                    if old_availability == "Да" and new_availability == "Нет":
                        notify_reason = "sold_out"
                        logger.info(f"❌ Билеты закончились: {event.get('title')}")
                    elif old_availability == "Нет" and new_availability == "Да":
                        notify_reason = "available"
                        logger.info(f"✅ Билеты появились: {event.get('title')}")
                    else:
                        notify_reason = "changed"
                        logger.info(f"🔄 Статус изменился: {old_availability} -> {new_availability}")
                else:
                    logger.debug(f"Без изменений: {event.get('title')}")

                if should_notify:
                    subscriber_ids = await self.db.get_subscribers_for_teams(teams)
                    logger.debug(f"Подписчиков на команды {teams}: {len(subscriber_ids)}")

                    if venue and city:
                        venue_key = f"{city}, {venue}".lower()
                        logger.debug(f"Поиск подписчиков на стадион: '{venue_key}'")

                        venue_subscribers = await self.db.get_subscribers_for_venues([venue_key])
                        logger.debug(f"Найдено подписчиков на стадион: {len(venue_subscribers)}")

                        subscriber_ids = list(set(subscriber_ids + venue_subscribers))

                    if not subscriber_ids:
                        logger.info(
                            f"Нет подписчиков на команды/стадион, "
                            f"пропускаем уведомление (причина: {notify_reason})")

                    if subscriber_ids:
                        sent = await self.notifier.notify_subscribers(
                            event=event,
                            subscriber_chat_ids=subscriber_ids,
                            db=self.db,
                            reason=notify_reason,
                        )
                        total_notified += sent

                    # Email-уведомление админу
                    if self.email_sender:
                        await self.email_sender.notify_admin_about_event(
                            event=event, teams_str=teams_str, reason=notify_reason,
                        )

            logger.info(f"[{name}] Обработано {len(events)} событий, отправлено {total_notified} уведомлений")
            self._save_results_csv(name, events)

        except Exception as e:
            logger.error(f"[{name}] Ошибка: {e}", exc_info=True)
            if self.email_sender:
                await self.email_sender.notify_admin_about_error(name, str(e))

    def _clean_city_name(self, city: str) -> str:
        city = city.strip().lower()
        prefixes = ["г.", "город ", "г ", "г. "]
        for prefix in prefixes:
            if city.startswith(prefix):
                city = city[len(prefix):].strip()
        city = " ".join(city.split())
        return city

    def _save_results_csv(self, site_name: str, events: list[dict]) -> None:
        output_dir = self._settings.get("output_dir", "data")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"all_events_{site_name}.csv")

        try:
            with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
                fieldnames = ["Дата", "Название", "Место", "Цена мин", "Цена макс", "Наличие", "Ссылка"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for event in events:
                    writer.writerow({
                        "Дата": event.get("date", ""),
                        "Название": event.get("title", ""),
                        "Место": event.get("place", ""),
                        "Цена мин": event.get("price_min", ""),
                        "Цена макс": event.get("price_max", ""),
                        "Наличие": event.get("availability", ""),
                        "Ссылка": event.get("link", ""),
                    })
        except Exception as e:
            logger.error(f"Ошибка сохранения CSV: {e}")

    async def run_cycle(self) -> None:
        for site_config in self._sites:
            if self._shutdown_event.is_set():
                break
            try:
                await self._process_site(site_config)
            except Exception as e:
                logger.exception(f"Ошибка в цикле для {site_config.get('name')}: {e}")

    async def run_forever(self) -> None:
        await self.load_config()
        await self.db.init()
        await self.load_proxies_from_db()

        if not self._sites:
            logger.warning("Нет активных сайтов")
            return

        try:
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                try:
                    loop.add_signal_handler(sig, lambda: self._shutdown_event.set())
                except (NotImplementedError, AttributeError):
                    pass
        except RuntimeError:
            pass

        default_interval = self._settings.get("default_interval_minutes", 30)
        cycle_num = 0

        logger.info("=" * 60)
        logger.info("МОНИТОРИНГ ХОККЕЙНЫХ БИЛЕТОВ ЗАПУЩЕН")
        logger.info(f"Сайтов: {len(self._sites)}")
        logger.info(f"Интервал: {default_interval} мин")
        stats = await self.db.get_stats()
        logger.info(f"Пользователей в базе: {stats['users']}")
        logger.info("Для остановки нажмите Ctrl+C")
        logger.info("=" * 60)

        try:
            while not self._shutdown_event.is_set():
                cycle_num += 1
                logger.info(f"\n{'='*30} Цикл #{cycle_num} ({datetime.now().strftime('%H:%M:%S')}) {'='*30}")

                await self.run_cycle()

                if self.once:
                    logger.info("Режим одноразового запуска - завершаем")
                    break

                db_interval = await self.db.get_setting("parse_interval_minutes", str(default_interval))
                try:
                    sleep_minutes = int(db_interval)
                except ValueError:
                    sleep_minutes = default_interval
                sleep_minutes = max(1, min(sleep_minutes, 1440))
                sleep_seconds = sleep_minutes * 60

                trigger = await self.db.get_setting("parse_trigger_requested_at", "")
                if trigger:
                    await self.db.delete_setting("parse_trigger_requested_at")
                    logger.info("Ручной запуск парсинга — пропускаем ожидание")
                    continue

                logger.info(f"Следующая проверка через {sleep_minutes} мин (интервал из БД)...")

                try:
                    await asyncio.wait_for(
                        self._shutdown_event.wait(),
                        timeout=sleep_seconds,
                    )
                except asyncio.TimeoutError:
                    pass
        finally:
            logger.info("Мониторинг корректно остановлен")
