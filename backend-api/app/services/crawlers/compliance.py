import time
from dataclasses import dataclass
from urllib import robotparser

import httpx

from app.core.config import settings
from app.models.source import Source, SourceStatus


@dataclass(frozen=True)
class ComplianceResult:
    allowed: bool
    reason: str = ""


class ComplianceChecker:
    def __init__(self) -> None:
        self._robots_cache: dict[str, robotparser.RobotFileParser] = {}
        self._last_request_at: dict[str, float] = {}

    def validate_source(self, source: Source) -> ComplianceResult:
        if source.status == SourceStatus.enabled:
            return ComplianceResult(True)
        return ComplianceResult(False, f"source_{source.status.value}")

    def can_fetch(self, source: Source, url: str) -> ComplianceResult:
        parser = self._robots_cache.get(source.domain)
        if parser is None:
            parser = robotparser.RobotFileParser()
            parser.set_url(f"https://{source.domain}/robots.txt")
            try:
                parser.read()
            except Exception:
                pass
            self._robots_cache[source.domain] = parser
        if not parser.can_fetch(settings.CRAWLER_USER_AGENT, url):
            return ComplianceResult(False, "robots_disallow")
        return ComplianceResult(True)

    def throttle(self, source: Source) -> None:
        delay = max(source.domain_delay_seconds, settings.DEFAULT_DOMAIN_DELAY_SECONDS)
        last = self._last_request_at.get(source.domain, 0.0)
        wait = delay - (time.monotonic() - last)
        if wait > 0:
            time.sleep(wait)
        self._last_request_at[source.domain] = time.monotonic()


def http_client() -> httpx.Client:
    return httpx.Client(
        timeout=12,
        headers={"User-Agent": settings.CRAWLER_USER_AGENT, "Accept": "text/html,application/rss+xml"},
        follow_redirects=True,
    )
