"""
Кастомные парсеры для официальных билетных сайтов клубов КХЛ.

Каждый клуб имеет свою вёрстку. Часть сайтов — SPA (JS-рендер через Playwright),
часть требует авторизации. Универсального решения нет — под каждый клуб свои селекторы.
"""
import re
from typing import Optional

from bs4 import BeautifulSoup, Tag

from parsers.club_parser import ClubParser


class ClubSiteParser(ClubParser):
    """Парсер для клубных сайтов с переопределёнными селекторами."""

    # ───── Селекторы для каждого клуба ─────
    CLUB_SELECTORS = {
        # Ворк — public listings
        "cska": {
            "card": "[class*=match], [class*=event], [class*=ticket], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost], [class*=amount]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket], a[href*=/buy]",
            "note": "SPA / личный кабинет — может не работать без авторизации",
        },
        "ska": {
            "card": "[class*=match], [class*=event], [class*=game-card], .schedule-item",
            "title": "h1, h2, h3, [class*=title], [class*=team], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket], a[href*=/buy], a[class*=buy]",
            "note": "SPA — нужен wait_selector для динамической загрузки",
        },
        "spartak": {
            "card": "[class*=match], [class*=event], [class*=ticket], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket]",
            "note": "личный кабинет — требуется регистрация",
        },
        "dynamo_moscow": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=item]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket], a[href*=/buy]",
            "note": "SPA / виджет — может не работать",
        },
        "avangard": {
            "card": "[class*=product], [class*=item], [class*=card], [class*=ticket]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost], [class*=amount]",
            "link": "a[href*=/event], a[href*=/ticket], a[href*=/buy], a[class*=buy]",
            "note": "SPA + авторизация — нужны куки",
        },
        "ak_bars": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=item]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket]",
            "note": "показывает 'нет билетов' в межсезонье",
        },
        "salavat_yulaev": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=item]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/ticket], a[href*=/match]",
            "note": "редирект на Яндекс Афишу",
        },
        "metallurg": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket]",
            "note": "GetSeat SPA — нужен Playwright + wait",
        },
        "traktor": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket]",
            "note": "личный кабинет — обязательна авторизация",
        },
        "lokomotiv": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket]",
            "note": "личный кабинет — требуется регистрация",
        },
        "sibir": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket]",
            "note": "личный кабинет + Яндекс Афиша",
        },
        "torpedo": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket], a[href*=buy]",
            "note": "SPA — Яндекс Сплит виджет",
        },
        "lada": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket]",
            "note": "страница билетной программы, не афиша",
        },
        "vityaz": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket]",
            "note": "виджет Яндекс Афиши — уже парсится yandex_parser",
        },
        "severstal": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket]",
            "note": "Яндекс Афиша — уже парсится yandex_parser",
        },
        "neftekhimik": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket]",
            "note": "билеты проданы / межсезонье",
        },
        "amur": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket], a[href*=buy]",
            "note": "возможна публичная афиша",
        },
        "admiral": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket]",
            "note": "личный кабинет — требуется регистрация",
        },
        "kunlun": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket]",
            "note": "играет в СПб на СКА Арене — билеты через arena-mo.ru",
        },
        "barys": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket]",
            "note": "SPA / личный кабинет",
        },
        "dynamo_minsk": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket], a[href*=buy]",
            "note": "Ticketpro — внешний билетный оператор",
        },
        "sochi": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket], a[href*=buy]",
            "note": "SPA / Кассир.ру — внешний оператор",
        },
        "avtomobilist": {
            "card": "[class*=match], [class*=event], [class*=card], [class*=game]",
            "title": "h1, h2, h3, [class*=title], [class*=name]",
            "date": "[class*=date], [class*=time], time",
            "place": "[class*=place], [class*=location], [class*=venue], address",
            "price": "[class*=price], [class*=cost]",
            "link": "a[href*=/event], a[href*=/match], a[href*=/ticket]",
            "note": "УГМК-Арена — SPA билетная система",
        },
    }

    def __init__(self, config: dict, proxy_rotator=None):
        super().__init__(config, proxy_rotator=proxy_rotator)
        club_name = self.name
        self._sel = self.CLUB_SELECTORS.get(club_name, {})
        if not self._sel:
            self.logger.warning(f"[{club_name}] нет кастомных селекторов — используется ClubParser")

    def _find_event_cards(self, soup: BeautifulSoup) -> list:
        """Ищет карточки событий по селекторам клуба (если есть), иначе — базовый поиск."""
        card_sel = self._sel.get("card")
        if not card_sel:
            return super()._find_event_cards(soup)

        cards = []
        seen = set()
        for found in soup.select(card_sel):
            cid = id(found)
            if cid not in seen:
                cards.append(found)
                seen.add(cid)

        if cards:
            self.logger.debug(f"[{self.name}] Найдено {len(cards)} карточек по селектору '{card_sel}'")
        else:
            self.logger.debug(f"[{self.name}] Селектор '{card_sel}' ничего не дал — fallback на ClubParser")
            return super()._find_event_cards(soup)

        return cards

    def _extract_title(self, card: Tag) -> Optional[str]:
        sel = self._sel.get("title")
        if sel:
            for el in card.select(sel):
                text = el.get_text(strip=True)
                if text and len(text) >= 5:
                    return text
        return super()._extract_title(card)

    def _extract_date(self, card: Tag) -> Optional[str]:
        sel = self._sel.get("date")
        if sel:
            for el in card.select(sel):
                text = el.get_text(strip=True)
                if text:
                    return text
            time_tag = card.find("time")
            if time_tag:
                return time_tag.get("datetime") or time_tag.get_text(strip=True)
        return super()._extract_date(card)

    def _extract_place(self, card: Tag) -> Optional[str]:
        sel = self._sel.get("place")
        if sel:
            for el in card.select(sel):
                text = el.get_text(strip=True)
                if text and len(text) > 3:
                    return text
            address = card.find("address")
            if address:
                return address.get_text(strip=True)
        return super()._extract_place(card)

    def _extract_prices(self, card: Tag) -> tuple[str, str]:
        sel = self._sel.get("price")
        if sel:
            price_text = ""
            for el in card.select(sel):
                price_text += " " + el.get_text()
            if price_text:
                matches = self.PRICE_REGEX.findall(price_text)
                if matches:
                    prices = []
                    for m in matches:
                        try:
                            p = int(m.replace(" ", ""))
                            if 100 < p < 1000000:
                                prices.append(p)
                        except ValueError:
                            pass
                    if prices:
                        return f"{min(prices)} ₽", f"{max(prices)} ₽"
        return super()._extract_prices(card)

    def _extract_link(self, card: Tag) -> Optional[str]:
        sel = self._sel.get("link")
        if sel:
            for a in card.select(sel):
                href = a.get("href")
                if href:
                    if href.startswith("/"):
                        from urllib.parse import urlparse
                        parsed = urlparse(self.url)
                        href = f"{parsed.scheme}://{parsed.netloc}{href}"
                    return href
            buy_btn = card.find("button", string=re.compile(r"купит", re.IGNORECASE))
            if buy_btn and buy_btn.get("onclick"):
                import re as re2
                m = re2.search(r"window\.location\s*=\s*['\"]([^'\"]+)['\"]", buy_btn["onclick"])
                if m:
                    return m.group(1)
        return super()._extract_link(card)
