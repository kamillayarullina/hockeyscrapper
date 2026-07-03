"""
Модуль обнаружения антибот-защиты (CAPTCHA, Cloudflare и т.п.).
Все методы — статические, чтобы их можно было вызывать без создания экземпляра.
"""

import logging
from typing import Optional
from urllib.parse import urlparse

import aiohttp

logger = logging.getLogger(__name__)

# Ключевые слова, характерные для различных видов защиты
_CAPTCHA_KEYWORDS = [
    "captcha", "recaptcha", "hcaptcha", "geetest",
    "подтвердите, что вы не робот", "я не робот",
    "i'm not a robot", "please verify you are a human",
    "g-recaptcha", "h-captcha", "cf-captcha",
]

_CLOUDFLARE_KEYWORDS = [
    "cf-challenge", "cf_challenge", "cloudflare",
    "attention required", "checking your browser",
    "ddos protection by cloudflare", "ray id",
    "error 1015", "error 1012", "error 1020",
    "_cf_chl", "cf_chl_out",
]


class ProtectionDetector:
    """Статический класс для анализа HTML на наличие антибот-защиты."""

    @staticmethod
    def detect_captcha(html: str) -> bool:
        """
        Проверяет наличие признаков CAPTCHA в HTML.
        Возвращает True, если обнаружены маркеры CAPTCHA.
        """
        if not html:
            return False
        html_lower = html.lower()
        for keyword in _CAPTCHA_KEYWORDS:
            if keyword in html_lower:
                logger.warning(f"Обнаружен маркер CAPTCHA: '{keyword}'")
                return True
        return False

    @staticmethod
    def detect_cloudflare(html: str) -> bool:
        """
        Проверяет наличие признаков защиты Cloudflare.
        Возвращает True, если обнаружены маркеры Cloudflare.
        """
        if not html:
            return False
        html_lower = html.lower()
        for keyword in _CLOUDFLARE_KEYWORDS:
            if keyword in html_lower:
                logger.warning(f"Обнаружен маркер Cloudflare: '{keyword}'")
                return True
        return False

    @staticmethod
    async def check_robots_txt(base_url: str, user_agent: str = "*") -> bool:
        """
        Асинхронно скачивает robots.txt и проверяет, разрешён ли парсинг.
        Возвращает True, если парсинг разрешён (или robots.txt недоступен).
        Возвращает False, если путь явно запрещён.
        """
        parsed = urlparse(base_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        logger.debug(f"Проверка robots.txt: {robots_url}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    robots_url,
                    timeout=aiohttp.ClientTimeout(total=10),
                    headers={"User-Agent": user_agent},
                ) as resp:
                    if resp.status != 200:
                        logger.debug(
                            f"robots.txt недоступен (HTTP {resp.status}), "
                            "считаем парсинг разрешённым"
                        )
                        return True

                    content = await resp.text()
                    return ProtectionDetector._is_path_allowed(
                        content, parsed.path, user_agent
                    )
        except Exception as e:
            logger.warning(f"Не удалось получить robots.txt: {e}")
            return True

    @staticmethod
    def _is_path_allowed(
        robots_content: str, path: str, user_agent: str
    ) -> bool:
        """
        Упрощённый парсер robots.txt.
        Проверяет, есть ли для данного User-Agent директива Disallow,
        покрывающая указанный путь.
        """
        if not path:
            path = "/"
        if not path.startswith("/"):
            path = "/" + path

        current_agents: list[str] = []
        current_disallows: list[str] = []
        current_allows: list[str] = []
        blocks: list[tuple[list[str], list[str], list[str]]] = []

        for raw_line in robots_content.splitlines():
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue

            lower_line = line.lower()
            if lower_line.startswith("user-agent:"):
                if current_agents:
                    blocks.append(
                        (current_agents, current_disallows, current_allows)
                    )
                agent = line.split(":", 1)[1].strip().lower()
                current_agents = [agent]
                current_disallows = []
                current_allows = []
            elif lower_line.startswith("disallow:"):
                value = line.split(":", 1)[1].strip()
                if value:
                    current_disallows.append(value)
            elif lower_line.startswith("allow:"):
                value = line.split(":", 1)[1].strip()
                if value:
                    current_allows.append(value)

        if current_agents:
            blocks.append(
                (current_agents, current_disallows, current_allows)
            )

        target_ua = user_agent.lower()
        relevant_block: Optional[tuple[list[str], list[str], list[str]]] = None

        for agents, disallows, allows in blocks:
            if target_ua in agents:
                relevant_block = (agents, disallows, allows)
                break

        if relevant_block is None:
            for agents, disallows, allows in blocks:
                if "*" in agents:
                    relevant_block = (agents, disallows, allows)
                    break

        if relevant_block is None:
            return True

        _, disallows, allows = relevant_block

        for allow_path in allows:
            if path.startswith(allow_path):
                logger.debug(f"robots.txt: путь '{path}' разрешён (Allow)")
                return True

        for disallow_path in disallows:
            if path.startswith(disallow_path):
                logger.warning(
                    f"robots.txt: путь '{path}' запрещён "
                    f"(Disallow: {disallow_path})"
                )
                return False

        return True

    @staticmethod
    def get_protection_level(html: str, url: str) -> str:
        """
        Определяет общий уровень защиты страницы.
        Возвращает: "none" | "captcha" | "cloudflare" | "mixed" | "unknown".
        """
        if not html or len(html.strip()) < 50:
            return "unknown"

        has_captcha = ProtectionDetector.detect_captcha(html)
        has_cf = ProtectionDetector.detect_cloudflare(html)

        if has_captcha and has_cf:
            return "mixed"
        if has_captcha:
            return "captcha"
        if has_cf:
            return "cloudflare"
        return "none"