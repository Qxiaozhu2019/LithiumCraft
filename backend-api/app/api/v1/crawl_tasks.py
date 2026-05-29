from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app.models.crawl_task import CrawlTask
from app.models.source import Source, SourceStatus
from app.schemas import CrawlTaskRead, Page
from app.services.crawl_runner import run_source_crawl

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("", response_model=Page[CrawlTaskRead])
def list_tasks(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)) -> Page[CrawlTaskRead]:
    query = db.query(CrawlTask)
    total = query.with_entities(func.count()).scalar() or 0
    items = query.order_by(CrawlTask.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=dict)
def trigger_crawl(source_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    task = run_source_crawl(db, source_id, task_type="manual_crawl")
    return {
        "task_id": task.id,
        "source_id": source_id,
        "status": task.status.value,
        "fetched_count": task.fetched_count,
        "inserted_count": task.inserted_count,
        "blocked_count": task.blocked_count,
        "message": "manual_crawl_finished",
    }


@router.post("/enabled", response_model=dict)
def trigger_enabled_sources_crawl(db: Session = Depends(get_db)) -> dict[str, object]:
    source_ids = [
        source_id
        for (source_id,) in db.query(Source.id)
        .filter(Source.status == SourceStatus.enabled)
        .order_by(Source.id)
        .all()
    ]
    results = []
    for source_id in source_ids:
        task = run_source_crawl(db, source_id, task_type="manual_enabled_sources_crawl")
        results.append(
            {
                "task_id": task.id,
                "source_id": source_id,
                "status": task.status.value,
                "fetched_count": task.fetched_count,
                "inserted_count": task.inserted_count,
                "blocked_count": task.blocked_count,
            }
        )
    return {
        "source_count": len(source_ids),
        "tasks": results,
        "message": "manual_enabled_sources_crawl_finished",
    }
