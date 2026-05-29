from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app.models.source import Source
from app.schemas import Page, SourceCreate, SourceRead, SourceUpdate
from app.services.text import domain_from_url

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("", response_model=Page[SourceRead])
def list_sources(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)) -> Page[SourceRead]:
    query = db.query(Source)
    total = query.with_entities(func.count()).scalar() or 0
    items = query.order_by(Source.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=SourceRead)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)) -> Source:
    source = Source(**payload.model_dump(mode="json"))
    if not source.domain:
        source.domain = domain_from_url(source.entry_url)
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.patch("/{source_id}", response_model=SourceRead)
def update_source(source_id: int, payload: SourceUpdate, db: Session = Depends(get_db)) -> Source:
    source = db.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="source_not_found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(source, key, value)
    db.commit()
    db.refresh(source)
    return source
