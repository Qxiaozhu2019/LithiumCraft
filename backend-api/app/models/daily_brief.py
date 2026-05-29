from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Date, DateTime, Enum, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class BriefStatus(StrEnum):
    pending = "pending"
    success = "success"
    failed = "failed"


class DailyBrief(Base):
    __tablename__ = "daily_briefs"
    __table_args__ = (UniqueConstraint("brief_date", name="uq_daily_brief_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brief_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    overview: Mapped[str] = mapped_column(Text, default="")
    highlights: Mapped[str] = mapped_column(Text, default="[]")
    category_summary: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[BriefStatus] = mapped_column(Enum(BriefStatus), default=BriefStatus.pending)
    error_message: Mapped[str | None] = mapped_column(Text)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
