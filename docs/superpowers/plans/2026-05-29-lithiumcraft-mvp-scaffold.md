# LithiumCraft MVP Scaffold Implementation Plan

> **给 agentic workers：** 实施本计划时必须使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans`，并按任务逐项执行。步骤使用 checkbox（`- [ ]`）语法跟踪进度。

**Goal:** 搭建一个长期可维护、可运行的 LithiumCraft 单仓库项目骨架，包含项目规范、Nuxt 前台门户、Vue 管理后台、FastAPI API、Celery 抓取流水线、PostgreSQL/Redis 数据层和 Docker Compose 部署。

**Architecture:** 项目采用前后端分离、API-first 的单仓库架构。Nuxt 前台调用公开只读 API，Vue 管理后台调用带鉴权的管理 API，FastAPI 负责领域逻辑和数据库访问，Celery 通过 Redis 和 PostgreSQL 执行合规抓取、AI 处理和自动发布任务。

**Tech Stack:** Python 3.12、FastAPI、Pydantic、SQLAlchemy 2、Alembic、Celery、Redis、PostgreSQL、Nuxt 3、Vue 3、Vite、Element Plus、Docker Compose、Nginx。

---

## 文件结构

- `.gitignore`、`.env.example`、`README.md`：仓库基础、环境变量模板和快速启动说明。
- `Agent.md`：面向后续 Agent/维护者的项目级协作规则，包含文档语言规则。
- `docs/requirements.md`、`docs/architecture.md`、`docs/api.md`、`docs/data-model.md`、`docs/crawling-compliance.md`、`docs/development.md`、`docs/deployment.md`：产品与工程规范。
- `backend-api/app/core`：配置、安全、API 错误处理。
- `backend-api/app/db`：SQLAlchemy base/session/seed 和 Alembic 集成。
- `backend-api/app/models`：Source、Article、CrawlTask、Category、Tag、PublishRule、SystemLog。
- `backend-api/app/schemas`：Pydantic 请求/响应模型和分页包装模型。
- `backend-api/app/api/v1`：auth、articles、sources、crawl tasks、categories、publish rules。
- `backend-api/app/services`：AI 适配器、发布风控、抓取运行器、文本工具。
- `backend-api/app/services/crawlers`：合规检查器、RSS 抓取器、公开网页抓取器。
- `backend-api/app/tasks`：Celery 应用和抓取任务。
- `backend-api/tests`：models、API、auth、publish guard、compliance、tasks 的 pytest 测试。
- `frontend-web`：Nuxt 前台门户。
- `frontend-admin`：Vue/Vite 管理后台。
- `deploy`：Docker Compose、Nginx、备份脚本。

---

### Task 1: Foundation And Standards

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `README.md`
- Create: `docs/requirements.md`
- Create: `docs/architecture.md`
- Create: `docs/api.md`
- Create: `docs/data-model.md`
- Create: `docs/crawling-compliance.md`
- Create: `docs/development.md`
- Create: `docs/deployment.md`

- [ ] **Step 1: 创建仓库基础文件**

创建 `.gitignore`，忽略 Python 缓存、Node 构建产物、环境变量文件、日志、`.superpowers/`、Docker 本地卷目录、系统文件和编辑器目录。

创建 `.env.example`，包含以下配置：`API_PREFIX=/api/v1`、`NUXT_PUBLIC_API_BASE`、`VITE_API_BASE`、`DATABASE_URL`、PostgreSQL 账号密码、`REDIS_URL`、JWT 配置、管理员账号密码、抓取器 User-Agent、域名访问间隔、每日抓取上限和 AI provider 配置。

创建 `README.md`，内容包括：项目简介、单仓库服务说明、快速启动命令 `docker compose -f deploy/docker-compose.yml --env-file .env up --build`、前台/后台/API 文档访问地址，以及合规声明：LithiumCraft 只聚合公开合规来源，遵守 `robots.txt` 和限频规则，不绕过登录、付费墙、验证码、反爬限制或非公开 API。

- [ ] **Step 2: 创建规范文档**

创建以下文档，并按中文撰写说明内容：

- `docs/requirements.md`：产品定位、前台门户需求、管理后台需求、自动发布机制、一期范围边界。
- `docs/architecture.md`：系统拓扑、数据流、任务流、部署拓扑。
- `docs/api.md`：`/api/v1` 版本策略、Bearer JWT 管理接口鉴权、公开只读接口、分页格式 `{items,total,page,page_size}`、错误格式 `{code,message,details}`。
- `docs/data-model.md`：状态值 `published|blocked|removed`、`public_allowed|rss_api|manual_only|disabled`、`pending|running|success|failed|skipped`，以及核心实体字段定义。
- `docs/crawling-compliance.md`：允许抓取的来源、禁止行为、robots 策略、限频规则、展示与版权边界。
- `docs/development.md`：本地开发流程、代码规范、测试命令、新增数据源流程、提交信息风格。
- `docs/deployment.md`：阿里云 ECS、Docker Compose、Nginx、HTTPS、备份、日志和恢复检查。

- [ ] **Step 3: 提交基础规范**

运行：

```bash
git add Agent.md .gitignore .env.example README.md docs
git commit -m "docs: define LithiumCraft project standards"
```

预期结果：生成一个只包含基础文件和规范文档的提交。

---

### Task 2: Backend Models And Schemas

**Files:**
- Create: `backend-api/pyproject.toml`
- Create: `backend-api/Dockerfile`
- Create: `backend-api/app/db/base.py`
- Create: `backend-api/app/db/session.py`
- Create: `backend-api/app/models/source.py`
- Create: `backend-api/app/models/article.py`
- Create: `backend-api/app/models/category.py`
- Create: `backend-api/app/models/crawl_task.py`
- Create: `backend-api/app/models/publish_rule.py`
- Create: `backend-api/app/models/system_log.py`
- Create: `backend-api/app/schemas/common.py`
- Create: `backend-api/tests/conftest.py`
- Create: `backend-api/tests/test_models.py`

- [ ] **Step 1: 编写失败的模型测试**

创建 `backend-api/tests/test_models.py`：

```python
from app.models.article import Article, ArticleStatus
from app.models.source import ComplianceStatus, Source, SourceType


def test_model_defaults_are_stable():
    source = Source(name="Demo RSS", type=SourceType.rss, entry_url="https://example.com/feed.xml", domain="example.com")
    article = Article(title="锂电设备更新", normalized_title="锂电设备更新", source_url="https://example.com/a", source_name="Demo RSS")
    assert source.compliance_status == ComplianceStatus.public_allowed
    assert source.enabled is True
    assert article.status == ArticleStatus.published
```

- [ ] **Step 2: 运行测试并确认失败**

运行：`cd backend-api && python -m pytest tests/test_models.py -q`

预期结果：测试失败，因为后端包和模型尚未创建。

- [ ] **Step 3: 实现模型和 Schema**

创建 `backend-api/pyproject.toml`，包含 FastAPI、SQLAlchemy、psycopg、Alembic、pydantic-settings、python-jose、passlib、Celery、Redis、httpx、beautifulsoup4、lxml、feedparser、rapidfuzz、structlog、pytest、ruff 等依赖，并要求 Python `>=3.12`。

创建 `backend-api/app/db/base.py`，定义 SQLAlchemy `DeclarativeBase`。创建 Source 枚举 `SourceType(rss,sitemap,webpage,api,manual)` 和 `ComplianceStatus(public_allowed,rss_api,manual_only,disabled)`。创建 Article 枚举 `ArticleStatus(published,blocked,removed)`。所有模型字段按 `docs/data-model.md` 中定义实现。

创建 `backend-api/app/schemas/common.py`，包含 Source create/update/read、Article read/update、Category read、PublishRule read/update、CrawlTask read 和分页列表响应模型。

- [ ] **Step 4: 运行测试并提交**

运行：`cd backend-api && python -m pytest tests/test_models.py -q`

预期结果：测试通过。

提交：

```bash
git add backend-api
git commit -m "feat(api): add backend domain models"
```

---

### Task 3: FastAPI Routes And Admin Auth

**Files:**
- Create: `backend-api/app/main.py`
- Create: `backend-api/app/core/config.py`
- Create: `backend-api/app/core/security.py`
- Create: `backend-api/app/api/v1/router.py`
- Create: `backend-api/app/api/v1/auth.py`
- Create: `backend-api/app/api/v1/articles.py`
- Create: `backend-api/app/api/v1/sources.py`
- Create: `backend-api/app/api/v1/crawl_tasks.py`
- Create: `backend-api/app/api/v1/categories.py`
- Create: `backend-api/app/api/v1/publish_rules.py`
- Create: `backend-api/tests/test_api.py`

- [ ] **Step 1: 编写失败的 API 测试**

创建 `backend-api/tests/test_api.py`：

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_article_list_shape():
    response = client.get("/api/v1/articles?page=1&page_size=10")
    assert response.status_code == 200
    assert set(response.json()) == {"items", "total", "page", "page_size"}


def test_admin_requires_auth():
    response = client.get("/api/v1/sources")
    assert response.status_code == 401
```

- [ ] **Step 2: 实现 API 应用**

创建配置模块、数据库 session、FastAPI app、CORS、`/health` 和 `/api/v1` router。实现 `/auth/login`，使用环境变量 `ADMIN_USERNAME` 和 `ADMIN_PASSWORD` 校验登录，返回 `{access_token, token_type}`。管理接口和写操作接口使用 Bearer JWT 鉴权。公开接口为 `GET /articles`、`GET /articles/{id}` 和 `GET /categories`。

- [ ] **Step 3: 运行测试并提交**

运行：`cd backend-api && python -m pytest tests/test_api.py -q`

预期结果：测试通过。

提交：

```bash
git add backend-api/app backend-api/tests
git commit -m "feat(api): add versioned API and admin auth"
```

---

### Task 4: Compliance Crawler And Auto Publish Pipeline

**Files:**
- Create: `backend-api/app/services/text.py`
- Create: `backend-api/app/services/ai.py`
- Create: `backend-api/app/services/publish.py`
- Create: `backend-api/app/services/crawlers/base.py`
- Create: `backend-api/app/services/crawlers/compliance.py`
- Create: `backend-api/app/services/crawlers/rss.py`
- Create: `backend-api/app/services/crawlers/web.py`
- Create: `backend-api/app/services/crawl_runner.py`
- Create: `backend-api/tests/test_publish_guard.py`
- Create: `backend-api/tests/test_compliance.py`

- [ ] **Step 1: 编写失败的流水线测试**

创建 `test_publish_guard.py`，验证：低于默认最小长度的内容会以 `content_too_short` 阻断；缺少来源 URL 会以 `missing_source_url` 阻断；normalized title 重复会以 `duplicate_title` 阻断。

创建 `test_compliance.py`，验证：`disabled` 和 `manual_only` 来源会被阻断；`public_allowed` 来源能通过 `validate_source`。

- [ ] **Step 2: 实现服务层**

实现以下函数和类：

- `normalize_title(title: str) -> str`
- `domain_from_url(url: str) -> str`
- `AIAdapter.analyze(title, content)`：返回确定性的摘要、标签、分类和重要性评分。
- `PublishGuard.evaluate(...)`：返回 `PublishDecision(allowed: bool, reason: str)`。
- `ComplianceChecker.validate_source`、`can_fetch`、`throttle`：使用 `urllib.robotparser` 和每域名访问时间记录。
- `RssCrawler`：使用 `feedparser` 解析 RSS。
- `GenericWebCrawler`：使用 `httpx` 和 BeautifulSoup 解析公开 HTML 链接。
- `run_source_crawl(db, source_id)`：创建 `CrawlTask`，将 `Article` 保存为 `published` 或 `blocked`，并记录抓取数量、入库数量、阻断数量和错误信息。

- [ ] **Step 3: 运行测试并提交**

运行：`cd backend-api && python -m pytest tests/test_publish_guard.py tests/test_compliance.py -q`

预期结果：测试通过。

提交：

```bash
git add backend-api/app/services backend-api/tests
git commit -m "feat(crawler): add compliant auto publish pipeline"
```

---

### Task 5: Celery Worker And Scheduled Crawl Jobs

**Files:**
- Create: `backend-api/app/tasks/celery_app.py`
- Create: `backend-api/app/tasks/crawl.py`
- Create: `backend-api/tests/test_tasks.py`

- [ ] **Step 1: 编写失败的任务注册测试**

创建 `backend-api/tests/test_tasks.py`：

```python
from app.tasks.celery_app import celery_app


def test_crawl_task_is_registered():
    assert "app.tasks.crawl.crawl_source_task" in celery_app.tasks
```

- [ ] **Step 2: 实现 Celery**

创建 Celery app，使用 `REDIS_URL`，时区为 `Asia/Shanghai`，beat 每 15 分钟调度一次启用来源抓取任务。实现 `crawl_source_task(source_id: int)` 和 `crawl_enabled_sources_task()`。

- [ ] **Step 3: 运行测试并提交**

运行：`cd backend-api && python -m pytest tests/test_tasks.py -q`

预期结果：测试通过。

提交：

```bash
git add backend-api/app/tasks backend-api/tests/test_tasks.py
git commit -m "feat(worker): add scheduled crawl tasks"
```

---

### Task 6: Nuxt Public Portal

**Files:**
- Create: `frontend-web/package.json`
- Create: `frontend-web/nuxt.config.ts`
- Create: `frontend-web/app.vue`
- Create: `frontend-web/assets/css/main.css`
- Create: `frontend-web/composables/useApi.ts`
- Create: `frontend-web/pages/index.vue`
- Create: `frontend-web/pages/articles/index.vue`
- Create: `frontend-web/pages/articles/[id].vue`

- [ ] **Step 1: 创建 Nuxt 应用文件**

创建 package scripts：`dev`、`build`、`preview`；配置 `NUXT_PUBLIC_API_BASE`；创建 `useApi<T>(path, query)` composable。

- [ ] **Step 2: 创建前台页面**

首页展示 hero、分类卡片、最新资讯和合规说明。资讯列表支持 `q`、`category`、`page`、`page_size`。详情页展示标题、摘要、标签、分类、来源名称、原文链接、发布时间和抓取时间。

- [ ] **Step 3: 构建并提交**

运行：

```bash
cd frontend-web
npm install
npm run build
```

预期结果：Nuxt 构建成功。

提交：

```bash
git add frontend-web
git commit -m "feat(web): add Nuxt public portal"
```

---

### Task 7: Vue Admin Console

**Files:**
- Create: `frontend-admin/package.json`
- Create: `frontend-admin/vite.config.ts`
- Create: `frontend-admin/index.html`
- Create: `frontend-admin/src/main.ts`
- Create: `frontend-admin/src/api/client.ts`
- Create: `frontend-admin/src/router/index.ts`
- Create: `frontend-admin/src/views/LoginView.vue`
- Create: `frontend-admin/src/views/DashboardView.vue`
- Create: `frontend-admin/src/views/SourcesView.vue`
- Create: `frontend-admin/src/views/ArticlesView.vue`
- Create: `frontend-admin/src/views/TasksView.vue`
- Create: `frontend-admin/src/views/RulesView.vue`

- [ ] **Step 1: 创建 Vue 管理后台应用**

创建 Vite Vue package，引入 Element Plus 和 Vue Router。创建 API client，使用 `VITE_API_BASE`，并从 localStorage 的 `lithiumcraft_admin_token` 读取 token，设置 `Authorization: Bearer <token>`。

- [ ] **Step 2: 创建后台页面**

Login 页面调用 `/auth/login`。Dashboard 链接到 Sources、Articles、Tasks、Rules。Sources 页面展示来源并支持创建/禁用来源。Articles 页面展示 published/blocked/removed 内容，并支持 PATCH 状态为 `removed`。Tasks 页面展示抓取日志并支持触发抓取。Rules 页面编辑发布规则字段。

- [ ] **Step 3: 构建并提交**

运行：

```bash
cd frontend-admin
npm install
npm run build
```

预期结果：Vite 构建成功。

提交：

```bash
git add frontend-admin
git commit -m "feat(admin): add Vue admin console"
```

---

### Task 8: Deployment, Seeds, Verification, Push

**Files:**
- Create: `backend-api/Dockerfile`
- Create: `frontend-web/Dockerfile`
- Create: `frontend-admin/Dockerfile`
- Create: `deploy/docker-compose.yml`
- Create: `deploy/nginx/default.conf`
- Create: `deploy/scripts/backup-postgres.sh`
- Create: `backend-api/app/db/seed.py`

- [ ] **Step 1: 添加 Docker 部署配置**

创建 backend、Nuxt、admin 的 Dockerfile。创建 Compose services：`postgres`、`redis`、`api`、`worker`、`beat`、`web`、`admin`、`nginx`；使用 named volumes，并暴露本地端口 `3000`、`3001`、`8000`、`8080`。

创建 `deploy/nginx/default.conf`，将 `/api/` 转发到 API，`/admin/` 转发到 admin，`/` 转发到 web。

创建 `backup-postgres.sh`，从 postgres service 执行 `pg_dump`，输出到 `backups/lithiumcraft-YYYYmmdd-HHMMSS.sql`。

- [ ] **Step 2: 添加种子数据**

创建 seed script，插入默认分类、一个默认发布规则和一个 disabled demo source。demo source 必须为 disabled，确保第一次启动全栈时不会自动抓取外部网站。

- [ ] **Step 3: 验证**

运行：

```bash
cd backend-api
python -m pytest -q
cd ..
cp .env.example .env
docker compose -f deploy/docker-compose.yml --env-file .env up --build
```

预期结果：

- `http://localhost:8000/health` 返回 `{"status":"ok"}`。
- `http://localhost:8000/docs` 打开 OpenAPI 文档。
- `http://localhost:3000` 打开前台门户。
- `http://localhost:3001` 打开后台登录页。
- Docker 重启后 PostgreSQL 数据通过 named volume 保留。

- [ ] **Step 4: 提交并推送**

运行：

```bash
git add .
git commit -m "chore: wire runnable LithiumCraft MVP skeleton"
git push -u origin main
```

预期结果：代码推送到 `https://github.com/Qxiaozhu2019/LithiumCraft.git`，使用仅针对 GitHub 的 SOCKS 代理配置。

---

## Self-Review

- 需求覆盖：本计划覆盖文档规范、前后端分离、FastAPI API、后台鉴权、Celery 任务、合规抓取、自动发布、PostgreSQL/Redis、Docker Compose、测试和 GitHub 推送。
- 占位扫描：没有未落地的需求占位；状态值、接口、文件、命令和预期结果均已明确。
- 类型一致性：Article 状态为 `published`、`blocked`、`removed`；Source 合规状态为 `public_allowed`、`rss_api`、`manual_only`、`disabled`；API 前缀为 `/api/v1`；后台鉴权为 Bearer JWT。
