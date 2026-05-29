from collections import defaultdict
from datetime import date, datetime, time, timezone
import json

from sqlalchemy.orm import Session

from app.models.daily_brief import BriefStatus, DailyBrief
from app.models.intelligence import IntelligenceItem, IntelligenceStatus


def generate_daily_brief(db: Session, target_date: date | None = None) -> DailyBrief:
    target_date = target_date or date.today()
    start = datetime.combine(target_date, time.min).replace(tzinfo=timezone.utc)
    end = datetime.combine(target_date, time.max).replace(tzinfo=timezone.utc)
    items = db.query(IntelligenceItem).filter(
        IntelligenceItem.status == IntelligenceStatus.active,
        IntelligenceItem.crawled_at >= start,
        IntelligenceItem.crawled_at <= end,
    ).order_by(IntelligenceItem.importance_score.desc()).all()

    highlights = [{"id": item.id, "title": item.title, "score": item.importance_score} for item in items[:8]]
    grouped: dict[str, list[str]] = defaultdict(list)
    for item in items:
        grouped[item.category].append(item.title)
    category_summary = {key: value[:5] for key, value in grouped.items()}
    overview = f"今日新增 {len(items)} 条锂电投研情报。" if items else "今日暂无新增情报。"

    brief = db.query(DailyBrief).filter(DailyBrief.brief_date == target_date).first()
    if brief is None:
        brief = DailyBrief(brief_date=target_date, title=f"{target_date.isoformat()} 锂电投研摘要")
        db.add(brief)
    brief.overview = overview
    brief.highlights = json.dumps(highlights, ensure_ascii=False)
    brief.category_summary = json.dumps(category_summary, ensure_ascii=False)
    brief.status = BriefStatus.success
    brief.generated_at = datetime.now(timezone.utc)
    brief.error_message = None
    db.commit()
    db.refresh(brief)
    return brief
