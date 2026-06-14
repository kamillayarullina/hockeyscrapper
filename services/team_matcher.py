"""Match team/venue extraction from title."""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

KHL_TEAMS = {
    "ЦСКА": {"variants": ["цска", "армейцы", "красная машина"], "venue": "ЦСКА Арена", "city": "Москва"},
    "Спартак": {"variants": ["спартак", "красно-белые", "народная команда"], "venue": "Мегаспорт", "city": "Москва"},
    "Динамо Москва": {"variants": ["динамо москва", "динамо", "бело-голубые"], "venue": "ВТБ Арена", "city": "Москва"},
    "СКА": {"variants": ["ска", "санкт-петербург", "питер"], "venue": "СКА Арена", "city": "Санкт-Петербург"},
    "Авангард": {"variants": ["авангард", "омск", "ястребы"], "venue": "G-Drive Арена", "city": "Омск"},
    "Ак Барс": {"variants": ["ак барс", "казань", "барсы"], "venue": "Татнефть Арена", "city": "Казань"},
    "Салават Юлаев": {"variants": ["салават юлаев", "салават", "уфа", "сю"], "venue": "Уфа-Арена", "city": "Уфа"},
    "Трактор": {"variants": ["трактор", "челябинск"], "venue": "Арена Трактор", "city": "Челябинск"},
    "Металлург": {"variants": ["металлург", "магнитогорск", "магнитка"], "venue": "Арена Металлург",
                  "city": "Магнитогорск"},
    "Локомотив": {"variants": ["локомотив", "локо", "ярославль"], "venue": "Арена 2000", "city": "Ярославль"},
    "Сибирь": {"variants": ["сибирь", "новосибирск"], "venue": "Сибирь Арена", "city": "Новосибирск"},
    "Торпедо": {"variants": ["торпедо", "нижний новгород"], "venue": "Нагорный ДС", "city": "Нижний Новгород"},
    "Лада": {"variants": ["лада", "тольятти"], "venue": "Лада Арена", "city": "Тольятти"},
    "Витязь": {"variants": ["витязь", "подольск"], "venue": "Арена Витязь", "city": "Подольск"},
    "Северсталь": {"variants": ["северсталь", "череповец"], "venue": "Ледовый дворец", "city": "Череповец"},
    "Нефтехимик": {"variants": ["нефтехимик", "нижнекамск", "химик"], "venue": "Нефтехим Арена", "city": "Нижнекамск"},
    "Амур": {"variants": ["амур", "хабаровск"], "venue": "Платинум Арена", "city": "Хабаровск"},
    "Адмирал": {"variants": ["адмирал", "владивосток"], "venue": "Фетисов Арена", "city": "Владивосток"},
    "Куньлунь": {"variants": ["куньлунь", "ред стар", "red star", "пекин"], "venue": "Мытищинская Арена",
                 "city": "Мытищи"},
    "Барыс": {"variants": ["барыс", "астана"], "venue": "Барыс Арена", "city": "Астана"},
    "Динамо Минск": {"variants": ["динамо минск", "минск"], "venue": "Минск-Арена", "city": "Минск"},
    "Сочи": {"variants": ["сочи", "леопарды"], "venue": "Большой Ледовый Дворец", "city": "Сочи"},
}

_VARIANT_TO_TEAM = {}
for team, info in KHL_TEAMS.items():
    _VARIANT_TO_TEAM[team.lower()] = team
    for v in info["variants"]:
        _VARIANT_TO_TEAM[v.lower()] = team


def extract_teams_from_title(title: str) -> list[str]:
    """Extract team names from match title (whole words only)."""
    if not title:
        return []

    title_lower = title.lower()
    sorted_variants = sorted(_VARIANT_TO_TEAM.keys(), key=len, reverse=True)

    consumed = set()
    found_teams = set()

    for variant in sorted_variants:
        for match in re.finditer(re.escape(variant), title_lower):
            start, end = match.start(), match.end()

            is_whole_word = True
            if start > 0 and title_lower[start - 1].isalpha():
                is_whole_word = False
            if end < len(title_lower) and title_lower[end].isalpha():
                is_whole_word = False

            if not is_whole_word:
                continue

            pos_range = set(range(start, end))
            if pos_range & consumed:
                continue

            consumed.update(pos_range)
            team = _VARIANT_TO_TEAM[variant]
            found_teams.add(team)
            break

    return list(found_teams)


def get_team_info(team: str) -> Optional[dict]:
    """Return team info (venue, city)."""
    if not team:
        return None
    return KHL_TEAMS.get(team)


def get_all_team_names() -> list[str]:
    return list(KHL_TEAMS.keys())


def normalize_team_name(name: str) -> Optional[str]:
    if not name:
        return None
    return _VARIANT_TO_TEAM.get(name.lower().strip())