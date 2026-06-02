# API Specification

## Base Rules

- All business APIs use the `/api/v1` prefix.
- Public content APIs allow anonymous read-only access; management APIs require `Authorization: Bearer <token>`.
- Paginated responses use `items`, `total`, `page`, and `page_size`.
- Error responses use FastAPI `detail`; the frontend can map details to readable messages.

## Public Read-Only APIs

- `POST /api/v1/auth/login`: admin login, returns a Bearer JWT.
- `GET /api/v1/processes`: manufacturing process directory with item counts and latest update time.
- `GET /api/v1/processes/{slug}`: process detail with keywords, local diagram, related material topics, and public materials.
- `GET /api/v1/topics`: material and property topic directory; v1 covers cathode materials, anode materials, electrolyte, separator, and dry electrode.
- `GET /api/v1/topics/{slug}`: topic detail with key properties, related processes, process impacts, and public materials.
- `GET /api/v1/intelligence`: source material list with keyword, category, process, status, and date filters; anonymous users only see `active` data.
- `GET /api/v1/intelligence/{id}`: source material detail; anonymous users get 404 for non-`active` data.
- `GET /api/v1/daily-briefs`: material summary list.
- `GET /api/v1/daily-briefs/{date}`: material summary for one date.
- `GET /api/v1/categories`: category list.

## Admin APIs

The following APIs require an admin Bearer JWT; anonymous access returns 401.

- `PATCH /api/v1/intelligence/{id}`: archive, restore, or correct material status.
- `POST /api/v1/daily-briefs/generate`: manually generate a material summary.
- `GET /api/v1/sources`: source list.
- `POST /api/v1/sources`: create source.
- `PATCH /api/v1/sources/{id}`: update source or source status.
- `GET /api/v1/crawl-tasks`: crawl task logs.
- `POST /api/v1/crawl-tasks`: manually trigger one source crawl; local/admin runs synchronously and does not require Redis.
- `POST /api/v1/crawl-tasks/enabled`: manually trigger all `enabled` sources; excludes `manual_only` candidate sources.
- `GET /api/v1/settings`: system settings.
- `PATCH /api/v1/settings/{key}`: update one system setting by key.

## Scheduling

- `app.tasks.crawl.crawl_enabled_sources`: runs daily at `Asia/Shanghai 07:00`.
- `app.tasks.daily_brief.generate_daily_brief`: runs daily at `Asia/Shanghai 07:30`.
- Automatic crawling uses Celery/Redis in deployment; manual crawling runs synchronously in the API process for local management convenience.

## Status Values

- Material status: `active`, `blocked`, `archived`.
- Source status: `enabled`, `disabled`, `manual_only`, `blocked_by_policy`.
- Task status: `pending`, `running`, `success`, `failed`, `skipped`.
