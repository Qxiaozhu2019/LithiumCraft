from typing import Any

from app.db.session import SessionLocal
from app.models.crawl_task import CrawlTask
from app.models.source import Source, SourceStatus
from app.services.crawl_runner import run_source_crawl
from app.tasks.celery_app import celery_app


def _serialize_crawl_task(task: CrawlTask) -> dict[str, Any]:
    return {
        "id": task.id,
        "source_id": task.source_id,
        "status": task.status.value,
        "fetched_count": task.fetched_count,
        "inserted_count": task.inserted_count,
        "blocked_count": task.blocked_count,
        "error_message": task.error_message,
        "duration_ms": task.duration_ms,
    }


@celery_app.task(name="app.tasks.crawl.crawl_source")
def crawl_source_task(source_id: int) -> dict[str, Any]:
    with SessionLocal() as db:
        task = run_source_crawl(db, source_id)
        return _serialize_crawl_task(task)


@celery_app.task(name="app.tasks.crawl.crawl_enabled_sources")
def crawl_enabled_sources_task() -> dict[str, Any]:
    with SessionLocal() as db:
        source_ids = [
            source_id
            for (source_id,) in db.query(Source.id)
            .filter(Source.status == SourceStatus.enabled)
            .order_by(Source.id)
            .all()
        ]

    results = []
    for source_id in source_ids:
        with SessionLocal() as db:
            task = run_source_crawl(db, source_id)
            results.append(_serialize_crawl_task(task))

    return {"source_count": len(source_ids), "tasks": results}
