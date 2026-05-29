from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app.models.daily_brief import DailyBrief
from app.schemas import DailyBriefRead, Page
from app.services.daily_brief import generate_daily_brief

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("", response_model=Page[DailyBriefRead])
def list_briefs(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)) -> Page[DailyBriefRead]:
    query = db.query(DailyBrief)
    total = query.with_entities(func.count()).scalar() or 0
    items = query.order_by(DailyBrief.brief_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.get("/{brief_date}", response_model=DailyBriefRead)
def get_brief(brief_date: date, db: Session = Depends(get_db)) -> DailyBrief:
    brief = db.query(DailyBrief).filter(DailyBrief.brief_date == brief_date).first()
    if brief is None:
        raise HTTPException(status_code=404, detail="daily_brief_not_found")
    return brief


@router.post("/generate", response_model=DailyBriefRead)
def generate_brief(target_date: date | None = None, db: Session = Depends(get_db)) -> DailyBrief:
    return generate_daily_brief(db, target_date)
