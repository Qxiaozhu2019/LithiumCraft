from app.core.config import settings
from app.tasks import celery_app


def test_celery_app_uses_redis_and_shanghai_timezone() -> None:
    assert celery_app.conf.broker_url == settings.REDIS_URL
    assert celery_app.conf.result_backend == settings.REDIS_URL
    assert celery_app.conf.timezone == "Asia/Shanghai"


def test_celery_tasks_are_registered() -> None:
    assert "app.tasks.crawl.crawl_source" in celery_app.tasks
    assert "app.tasks.crawl.crawl_enabled_sources" in celery_app.tasks
    assert "app.tasks.daily_brief.generate_daily_brief" in celery_app.tasks


def test_beat_schedule_contains_crawl_and_daily_brief_tasks() -> None:
    schedule = celery_app.conf.beat_schedule

    assert schedule["crawl-enabled-sources-low-frequency"]["task"] == (
        "app.tasks.crawl.crawl_enabled_sources"
    )
    assert schedule["generate-daily-brief-every-evening"]["task"] == (
        "app.tasks.daily_brief.generate_daily_brief"
    )
