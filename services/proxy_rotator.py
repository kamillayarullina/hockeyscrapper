"""Proxy rotation module with health checks, stats, and automatic exclusion of dead servers."""

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from urllib.parse import urlparse

import aiohttp

logger = logging.getLogger(__name__)


class ProxyType(str, Enum):
    """Proxy server type."""
    HTTP = "http"
    HTTPS = "https"
    SOCKS5 = "socks5"


class RotationStrategy(str, Enum):
    """Strategy for selecting the next proxy."""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_USED = "least_used"
    FASTEST = "fastest"


@dataclass
class ProxyStats:
    """Usage statistics for a specific proxy."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    consecutive_failures: int = 0
    last_used_at: Optional[float] = None
    last_success_at: Optional[float] = None
    last_failure_at: Optional[float] = None
    avg_response_time_ms: float = 0.0
    _response_times: list[float] = field(default_factory=list)

    def record_success(self, response_time_ms: float) -> None:
        """Record a successful request."""
        self.total_requests += 1
        self.successful_requests += 1
        self.consecutive_failures = 0
        self.last_used_at = time.time()
        self.last_success_at = time.time()
        self._response_times.append(response_time_ms)
        if len(self._response_times) > 50:
            self._response_times = self._response_times[-50:]
        self.avg_response_time_ms = (
            sum(self._response_times) / len(self._response_times)
        )

    def record_failure(self) -> None:
        """Record a failed request."""
        self.total_requests += 1
        self.failed_requests += 1
        self.consecutive_failures += 1
        self.last_used_at = time.time()
        self.last_failure_at = time.time()

    @property
    def success_rate(self) -> float:
        """Fraction of successful requests (0.0 — 1.0)."""
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests


@dataclass
class ProxyServer:
    """A single proxy server."""
    url: str
    proxy_type: ProxyType = ProxyType.HTTP
    country: Optional[str] = None
    note: Optional[str] = None

    enabled: bool = True
    disabled_at: Optional[float] = None
    stats: ProxyStats = field(default_factory=ProxyStats)

    host: str = ""
    port: int = 0
    username: Optional[str] = None
    password: Optional[str] = None

    def __post_init__(self) -> None:
        """Parse proxy URL into components."""
        parsed = urlparse(self.url)
        self.host = parsed.hostname or ""
        self.port = parsed.port or 8080
        self.username = parsed.username
        self.password = parsed.password

        if parsed.scheme.lower() in ("socks5", "socks5h"):
            self.proxy_type = ProxyType.SOCKS5
        elif parsed.scheme.lower() == "https":
            self.proxy_type = ProxyType.HTTPS
        else:
            self.proxy_type = ProxyType.HTTP

    def get_playwright_proxy(self) -> dict[str, Any]:
        """Return dict in Playwright proxy format: {"server": "...", "username": "...", "password": "..."}"""
        server_url = f"{self.proxy_type.value}://{self.host}:{self.port}"
        result: dict[str, Any] = {"server": server_url}
        if self.username:
            result["username"] = self.username
        if self.password:
            result["password"] = self.password
        return result

    def get_aiohttp_proxy(self) -> str:
        """Return proxy URL for aiohttp."""
        return self.url

    def disable(self) -> None:
        """Disable this proxy."""
        self.enabled = False
        self.disabled_at = time.time()
        logger.warning(
            f"Прокси {self.host}:{self.port} отключён "
            f"(успешных: {self.stats.successful_requests}, "
            f"ошибок подряд: {self.stats.consecutive_failures})"
        )

    def try_reanimate(self, reanimate_after_seconds: float) -> bool:
        """Try to re-enable a disabled proxy after enough time has passed."""
        if self.enabled:
            return False
        if self.disabled_at is None:
            return False
        if time.time() - self.disabled_at >= reanimate_after_seconds:
            self.enabled = True
            self.disabled_at = None
            self.stats.consecutive_failures = 0
            logger.info(
                f"Прокси {self.host}:{self.port} реанимирован"
            )
            return True
        return False

    def __str__(self) -> str:
        auth = "auth" if self.username else "no-auth"
        country = f"[{self.country}]" if self.country else ""
        status = "✓" if self.enabled else "✗"
        return (
            f"{status} {self.proxy_type.value}://"
            f"{self.host}:{self.port} {country} ({auth})"
        )


class ProxyRotator:
    """Proxy rotator with health checks and statistics."""

    def __init__(self, config: dict[str, Any]):
        self.enabled: bool = bool(config.get("enabled", False))
        strategy_name = config.get("rotation_strategy", "round_robin")
        try:
            self.strategy = RotationStrategy(strategy_name)
        except ValueError:
            logger.warning(
                f"Неизвестная стратегия '{strategy_name}', "
                f"использую round_robin"
            )
            self.strategy = RotationStrategy.ROUND_ROBIN

        self.health_check_enabled: bool = bool(
            config.get("health_check_enabled", True)
        )
        self.health_check_interval: float = float(
            config.get("health_check_interval_seconds", 300)
        )
        self.health_check_timeout: float = float(
            config.get("health_check_timeout_seconds", 10)
        )
        self.health_check_url: str = config.get(
            "health_check_url", "https://httpbin.org/ip"
        )
        self.max_failures: int = int(
            config.get("max_failures_before_disable", 3)
        )
        self.reanimate_after: float = float(
            config.get("reanimate_after_seconds", 600)
        )
        self.use_direct_fallback: bool = bool(
            config.get("use_direct_as_fallback", True)
        )

        self._servers: list[ProxyServer] = []
        self._load_servers(config.get("servers", []))

        self._rr_index: int = 0

        self._health_check_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()

        self._lock = asyncio.Lock()

        logger.info(
            f"ProxyRotator инициализирован: "
            f"enabled={self.enabled}, strategy={self.strategy.value}, "
            f"серверов={len(self._servers)}"
        )

    def _load_servers(self, servers_config: list[dict]) -> None:
        """Load proxy server list from config."""
        for i, srv_cfg in enumerate(servers_config):
            if not isinstance(srv_cfg, dict):
                logger.warning(f"Прокси #{i} имеет некорректный формат")
                continue
            url = srv_cfg.get("url")
            if not url:
                logger.warning(f"Прокси #{i} не имеет URL")
                continue
            try:
                proxy_type_str = srv_cfg.get("type", "http")
                proxy_type = ProxyType(proxy_type_str)
            except ValueError:
                logger.warning(
                    f"Неизвестный тип прокси '{proxy_type_str}' "
                    f"для {url}, использую http"
                )
                proxy_type = ProxyType.HTTP

            server = ProxyServer(
                url=url,
                proxy_type=proxy_type,
                country=srv_cfg.get("country"),
                note=srv_cfg.get("note"),
            )
            self._servers.append(server)
            logger.debug(f"Добавлен прокси: {server}")

    async def get_next(
        self,
        country: Optional[str] = None,
    ) -> Optional[ProxyServer]:
        """Return the next proxy per rotation strategy, optionally filtered by country."""
        if not self.enabled or not self._servers:
            return None

        async with self._lock:
            for server in self._servers:
                server.try_reanimate(self.reanimate_after)

            pool = [s for s in self._servers if s.enabled]
            if country:
                country_pool = [
                    s for s in pool
                    if s.country and s.country.lower() == country.lower()
                ]
                if country_pool:
                    pool = country_pool
                else:
                    logger.debug(
                        f"Прокси для страны '{country}' не найдены, "
                        f"использую весь пул"
                    )

            if not pool:
                logger.warning("Нет доступных прокси")
                return None

            if self.strategy == RotationStrategy.ROUND_ROBIN:
                return self._select_round_robin(pool)
            elif self.strategy == RotationStrategy.RANDOM:
                return self._select_random(pool)
            elif self.strategy == RotationStrategy.LEAST_USED:
                return self._select_least_used(pool)
            elif self.strategy == RotationStrategy.FASTEST:
                return self._select_fastest(pool)
            else:
                return self._select_round_robin(pool)

    def _select_round_robin(self, pool: list[ProxyServer]) -> ProxyServer:
        """Round-robin selection."""
        all_enabled_ids = [
            i for i, s in enumerate(self._servers) if s.enabled
        ]
        if not all_enabled_ids:
            return pool[0]

        pos = 0
        for i, idx in enumerate(all_enabled_ids):
            if idx >= self._rr_index:
                pos = i
                break

        chosen_idx = all_enabled_ids[pos % len(all_enabled_ids)]
        self._rr_index = (chosen_idx + 1) % len(self._servers)
        return self._servers[chosen_idx]

    def _select_random(self, pool: list[ProxyServer]) -> ProxyServer:
        """Random selection."""
        return random.choice(pool)

    def _select_least_used(self, pool: list[ProxyServer]) -> ProxyServer:
        """Least-used proxy selection."""
        return min(pool, key=lambda s: s.stats.total_requests)

    def _select_fastest(self, pool: list[ProxyServer]) -> ProxyServer:
        """Fastest proxy selection (by avg response time)."""
        with_stats = [s for s in pool if s.stats.total_requests > 0]
        if not with_stats:
            return random.choice(pool)
        return min(with_stats, key=lambda s: s.stats.avg_response_time_ms)

    async def record_success(
        self, server: ProxyServer, response_time_ms: float
    ) -> None:
        """Record a successful proxy usage."""
        async with self._lock:
            server.stats.record_success(response_time_ms)
            logger.debug(
                f"Прокси {server.host}:{server.port} — успех "
                f"({response_time_ms:.0f} мс)"
            )

    async def record_failure(self, server: ProxyServer) -> None:
        """Record a failed proxy usage; disable if limit exceeded."""
        async with self._lock:
            server.stats.record_failure()
            logger.debug(
                f"Прокси {server.host}:{server.port} — ошибка "
                f"(подряд: {server.stats.consecutive_failures})"
            )
            if server.stats.consecutive_failures >= self.max_failures:
                server.disable()

    async def start(self) -> None:
        """Start background health checks."""
        if not self.enabled or not self.health_check_enabled:
            logger.info("Проверка здоровья прокси отключена")
            return

        await self._run_health_check()

        self._stop_event.clear()
        self._health_check_task = asyncio.create_task(
            self._health_check_loop()
        )
        logger.info(
            f"Фоновая проверка здоровья запущена "
            f"(интервал {self.health_check_interval} с)"
        )

    async def stop(self) -> None:
        """Stop background health checks."""
        self._stop_event.set()
        if self._health_check_task is not None:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None
        logger.info("ProxyRotator остановлен")

    async def _health_check_loop(self) -> None:
        """Periodic health check loop."""
        try:
            while not self._stop_event.is_set():
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=self.health_check_interval,
                    )
                    break
                except asyncio.TimeoutError:
                    await self._run_health_check()
        except asyncio.CancelledError:
            raise

    async def _run_health_check(self) -> None:
        """Check all proxies; disable dead ones, reanimate disabled."""
        logger.debug("Запуск проверки здоровья прокси")

        for server in self._servers:
            server.try_reanimate(self.reanimate_after)

        tasks = [
            self._check_single_proxy(server)
            for server in self._servers
            if server.enabled
        ]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        enabled = sum(1 for s in self._servers if s.enabled)
        total = len(self._servers)
        logger.info(
            f"Проверка здоровья: {enabled}/{total} прокси доступны"
        )

    async def _check_single_proxy(self, server: ProxyServer) -> None:
        """Check a single proxy's health."""
        try:
            start = time.time()
            if server.proxy_type == ProxyType.SOCKS5:
                try:
                    from aiohttp_socks import ProxyConnector
                    connector = ProxyConnector.from_url(server.url)
                    timeout = aiohttp.ClientTimeout(
                        total=self.health_check_timeout
                    )
                    async with aiohttp.ClientSession(
                        connector=connector, timeout=timeout
                    ) as session:
                        async with session.get(self.health_check_url) as resp:
                            if resp.status == 200:
                                elapsed_ms = (time.time() - start) * 1000
                                server.stats.record_success(elapsed_ms)
                                logger.debug(
                                    f"Health check OK: {server} "
                                    f"({elapsed_ms:.0f} мс)"
                                )
                            else:
                                raise RuntimeError(
                                    f"HTTP {resp.status}"
                                )
                except ImportError:
                    logger.warning(
                        "aiohttp-socks не установлен, "
                        "пропускаю проверку SOCKS5 прокси"
                    )
            else:
                timeout = aiohttp.ClientTimeout(
                    total=self.health_check_timeout
                )
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(
                        self.health_check_url,
                        proxy=server.url,
                    ) as resp:
                        if resp.status == 200:
                            elapsed_ms = (time.time() - start) * 1000
                            server.stats.record_success(elapsed_ms)
                            logger.debug(
                                f"Health check OK: {server} "
                                f"({elapsed_ms:.0f} мс)"
                            )
                        else:
                            raise RuntimeError(f"HTTP {resp.status}")
        except Exception as e:
            logger.debug(f"Health check FAILED: {server} — {e}")
            await self.record_failure(server)

    def get_stats(self) -> list[dict[str, Any]]:
        """Return stats for all proxies."""
        result = []
        for server in self._servers:
            result.append({
                "url": f"{server.host}:{server.port}",
                "type": server.proxy_type.value,
                "country": server.country,
                "enabled": server.enabled,
                "total_requests": server.stats.total_requests,
                "success_rate": f"{server.stats.success_rate:.1%}",
                "avg_response_ms": f"{server.stats.avg_response_time_ms:.0f}",
                "consecutive_failures": server.stats.consecutive_failures,
            })
        return result

    def __len__(self) -> int:
        return len(self._servers)

    def __bool__(self) -> bool:
        """True if at least one proxy is enabled."""
        return self.enabled and any(s.enabled for s in self._servers)