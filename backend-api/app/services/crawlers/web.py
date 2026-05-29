from bs4 import BeautifulSoup

from app.models.source import Source
from app.services.crawlers.base import CrawledItem
from app.services.crawlers.compliance import ComplianceChecker, http_client


class GenericWebCrawler:
    def __init__(self, checker: ComplianceChecker | None = None) -> None:
        self.checker = checker or ComplianceChecker()

    def crawl(self, source: Source) -> list[CrawledItem]:
        source_check = self.checker.validate_source(source)
        if not source_check.allowed:
            raise ValueError(source_check.reason)
        url_check = self.checker.can_fetch(source, source.entry_url)
        if not url_check.allowed:
            raise ValueError(url_check.reason)
        self.checker.throttle(source)
        with http_client() as client:
            response = client.get(source.entry_url)
            response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        items: list[CrawledItem] = []
        for anchor in soup.select("a[href]")[: source.max_pages_per_run * 4]:
            title = anchor.get_text(" ", strip=True)
            href = anchor.get("href", "")
            if len(title) < 8 or href.startswith("javascript:"):
                continue
            url = str(response.url.join(href)) if hasattr(response.url, "join") else href
            items.append(CrawledItem(title=title, url=url, content=title))
            if len(items) >= source.max_pages_per_run:
                break
        return items
