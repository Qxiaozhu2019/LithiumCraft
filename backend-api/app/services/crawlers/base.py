from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CrawledItem:
    title: str
    url: str
    content: str
    source_published_at: datetime | None = None
