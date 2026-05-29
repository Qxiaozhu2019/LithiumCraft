# Execution Board

> 本文件是 agentic workers 的轻量任务看板。领取任务前先更新状态，完成后同步 `docs/agents/handoff-log.md`。

## 状态规则

- `Backlog`：可领取，但尚未开始。
- `In Progress`：已有 agent 正在处理，同一时间避免多人修改同一区域。
- `Review / Verify`：实现完成，等待测试、构建、人工审阅或提交。
- `Done`：已完成并记录验证结果。
- `Blocked`：因权限、需求或外部依赖暂停，必须写明阻塞原因。

## Backlog

| ID | 任务 | 建议 Agent | 验收要点 |
| --- | --- | --- | --- |
| LC-009 | Docker Compose 真实启动验收 | Deployment Agent | 在具备 Docker CLI 的环境运行 `docker compose config/up --build`，核验 Nginx、API、worker、beat |

## In Progress

| ID | 任务 | Owner | 开始时间 | 备注 |
| --- | --- | --- | --- | --- |
| - | - | - | - | - |

## Review / Verify

| ID | 任务 | Owner | 待验证内容 |
| --- | --- | --- | --- |
| LC-006 | 添加 Docker Compose 与 Nginx | Deployment Agent | 需要 Docker CLI 环境运行 `docker compose config/up --build` |

## Done

| ID | 任务 | 完成时间 | 结果 |
| --- | --- | --- | --- |
| LC-001 | 项目基础文档、环境模板和后端目录初稿 | 2026-05-29 | 已创建 README、docs 基础文档、`.env.example`、`backend-api` 初始代码 |
| LC-003 | 创建 agents 协作文档并更新实施计划 | 2026-05-29 | 已新增 agents 三份协作文档并更新实施计划 |
| LC-002 | 后端 API 骨架与服务初稿 | 2026-05-29 | 已通过后端测试和 ruff 核验；公开只读与管理鉴权边界已补测 |
| LC-004 | 补齐 Celery 任务目录与每日摘要调度 | 2026-05-29 | 已创建 Celery app、抓取任务、每日摘要任务和任务注册测试 |
| LC-005 | 创建 Vue 3 内部工作台 | 2026-05-29 | 已创建 Vue 工作台并通过 `npm run build` |
| LC-007 | 补齐后端测试与前端构建验收 | 2026-05-29 | `pytest tests`、`ruff check app tests`、`npm run build` 均通过；Docker Compose 真实启动拆至 LC-009 |
| LC-008 | 公开首页、每日 7 点抓取与手动抓取调整 | 2026-05-29 | `/` 与内容页公开只读，`/admin/*` 管理保护；Celery 07:00/07:30；新增抓取全部启用来源入口 |

## Blocked

| ID | 任务 | 阻塞原因 | 解除条件 |
| --- | --- | --- | --- |
| - | - | - | - |

## 下次领取建议

优先在具备 Docker CLI 的环境处理 `LC-009`，完成 Compose 全栈真实启动验收；后续再接入真实中文公开来源并按合规流程启用。
