# LithiumCraft

LithiumCraft 是一个面向内部投研场景的锂电池工艺情报工作台。第一版聚焦少量精选公开合规来源，自动抓取、清洗、摘要、分类、入库，并提供内部检索和每日摘要。

## 服务组成

- `frontend-app`：Vue 3 + Vite + Element Plus 内部工作台。
- `backend-api`：FastAPI REST API、领域模型和业务服务。
- `worker`：Celery worker/beat，执行抓取和每日摘要任务。
- `deploy`：Docker Compose、Nginx、备份脚本。
- `docs`：需求、架构、API、数据模型、合规、开发和部署文档。

## 快速启动

```bash
cp .env.example .env
docker compose -f deploy/docker-compose.yml --env-file .env up --build
```

默认地址：

- 工作台：http://localhost:3000
- API 文档：http://localhost:8000/docs
- Nginx 入口：http://localhost:8080

## 合规声明

LithiumCraft 只处理公开、合规、低频访问的信息来源。系统不抓取登录后、付费墙、验证码后、非公开接口或被 `robots.txt` 禁止的内容，不绕过反爬，不使用代理池轰炸，不全文搬运受版权保护内容。
