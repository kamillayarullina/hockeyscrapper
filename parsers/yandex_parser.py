import re
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse
import asyncio

from bs4 import BeautifulSoup
from .base_parser import BaseParser


class YandexParser(BaseParser):
    """Двухступенчатый парсер: каталог -> страница каждого события."""

    # Паттерны URL для РЕАЛЬНЫХ событий (whitelist)
    EVENT_URL_PATTERNS = [
        r'/moscow/sport/hockey-[\w-]+',  # /moscow/sport/hockey-match-name
        r'/moscow/sport/[\w-]+-hockey',  # /moscow/sport/cska-hockey
        r'/event/[\w-]+',  # /event/event-id
        r'/spb/sport/hockey-[\w-]+',  # /spb/sport/hockey-match-name
    ]

    # Паттерны URL, которые нужно ИСКЛЮЧИТЬ (blacklist)
    BLACKLIST_URL_PATTERNS = [
        r'/places/',  # страницы мест
        r'/pushkin-card',  # пушкинская карта
        r'/discount-event',  # скидки
        r'/abonement',  # абонементы
        r'/afisha/$',  # главная страница
        r'/moscow/sport/hockey/?$',  # сам каталог
        r'\?source=',  # навигационные параметры
        r'/support/',  # поддержка
        r'/legal/',  # юридические страницы
    ]

    # Черный список доменов
    BLACKLIST_DOMAINS = [
        'apps.apple.com', 'play.google.com', 'radar.yandex.ru',
        'vk.com', 't.me', 'telegram.org', 'youtube.com', 'ok.ru',
        'mail.ru', 'google.com'
    ]

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

    def _find_event_urls(self, soup: BeautifulSoup) -> list[str]:
        """Находит ссылки на реальные события, фильтруя мусор."""
        all_links = soup.find_all("a", href=True)
        valid_urls = set()

        for link in all_links:
            href = link["href"]

            # Пропускаем внешние ссылки
            if not self._is_internal_link(href):
                continue

            # Делаем абсолютный URL
            if href.startswith("/"):
                href = "https://afisha.yandex.ru" + href

            # Проверяем по whitelist паттернам
            if not self._matches_event_pattern(href):
                continue

            # Проверяем по blacklist паттернам
            if self._matches_blacklist_pattern(href):
                continue

            valid_urls.add(href)

        return list(valid_urls)

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
        try:
            # Используем метод fetch из базового класса, но с другим URL
            old_url = self.url
            self.url = url
            html = await self.fetch()
            self.url = old_url
            return html
        except Exception as e:
            self.logger.error(f"Не удалось загрузить {url}: {e}")
            return None

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