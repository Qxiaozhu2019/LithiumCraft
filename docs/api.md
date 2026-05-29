# API 规范

## 基础规则

- 所有业务接口使用 `/api/v1` 前缀。
- 公开内容接口允许未登录只读访问；管理接口仍需要 `Authorization: Bearer <token>`。
- 列表响应统一使用 `items`、`total`、`page`、`page_size`。
- 错误响应统一使用 `code`、`message`、`details`。

## 公开只读接口

- `POST /api/v1/auth/login`：单管理员登录，返回 Bearer JWT。
- `GET /api/v1/intelligence`：情报列表，支持关键词、分类、状态、日期筛选。
- `GET /api/v1/intelligence/{id}`：情报详情。
- `GET /api/v1/daily-briefs`：每日摘要列表。
- `GET /api/v1/daily-briefs/{date}`：指定日期摘要。
- `GET /api/v1/categories`：分类列表。

## 管理员接口

以下接口必须携带管理员 Bearer JWT；未登录访问应返回 401。

- `PATCH /api/v1/intelligence/{id}`：归档、恢复或修正情报状态。
- `POST /api/v1/daily-briefs/generate`：手动生成每日摘要。
- `GET /api/v1/sources`：来源列表。
- `POST /api/v1/sources`：新增来源。
- `PATCH /api/v1/sources/{id}`：修改来源或启停。
- `GET /api/v1/crawl-tasks`：抓取任务日志。
- `POST /api/v1/crawl-tasks`：手动触发单来源抓取；本地和管理端同步执行，不依赖 Redis。
- `POST /api/v1/crawl-tasks/enabled`：手动触发全部启用来源抓取；同步执行所有 `enabled` 来源，不包含 `manual_only` 候选来源。
- `GET /api/v1/settings`：系统设置。
- `PATCH /api/v1/settings`：更新系统设置。

## 调度约定

- `app.tasks.crawl.crawl_enabled_sources`：每天 `Asia/Shanghai 07:00` 执行。
- `app.tasks.daily_brief.generate_daily_brief`：每天 `Asia/Shanghai 07:30` 执行。
- 自动抓取由 Celery/Redis 在部署环境执行；手动抓取为了本地管理便利，在 API 进程同步执行并写入抓取日志。

## 状态值

- 情报状态：`active`、`blocked`、`archived`。
- 来源状态：`enabled`、`disabled`、`manual_only`、`blocked_by_policy`。
- 任务状态：`pending`、`running`、`success`、`failed`、`skipped`。
