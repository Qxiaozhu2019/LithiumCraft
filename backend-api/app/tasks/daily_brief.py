from datetime import date
from typing import Any

from app.db.session import SessionLocal
from app.models.daily_brief import DailyBrief
from app.services.daily_brief import generate_daily_brief
from app.tasks.celery_app import celery_app


def _serialize_daily_brief(brief: DailyBrief) -> dict[str, Any]:
    return {
        "id": brief.id,
        "brief_date": brief.brief_date.isoformat(),
        "title": brief.title,
        "status": brief.status.value,
        "generated_at": brief.generated_at.isoformat() if brief.generated_at else None,
    }


@celery_app.task(name="app.tasks.daily_brief.generate_daily_brief")
def generate_daily_brief_task(target_date: str | None = None) -> dict[str, Any]:
    parsed_date = date.fromisoformat(target_date) if target_date else None
    with SessionLocal() as db:
        brief = generate_daily_brief(db, parsed_date)
        return _serialize_daily_brief(brief)
