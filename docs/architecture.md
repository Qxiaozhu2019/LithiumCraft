# Architecture

## 总览

LithiumCraft 是单仓库、前后端分离、单机 Docker Compose 部署的锂电池工艺情报工作台。浏览器访问 Vue 前台首页和管理工作台；前端通过相对路径 `/api/v1` 调用 FastAPI；Nginx 在部署环境中作为统一入口，把 `/api/`、`/health`、`/docs` 转发到后端，把其他路径转发到前端静态站点。

后端使用 FastAPI、SQLAlchemy 2 和 Pydantic Settings。业务数据的生产默认数据库是 PostgreSQL 16；Redis 不是业务数据库，只作为 Celery 的 broker/result backend。API 启动时通过 SQLAlchemy `Base.metadata.create_all()` 创建表，并执行默认分类、系统设置和候选来源 seed；当前没有独立迁移流程。

## 技术栈

- 前端：Vue 3、Vue Router、TypeScript、Vite、Element Plus。
- 后端：Python 3.12、FastAPI、SQLAlchemy 2、Pydantic Settings、python-jose JWT、Uvicorn。
- 抓取与处理：httpx、BeautifulSoup、lxml、feedparser、rapidfuzz、合规检查、AI stub 摘要/分类。
- 后台任务：Celery worker + Celery beat，Redis 7 作为 broker/backend。
- 数据库：PostgreSQL 16 是生产和 Docker Compose 默认业务数据库；本地开发可显式覆盖为 SQLite 文件；测试使用临时 SQLite。
- 部署：Docker Compose、容器内 Nginx、PostgreSQL named volume、Redis named volume、PostgreSQL 备份脚本。

## 服务拓扑

```text
Browser
  -> Nginx :80
      -> /api/*, /health, /docs -> FastAPI api:8000
      -> /                    -> Vue static frontend:80

FastAPI api
  -> PostgreSQL postgres:5432   # 业务数据
  -> Redis redis:6379           # 仅 Celery 队列/结果

Celery worker / beat
  -> Redis redis:6379
  -> PostgreSQL postgres:5432
```

Docker Compose 服务为 `postgres`、`redis`、`api`、`worker`、`beat`、`frontend`、`nginx`。生产入口只暴露 Nginx 端口；PostgreSQL、Redis、FastAPI 和前端容器端口不直接对公网开放。

## 数据库与初始化

- 生产/Compose：`DATABASE_URL=postgresql+psycopg://...@postgres:5432/lithiumcraft`，数据库容器为 `postgres:16-alpine`，数据持久化在 `postgres_data` volume。
- 本地开发：开发文档中的 Windows 启动命令显式设置 `DATABASE_URL=sqlite:///./lithiumcraft-dev.db`，只用于本机联调，不代表生产数据库。
- 测试：`backend-api/tests/conftest.py` 使用临时 SQLite 文件隔离测试数据。
- 初始化：FastAPI startup 调用 `init_db()`，用 SQLAlchemy `create_all()` 建表，再调用 `seed_defaults()` 写入默认分类、系统设置和 `manual_only` 候选来源。
- 管理员账号：当前不在数据库建用户表，登录校验读取 `.env` 中的 `ADMIN_USERNAME` 和 `ADMIN_PASSWORD`，JWT 使用 `JWT_SECRET_KEY` 签名。

## 访问与鉴权

- 公开访问：`/`、`/intelligence`、`/intelligence/:id`、`/daily-briefs` 等前端页面，以及公开只读 API。
- 管理访问：`/admin/*` 页面需要登录，前端将 JWT 存在浏览器 `localStorage` 的 `lithiumcraft.token`。
- API 鉴权：管理接口依赖 `Authorization: Bearer <token>`；JWT subject 必须等于 `ADMIN_USERNAME`。
- CORS：由 `CORS_ORIGINS` 环境变量配置。Docker/Nginx 同源访问时主要依赖相对路径 `/api/v1`。

## 抓取与任务流

```text
公开来源配置
  -> 来源状态检查 enabled/manual_only/blocked_by_policy
  -> robots 与合规检查
  -> 域名限频
  -> RSS/网页/single_page 解析
  -> URL 与标题去重
  -> AI stub 摘要/标签/分类/评分
  -> 发布与风控过滤
  -> IntelligenceItem active / blocked / archived
  -> 公开前台和管理后台读取
```

自动任务使用 Celery/Redis：

```text
Celery Beat 07:00 Asia/Shanghai
  -> app.tasks.crawl.crawl_enabled_sources
  -> 逐个抓取 enabled 来源，不抓取 manual_only 候选来源

Celery Beat 07:30 Asia/Shanghai
  -> app.tasks.daily_brief.generate_daily_brief
  -> 基于当天已入库内容生成每日摘要
```

手动抓取不走 Celery 入队：管理员在 `/admin/crawl-logs` 触发单来源或全部 `enabled` 来源时，FastAPI 进程内同步调用 `run_source_crawl()`，直接写入 `CrawlTask` 和情报数据。这个设计适合低频管理验证；大规模定时抓取仍依赖 Celery worker/beat。

## 前端运行方式

- 本地开发：Vite dev server 监听 `5173`，`vite.config.ts` 将 `/api` 代理到 `http://127.0.0.1:8000`。
- Docker/生产：`frontend-app/Dockerfile` 使用 Node 22 构建静态资源，再用 Nginx 1.27 托管；`VITE_API_BASE` 默认 `/api/v1`。
- 统一入口：`deploy/nginx/lithiumcraft.conf` 将前端路由交给前端静态站点，API 路径转发到 FastAPI。

## 部署策略

第一期使用单台阿里云 ECS + Docker Compose，当前已验证可运行 `api`、`worker`、`beat`、`frontend`、`postgres`、`redis`、`nginx`。数据备份通过 `deploy/scripts/backup-postgres.sh` 执行 `pg_dump` 并生成 `.sql.gz`。

后续扩展方向：

- 将 PostgreSQL 迁移到阿里云 RDS。
- 将 Redis 迁移到云 Redis。
- 将 worker 拆到独立机器或增加 worker 副本。
- 增加正式迁移工具流程，替代仅依赖 `create_all()` 的初始化方式。
- 如后续需要全文检索，再引入 OpenSearch；当前代码未实现搜索引擎服务。
