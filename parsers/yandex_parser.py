import re
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse
import asyncio

from bs4 import BeautifulSoup
from .base_parser import BaseParser


class YandexParser(BaseParser):
    """Two-stage parser: catalog -> individual event pages."""

    EVENT_URL_PATTERNS = [
        r'/moscow/sport/hockey-[\w-]+',
        r'/moscow/sport/[\w-]+-hockey',
        r'/event/[\w-]+',
        r'/spb/sport/hockey-[\w-]+',
    ]

    BLACKLIST_URL_PATTERNS = [
        r'/places/',
        r'/pushkin-card',
        r'/discount-event',
        r'/abonement',
        r'/afisha/$',
        r'/moscow/sport/hockey/?$',
        r'\?source=',
        r'/support/',
        r'/legal/',
    ]

    BLACKLIST_DOMAINS = [
        'apps.apple.com', 'play.google.com', 'radar.yandex.ru',
        'vk.com', 't.me', 'telegram.org', 'youtube.com', 'ok.ru',
        'mail.ru', 'google.com'
    ]

    async def parse(self, html: str) -> list[dict]:
        """Main method: find event links and parse each individually."""
        soup = BeautifulSoup(html, "html.parser")
        keywords = self.params.get("keywords", ["хоккей"])
        if isinstance(keywords, str):
            keywords = [keywords]

        self.logger.info(f"[{self.name}] Шаг 1: Поиск ссылок на события в каталоге")

        event_urls = self._find_event_urls(soup)
        self.logger.info(f"[{self.name}] Найдено {len(event_urls)} потенциальных событий")

        if not event_urls:
            return []

        self.logger.info(f"[{self.name}] Шаг 2: Загрузка страниц событий")
        events = []

        for i, url in enumerate(event_urls, 1):
            self.logger.info(f"[{self.name}] Парсинг события {i}/{len(event_urls)}: {url}")

            try:
                event_html = await self._fetch_event_page(url)
                if not event_html:
                    continue

                event_data = self._parse_event_page(event_html, url)
                if event_data:
                    events.append(event_data)
                    self.logger.info(f"  ✅ Извлечено: {event_data.get('title')}")
                else:
                    self.logger.warning("  ❌ Не удалось извлечь данные")

                await asyncio.sleep(1)

            except Exception as e:
                self.logger.error(f"  ❌ Ошибка при парсинге {url}: {e}")
                continue

        self.logger.info(f"[{self.name}] Успешно извлечено {len(events)} событий")
        return events

    def _find_event_urls(self, soup: BeautifulSoup) -> list[str]:
        """Find event URLs, filtering out junk."""
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

            valid_urls.add(href)

        return list(valid_urls)

    def _is_internal_link(self, href: str) -> bool:
        """Check if link is internal."""
        if href.startswith("/"):
            return True

        try:
            parsed = urlparse(href)
            domain = parsed.netloc.lower()

            for blacklisted in self.BLACKLIST_DOMAINS:
                if blacklisted in domain:
                    return False

            return "afisha.yandex.ru" in domain
        except Exception:
            return False

    def _matches_event_pattern(self, url: str) -> bool:
        """Check URL against event path patterns."""
        path = urlparse(url).path
        for pattern in self.EVENT_URL_PATTERNS:
            if re.search(pattern, path, re.IGNORECASE):
                return True
        return False

    def _matches_blacklist_pattern(self, url: str) -> bool:
        """Check URL against blacklist path patterns."""
        path = urlparse(url).path + urlparse(url).query
        for pattern in self.BLACKLIST_URL_PATTERNS:
            if re.search(pattern, path, re.IGNORECASE):
                return True
        return False

    async def _fetch_event_page(self, url: str) -> Optional[str]:
        """Load individual event page via Playwright."""
        try:
            old_url = self.url
            self.url = url
            html = await self.fetch()
            self.url = old_url
            return html
        except Exception as e:
            self.logger.error(f"Не удалось загрузить {url}: {e}")
            return None

    def _parse_event_page(self, html: str, url: str) -> Optional[dict]:
        """Extract data from event page."""
        soup = BeautifulSoup(html, "html.parser")

        event_data = self._extract_from_json_ld(soup)

        if not event_data:
            event_data = self._extract_from_html(soup)

        if not event_data:
            return None

        event_data.setdefault("source", self.name)
        event_data.setdefault("link", url)
        event_data.setdefault("parsed_at", datetime.utcnow().isoformat())

        return event_data

    def _extract_from_json_ld(self, soup: BeautifulSoup) -> Optional[dict]:
        """Extract data from JSON-LD (schema.org Event)."""
        scripts = soup.find_all("script", type="application/ld+json")

        for script in scripts:
            try:
                import json
                data = json.loads(script.string)

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
        """Parse schema.org Event data."""
        try:
            title = schema.get("name", "")
            if not title:
                return None

            date_str = schema.get("startDate", "")
            date = self._format_schema_date(date_str)

            location = schema.get("location", {})
            place = ""
            if isinstance(location, dict):
                place = location.get("name", "")
                address = location.get("address", {})
                if isinstance(address, dict):
                    place = f"{place}, {address.get('addressLocality', '')}"

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
        """Format date from ISO format."""
        if not date_str:
            return "Дата не указана"

        try:
            # 2026-06-15T19:30:00+03:00
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%d %B %Y, %H:%M")
        except Exception:
            return date_str

    def _extract_from_html(self, soup: BeautifulSoup) -> Optional[dict]:
        """Extract data from HTML tags."""
        title = ""
        for tag in ["h1", "h2"]:
            header = soup.find(tag)
            if header:
                title = header.get_text(strip=True)
                if title and len(title) >= 5:
                    break

        if not title:
            return None

        date = "Дата не указана"
        time_tag = soup.find("time")
        if time_tag:
            date = time_tag.get("datetime", "") or time_tag.get_text(strip=True)
            date = self._format_schema_date(date)

        place = "Место не указано"
        address_tag = soup.find("address")
        if address_tag:
            place = address_tag.get_text(strip=True)

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
        """Extract prices from HTML."""
        price_regex = re.compile(r'(\d[\d\s]{2,})\s*(?:₽|р\.|руб)', re.IGNORECASE)

        text = soup.get_text(separator=" ", strip=True)
        matches = price_regex.findall(text)

        if not matches:
            return "Не указана", "Не указана", "Уточняется"

        prices = []
        for match in matches:
            price_str = match.replace(" ", "")
            try:
                price = int(price_str)
                if price > 100:
                    prices.append(price)
            except ValueError:
                continue

        if not prices:
            return "Не указана", "Не указана", "Уточняется"

        availability = "Да"
        if "распродано" in text.lower() or "нет билетов" in text.lower():
            availability = "Нет"

        return f"{min(prices)} ₽", f"{max(prices)} ₽", availability

    def _clean_title(self, title: str) -> str:
        """Clean title."""
        title = re.sub(r'от\s*\d+[\d\s]*\s*₽', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\d+[\d\s]*\s*₽', '', title)

        title = re.sub(r'^(билеты|афиша)\s*', '', title, flags=re.IGNORECASE)

        title = re.sub(r'\s+', ' ', title).strip()

        return title