from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.intelligence import IntelligenceItem, IntelligenceStatus
from app.models.source import Source, SourceStatus, SourceType


def test_public_readonly_endpoints_do_not_require_login() -> None:
    with TestClient(app) as client:
        assert client.get("/api/v1/intelligence").status_code == 200
        assert client.get("/api/v1/processes").status_code == 200
        assert client.get("/api/v1/topics").status_code == 200
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


def test_process_stage_api_matches_crawled_content() -> None:
    with TestClient(app) as client:
        with SessionLocal() as db:
            source = Source(
                name="公开工艺来源",
                type=SourceType.webpage,
                entry_url="https://example.com/process-source",
                domain="example.com",
                status=SourceStatus.manual_only,
            )
            db.add(source)
            db.commit()
            db.refresh(source)
            item = IntelligenceItem(
                title="涂布厚度一致性控制公开资料",
                normalized_title="涂布厚度一致性控制公开资料",
                summary="极片涂布面密度与干燥窗口说明",
                content_excerpt="涂布工艺关注浆料流变、干燥温度和极片厚度。",
                source_url="https://example.com/process-coating",
                source_name="公开工艺来源",
                source_id=source.id,
                source_published_at=datetime.now(timezone.utc),
                category="制造工艺",
                tags="涂布,极片,干燥",
                status=IntelligenceStatus.active,
            )
            db.add(item)
            db.commit()

        list_response = client.get("/api/v1/processes")
        detail_response = client.get("/api/v1/processes/coating")

    assert list_response.status_code == 200
    coating = next(stage for stage in list_response.json() if stage["slug"] == "coating")
    assert coating["item_count"] >= 1
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["name"] == "涂布"
    assert detail["diagram_steps"]
    assert detail["images"][0]["is_local"] is True
    assert detail["source_count"] >= 1
    assert any("涂布厚度" in item["title"] for item in detail["items"])


def test_topic_api_matches_material_content() -> None:
    with TestClient(app) as client:
        with SessionLocal() as db:
            source = Source(
                name="material public source",
                type=SourceType.webpage,
                entry_url="https://example.com/material-source",
                domain="example.com",
                status=SourceStatus.manual_only,
            )
            db.add(source)
            db.commit()
            db.refresh(source)
            item = IntelligenceItem(
                title="LFP cathode material calendering reference",
                normalized_title="LFP cathode material calendering reference",
                summary="LFP cathode material affects slurry dispersion, coating loading, and calendering window.",
                content_excerpt="Cathode material particle morphology, capacity, and thermal stability affect cell manufacturing.",
                source_url="https://example.com/material-cathode",
                source_name="material public source",
                source_id=source.id,
                source_published_at=datetime.now(timezone.utc),
                category="manufacturing process",
                tags="cathode,LFP,calendering",
                status=IntelligenceStatus.active,
            )
            db.add(item)
            db.commit()

        list_response = client.get("/api/v1/topics")
        detail_response = client.get("/api/v1/topics/cathode-materials")

    assert list_response.status_code == 200
    cathode = next(topic for topic in list_response.json() if topic["slug"] == "cathode-materials")
    assert cathode["item_count"] >= 1
    assert "calendering" in cathode["related_process_slugs"]
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["slug"] == "cathode-materials"
    assert detail["source_count"] >= 1
    assert any(item["source_url"] == "https://example.com/material-cathode" for item in detail["items"])


def test_topic_detail_returns_404_for_unknown_slug() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/topics/not-found")

    assert response.status_code == 404
    assert response.json()["detail"] == "topic_not_found"


def test_public_search_includes_excerpt_and_tags() -> None:
    with TestClient(app) as client:
        with SessionLocal() as db:
            item = IntelligenceItem(
                title="公开制造资料",
                normalized_title="公开制造资料",
                summary="常规公开摘要",
                content_excerpt="化成分容阶段需要关注容量分档和内阻一致性。",
                source_url="https://example.com/search-process-excerpt",
                source_name="公开工艺来源",
                source_published_at=datetime.now(timezone.utc),
                category="制造工艺",
                tags="化成,分容",
                status=IntelligenceStatus.active,
            )
            db.add(item)
            db.commit()

        response = client.get("/api/v1/intelligence", params={"q": "化成分容"})

    assert response.status_code == 200
    assert any(item["source_url"] == "https://example.com/search-process-excerpt" for item in response.json()["items"])


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


def test_crawl_runner_only_publishes_process_related_items(monkeypatch) -> None:
    from app.services import crawl_runner
    from app.services.crawlers.base import CrawledItem

    monkeypatch.setattr(
        crawl_runner,
        "crawl_source",
        lambda source: [
            CrawledItem(
                title="企业融资普通新闻",
                url="https://example.com/non-process-news",
                content="这是一条企业融资新闻，不包含电芯制造工序资料。",
            ),
            CrawledItem(
                title="涂布干燥窗口控制公开资料",
                url="https://example.com/process-coating-only",
                content="锂电池极片涂布工艺关注面密度、干燥窗口、厚度一致性和缺陷控制，适合归入制造工艺资料。",
            ),
        ],
    )

    with TestClient(app):
        with SessionLocal() as db:
            source = Source(
                name="工艺过滤测试来源",
                type=SourceType.webpage,
                entry_url="https://example.com/process-filter",
                domain="example.com",
                status=SourceStatus.manual_only,
            )
            db.add(source)
            db.commit()
            db.refresh(source)

            task = crawl_runner.run_source_crawl(db, source.id, task_type="manual_crawl")

            assert task.fetched_count == 2
            assert task.inserted_count == 1
            assert task.blocked_count == 1
            assert (
                db.query(IntelligenceItem)
                .filter(IntelligenceItem.source_url == "https://example.com/non-process-news")
                .first()
                is None
            )




def test_known_process_materials_are_translated_before_insert(monkeypatch) -> None:
    from app.services import crawl_runner
    from app.services.crawlers.base import CrawledItem

    monkeypatch.setattr(
        crawl_runner,
        "crawl_source",
        lambda source: [
            CrawledItem(
                title="Coating",
                url="https://example.com/translated-coating",
                content="The process of uniformly applying slurry onto the current collector for lithium-ion battery electrodes.",
            )
        ],
    )

    with TestClient(app):
        with SessionLocal() as db:
            source = Source(
                name="translation test source",
                type=SourceType.webpage,
                entry_url="https://example.com/translated-coating-source",
                domain="example.com",
                status=SourceStatus.manual_only,
            )
            db.add(source)
            db.commit()
            db.refresh(source)

            task = crawl_runner.run_source_crawl(db, source.id, task_type="manual_crawl")
            item = (
                db.query(IntelligenceItem)
                .filter(IntelligenceItem.source_url == "https://example.com/translated-coating")
                .first()
            )

            assert task.inserted_count == 1
            assert item is not None
            assert item.title == "\u6d82\u5e03"
            assert "\u96c6\u6d41\u4f53" in item.summary
            assert "coating" not in item.summary.lower()

def test_single_page_crawler_respects_robots_and_extracts_detail(monkeypatch) -> None:
    from app.services.crawlers.compliance import ComplianceResult
    from app.services.crawlers.web import SinglePageCrawler

    class FakeChecker:
        def validate_source(self, source: Source) -> ComplianceResult:
            return ComplianceResult(True)

        def can_fetch(self, source: Source, url: str, purpose: str = "page") -> ComplianceResult:
            return ComplianceResult(True)

        def throttle(self, source: Source, url: str | None = None) -> None:
            return None

    class FakeResponse:
        url = "https://example.com/process-page"
        headers = {"content-type": "text/html"}
        text = """
        <html><head><meta name="description" content="Battery coating process summary"></head>
        <body><h1>Coating manufacturing process</h1><p>Lithium-ion battery electrode coating controls thickness and drying.</p></body></html>
        """

        def raise_for_status(self) -> None:
            return None

    class FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def get(self, url: str):
            return FakeResponse()

    monkeypatch.setattr("app.services.crawlers.web.http_client", lambda: FakeClient())

    source = Source(
        name="single page",
        type=SourceType.webpage,
        entry_url="https://example.com/process-page",
        domain="example.com",
        status=SourceStatus.manual_only,
        parser_key="single_page",
    )
    items = SinglePageCrawler(FakeChecker()).crawl(source)

    assert len(items) == 1
    assert items[0].title == "Coating manufacturing process"
    assert "Lithium-ion battery electrode coating" in items[0].content

def test_robots_disallow_marks_source_blocked_by_policy(monkeypatch) -> None:
    from app.services import crawl_runner

    def raise_robots_disallow(source: Source) -> list[object]:
        raise ValueError("robots_disallow")

    monkeypatch.setattr(crawl_runner, "crawl_source", raise_robots_disallow)

    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "ChangeMe123!"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        with SessionLocal() as db:
            source = Source(
                name="robots 禁止测试来源",
                type=SourceType.webpage,
                entry_url="https://example.com/robots-disallow",
                domain="example.com",
                status=SourceStatus.enabled,
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

        with SessionLocal() as db:
            updated = db.get(Source, source_id)
            assert updated is not None
            assert updated.status == SourceStatus.blocked_by_policy
            assert updated.last_error == "robots_disallow"

    assert response.status_code == 200
    assert response.json()["status"] == "failed"
