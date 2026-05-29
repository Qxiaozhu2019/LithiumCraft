from app.models.source import Source, SourceType
from app.services.crawlers.base import CrawledItem
from app.services.crawlers.rss import RssCrawler
from app.services.crawlers.web import GenericWebCrawler


def crawl_source(source: Source) -> list[CrawledItem]:
    if source.type == SourceType.rss:
        return RssCrawler().crawl(source)
    return GenericWebCrawler().crawl(source)
