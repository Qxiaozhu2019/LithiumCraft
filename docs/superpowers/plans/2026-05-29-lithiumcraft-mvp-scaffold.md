# LithiumCraft 内部投研情报台实施计划

> **给 agentic workers：** 实施本计划时必须使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans`，并按任务逐项执行。步骤使用 checkbox（`- [ ]`）语法跟踪进度。

**Goal:** 搭建一个面向内部投研的锂电池工艺情报工作台，支持登录、精选公开来源自动抓取、AI 摘要分类、情报检索、每日摘要和 Docker 部署。

**Architecture:** 项目采用单仓库前后端分离架构。Vue 3 内部工作台通过 Bearer JWT 调用 FastAPI `/api/v1`；FastAPI 负责鉴权、业务 API 和数据库访问；Celery Beat 定时触发抓取、AI 处理和每日摘要生成；PostgreSQL 存储业务数据，Redis 承担队列和缓存。

**Tech Stack:** Python 3.12、FastAPI、Pydantic、SQLAlchemy 2、Alembic、Celery、Redis、PostgreSQL、Vue 3、Vite、TypeScript、Element Plus、Docker Compose、Nginx。

---

## 文件结构

- `Agent.md`：项目协作规则，要求文档默认中文撰写。
- `.env.example`、`.gitignore`、`README.md`：环境模板、忽略规则和快速启动说明。
- `docs/requirements.md`：内部投研情报台的产品范围和一期边界。
- `docs/architecture.md`：服务拓扑、数据流、任务流和部署方式。
- `docs/api.md`：`/api/v1`、JWT、分页、错误格式和核心接口。
- `docs/data-model.md`：Source、IntelligenceItem、DailyBrief、CrawlTask、Category、SystemSetting、SystemLog。
- `docs/crawling-compliance.md`：公开合规来源、robots、限频、禁止行为和展示边界。
- `docs/development.md`：本地开发、测试、目录约定、提交规范和新增来源流程。
- `docs/deployment.md`：阿里云 ECS、Docker Compose、Nginx、备份和排障。
- `docs/agents/subagents.md`：子代理角色、边界、交接模板和协作规则。
- `docs/agents/execution-board.md`：轻量任务看板，用于领取、推进和核验 agentic work。
- `docs/agents/handoff-log.md`：跨 agent 的上下文交接记录、验证结果和遗留风险。
- `backend-api`：FastAPI、Celery、模型、服务、测试。
- `frontend-app`：统一 Vue 3 内部工作台。
- `deploy`：Docker Compose、Nginx 和运维脚本。

---

## Tasks

- [ ] **Task 1: 规范文档落地**
  - 创建 `.env.example`、`README.md` 和 `docs/*.md`。
  - 明确内部使用、精选 5-10 个来源、只自动抓取、每日摘要、单管理员登录、全业务 API 鉴权。

- [ ] **Task 1.1: Agent 协作板落地**
  - 创建 `docs/agents/subagents.md`、`docs/agents/execution-board.md`、`docs/agents/handoff-log.md`。
  - 明确 Coordinator、Backend API、Crawler & AI、Frontend、Deployment、QA & Docs 的职责边界。
  - 后续 agent 领取任务前更新执行板，交接时追加验证结果和遗留风险。

- [ ] **Task 2: 后端领域模型与 API**
  - 创建 `Source`、`IntelligenceItem`、`DailyBrief`、`CrawlTask`、`Category`、`SystemSetting`、`SystemLog`。
  - 实现 `/api/v1/auth/login`、`/api/v1/intelligence`、`/api/v1/daily-briefs`、`/api/v1/sources`、`/api/v1/crawl-tasks`、`/api/v1/categories`、`/api/v1/settings`。
  - 除 `/health` 和登录外，所有业务 API 使用 Bearer JWT。

- [ ] **Task 3: 合规抓取与 AI Stub**
  - 实现 robots/source policy 检查、域名限频、RSS/公开网页抓取、去重、风控过滤。
  - AI 适配器第一期使用 deterministic stub，输出摘要、标签、分类、重要性评分。
  - 抓取结果入内部情报库，异常内容标记为 `blocked`。

- [ ] **Task 4: 每日摘要任务**
  - Celery Beat 每日生成 `DailyBrief`。
  - 每日摘要包含总览、重点条目和分类摘要。
  - 首次启动的示例来源保持 disabled，避免自动访问外部网站。

- [ ] **Task 5: Vue 统一工作台**
  - 创建登录页、仪表盘、情报列表、情报详情、每日摘要、来源管理、抓取日志、系统设置。
  - 未登录自动跳转登录；API client 统一附加 Bearer token。

- [ ] **Task 6: Docker 部署与验证**
  - Docker Compose 启动 `api`、`worker`、`beat`、`frontend`、`postgres`、`redis`、`nginx`。
  - 验证 `/health`、OpenAPI、登录页、API 鉴权、数据库持久化。

---

## 验收标准

- 本地可通过 Docker Compose 启动完整服务。
- 单管理员可登录内部工作台。
- 来源管理可新增、禁用、查看精选来源。
- 抓取任务遵守来源状态、robots、限频和失败重试。
- 情报可检索、筛选、查看详情，状态支持 `active`、`blocked`、`archived`。
- 每日摘要可按日期查看。
- 文档覆盖内部定位、合规抓取、API、数据模型、开发和部署。
