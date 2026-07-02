"""Base abstract parser class with Playwright loading, retries, delays, UA/proxy rotation."""

import abc
import asyncio
import logging
import random
import time
from typing import Any, Optional, TYPE_CHECKING

from fake_useragent import UserAgent
from playwright.async_api import (
    async_playwright, Browser, Page,
    Error as PlaywrightError,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from services.proxy_rotator import ProxyRotator, ProxyServer

class ParseError(Exception):
    """Parsing error (failed to extract data)."""
    pass


class NetworkError(Exception):
    """Network error (timeout, 5xx, etc.)."""
    pass


class ProtectionError(Exception):
    """Page is protected by anti-bot system."""
    pass


class BaseParser(abc.ABC):
    """Abstract base class for all parsers. Subclasses must implement `parse(html) -> list[dict]`."""

    _FALLBACK_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) "
        "Gecko/20100101 Firefox/121.0",
    ]

    def __init__(
        self,
        config: dict[str, Any],
        proxy_rotator: Optional["ProxyRotator"] = None,
    ):
        """
        :param config: Site configuration dict from sites.yaml.
        :param proxy_rotator: Optional proxy rotator.
        """
        self.config = config
        self.name: str = config["name"]
        self.url: str = config["url"]
        self.params: dict[str, Any] = config.get("params", {}) or {}

        self.logger = logging.getLogger(self.__class__.__name__)


        self.retry_attempts: int = config.get("_retry_attempts", 3)
        self.retry_backoff_base: int = config.get("_retry_backoff_base", 2)
        self.min_delay: float = config.get("_min_delay", 1.0)
        self.max_delay: float = config.get("_max_delay", 3.0)
        self.headless: bool = config.get("_headless", True)


        self.proxy_rotator = proxy_rotator
        self.proxy_country: Optional[str] = config.get("proxy_country")
        self.proxy_disabled: bool = bool(config.get("proxy_disabled", False))


        self._ua_fallback_index = 0
        try:
            self._ua = UserAgent(fallback=self._FALLBACK_USER_AGENTS[0])
        except Exception:
            self._ua = None

        self._fixed_ua: Optional[str] = config.get("user_agent")

    def _get_user_agent(self) -> str:
        """Return User-Agent: fixed or random."""
        if self._fixed_ua:
            return self._fixed_ua
        if self._ua is not None:
            try:
                return self._ua.random
            except Exception:
                pass
        ua = self._FALLBACK_USER_AGENTS[self._ua_fallback_index]
        self._ua_fallback_index = (
            (self._ua_fallback_index + 1) % len(self._FALLBACK_USER_AGENTS)
        )
        return ua

    async def _random_delay(self) -> None:
        """Wait a random delay between requests."""
        delay = random.uniform(self.min_delay, self.max_delay)
        self.logger.debug(f"Задержка {delay:.2f} с перед запросом")
        await asyncio.sleep(delay)

    async def _get_proxy(self) -> Optional["ProxyServer"]:
        """Get the next proxy from the rotator, or None if disabled/unavailable."""
        if self.proxy_disabled or self.proxy_rotator is None:
            return None
        if not self.proxy_rotator.enabled:
            return None
        return await self.proxy_rotator.get_next(country=self.proxy_country)

    async def fetch(self) -> str:
        """Load page HTML via Playwright with retries, exponential backoff, and proxy rotation."""
        last_error: Optional[Exception] = None
        used_proxies: list["ProxyServer"] = []
        direct_attempt_done = False

        for attempt in range(1, self.retry_attempts + 1):
            try:
                proxy = await self._get_proxy()
                if proxy is not None and proxy in used_proxies:
                    for _ in range(len(self.proxy_rotator or [])):
                        alt = await self._get_proxy()
                        if alt is not None and alt not in used_proxies:
                            proxy = alt
                            break

                user_agent = self._get_user_agent()
                timeout_ms = int(self.params.get("timeout_ms", 30000))
                wait_selector = self.params.get("wait_selector")

                proxy_desc = (
                    f"{proxy.host}:{proxy.port}" if proxy else "direct"
                )
                self.logger.info(
                    f"[{self.name}] Попытка {attempt}/{self.retry_attempts}: "
                    f"загрузка {self.url} через {proxy_desc}"
                )

                await self._random_delay()
                start_time = time.time()

                html = await self._fetch_with_playwright(
                    user_agent=user_agent,
                    timeout_ms=timeout_ms,
                    wait_selector=wait_selector,
                    proxy=proxy,
                )

                elapsed_ms = (time.time() - start_time) * 1000

                if not html or len(html.strip()) < 100:
                    raise NetworkError(
                        f"Получена пустая/слишком короткая страница "
                        f"({len(html or '')} символов)"
                    )

                if proxy is not None and self.proxy_rotator is not None:
                    await self.proxy_rotator.record_success(proxy, elapsed_ms)

                self.logger.debug(
                    f"[{self.name}] Страница загружена через {proxy_desc}, "
                    f"{len(html)} символов, {elapsed_ms:.0f} мс"
                )
                return html

            except PlaywrightError as e:
                last_error = e
                self.logger.warning(
                    f"[{self.name}] Playwright ошибка "
                    f"(попытка {attempt}, прокси {proxy_desc}): {e}"
                )
                if proxy is not None and self.proxy_rotator is not None:
                    await self.proxy_rotator.record_failure(proxy)
                    if proxy not in used_proxies:
                        used_proxies.append(proxy)

            except NetworkError as e:
                last_error = e
                self.logger.warning(
                    f"[{self.name}] Сетевая ошибка "
                    f"(попытка {attempt}, прокси {proxy_desc}): {e}"
                )
                if proxy is not None and self.proxy_rotator is not None:
                    await self.proxy_rotator.record_failure(proxy)
                    if proxy not in used_proxies:
                        used_proxies.append(proxy)

            except Exception as e:
                last_error = e
                self.logger.error(
                    f"[{self.name}] Неожиданная ошибка "
                    f"(попытка {attempt}): {e}"
                )

            use_direct_fallback = (
                self.proxy_rotator is not None
                and self.proxy_rotator.use_direct_fallback
                and not self.proxy_disabled
                and not direct_attempt_done
            )
            if use_direct_fallback and proxy is not None:
                self.logger.info(
                    f"[{self.name}] Все прокси исчерпаны, "
                    f"пробую прямое соединение"
                )
                direct_attempt_done = True
                try:
                    user_agent = self._get_user_agent()
                    timeout_ms = int(self.params.get("timeout_ms", 30000))
                    wait_selector = self.params.get("wait_selector")

                    html = await self._fetch_with_playwright(
                        user_agent=user_agent,
                        timeout_ms=timeout_ms,
                        wait_selector=wait_selector,
                        proxy=None,
                    )
                    if html and len(html.strip()) >= 100:
                        self.logger.info(
                            f"[{self.name}] Прямое соединение успешно"
                        )
                        return html
                except Exception as e:
                    self.logger.warning(
                        f"[{self.name}] Прямое соединение тоже упало: {e}"
                    )
                    last_error = e

            if attempt < self.retry_attempts:
                backoff = self.retry_backoff_base ** attempt
                self.logger.info(
                    f"[{self.name}] Повтор через {backoff} с..."
                )
                await asyncio.sleep(backoff)

        raise NetworkError(
            f"[{self.name}] Не удалось загрузить страницу после "
            f"{self.retry_attempts} попыток: {last_error}"
        )

    async def _fetch_with_playwright(
        self,
        user_agent: str,
        timeout_ms: int,
        wait_selector: Optional[str],
        proxy: Optional["ProxyServer"] = None,
    ) -> str:
        """Internal method: run Playwright with the given proxy."""
        browser: Optional[Browser] = None
        pw = None
        try:
            pw = await async_playwright().start()

            launch_kwargs: dict[str, Any] = {"headless": self.headless}
            context_kwargs: dict[str, Any] = {
                "user_agent": user_agent,
                "viewport": {"width": 1920, "height": 1080},
                "locale": "ru-RU",
            }

            if proxy is not None:
                if proxy.proxy_type.value == "socks5":
                    context_kwargs["proxy"] = proxy.get_playwright_proxy()
                else:
                    launch_kwargs["proxy"] = proxy.get_playwright_proxy()

            browser = await pw.chromium.launch(**launch_kwargs)
            context = await browser.new_context(**context_kwargs)
            page: Page = await context.new_page()

            response = await page.goto(
                self.url,
                wait_until="domcontentloaded",
                timeout=timeout_ms,
            )

            if response is not None and response.status >= 500:
                raise NetworkError(
                    f"Сервер вернул HTTP {response.status}"
                )

            if wait_selector:
                try:
                    selectors = [s.strip() for s in wait_selector.split(",")]
                    waited = False
                    for selector in selectors:
                        try:
                            await page.wait_for_selector(
                                selector, timeout=timeout_ms
                            )
                            self.logger.debug(
                                f"Дожд Selector '{selector}' появился"
                            )
                            waited = True
                            break
                        except PlaywrightError:
                            continue
                    if not waited:
                        self.logger.warning(
                            f"Ни один из селекторов не появился: "
                            f"{wait_selector}"
                        )
                except Exception as e:
                    self.logger.warning(f"Ошибка ожидания селектора: {e}")

            await asyncio.sleep(1.0)

            html = await page.content()
            return html

        finally:
            if browser is not None:
                try:
                    await browser.close()
                except Exception:
                    pass
            if pw is not None:
                try:
                    await pw.stop()
                except Exception:
                    pass

    @abc.abstractmethod
    async def parse(self, html: str) -> list[dict]:
        """Abstract HTML parsing method. Subclasses must implement data extraction."""
        ...

    async def run(self, db: Optional["Session"] = None) -> list[dict]:
        """Main method: load page and parse it."""
        self.logger.info(f"[{self.name}] Запуск парсинга {self.url}")
        try:
            html = await self.fetch()
            events = await self.parse(html)
            self.logger.info(
                f"[{self.name}] Успешно получено {len(events)} событий"
            )
            if db is not None:
                from Backend import models

                new_events = []
                for event in events:
                    existing = db.query(models.MatchModel).filter(
                        models.MatchModel.title == event.get('title'),
                        models.MatchModel.date == event.get('date')
                    ).first()
                    if not existing:
                        new_events.append(event)
                for event in new_events:
                    self.logger.info(f"Новый матч: {event.get('title')}")
                    await self._send_email_notifications(event, db)
            return events
        except ProtectionError as e:
            self.logger.error(f"[{self.name}] Антибот-защита: {e}")
            raise
        except ParseError as e:
            self.logger.error(f"[{self.name}] Ошибка парсинга: {e}")
            raise
        except NetworkError as e:
            self.logger.error(f"[{self.name}] Ошибка сети: {e}")
            raise
        except Exception as e:
            self.logger.exception(
                f"[{self.name}] Неизвестная ошибка при запуске: {e}"
            )
            raise

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} name={self.name!r} "
            f"url={self.url!r}>"
        )
    
    async def _send_email_notifications(self, match_data: dict, db: "Session") -> None:
        from Backend import models

        try:
            team_names = self._extract_team_names(match_data)
            if not team_names:
                self.logger.warning(f"Не удалось извлечь названия команд из матча: {match_data.get('title')}")
                return
            
            self.logger.info(f"Поиск подписчиков для команд: {team_names}")
            
            subscribers = db.query(models.SubscriptionModel).filter(
                models.SubscriptionModel.type == "team",
                models.SubscriptionModel.value.in_([name.lower() for name in team_names])
            ).all()
            
            if not subscribers:
                self.logger.info(f"Нет подписчиков для команд {team_names}")
                return
            
            user_ids = list(set([sub.chat_id for sub in subscribers]))
            
            users = db.query(models.UserModel).filter(
                models.UserModel.chat_id.in_(user_ids),
                models.UserModel.is_active == 1
            ).all()
            
            self.logger.info(f"Найдено {len(users)} активных подписчиков")
            
            email_sent = 0
            for user in users:
                try:
                    await self._send_match_notification_email(user, match_data)
                    email_sent += 1
                except Exception as e:
                    self.logger.error(f"Ошибка отправки письма пользователю {user.email}: {e}")
                    continue
            
            self.logger.info(f"Успешно отправлено {email_sent} уведомлений")
            
        except Exception as e:
            self.logger.error(f"Ошибка при отправке уведомлений: {e}")
    
    def _extract_team_names(self, match_data: dict) -> list[str]:
        from services.team_matcher import extract_teams_from_title
        return extract_teams_from_title(match_data.get('title', ''))
    
    async def _send_match_notification_email(self, user, match_data: dict) -> None:
        import os
        from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

        conf_email = ConnectionConfig(
            MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "hqbo bhdk cxfg gabq"),
            MAIL_USERNAME = os.getenv("MAIL_USERNAME", "sakirovsamir401@gmail.com"),
            MAIL_FROM = os.getenv("MAIL_USERNAME", "sakirovsamir401@gmail.com"),
            MAIL_PORT = int(os.getenv("MAIL_PORT", "587")),
            MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com"),
            MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "True") == "True",
            MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", "False") == "True",
        )

        try:
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; }}
                    .match {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .price {{ color: #28a745; font-weight: bold; }}
                    .button {{ display: inline-block; background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                    .footer {{ margin-top: 20px; color: #6c757d; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>🏒 Новый матч по хоккею!</h2>
                </div>
                <div class="content">
                    <div class="match">
                        <h3>📋 {match_data.get('title', 'Матч')}</h3>
                        <p>📅 <strong>Дата:</strong> {match_data.get('date', 'Дата не указана')}</p>
                        <p>📍 <strong>Место:</strong> {match_data.get('place', 'Место не указано')}</p>
                        <p>💰 <strong>Цена:</strong> <span class="price">{match_data.get('price_min', 'Не указана')}</span>
                        {f" - <span class='price'>{match_data.get('price_max', '')}</span>" if match_data.get('price_max') and match_data.get('price_max') != match_data.get('price_min') else ''}</p>
                        <p>🎟️ <strong>Доступность:</strong> {match_data.get('availability', 'Уточняется')}</p>
                        <p>🔗 <strong>Источник:</strong> {self.name}</p>
                    </div>
                    <div class="footer">
                        <p>Вы получили это письмо, потому что подписаны на обновления о матчах.</p>
                        <p>Для отписки перейдите в настройки профиля.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = MessageSchema(
                subject=f"🏒 Новый матч: {match_data.get('title', 'Хоккей')}",
                recipients=[user.email],
                body=html_body,
                subtype=MessageType.html
            )
            
            fm = FastMail(conf_email)
            await fm.send_message(message)
            
            self.logger.debug(f"Письмо отправлено на {user.email}")
            
        except Exception as e:
            self.logger.error(f"Ошибка отправки письма на {user.email}: {e}")
            raise