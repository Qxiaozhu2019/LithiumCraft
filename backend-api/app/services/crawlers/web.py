from urllib.parse import urljoin

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
        url_check = self.checker.can_fetch(source, source.entry_url, purpose="entry")
        if not url_check.allowed:
            raise ValueError(url_check.reason)
        self.checker.throttle(source, source.entry_url)
        with http_client() as client:
            response = client.get(source.entry_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            items: list[CrawledItem] = []
            for anchor in soup.select("a[href]")[: source.max_pages_per_run * 6]:
                title = anchor.get_text(" ", strip=True)
                href = anchor.get("href", "")
                if len(title) < 8 or href.startswith(("javascript:", "mailto:", "tel:")):
                    continue
                url = urljoin(str(response.url), href)
                detail_check = self.checker.can_fetch(source, url, purpose="detail")
                if not detail_check.allowed:
                    continue
                detail_item = self._fetch_detail(client, source, url, title)
                items.append(detail_item)
                if len(items) >= source.max_pages_per_run:
                    break
        return items

    def _fetch_detail(self, client, source: Source, url: str, fallback_title: str) -> CrawledItem:
        self.checker.throttle(source, url)
        response = client.get(url)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "html" not in content_type and "text" not in content_type:
            return CrawledItem(title=fallback_title, url=url, content=fallback_title)
        soup = BeautifulSoup(response.text, "lxml")
        page_title = soup.select_one("h1")
        title = page_title.get_text(" ", strip=True) if page_title else fallback_title
        description = soup.select_one("meta[name='description']")
        summary = description.get("content", "").strip() if description else ""
        paragraphs = [p.get_text(" ", strip=True) for p in soup.select("p") if len(p.get_text(strip=True)) >= 20]
        content = " ".join([summary, *paragraphs])[:2000].strip() or title

        for image in soup.select("img[src]")[:5]:
            image_url = urljoin(str(response.url), image.get("src", ""))
            self.checker.can_fetch(source, image_url, purpose="image")
        return CrawledItem(title=title, url=url, content=content)
