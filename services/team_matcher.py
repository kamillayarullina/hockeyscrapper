"""Определяет команды и стадионы из названия матча."""

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
    "Металлург": {"variants": ["металлург", "металлург мг", "магнитогорск", "магнитка"], "venue": "Арена Металлург",
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
    "Куньлунь": {"variants": ["куньлунь", "куньлунь ред стар", "ред стар", "red star", "шанхай", "shanghai dragons", "drago"],
                  "venue": "СКА Арена", "city": "Санкт-Петербург"},
    "Барыс": {"variants": ["барыс", "астана"], "venue": "Барыс Арена", "city": "Астана"},
    "Динамо Минск": {"variants": ["динамо минск", "минск"], "venue": "Минск-Арена", "city": "Минск"},
    "Сочи": {"variants": ["сочи", "леопарды"], "venue": "Большой Ледовый Дворец", "city": "Сочи"},
    "Автомобилист": {"variants": ["автомобилист", "екатеринбург"], "venue": "УГМК-Арена", "city": "Екатеринбург"},
}

_VARIANT_TO_TEAM = {}
for team, info in KHL_TEAMS.items():
    _VARIANT_TO_TEAM[team.lower()] = team
    for v in info["variants"]:
        _VARIANT_TO_TEAM[v.lower()] = team


def extract_teams_from_title(title: str) -> list[str]:
    """Извлекает команды из названия матча (только целые слова)."""
    if not title:
        return []

    title_lower = title.lower()
    sorted_variants = sorted(_VARIANT_TO_TEAM.keys(), key=len, reverse=True)

    consumed = set()
    found_teams = {}  # dict preserves insertion order, team -> first_position

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
            if team not in found_teams:
                found_teams[team] = start
            break

    return sorted(found_teams.keys(), key=lambda t: found_teams[t])


def get_team_info(team: str) -> Optional[dict]:
    """Возвращает информацию о команде (стадион, город)."""
    if not team:
        return None
    return KHL_TEAMS.get(team)


def get_all_team_names() -> list[str]:
    return list(KHL_TEAMS.keys())


def normalize_team_name(name: str) -> Optional[str]:
    if not name:
        return None
    return _VARIANT_TO_TEAM.get(name.lower().strip())