"""
Универсальный парсер для сайтов типа ticket-hockey.ru.
Использует расширенные CSS-селекторы с умной фильтрацией.
"""

import re
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag
from .base_parser import BaseParser


class ClubParser(BaseParser):
    """Парсер для ticket-hockey.ru и подобных сайтов."""

    PRICE_REGEX = re.compile(r'(\d[\d\s]{1,})\s*(?:₽|р\.|руб)', re.IGNORECASE)
    DATE_REGEX = re.compile(r'(\d{1,2})\s+([а-яё]+)(?:\s+(\d{2,4}))?', re.IGNORECASE)

    EVENT_CARD_SELECTORS = [
        'div.event-card',
        'div.event-item',
        'div.event-block',
        'div.card-event',
        'div[class*="event-card"]',
        'div[class*="event-item"]',
        'div[class*="event-block"]',
        'article.event',
        'article[class*="event"]',
        '.col-md-4',
        '.col-lg-4',
    ]

    LINK_SELECTORS = [
        'a[href*="/event/"]',
        'a[href*="/afisha/"]',
        'a[href*="/match/"]',
        'a[href*="/ticket/"]',
        'a[href*="/buy"]',
        'button[class*="buy"]',
    ]

    async def parse(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        keywords = self.params.get("keywords", ["хоккей"])
        if isinstance(keywords, str):
            keywords = [keywords]

        keywords_lower = [kw.lower() for kw in keywords]
        self.logger.info(f"[{self.name}] Поиск событий по ключевым словам: {keywords_lower}")

        events = []
        seen_links = set()

        event_cards = self._find_event_cards(soup)
        self.logger.debug(f"[{self.name}] Найдено {len(event_cards)} карточек")

        for card in event_cards:
            try:
                event = self._extract_event_from_card(card, soup)
                if event and self._is_valid_event(event, keywords_lower):
                    if event['link'] not in seen_links:
                        events.append(event)
                        seen_links.add(event['link'])
                        self.logger.debug(f"✅ Добавлено: {event.get('title')}")
            except Exception as e:
                self.logger.debug(f"❌ Ошибка парсинга карточки: {e}")
                continue

        self.logger.info(f"[{self.name}] Успешно извлечено {len(events)} событий")
        return events

    def _find_event_cards(self, soup: BeautifulSoup) -> list:
        cards = []
        seen_cards = set()

        for selector in self.EVENT_CARD_SELECTORS:
            try:
                found = soup.select(selector)
                for card in found:
                    card_id = id(card)
                    if card_id not in seen_cards:
                        cards.append(card)
                        seen_cards.add(card_id)
            except Exception:
                continue

        if not cards:
            for div in soup.find_all('div'):
                if div.find('button') or div.find('a', href=lambda h: h and 'buy' in h.lower()):
                    card_id = id(div)
                    if card_id not in seen_cards:
                        cards.append(div)
                        seen_cards.add(card_id)

        if not cards:
            self.logger.debug("Основные селекторы не сработали, пробую универсальный поиск")
            for div in soup.find_all('div'):
                has_link = div.find('a', href=True)
                has_price_text = bool(self.PRICE_REGEX.search(div.get_text()))
                has_date_text = bool(self.DATE_REGEX.search(div.get_text()))

                if has_link and (has_price_text or has_date_text):
                    card_id = id(div)
                    if card_id not in seen_cards:
                        cards.append(div)
                        seen_cards.add(card_id)

        return cards

    def _extract_event_from_card(self, card: Tag, soup: BeautifulSoup) -> Optional[dict]:
        link = self._extract_link(card)
        if not link:
            return None

        title = self._extract_title(card)
        if not title or len(title) < 5:
            return None

        date = self._extract_date(card)
        place = self._extract_place(card)
        price_min, price_max = self._extract_prices(card)

        availability = "Да"
        card_text = card.get_text().lower()
        if "распродано" in card_text or "нет билетов" in card_text:
            availability = "Нет"
        elif price_min == "Не указана":
            availability = "Уточняется"

        return {
            "source": self.name,
            "title": self._clean_title(title),
            "date": date or "Дата не указана",
            "place": place or "Место не указано",
            "price_min": price_min,
            "price_max": price_max,
            "availability": availability,
            "link": link,
            "parsed_at": datetime.now(timezone.utc).isoformat(),
        }

    def _extract_link(self, card: Tag) -> Optional[str]:
        for selector in self.LINK_SELECTORS:
            link_tag = card.select_one(selector)
            if link_tag:
                href = link_tag.get('href') or link_tag.get('onclick', '')
                if href.startswith('http'):
                    return href
                if href.startswith('/'):
                    parsed = urlparse(self.url)
                    return f"{parsed.scheme}://{parsed.netloc}{href}"
                match = re.search(r"window\.location\s*=\s*['\"]([^'\"]+)['\"]", href)
                if match:
                    return match.group(1)

        for btn in card.find_all('button'):
            text = btn.get_text(strip=True).lower()
            if 'купит' in text and btn.get('onclick'):
                match = re.search(r"window\.location\s*=\s*['\"]([^'\"]+)['\"]", btn['onclick'])
                if match:
                    return match.group(1)

        buy_link = card.find('a', string=re.compile(r'купить\s*билет', re.IGNORECASE))
        if buy_link and buy_link.get('href'):
            href = buy_link['href']
            if href.startswith('/'):
                parsed = urlparse(self.url)
                return f"{parsed.scheme}://{parsed.netloc}{href}"
            return href

        first_link = card.find('a', href=True)
        if first_link:
            href = first_link['href']
            if href.startswith('/'):
                parsed = urlparse(self.url)
                return f"{parsed.scheme}://{parsed.netloc}{href}"
            return href

        return None

    def _extract_title(self, card: Tag) -> Optional[str]:
        for tag in ['h3', 'h2', 'h4', 'h1']:
            header = card.find(tag)
            if header:
                text = header.get_text(strip=True)
                if text and len(text) >= 5:
                    return text

        title_classes = ['title', 'name', 'event-title', 'card-title']
        for cls in title_classes:
            el = card.find(class_=lambda x: x and cls in x.lower())
            if el:
                text = el.get_text(strip=True)
                if text and len(text) >= 5:
                    return text

        all_text = card.get_text(separator='|', strip=True)
        parts = all_text.split('|')
        for part in parts:
            part = part.strip()
            if len(part) >= 10 and len(part) <= 200:
                if not self.PRICE_REGEX.search(part) and not self.DATE_REGEX.search(part):
                    return part

        return None

    def _extract_date(self, card: Tag) -> Optional[str]:
        time_tag = card.find('time')
        if time_tag:
            return time_tag.get('datetime') or time_tag.get_text(strip=True)

        date_classes = ['date', 'time', 'datetime', 'event-date']
        for cls in date_classes:
            el = card.find(class_=lambda x: x and cls in x.lower())
            if el:
                text = el.get_text(strip=True)
                if text:
                    return text

        text = card.get_text()
        match = self.DATE_REGEX.search(text)
        if match:
            day, month, year = match.groups()
            return f"{day} {month} {year or ''}".strip()

        return None

    def _extract_place(self, card: Tag) -> Optional[str]:
        address = card.find('address')
        if address:
            return address.get_text(strip=True)

        place_classes = ['place', 'location', 'venue', 'arena', 'address']
        for cls in place_classes:
            el = card.find(class_=lambda x: x and cls in x.lower())
            if el:
                text = el.get_text(strip=True)
                if text and len(text) > 3:
                    return text

        text = card.get_text()
        match = re.search(r'(г\.\s*[^,\n]+,\s*[^,\n]+)', text)
        if match:
            return match.group(1).strip()

        return None

    def _extract_prices(self, card: Tag) -> tuple[str, str]:
        text = card.get_text()
        matches = self.PRICE_REGEX.findall(text)

        if not matches:
            return "Не указана", "Не указана"

        prices = []
        for match in matches:
            price_str = match.replace(" ", "")
            try:
                price = int(price_str)
                if 100 < price < 1000000:
                    prices.append(price)
            except ValueError:
                continue

        if not prices:
            return "Не указана", "Не указана"

        return f"{min(prices)} ₽", f"{max(prices)} ₽"

    def _is_valid_event(self, event: dict, keywords: list[str]) -> bool:
        title = event.get('title', '').lower()
        place = event.get('place', '').lower()

        blacklist = [
            'скачать', 'download', 'app store', 'google play',
            'подписка', 'subscribe', 'регистрация', 'register',
            'о нас', 'about', 'контакты', 'contacts', 'помощь',
            'статистика', 'statistics', 'радар',
        ]

        for word in blacklist:
            if word in title or word in place:
                self.logger.debug(f"❌ Отфильтровано по blacklist '{word}': {title}")
                return False

        combined = f"{title} {place}"
        if not any(kw in combined for kw in keywords):
            self.logger.debug(f"❌ Нет ключевых слов: {title}")
            return False

        link = event.get('link', '')
        if 'apple.com' in link or 'google.com' in link or 'yandex.ru/radar' in link:
            self.logger.debug(f"❌ Внешняя ссылка: {link}")
            return False

        return True

    def _clean_title(self, title: str) -> str:
        title = re.sub(r'от\s*\d+[\d\s]*\s*₽', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s+', ' ', title).strip()
        return title