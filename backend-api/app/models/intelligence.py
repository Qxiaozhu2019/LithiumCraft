from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class IntelligenceStatus(StrEnum):
    active = "active"
    blocked = "blocked"
    archived = "archived"


class IntelligenceItem(Base):
    __tablename__ = "intelligence_items"
    __table_args__ = (UniqueConstraint("source_url", name="uq_intelligence_source_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    normalized_title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    content_excerpt: Mapped[str] = mapped_column(Text, default="")
    source_url: Mapped[str] = mapped_column(String(1200), nullable=False)
    source_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"))
    source_published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    crawled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    category: Mapped[str] = mapped_column(String(120), default="行业快讯", index=True)
    tags: Mapped[str] = mapped_column(String(500), default="")
    importance_score: Mapped[float] = mapped_column(Float, default=0.5)
    status: Mapped[IntelligenceStatus] = mapped_column(Enum(IntelligenceStatus), default=IntelligenceStatus.active, index=True)
    block_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
