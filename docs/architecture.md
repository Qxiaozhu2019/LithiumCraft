# Architecture

## 总览

LithiumCraft 使用单仓库、前后端分离架构。浏览器访问 Vue 内部工作台，工作台通过 `/api/v1` 调用 FastAPI。FastAPI 负责鉴权、业务 API、数据库读写。Celery Worker 和 Beat 负责抓取、AI 处理和每日摘要。PostgreSQL 保存业务数据，Redis 用作 Celery broker/backend。

## 服务拓扑

```text
Browser
  -> Vue 工作台
  -> FastAPI /api/v1
  -> PostgreSQL
  -> Redis
  -> Celery Worker / Beat
```

Nginx 在 Docker Compose 中作为统一入口，将 `/api/` 转发到 FastAPI，将 `/` 转发到 Vue 工作台。

## 数据流

```text
精选公开来源
  -> 来源状态与 robots 检查
  -> 域名限频抓取
  -> RSS/网页解析
  -> URL 与标题去重
  -> AI stub 摘要/标签/分类/评分
  -> 风控过滤
  -> 情报库 active 或 blocked
  -> 工作台检索与每日摘要
```

## 部署策略

第一期部署在单台阿里云 ECS 上，使用 Docker Compose 管理 API、Worker、Beat、Frontend、PostgreSQL、Redis、Nginx。后续如规模增大，可将 PostgreSQL 迁移至 RDS，将搜索迁移至 OpenSearch，将 Worker 拆分到独立服务器。
