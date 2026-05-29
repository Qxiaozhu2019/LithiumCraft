from celery import Celery
from celery.schedules import crontab

from app.core.config import settings


def _get_redis_url() -> str:
    return getattr(settings, "redis_url", settings.REDIS_URL)


celery_app = Celery(
    "lithiumcraft",
    broker=_get_redis_url(),
    backend=_get_redis_url(),
    include=["app.tasks.crawl", "app.tasks.daily_brief"],
)

celery_app.conf.update(
    timezone="Asia/Shanghai",
    enable_utc=False,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_default_queue="lithiumcraft",
    beat_schedule={
        "crawl-enabled-sources-low-frequency": {
            "task": "app.tasks.crawl.crawl_enabled_sources",
            "schedule": crontab(hour=7, minute=0),
        },
        "generate-daily-brief-every-evening": {
            "task": "app.tasks.daily_brief.generate_daily_brief",
            "schedule": crontab(hour=7, minute=30),
        },
    },
)
