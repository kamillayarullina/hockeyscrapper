"""Парсер официального сайта КХЛ (khl.ru/tickets) с Deep Crawl."""

import re
from typing import Optional

from bs4 import BeautifulSoup, Tag
from .base_parser import BaseParser


class KHLParser(BaseParser):
    """Парсит страницу билетов КХЛ с матчами, ценами и доступностью."""

    MATCH_CARD_SELECTORS = [
        'div.match-card',
        'div.ticket-card',
        'div[class*="match"]',
        'div[class*="ticket"]',
        'div[class*="game"]',
        'div.event-item',
        'tr.match-row',
        'tr[class*="match"]',
    ]

    PRICE_REGEX = re.compile(r'(\d[\d\s]{2,})\s*(?:₽|р\.|руб)', re.IGNORECASE)
    DATE_REGEX = re.compile(r'(\d{1,2})\s+([а-яё]+)\s+(\d{4})', re.IGNORECASE)
    TEAM_VS_REGEX = re.compile(r'([А-Я][а-яё\s\-]+)\s*[–—-]\s*([А-Я][а-яё\s\-]+)', re.IGNORECASE)

    DETAIL_PRICE_SELECTORS = [
        'table[class*="price"] td',
        '[class*="price"] [class*="value"]',
        '[class*="ticket-type"] [class*="cost"]',
        '[class*="category"] [class*="price"]',
        '.seat-category .price',
        '.tariff .price',
    ]

    async def _run(self) -> list[dict]:
        """Загружает список матчей, затем углубляется в каждый."""
        events = await super()._run()
        deep_crawl = self.params.get("deep_crawl", True)
        if not deep_crawl:
            return events

        enriched = []
        for event in events:
            link = event.get("link", "")
            if link and link != self.url and link.startswith("http"):
                try:
                    self.logger.info(f"[{self.name}] Deep crawl: {link}")
                    html = await self.fetch(url=link, wait_selector=None, timeout_ms=20000)
                    extras = self._deep_parse(html)
                    event.update(extras)
                    event["deep_crawled"] = True
                except Exception as e:
                    self.logger.debug(f"[{self.name}] Deep crawl failed for {link}: {e}")
            enriched.append(event)

        dc_count = sum(1 for e in enriched if e.get("deep_crawled"))
        self.logger.info(f"[{self.name}] Deep crawl: {dc_count}/{len(enriched)} events enriched")
        return enriched

    def _deep_parse(self, html: str) -> dict:
        """Извлекает уточнённые данные со страницы матча."""
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        extras: dict = {}

        price_min, price_max = self._extract_prices(text)
        if price_min != "Не указана":
            extras["price_min"] = price_min
            extras["price_max"] = price_max

        detail_prices = self._extract_detail_prices(soup)
        if detail_prices:
            extras["price_min"] = detail_prices[0]
            extras["price_max"] = detail_prices[1]

        extras["availability"] = self._extract_availability(text)

        place = self._extract_place(soup, text)
        if place:
            extras["place"] = place

        return extras

    def _extract_detail_prices(self, soup: BeautifulSoup) -> Optional[tuple[str, str]]:
        """Пытается найти таблицу цен на странице матча."""
        prices = []
        for selector in self.DETAIL_PRICE_SELECTORS:
            for el in soup.select(selector):
                m = self.PRICE_REGEX.search(el.get_text())
                if m:
                    try:
                        p = int(m.group(1).replace(" ", ""))
                        if 100 < p < 1000000:
                            prices.append(p)
                    except ValueError:
                        pass
            if prices:
                break
        if prices:
            return f"{min(prices)} ₽", f"{max(prices)} ₽"
        return None

    async def parse(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        events = []
        seen_links = set()

        cards = self._find_match_cards(soup)
        self.logger.info(f"[{self.name}] Найдено {len(cards)} карточек матчей")

        for card in cards:
            try:
                event = self._extract_match(card)
                if event and event.get('link', '') not in seen_links:
                    events.append(event)
                    seen_links.add(event.get('link', ''))
                    self.logger.debug(f"Добавлен матч: {event.get('title')}")
            except Exception as e:
                self.logger.debug(f"Ошибка парсинга карточки: {e}")
                continue

        if not events:
            events = self._fallback_parse(soup)

        self.logger.info(f"[{self.name}] Извлечено {len(events)} матчей")
        return events

    def _find_match_cards(self, soup: BeautifulSoup) -> list:
        cards = []
        seen = set()
        for selector in self.MATCH_CARD_SELECTORS:
            try:
                found = soup.select(selector)
                for card in found:
                    cid = id(card)
                    if cid not in seen:
                        cards.append(card)
                        seen.add(cid)
            except Exception:
                continue
        return cards

    def _extract_match(self, card: Tag) -> Optional[dict]:
        html_text = card.get_text(separator=" ", strip=True)

        teams = self._extract_teams(html_text)
        if not teams:
            return None

        title = " — ".join(teams)

        link = self._extract_link(card)
        if not link:
            link = "https://www.khl.ru/tickets/"

        date = self._extract_date(card, html_text)
        place = self._extract_place(card, html_text)
        price_min, price_max = self._extract_prices(html_text)
        availability = self._extract_availability(html_text)

        return {
            "source": self.name,
            "title": title,
            "date": date or "Дата не указана",
            "place": place or "Место не указано",
            "price_min": price_min,
            "price_max": price_max,
            "availability": availability,
            "link": link,
        }

    def _extract_teams(self, text: str) -> Optional[list[str]]:
        match = self.TEAM_VS_REGEX.search(text)
        if match:
            home = match.group(1).strip()
            away = match.group(2).strip()
            if len(home) > 2 and len(away) > 2:
                return [home, away]
        return None

    def _extract_link(self, card: Tag) -> Optional[str]:
        link_tag = card.find('a', href=True)
        if link_tag:
            href = link_tag['href']
            if href.startswith('/'):
                href = f"https://www.khl.ru{href}"
            return href
        return None

    def _extract_date(self, card: Tag, text: str) -> Optional[str]:
        time_tag = card.find('time')
        if time_tag:
            return time_tag.get('datetime') or time_tag.get_text(strip=True)

        date_match = self.DATE_REGEX.search(text)
        if date_match:
            day, month, year = date_match.groups()
            return f"{day} {month} {year}"

        return None

    def _extract_place(self, card: Tag, text: str) -> Optional[str]:
        for cls in ['place', 'location', 'venue', 'arena', 'address']:
            el = card.find(class_=lambda x: x and cls in x.lower())
            if el:
                return el.get_text(strip=True)
        place_match = re.search(r'(?:г\.\s*)?([А-Я][а-яё]+),\s*([А-Я][а-яё\s\-]+)', text)
        if place_match:
            return f"{place_match.group(1)}, {place_match.group(2)}"
        return None

    def _extract_prices(self, text: str) -> tuple[str, str]:
        matches = self.PRICE_REGEX.findall(text)
        prices = []
        for match in matches:
            try:
                price = int(match.replace(" ", ""))
                if 100 < price < 1000000:
                    prices.append(price)
            except ValueError:
                continue
        if not prices:
            return "Не указана", "Не указана"
        return f"{min(prices)} ₽", f"{max(prices)} ₽"

    def _extract_availability(self, text: str) -> str:
        text_lower = text.lower()
        if "распродано" in text_lower or "нет билетов" in text_lower or "sold out" in text_lower:
            return "Нет"
        if "скоро" in text_lower or "coming soon" in text_lower:
            return "Скоро"
        if "в продаже" in text_lower or "купить" in text_lower or "заказать" in text_lower:
            return "Да"
        return "Да"

    def _fallback_parse(self, soup: BeautifulSoup) -> list[dict]:
        self.logger.info(f"[{self.name}] Использую fallback-парсинг (поиск всех ссылок с командами)")
        events = []
        seen = set()

        all_links = soup.find_all('a', href=True)
        for link in all_links:
            text = link.get_text(strip=True)
            if not text or len(text) < 5:
                continue

            teams = self._extract_teams(text)
            if not teams:
                continue

            title = " — ".join(teams)
            if title in seen:
                continue
            seen.add(title)

            parent = link.find_parent(['div', 'tr', 'li', 'section']) or link
            parent_text = parent.get_text(separator=" ", strip=True)

            date = self._extract_date(parent, parent_text)
            place = self._extract_place(parent, parent_text)
            price_min, price_max = self._extract_prices(parent_text)
            availability = self._extract_availability(parent_text)

            href = link['href']
            if href.startswith('/'):
                href = f"https://www.khl.ru{href}"

            events.append({
                "source": self.name,
                "title": title,
                "date": date or "Дата не указана",
                "place": place or "Место не указано",
                "price_min": price_min,
                "price_max": price_max,
                "availability": availability,
                "link": href,
            })

        return events
