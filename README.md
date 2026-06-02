# LithiumCraft

LithiumCraft 是一个面向内部投研场景的锂电池工艺情报工作台。第一版聚焦少量精选公开合规来源，自动抓取、清洗、摘要、分类、入库，并提供公开只读首页、情报检索和每日摘要；来源管理、抓取日志、系统设置等管理能力仍由单管理员登录后使用。

## 服务组成

- `frontend-app`：Vue 3 + Vite + Element Plus 前台首页与管理工作台。
- `backend-api`：FastAPI REST API、领域模型和业务服务。
- `worker`：Celery worker/beat，执行自动抓取和每日摘要任务。
- `postgres`：PostgreSQL 16 业务数据库；本地开发可显式覆盖为 SQLite。
- `redis`：Celery broker/result backend，不保存业务数据。
- `deploy`：Docker Compose、Nginx、备份脚本。
- `docs`：需求、架构、API、数据模型、合规、开发和部署文档。

## 默认访问

- `/`：公开首页，展示最新情报、每日摘要和空状态提示，不需要登录。
- `/intelligence`、`/intelligence/:id`、`/daily-briefs`：公开只读内容页。
- `/login`：管理员登录入口。
- `/admin/sources`、`/admin/crawl-logs`、`/admin/settings`：管理员入口，需要 Bearer JWT。

## 抓取策略

- Celery Beat 每天 `Asia/Shanghai 07:00` 自动抓取全部启用来源。
- 每日摘要在 `07:30` 生成，避免早于当天抓取结果。
- 管理员可在抓取日志页手动触发单来源抓取或“抓取全部启用来源”；手动抓取由 API 同步执行，不依赖 Redis/Celery。
- 首批候选来源默认 `manual_only`，可手动测试但不参与每日自动抓取；人工确认后再改为 `enabled`。
- 系统不放置演示情报。

## 快速启动

```bash
cp .env.example .env
docker compose -f deploy/docker-compose.yml --env-file .env up --build
```

默认地址：

- Docker Compose 统一入口：http://localhost:8080
- 前台/工作台：http://localhost:8080
- API 文档：http://localhost:8080/docs
- API 健康检查：http://localhost:8080/health

本地分离开发时，前端 Vite 默认使用 `http://localhost:5173`，后端 Uvicorn 使用 `http://127.0.0.1:8000`，详见 `docs/development.md`。

## 合规声明

LithiumCraft 只处理公开、合规、低频访问的信息来源。系统不抓取登录后、付费墙、验证码后、非公开接口或被 `robots.txt` 禁止的内容，不绕过反爬，不使用代理池轰炸，不全文搬运受版权保护内容。
