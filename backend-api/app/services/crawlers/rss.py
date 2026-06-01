from datetime import datetime

import feedparser

from app.models.source import Source
from app.services.crawlers.base import CrawledItem
from app.services.crawlers.compliance import ComplianceChecker, http_client


class RssCrawler:
    def __init__(self, checker: ComplianceChecker | None = None) -> None:
        self.checker = checker or ComplianceChecker()

    def crawl(self, source: Source) -> list[CrawledItem]:
        source_check = self.checker.validate_source(source)
        if not source_check.allowed:
            raise ValueError(source_check.reason)
        url_check = self.checker.can_fetch(source, source.entry_url, purpose="entry")
        if not url_check.allowed:
            raise ValueError(url_check.reason)
        self.checker.throttle(source, source.entry_url)
        with http_client() as client:
            response = client.get(source.entry_url)
            response.raise_for_status()
        feed = feedparser.parse(response.text)
        items: list[CrawledItem] = []
        for entry in feed.entries[: source.max_pages_per_run * 2]:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            content = getattr(entry, "summary", "") or getattr(entry, "description", "") or title
            published_at = datetime(*entry.published_parsed[:6]) if getattr(entry, "published_parsed", None) else None
            if not title or not link:
                continue
            detail_check = self.checker.can_fetch(source, link, purpose="detail")
            if not detail_check.allowed:
                continue
            items.append(CrawledItem(title=title, url=link, content=content, source_published_at=published_at))
            if len(items) >= source.max_pages_per_run:
                break
        return items
