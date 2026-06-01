import time
from dataclasses import dataclass
from urllib import robotparser
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.models.source import Source, SourceStatus

RESTRICTED_URL_MARKERS = (
    "/login",
    "login.",
    "/signin",
    "/register",
    "/paywall",
    "/captcha",
    "验证码",
    "/search",
    "?s=",
    "?q=",
    "keyword=",
    "/download",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".zip",
    ".rar",
)


@dataclass(frozen=True)
class ComplianceResult:
    allowed: bool
    reason: str = ""


class ComplianceChecker:
    def __init__(self) -> None:
        self._robots_cache: dict[str, robotparser.RobotFileParser] = {}
        self._last_request_at: dict[str, float] = {}
        self._crawl_delay_cache: dict[str, float | None] = {}

    def validate_source(self, source: Source) -> ComplianceResult:
        if source.status in {SourceStatus.enabled, SourceStatus.manual_only}:
            return ComplianceResult(True)
        return ComplianceResult(False, f"source_{source.status.value}")

    def can_fetch(self, source: Source, url: str, purpose: str = "page") -> ComplianceResult:
        if self.is_restricted_url(url):
            return ComplianceResult(False, f"restricted_url:{purpose}:{url}")

        parser = self._robots_for_url(url, source)
        if not parser.can_fetch(settings.CRAWLER_USER_AGENT, url):
            return ComplianceResult(False, f"robots_disallow:{purpose}:{url}")
        return ComplianceResult(True)

    def throttle(self, source: Source, url: str | None = None) -> None:
        key = self._cache_key(url or source.entry_url, source)
        delay = max(
            float(source.domain_delay_seconds),
            float(settings.DEFAULT_DOMAIN_DELAY_SECONDS),
            self._crawl_delay_for_key(key) or 0.0,
        )
        last = self._last_request_at.get(key, 0.0)
        wait = delay - (time.monotonic() - last)
        if wait > 0:
            time.sleep(wait)
        self._last_request_at[key] = time.monotonic()

    def is_restricted_url(self, url: str) -> bool:
        lowered = url.lower()
        return any(marker.lower() in lowered for marker in RESTRICTED_URL_MARKERS)

    def _robots_for_url(self, url: str, source: Source) -> robotparser.RobotFileParser:
        key = self._cache_key(url, source)
        parser = self._robots_cache.get(key)
        if parser is not None:
            return parser

        parsed = urlparse(url)
        scheme = parsed.scheme or "https"
        netloc = parsed.netloc or source.domain
        robots_url = f"{scheme}://{netloc}/robots.txt"
        parser = robotparser.RobotFileParser()
        parser.set_url(robots_url)
        try:
            parser.read()
        except Exception:
            pass
        self._robots_cache[key] = parser
        self._crawl_delay_cache[key] = parser.crawl_delay(settings.CRAWLER_USER_AGENT)
        return parser

    def _crawl_delay_for_key(self, key: str) -> float | None:
        delay = self._crawl_delay_cache.get(key)
        if delay is None:
            return None
        try:
            return float(delay)
        except (TypeError, ValueError):
            return None

    def _cache_key(self, url: str, source: Source) -> str:
        parsed = urlparse(url)
        host = parsed.netloc or source.domain
        scheme = parsed.scheme or "https"
        return f"{scheme}://{host}"


def http_client() -> httpx.Client:
    return httpx.Client(
        timeout=12,
        headers={"User-Agent": settings.CRAWLER_USER_AGENT, "Accept": "text/html,application/rss+xml"},
        follow_redirects=True,
    )
