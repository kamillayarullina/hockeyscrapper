"""Парсер КХЛ через страницу билетов khl.ru."""

import re
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup, Tag
from parsers.base_parser import BaseParser


class KHLParser(BaseParser):
    """Парсит матчи КХЛ со страницы khl.ru/tickets/ через Playwright+stealth."""

    TEAM_MAP = {
        "АВТ": "Автомобилист",
        "АДМ": "Адмирал",
        "АКБ": "Ак Барс",
        "АМР": "Амур",
        "АВГ": "Авангард",
        "БАР": "Барыс",
        "ДИН": "Динамо М",
        "ДМН": "Динамо Мн",
        "ЛАД": "Лада",
        "ЛОК": "Локомотив",
        "ММГ": "Металлург Мг",
        "НХК": "Нефтехимик",
        "СЕВ": "Северсталь",
        "СИБ": "Сибирь",
        "СКА": "СКА",
        "СПР": "Спартак",
        "СЮЛ": "Салават Юлаев",
        "СОЧ": "ХК Сочи",
        "ТРК": "Трактор",
        "ТОР": "Торпедо",
        "ЦСК": "ЦСКА",
        "ШДР": "Куньлунь Ред Стар",
    }

    MONTH_MAP = {
        "сен": 9, "окт": 10, "ноя": 11, "дек": 12,
        "янв": 1, "фев": 2, "мар": 3, "апр": 4,
        "мая": 5, "июн": 6, "июл": 7, "авг": 8,
    }

    PRICE_REGEX = re.compile(r'(\d[\d\s]{1,})\s*(?:₽|р\.|руб)', re.IGNORECASE)
    DATE_REGEX = re.compile(r'(\d{1,2})\s+([а-яёa-z]+)\s+(\d{4})', re.IGNORECASE)
    TEAM_VS_REGEX = re.compile(r'([А-ЯA-Z][а-яёa-z\s\-]+)\s*[–—-]\s*([А-ЯA-Z][а-яёa-z\s\-]+)', re.IGNORECASE)

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

    async def _fetch_with_playwright(self, user_agent, timeout_ms, wait_selector,
                                      proxy=None, url=None):
        """Загрузка страницы через Playwright с применением stealth."""
        from playwright.async_api import async_playwright, Browser
        from playwright_stealth import Stealth

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
                from parsers.base_parser import NetworkError
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

    def _parse_date(self, raw_date: str) -> str:
        """Парсит дату вида '5 сен' в '2026-09-05'."""
        m = re.match(r"(\d+)\s*(\w+)", raw_date.strip())
        if not m:
            return ""
        day = int(m.group(1))
        month_abbr = m.group(2).lower()[:3]
        month = self.MONTH_MAP.get(month_abbr)
        if month is None:
            return ""
        year = 2026 if month >= 9 else 2027
        try:
            return datetime(year, month, day).strftime("%Y-%m-%d")
        except ValueError:
            return ""

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
            events = self._fallback_parse(html)

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
            return None

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
        place_match = re.search(r'(?:г\.\s*)?([А-ЯA-Z][а-яёa-z]+),\s*([А-ЯA-Z][а-яёa-z\s\-]+)', text)
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

    def _fallback_parse(self, html: str) -> list[dict]:
        self.logger.info(f"[{self.name}] Использую fallback-парсинг (поиск всех ссылок с командами)")
        events = []
        seen = set()

        blocks = re.findall(
            r'<div class="slider-item[^"]*"[^>]*>.*?</div>\s*</div>\s*</div>',
            html, re.DOTALL
        )

        for block in blocks:
            text = re.sub(r"<[^>]+>", " ", block)
            text = re.sub(r"\s+", " ", text).strip()

            m = re.search(r'/game/(\d+)/(\d+)/preview/', block)
            if not m:
                continue
            season_id, game_id = m.group(1), m.group(2)

            # format: "АВТ 5 сен, Сб ДИН Екатеринбург ..."
            parts = text.split()
            if len(parts) < 6:
                continue

            team_a_abbr = parts[0]
            raw_date = f"{parts[1]} {parts[2].rstrip(',')}"
            team_b_abbr = parts[4]

            name_a = self.TEAM_MAP.get(team_a_abbr, team_a_abbr)
            name_b = self.TEAM_MAP.get(team_b_abbr, team_b_abbr)

            if len(name_a) < 2 or len(name_b) < 2:
                continue

            title = f"{name_a} — {name_b}"
            dedup_key = title + game_id
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            date = self._parse_date(raw_date)

            city = parts[5]
            if not city:
                city = "Место не указано"

            events.append({
                "source": self.name,
                "title": title,
                "date": date,
                "place": city,
                "price_min": "Не указана",
                "price_max": "Не указана",
                "availability": "Нет",
                "link": f"https://www.khl.ru/game/{season_id}/{game_id}/preview/",
            })

        self.logger.info(f"[{self.name}] Извлечено {len(events)} матчей из HTML")
        return events

    async def _run(self) -> list[dict]:
        html = await self.fetch()
        return await self.parse(html)
