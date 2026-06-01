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
        for noisy in soup.select("script, style, noscript, header, nav, footer"):
            noisy.decompose()
        page_title = soup.select_one("h1")
        title = page_title.get_text(" ", strip=True) if page_title else fallback_title
        description = soup.select_one("meta[name='description']")
        summary = description.get("content", "").strip() if description else ""
        root = self._content_root(soup, page_title)
        root_text = root.get_text(" ", strip=True) if root else ""
        paragraphs = [p.get_text(" ", strip=True) for p in soup.select("p") if len(p.get_text(strip=True)) >= 20]
        content = self._clean_text(" ".join([summary, root_text, *paragraphs]))[:2000].strip() or title

        for image in soup.select("img[src]")[:5]:
            image_url = urljoin(str(response.url), image.get("src", ""))
            self.checker.can_fetch(source, image_url, purpose="image")
        return CrawledItem(title=title, url=url, content=content)

    def _content_root(self, soup: BeautifulSoup, title_node):
        for selector in ("article", "main", ".article", ".content", ".newsinfo", ".detail"):
            node = soup.select_one(selector)
            if node and len(node.get_text(" ", strip=True)) >= 80:
                return node
        node = title_node
        while node and node.parent and node.parent.name != "body":
            parent_text = node.parent.get_text(" ", strip=True)
            if 120 <= len(parent_text) <= 5000:
                return node.parent
            node = node.parent
        return soup.body or soup

    def _clean_text(self, text: str) -> str:
        stop_phrases = (
            "Helpful? Yes No",
            "Thanks for allowing us to contact you",
            "Please don’t include any personal information",
            "Submit Thanks for your feedback",
            "Previous Next",
        )
        cleaned = text
        for phrase in stop_phrases:
            cleaned = cleaned.replace(phrase, " ")
        return " ".join(cleaned.split())


class SinglePageCrawler:
    def __init__(self, checker: ComplianceChecker | None = None) -> None:
        self.checker = checker or ComplianceChecker()

    def crawl(self, source: Source) -> list[CrawledItem]:
        source_check = self.checker.validate_source(source)
        if not source_check.allowed:
            raise ValueError(source_check.reason)
        url_check = self.checker.can_fetch(source, source.entry_url, purpose="entry")
        if not url_check.allowed:
            raise ValueError(url_check.reason)
        with http_client() as client:
            return [GenericWebCrawler(self.checker)._fetch_detail(client, source, source.entry_url, source.name)]
