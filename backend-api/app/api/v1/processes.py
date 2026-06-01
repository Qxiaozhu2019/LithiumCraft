from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.intelligence import IntelligenceItem
from app.schemas import ProcessStageDetail, ProcessStageRead
from app.services.process_stages import PROCESS_STAGES, get_process_stage, latest_crawled_at, process_stage_query

router = APIRouter()


@router.get("", response_model=list[ProcessStageRead])
def list_processes(db: Session = Depends(get_db)) -> list[ProcessStageRead]:
    stages: list[ProcessStageRead] = []
    for stage in PROCESS_STAGES:
        query = process_stage_query(db, stage)
        stages.append(
            ProcessStageRead(
                slug=stage.slug,
                name=stage.name,
                description=stage.description,
                keywords=list(stage.keywords),
                item_count=query.count(),
                latest_crawled_at=latest_crawled_at(query),
            )
        )
    return stages


@router.get("/{slug}", response_model=ProcessStageDetail)
def get_process(
    slug: str,
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ProcessStageDetail:
    stage = get_process_stage(slug)
    if stage is None:
        raise HTTPException(status_code=404, detail="process_stage_not_found")

    query = process_stage_query(db, stage)
    items = query.order_by(IntelligenceItem.crawled_at.desc()).limit(page_size).all()
    return ProcessStageDetail(
        slug=stage.slug,
        name=stage.name,
        description=stage.description,
        keywords=list(stage.keywords),
        item_count=query.count(),
        latest_crawled_at=latest_crawled_at(query),
        items=items,
    )
