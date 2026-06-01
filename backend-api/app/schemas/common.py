from datetime import date, datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, HttpUrl

from app.models.crawl_task import TaskStatus
from app.models.daily_brief import BriefStatus
from app.models.intelligence import IntelligenceStatus
from app.models.source import SourceStatus, SourceType

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class SourceBase(BaseModel):
    name: str
    type: SourceType
    entry_url: HttpUrl
    domain: str
    status: SourceStatus = SourceStatus.disabled
    crawl_interval_minutes: int = 360
    parser_key: str = "generic"
    domain_delay_seconds: int = 3
    max_pages_per_run: int = 20
    daily_limit: int = 100
    notes: str = ""


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    name: str | None = None
    type: SourceType | None = None
    status: SourceStatus | None = None
    crawl_interval_minutes: int | None = None
    parser_key: str | None = None
    domain_delay_seconds: int | None = None
    max_pages_per_run: int | None = None
    daily_limit: int | None = None
    notes: str | None = None


class SourceRead(SourceBase):
    id: int
    failure_count: int
    last_success_at: datetime | None
    last_error: str | None
    model_config = ConfigDict(from_attributes=True)


class IntelligenceRead(BaseModel):
    id: int
    title: str
    summary: str
    content_excerpt: str
    source_url: str
    source_name: str
    source_published_at: datetime | None
    crawled_at: datetime
    category: str
    tags: str
    importance_score: float
    status: IntelligenceStatus
    block_reason: str | None
    model_config = ConfigDict(from_attributes=True)


class IntelligenceUpdate(BaseModel):
    title: str | None = None
    summary: str | None = None
    category: str | None = None
    tags: str | None = None
    status: IntelligenceStatus | None = None
    block_reason: str | None = None


class ProcessStageRead(BaseModel):
    slug: str
    name: str
    description: str
    keywords: list[str]
    item_count: int
    latest_crawled_at: datetime | None


class ProcessStageDetail(ProcessStageRead):
    items: list[IntelligenceRead]


class DailyBriefRead(BaseModel):
    id: int
    brief_date: date
    title: str
    overview: str
    highlights: str
    category_summary: str
    status: BriefStatus
    error_message: str | None
    generated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class CrawlTaskRead(BaseModel):
    id: int
    task_type: str
    source_id: int | None
    status: TaskStatus
    fetched_count: int
    inserted_count: int
    blocked_count: int
    error_message: str | None
    duration_ms: int
    started_at: datetime | None
    finished_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class CategoryRead(BaseModel):
    id: int
    name: str
    kind: str
    description: str
    model_config = ConfigDict(from_attributes=True)


class SettingRead(BaseModel):
    id: int
    key: str
    value: str
    description: str
    model_config = ConfigDict(from_attributes=True)


class SettingUpdate(BaseModel):
    value: str
