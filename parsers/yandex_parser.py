import asyncio
import re
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser
from playwright_stealth import Stealth

from .base_parser import BaseParser, NetworkError


class YandexParser(BaseParser):
    """Двухступенчатый парсер: каталог -> страница каждого события."""

    # Города для поиска хоккейных событий
    CITIES = [
        "moscow", "saint-petersburg", "kazan", "omsk", "ufa",
        "nizhny-novgorod", "chelyabinsk", "yaroslavl", "cherepovets",
        "magnitogorsk", "nizhnekamsk", "astana", "novosibirsk",
        "krasnoyarsk", "khabarovsk", "vladivostok",
    ]

    # Паттерны URL для РЕАЛЬНЫХ событий (whitelist) — ловим ВСЕ sport-события,
    # фильтрация по ключевым словам идёт отдельно (по тексту ссылки).
    EVENT_URL_PATTERNS = [
        r'/[^/]+/sport/[^/]+',   # любой город + любое событие в sport
        r'/event/[\w-]+',         # прямые ссылки на события
    ]

    # Паттерны URL, которые нужно ИСКЛЮЧИТЬ (blacklist)
    BLACKLIST_URL_PATTERNS = [
        r'/places/',
        r'/pushkin-card',
        r'/discount-event',
        r'/abonement',
        r'/afisha/?$',
        r'/[^/]+/sport/?$',       # сами каталоги городов
        r'\?source=',
        r'/support/',
        r'/legal/',
    ]

    # Максимум страниц пагинации в каталоге города
    MAX_PAGINATION_PAGES = 10

    # Черный список доменов
    BLACKLIST_DOMAINS = [
        'apps.apple.com', 'play.google.com', 'radar.yandex.ru',
        'vk.com', 't.me', 'telegram.org', 'youtube.com', 'ok.ru',
        'mail.ru', 'google.com'
    ]

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Нормализует URL для дедупликации: убирает ?city=..."""
        parsed = urlparse(url)
        # Убираем только ?city параметр, остальное сохраняем
        qs = parsed.query
        if qs:
            params = [p for p in qs.split("&") if not p.startswith("city=")]
            qs = "&".join(params)
        path = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if qs:
            path += f"?{qs}"
        return path

    async def _run(self) -> list[dict]:
        """Собирает ссылки на хоккейные события со всех городов (с пагинацией), парсит каждое."""
        cities = self.params.get("cities", self.CITIES)
        keywords = self.params.get("keywords", ["хоккей"])
        if isinstance(keywords, str):
            keywords = [keywords]

        all_links = set()
        seen = set()

        def _add_url(url: str) -> None:
            norm = self._normalize_url(url)
            if norm not in seen:
                seen.add(norm)
                all_links.add(url)

        # Шаг 1: Собираем ссылки из /sport всех городов (с пагинацией)
        for i, city in enumerate(cities):
            page_num = 1
            while page_num <= self.MAX_PAGINATION_PAGES:
                city_url = f"https://afisha.yandex.ru/{city}/sport?source=menu"
                if page_num > 1:
                    city_url += f"&page={page_num}"
                try:
                    html = await self._fetch_city_page(city_url, city)
                    if not html:
                        break
                    soup = BeautifulSoup(html, "html.parser")
                    found = self._find_event_urls(soup, keywords=keywords)
                    for url in found:
                        _add_url(url)
                    self.logger.info(f"[{self.name}] {city} стр.{page_num}: {len(found)}")

                    if not self._find_next_page_url(soup):
                        break
                    page_num += 1
                    await asyncio.sleep(0.5)
                except Exception as e:
                    self.logger.debug(f"[{self.name}] {city} стр.{page_num}: {e}")
                    break

            if i < len(cities) - 1:
                await asyncio.sleep(0.5)

        self.logger.info(f"[{self.name}] Всего уникальных событий: {len(all_links)}")
        if not all_links:
            return []

        # Шаг 2: Парсим каждое событие
        events = []
        for i, url in enumerate(all_links, 1):
            self.logger.info(f"[{self.name}] Событие {i}/{len(all_links)}: {url}")
            try:
                event_html = await self._fetch_event_page(url)
                if not event_html:
                    continue
                event_data = self._parse_event_page(event_html, url)
                if event_data:
                    events.append(event_data)
                    self.logger.info(f"  ✅ {event_data.get('title')}")
                else:
                    self.logger.warning("  ❌ Не удалось извлечь данные")
            except Exception as e:
                self.logger.error(f"  ❌ {e}")

            if i < len(all_links):
                await asyncio.sleep(1)

        self.logger.info(f"[{self.name}] Успешно извлечено {len(events)} событий")
        return events

    async def _fetch_city_page(self, url: str, city: str) -> Optional[str]:
        """Загружает страницу города, возвращает None при ошибке."""
        try:
            return await self.fetch(url=url)
        except Exception:
            return None

    async def _fetch_with_playwright(self, user_agent, timeout_ms, wait_selector,
                                      proxy=None, url=None):
        """Загрузка страницы через Playwright с применением stealth."""
        target_url = url or self.url
        browser: Browser | None = None
        pw = None
        try:
            pw = await async_playwright().start()
            launch_kwargs = {"headless": self.headless}
            context_kwargs = {
                "user_agent": user_agent,
                "viewport": {"width": 1920, "height": 1080},
                "locale": "ru-RU",
            }
            if proxy is not None:
                context_kwargs["proxy"] = proxy.get_playwright_proxy()

            browser = await pw.chromium.launch(**launch_kwargs)
            context = await browser.new_context(**context_kwargs)
            page = await context.new_page()

            await Stealth().apply_stealth_async(page)

            response = await page.goto(
                target_url,
                wait_until="domcontentloaded",
                timeout=timeout_ms,
            )

            if response is not None and response.status >= 500:
                raise NetworkError(f"Сервер вернул HTTP {response.status}")

            await page.wait_for_timeout(3000)

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

    async def parse(self, html: str) -> list[dict]:
        """Основной метод: находит ссылки на события и парсит каждое отдельно."""
        soup = BeautifulSoup(html, "html.parser")
        keywords = self.params.get("keywords", ["хоккей"])
        if isinstance(keywords, str):
            keywords = [keywords]

        self.logger.info(f"[{self.name}] Шаг 1: Поиск ссылок на события в каталоге")

        # ШАГ 1: Найти ссылки на события
        event_urls = self._find_event_urls(soup)
        self.logger.info(f"[{self.name}] Найдено {len(event_urls)} потенциальных событий")

        if not event_urls:
            return []

        # ШАГ 2: Загрузить и распарсить каждое событие отдельно
        self.logger.info(f"[{self.name}] Шаг 2: Загрузка страниц событий")
        events = []

        for i, url in enumerate(event_urls, 1):
            self.logger.info(f"[{self.name}] Парсинг события {i}/{len(event_urls)}: {url}")

            try:
                # Загружаем страницу события через Playwright
                event_html = await self._fetch_event_page(url)
                if not event_html:
                    continue

                # Парсим данные со страницы события
                event_data = self._parse_event_page(event_html, url)
                if event_data:
                    events.append(event_data)
                    self.logger.info(f"  ✅ Извлечено: {event_data.get('title')}")
                else:
                    self.logger.warning("  ❌ Не удалось извлечь данные")

                # Задержка между запросами
                await asyncio.sleep(1)

            except Exception as e:
                self.logger.error(f"  ❌ Ошибка при парсинге {url}: {e}")
                continue

        self.logger.info(f"[{self.name}] Успешно извлечено {len(events)} событий")
        return events

    def _find_event_urls(self, soup: BeautifulSoup, keywords: Optional[list[str]] = None) -> list[str]:
        """Находит ссылки на реальные события, фильтруя мусор.

        Если передан keywords — дополнительно отсеивает ссылки,
        у которых ни текст, ни URL не содержат ни одного ключевого слова.
        """
        all_links = soup.find_all("a", href=True)
        valid_urls = set()

        for link in all_links:
            href = link["href"]

            if not self._is_internal_link(href):
                continue

            if href.startswith("/"):
                href = "https://afisha.yandex.ru" + href

            if not self._matches_event_pattern(href):
                continue

            if self._matches_blacklist_pattern(href):
                continue

            # Фильтрация по ключевым словам (текст ссылки + URL)
            if keywords:
                link_text = link.get_text(strip=True)
                if not self._matches_any_keyword(link_text, keywords) and \
                   not self._matches_any_keyword(href, keywords):
                    continue

            valid_urls.add(href)

        return list(valid_urls)

    @staticmethod
    def _matches_any_keyword(text: str, keywords: list[str]) -> bool:
        """Проверяет, содержит ли text хотя бы одно ключевое слово (со stem-матчингом для русских окончаний)."""
        text_lower = text.lower()
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in text_lower:
                return True
            stem = kw_lower[:5]
            if len(stem) >= 4 and stem in text_lower:
                return True
        return False

    def _find_next_page_url(self, soup: BeautifulSoup) -> Optional[str]:
        """Ищет ссылку на следующую страницу каталога."""
        next_link = soup.find("a", attrs={"rel": "next"})
        if next_link and next_link.get("href"):
            href = next_link["href"]
            return href if not href.startswith("/") else "https://afisha.yandex.ru" + href

        for text in ("дальше", "следующая", "вперед"):
            for link in soup.find_all("a", href=True):
                link_text = link.get_text(strip=True).lower()
                if text in link_text:
                    href = link["href"]
                    return href if not href.startswith("/") else "https://afisha.yandex.ru" + href

        return None

    def _is_internal_link(self, href: str) -> bool:
        """Проверяет, что ссылка внутренняя."""
        if href.startswith("/"):
            return True

        try:
            parsed = urlparse(href)
            domain = parsed.netloc.lower()

            # Черный список доменов
            for blacklisted in self.BLACKLIST_DOMAINS:
                if blacklisted in domain:
                    return False

            # Разрешены только ссылки на afisha.yandex.ru
            return "afisha.yandex.ru" in domain
        except Exception:
            return False

    def _matches_event_pattern(self, url: str) -> bool:
        """Проверяет, что URL соответствует паттерну события."""
        path = urlparse(url).path
        for pattern in self.EVENT_URL_PATTERNS:
            if re.search(pattern, path, re.IGNORECASE):
                return True
        return False

    def _matches_blacklist_pattern(self, url: str) -> bool:
        """Проверяет, что URL соответствует blacklist паттерну."""
        path = urlparse(url).path + urlparse(url).query
        for pattern in self.BLACKLIST_URL_PATTERNS:
            if re.search(pattern, path, re.IGNORECASE):
                return True
        return False

    async def _fetch_event_page(self, url: str) -> Optional[str]:
        """Загружает страницу отдельного события через Playwright."""
        old_url = self.url
        self.url = url
        try:
            html = await self.fetch()
            return html
        except Exception as e:
            self.logger.error(f"Не удалось загрузить {url}: {e}")
            return None
        finally:
            self.url = old_url

    def _parse_event_page(self, html: str, url: str) -> Optional[dict]:
        """Извлекает данные со страницы события."""
        soup = BeautifulSoup(html, "html.parser")

        # Попытка 1: Извлечь из JSON-LD (schema.org)
        event_data = self._extract_from_json_ld(soup)

        # Попытка 2: Извлечь из HTML-тегов
        if not event_data:
            event_data = self._extract_from_html(soup)

        if not event_data:
            return None

        # Добавляем недостающие поля
        event_data.setdefault("source", self.name)
        event_data.setdefault("link", url)
        event_data.setdefault("parsed_at", datetime.now(timezone.utc).isoformat())

        return event_data

    def _extract_from_json_ld(self, soup: BeautifulSoup) -> Optional[dict]:
        """Извлекает данные из JSON-LD (schema.org Event)."""
        scripts = soup.find_all("script", type="application/ld+json")

        for script in scripts:
            try:
                import json
                data = json.loads(script.string)

                # Может быть список или одиночный объект
                if isinstance(data, list):
                    for item in data:
                        if item.get("@type") == "Event":
                            return self._parse_schema_event(item)
                elif data.get("@type") == "Event":
                    return self._parse_schema_event(data)
            except Exception:
                continue

        return None

    def _parse_schema_event(self, schema: dict) -> Optional[dict]:
        """Парсит событие из schema.org Event."""
        try:
            title = schema.get("name", "")
            if not title:
                return None

            # Дата
            date_str = schema.get("startDate", "")
            date = self._format_schema_date(date_str)

            # Место
            location = schema.get("location", {})
            place = ""
            if isinstance(location, dict):
                place = location.get("name", "")
                address = location.get("address", {})
                if isinstance(address, dict):
                    place = f"{place}, {address.get('addressLocality', '')}"

            # Цены
            offers = schema.get("offers", [])
            if isinstance(offers, dict):
                offers = [offers]

            prices = []
            for offer in offers:
                price = offer.get("price")
                if price:
                    try:
                        prices.append(float(price))
                    except ValueError:
                        continue

            price_min = f"{int(min(prices))} ₽" if prices else "Не указана"
            price_max = f"{int(max(prices))} ₽" if prices else "Не указана"

            # Наличие
            availability = "Да"
            if not prices:
                availability = "Уточняется"
            elif any(offer.get("availability", "").endswith("OutOfStock") for offer in offers):
                availability = "Нет"

            return {
                "title": title,
                "date": date,
                "place": place,
                "price_min": price_min,
                "price_max": price_max,
                "availability": availability,
            }
        except Exception as e:
            self.logger.debug(f"Ошибка парсинга JSON-LD: {e}")
            return None

    def _format_schema_date(self, date_str: str) -> str:
        """Форматирует дату из ISO формата."""
        if not date_str:
            return "Дата не указана"

        try:
            # 2026-06-15T19:30:00+03:00
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%d %B %Y, %H:%M")
        except Exception:
            return date_str

    def _extract_from_html(self, soup: BeautifulSoup) -> Optional[dict]:
        """Извлекает данные из HTML-тегов."""
        # Название
        title = ""
        for tag in ["h1", "h2"]:
            header = soup.find(tag)
            if header:
                title = header.get_text(strip=True)
                if title and len(title) >= 5:
                    break

        if not title:
            return None

        # Дата
        date = "Дата не указана"
        time_tag = soup.find("time")
        if time_tag:
            date = time_tag.get("datetime", "") or time_tag.get_text(strip=True)
            date = self._format_schema_date(date)

        # Место
        place = "Место не указано"
        address_tag = soup.find("address")
        if address_tag:
            place = address_tag.get_text(strip=True)

        # Цены
        price_min, price_max, availability = self._extract_prices_from_html(soup)

        return {
            "title": self._clean_title(title),
            "date": date,
            "place": place,
            "price_min": price_min,
            "price_max": price_max,
            "availability": availability,
        }

    def _extract_prices_from_html(self, soup: BeautifulSoup) -> tuple[str, str, str]:
        """Извлекает цены из HTML."""
        price_regex = re.compile(r'(\d[\d\s]{2,})\s*(?:₽|р\.|руб)', re.IGNORECASE)

        # Ищем все цены на странице
        text = soup.get_text(separator=" ", strip=True)
        matches = price_regex.findall(text)

        if not matches:
            return "Не указана", "Не указана", "Уточняется"

        prices = []
        for match in matches:
            price_str = match.replace(" ", "")
            try:
                price = int(price_str)
                if price > 100:  # Игнорируем слишком маленькие числа
                    prices.append(price)
            except ValueError:
                continue

        if not prices:
            return "Не указана", "Не указана", "Уточняется"

        # Проверяем наличие
        availability = "Да"
        if "распродано" in text.lower() or "нет билетов" in text.lower():
            availability = "Нет"

        return f"{min(prices)} ₽", f"{max(prices)} ₽", availability

    def _clean_title(self, title: str) -> str:
        """Очищает название."""
        # Убираем прилипшие цены
        title = re.sub(r'от\s*\d+[\d\s]*\s*₽', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\d+[\d\s]*\s*₽', '', title)

        # Убираем "Билеты", "Афиша"
        title = re.sub(r'^(билеты|афиша)\s*', '', title, flags=re.IGNORECASE)

        # Убираем множественные пробелы
        title = re.sub(r'\s+', ' ', title).strip()

        return title