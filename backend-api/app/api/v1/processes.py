from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.intelligence import IntelligenceItem
from app.schemas import ProcessImageRead, ProcessStageDetail, ProcessStageRead
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
                diagram_steps=list(stage.diagram_steps),
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
        diagram_steps=list(stage.diagram_steps),
        item_count=query.count(),
        latest_crawled_at=latest_crawled_at(query),
        items=items,
        images=[
            ProcessImageRead(
                title=f"{stage.name}工艺示意图",
                alt=f"{stage.name}工序站内原创流程示意图",
                image_url=f"local://process-diagram/{stage.slug}",
                source_name="LithiumCraft 站内示意图",
                is_local=True,
            )
        ],
        source_count=len({item.source_id for item in items if item.source_id is not None}),
    )
