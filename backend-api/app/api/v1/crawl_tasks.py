from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app.models.crawl_task import CrawlTask
from app.schemas import CrawlTaskRead, Page
from app.tasks.crawl import crawl_source_task

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("", response_model=Page[CrawlTaskRead])
def list_tasks(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)) -> Page[CrawlTaskRead]:
    query = db.query(CrawlTask)
    total = query.with_entities(func.count()).scalar() or 0
    items = query.order_by(CrawlTask.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=dict)
def trigger_crawl(source_id: int) -> dict[str, object]:
    task = crawl_source_task.delay(source_id)
    return {"task_id": task.id, "source_id": source_id, "message": "crawl_queued"}
