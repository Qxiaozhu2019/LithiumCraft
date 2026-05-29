from datetime import datetime, timezone
from time import perf_counter

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.crawl_task import CrawlTask, TaskStatus
from app.models.intelligence import IntelligenceItem, IntelligenceStatus
from app.models.source import Source
from app.services.ai import AIAdapter
from app.services.crawlers import crawl_source
from app.services.publish import PublishGuard
from app.services.text import normalize_title


def run_source_crawl(db: Session, source_id: int) -> CrawlTask:
    source = db.get(Source, source_id)
    if source is None:
        raise ValueError("source_not_found")

    task = CrawlTask(source_id=source.id, status=TaskStatus.running, started_at=datetime.now(timezone.utc))
    db.add(task)
    db.commit()
    db.refresh(task)
    started = perf_counter()
    ai = AIAdapter()

    try:
        items = crawl_source(source)
        guard = PublishGuard(db)
        task.fetched_count = len(items)
        for item in items:
            analysis = ai.analyze(item.title, item.content)
            decision = guard.evaluate(title=item.title, content=item.content, source_url=item.url)
            record = IntelligenceItem(
                title=item.title,
                normalized_title=normalize_title(item.title),
                summary=analysis.summary,
                content_excerpt=item.content[:1000],
                source_url=item.url,
                source_name=source.name,
                source_id=source.id,
                source_published_at=item.source_published_at,
                category=analysis.category,
                tags=",".join(analysis.tags),
                importance_score=analysis.importance_score,
                status=IntelligenceStatus.active if decision.allowed else IntelligenceStatus.blocked,
                block_reason=decision.reason or None,
            )
            db.add(record)
            try:
                db.commit()
                if decision.allowed:
                    task.inserted_count += 1
                else:
                    task.blocked_count += 1
            except IntegrityError:
                db.rollback()
                task.blocked_count += 1
        source.last_success_at = datetime.now(timezone.utc)
        source.failure_count = 0
        source.last_error = None
        task.status = TaskStatus.success
    except Exception as exc:
        db.rollback()
        source.failure_count += 1
        source.last_error = str(exc)
        task.status = TaskStatus.failed
        task.error_message = str(exc)
    finally:
        task.finished_at = datetime.now(timezone.utc)
        task.duration_ms = int((perf_counter() - started) * 1000)
        db.add(task)
        db.add(source)
        db.commit()
        db.refresh(task)
    return task
