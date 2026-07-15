"""Парсер КХЛ через страницу билетов khl.ru."""

import re
from datetime import datetime

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
        """Извлекает матчи из HTML страницы /tickets/."""
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
