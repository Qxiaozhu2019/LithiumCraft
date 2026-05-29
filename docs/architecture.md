# Architecture

## 总览

LithiumCraft 使用单仓库、前后端分离架构。浏览器访问 Vue 前台首页与管理工作台，公开内容页通过 `/api/v1` 调用 FastAPI 只读接口，后台管理页登录后携带 Bearer JWT 调用管理接口。FastAPI 负责鉴权、业务 API、数据库读写。Celery Worker 和 Beat 负责抓取、AI 处理和每日摘要。PostgreSQL 保存业务数据，Redis 用作 Celery broker/backend。

## 服务拓扑

```text
Browser
  -> Vue 前台首页 / 管理工作台
  -> FastAPI /api/v1 公开只读接口 + 管理接口
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
  -> 公开前台展示 active 情报与每日摘要
  -> 管理工作台查看抓取日志、来源和设置
```

## 调度流

```text
Celery Beat 07:00 Asia/Shanghai
  -> app.tasks.crawl.crawl_enabled_sources
  -> 逐个启用来源执行合规抓取

Celery Beat 07:30 Asia/Shanghai
  -> app.tasks.daily_brief.generate_daily_brief
  -> 基于当天抓取结果生成每日摘要
```

管理员也可以在 `/admin/crawl-logs` 手动触发单来源抓取或全部启用来源抓取；API 进程只负责提交 Celery 任务，不同步访问外部站点。

## 部署策略

第一期部署在单台阿里云 ECS 上，使用 Docker Compose 管理 API、Worker、Beat、Frontend、PostgreSQL、Redis、Nginx。后续如规模增大，可将 PostgreSQL 迁移至 RDS，将搜索迁移至 OpenSearch，将 Worker 拆分到独立服务器。
