from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import optional_admin, require_admin
from app.db.session import get_db
from app.models.intelligence import IntelligenceItem, IntelligenceStatus
from app.schemas import IntelligenceRead, IntelligenceUpdate, Page

router = APIRouter()


@router.get("", response_model=Page[IntelligenceRead])
def list_intelligence(
    q: str | None = None,
    category: str | None = None,
    status: IntelligenceStatus | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: str | None = Depends(optional_admin),
    db: Session = Depends(get_db),
) -> Page[IntelligenceRead]:
    query = db.query(IntelligenceItem)
    if q:
        keyword = f"%{q}%"
        query = query.filter(IntelligenceItem.title.ilike(keyword) | IntelligenceItem.summary.ilike(keyword))
    if category:
        query = query.filter(IntelligenceItem.category == category)
    if date_from:
        query = query.filter(IntelligenceItem.crawled_at >= datetime.combine(date_from, time.min))
    if date_to:
        query = query.filter(IntelligenceItem.crawled_at <= datetime.combine(date_to, time.max))
    if admin is None:
        query = query.filter(IntelligenceItem.status == IntelligenceStatus.active)
    elif status:
        query = query.filter(IntelligenceItem.status == status)
    total = query.with_entities(func.count()).scalar() or 0
    items = query.order_by(IntelligenceItem.crawled_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=IntelligenceRead)
def get_intelligence(
    item_id: int,
    admin: str | None = Depends(optional_admin),
    db: Session = Depends(get_db),
) -> IntelligenceItem:
    item = db.get(IntelligenceItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="intelligence_not_found")
    if admin is None and item.status != IntelligenceStatus.active:
        raise HTTPException(status_code=404, detail="intelligence_not_found")
    return item


@router.patch("/{item_id}", response_model=IntelligenceRead)
def update_intelligence(
    item_id: int,
    payload: IntelligenceUpdate,
    _: str = Depends(require_admin),
    db: Session = Depends(get_db),
) -> IntelligenceItem:
    item = db.get(IntelligenceItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="intelligence_not_found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item
