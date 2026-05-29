from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.intelligence import IntelligenceItem, IntelligenceStatus
from app.models.source import Source, SourceStatus, SourceType


def test_public_readonly_endpoints_do_not_require_login() -> None:
    with TestClient(app) as client:
        assert client.get("/api/v1/intelligence").status_code == 200
        assert client.get("/api/v1/daily-briefs").status_code == 200
        assert client.get("/api/v1/categories").status_code == 200


def test_public_intelligence_detail_does_not_require_login() -> None:
    with TestClient(app) as client:
        with SessionLocal() as db:
            item = IntelligenceItem(
                title="锂电工艺公开情报",
                normalized_title="锂电工艺公开情报",
                summary="公开来源摘要",
                content_excerpt="公开来源摘要",
                source_url="https://example.com/public-intelligence-detail",
                source_name="测试公开来源",
                source_published_at=datetime.now(timezone.utc),
                category="行业快讯",
                tags="锂电",
                status=IntelligenceStatus.active,
            )
            db.add(item)
            db.commit()
            db.refresh(item)
            item_id = item.id

        response = client.get(f"/api/v1/intelligence/{item_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "锂电工艺公开情报"


def test_management_endpoints_still_require_login() -> None:
    with TestClient(app) as client:
        assert client.get("/api/v1/sources").status_code == 401
        assert client.get("/api/v1/settings").status_code == 401
        assert client.get("/api/v1/crawl-tasks").status_code == 401
        assert client.post("/api/v1/crawl-tasks", params={"source_id": 1}).status_code == 401
        assert client.post("/api/v1/crawl-tasks/enabled").status_code == 401
        assert client.post("/api/v1/daily-briefs/generate").status_code == 401
        assert client.patch("/api/v1/intelligence/1", json={"status": "archived"}).status_code == 401


def test_public_intelligence_only_exposes_active_items() -> None:
    with TestClient(app) as client:
        with SessionLocal() as db:
            active = IntelligenceItem(
                title="公开可见情报",
                normalized_title="公开可见情报",
                summary="公开摘要",
                content_excerpt="公开摘要",
                source_url="https://example.com/public-active-only",
                source_name="测试公开来源",
                source_published_at=datetime.now(timezone.utc),
                category="行业快讯",
                tags="锂电",
                status=IntelligenceStatus.active,
            )
            blocked = IntelligenceItem(
                title="公开隐藏情报",
                normalized_title="公开隐藏情报",
                summary="隐藏摘要",
                content_excerpt="隐藏摘要",
                source_url="https://example.com/public-blocked-hidden",
                source_name="测试公开来源",
                source_published_at=datetime.now(timezone.utc),
                category="行业快讯",
                tags="锂电",
                status=IntelligenceStatus.blocked,
                block_reason="policy",
            )
            db.add_all([active, blocked])
            db.commit()
            db.refresh(active)
            db.refresh(blocked)
            active_id = active.id
            blocked_id = blocked.id

        list_response = client.get("/api/v1/intelligence", params={"q": "公开"})
        blocked_detail_response = client.get(f"/api/v1/intelligence/{blocked_id}")
        active_detail_response = client.get(f"/api/v1/intelligence/{active_id}")

    assert list_response.status_code == 200
    titles = [item["title"] for item in list_response.json()["items"]]
    assert "公开可见情报" in titles
    assert "公开隐藏情报" not in titles
    assert blocked_detail_response.status_code == 404
    assert active_detail_response.status_code == 200


def test_manual_crawl_endpoint_runs_without_redis(monkeypatch) -> None:
    from app.services import crawl_runner
    from app.services.crawlers.base import CrawledItem

    monkeypatch.setattr(
        crawl_runner,
        "crawl_source",
        lambda source: [
                CrawledItem(
                    title="手动抓取公开情报唯一标题",
                    url="https://example.com/manual-crawl-item-unique",
                    content="手动抓取公开情报内容，包含足够长的正文用于通过发布检查。",
                )
        ],
    )

    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "ChangeMe123!"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        with SessionLocal() as db:
            source = Source(
                name="手动抓取测试来源",
                type=SourceType.webpage,
                entry_url="https://example.com/manual-crawl",
                domain="example.com",
                status=SourceStatus.manual_only,
            )
            db.add(source)
            db.commit()
            db.refresh(source)
            source_id = source.id

        response = client.post(
            "/api/v1/crawl-tasks",
            params={"source_id": source_id},
            headers=headers,
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "manual_crawl_finished"
    assert payload["status"] == "success"
    assert payload["fetched_count"] == 1
    assert payload["inserted_count"] + payload["blocked_count"] == 1
