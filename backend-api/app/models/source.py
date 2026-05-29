from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class SourceType(StrEnum):
    announcement = "announcement"
    policy = "policy"
    media = "media"
    paper = "paper"
    patent = "patent"
    rss = "rss"
    webpage = "webpage"


class SourceStatus(StrEnum):
    enabled = "enabled"
    disabled = "disabled"
    manual_only = "manual_only"
    blocked_by_policy = "blocked_by_policy"


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[SourceType] = mapped_column(Enum(SourceType), default=SourceType.rss)
    entry_url: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[SourceStatus] = mapped_column(Enum(SourceStatus), default=SourceStatus.disabled, index=True)
    crawl_interval_minutes: Mapped[int] = mapped_column(Integer, default=360)
    parser_key: Mapped[str] = mapped_column(String(100), default="generic")
    domain_delay_seconds: Mapped[int] = mapped_column(Integer, default=3)
    max_pages_per_run: Mapped[int] = mapped_column(Integer, default=20)
    daily_limit: Mapped[int] = mapped_column(Integer, default=100)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @property
    def enabled(self) -> bool:
        return self.status == SourceStatus.enabled
