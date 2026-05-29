# API 规范

## 基础规则

- 所有业务接口使用 `/api/v1` 前缀。
- 除 `/health` 和 `/api/v1/auth/login` 外，所有业务接口都需要 `Authorization: Bearer <token>`。
- 列表响应统一使用 `items`、`total`、`page`、`page_size`。
- 错误响应统一使用 `code`、`message`、`details`。

## 核心接口

- `POST /api/v1/auth/login`：单管理员登录。
- `GET /api/v1/intelligence`：情报列表，支持关键词、分类、状态、日期筛选。
- `GET /api/v1/intelligence/{id}`：情报详情。
- `PATCH /api/v1/intelligence/{id}`：归档、恢复或修正情报状态。
- `GET /api/v1/daily-briefs`：每日摘要列表。
- `GET /api/v1/daily-briefs/{date}`：指定日期摘要。
- `POST /api/v1/daily-briefs/generate`：手动生成每日摘要。
- `GET /api/v1/sources`：来源列表。
- `POST /api/v1/sources`：新增来源。
- `PATCH /api/v1/sources/{id}`：修改来源或启停。
- `GET /api/v1/crawl-tasks`：抓取任务日志。
- `POST /api/v1/crawl-tasks`：手动触发抓取。
- `GET /api/v1/categories`：分类列表。
- `GET /api/v1/settings`：系统设置。
- `PATCH /api/v1/settings`：更新系统设置。

## 状态值

- 情报状态：`active`、`blocked`、`archived`。
- 来源状态：`enabled`、`disabled`、`manual_only`、`blocked_by_policy`。
- 任务状态：`pending`、`running`、`success`、`failed`、`skipped`。
