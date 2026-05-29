# Subagents

## 目标

本文定义 LithiumCraft 后续由多个 agentic workers 协作时的角色边界、输入输出和交接规则。所有 agent 必须遵守根目录 `Agent.md`：项目文档默认使用中文，提交前不覆盖他人未提交变更。

## 通用协作规则

- 先阅读 `docs/superpowers/plans/2026-05-29-lithiumcraft-mvp-scaffold.md`、`docs/requirements.md` 和本目录下的协作板。
- 每次只领取 `docs/agents/execution-board.md` 中一个明确任务，开始前把任务移动到 `In Progress`。
- 任务完成后更新执行板和 `docs/agents/handoff-log.md`，说明完成内容、验证结果、遗留风险和下一步建议。
- 不主动访问外部网站；需要网络、安装依赖或推送时按当前运行环境申请授权。
- 抓取相关实现必须遵守 `docs/crawling-compliance.md`，不得添加演示情报；未经人工确认的来源必须保持 disabled。
- 发现与计划不一致的需求或未预期改动时先记录并暂停相关文件修改，避免覆盖他人工作。

## 推荐子代理

### Coordinator Agent

职责：维护计划、执行板和交接日志，拆分任务，合并跨模块决策。

输入：实施计划、需求文档、当前 git 状态、各子代理交接记录。

输出：更新后的计划文档、执行板状态、最终提交说明。

### Backend API Agent

职责：实现 FastAPI 应用、SQLAlchemy 模型、Pydantic Schema、鉴权和业务 API。

边界：只修改 `backend-api/app`、`backend-api/tests`、后端依赖和相关 API 文档。

交付：接口可被测试客户端调用；公开内容页对应的只读接口免登录，来源、设置、抓取、状态修改等管理接口必须需要 Bearer JWT。

### Crawler & AI Agent

职责：实现来源合规检查、RSS/公开网页抓取、去重、AI stub、风控过滤和每日摘要任务。

边界：只处理公开合规来源，不绕过登录、付费墙、验证码、反爬或 robots 限制。

交付：抓取结果可入库为 `active` 或 `blocked`，失败原因可追踪。

### Frontend Agent

职责：实现 Vue 3 内部工作台、路由、登录态、API client 和核心页面。

边界：只修改 `frontend-app`、前端构建配置和相关前端文档。

交付：未登录可访问公开首页、情报列表、情报详情和每日摘要；访问 `/admin/*` 管理页时才跳转登录。

### Deployment Agent

职责：实现 Docker Compose、Nginx、环境变量模板、启动脚本、备份和部署说明。

边界：只修改 `deploy`、Dockerfile、`.env.example` 和部署文档。

交付：本地 Compose 可启动 `api`、`worker`、`beat`、`frontend`、`postgres`、`redis`、`nginx`。

### QA & Docs Agent

职责：补齐测试、检查文档一致性、执行验收清单、记录风险。

边界：优先修改测试、文档和小范围修复，不引入未计划的新功能。

交付：测试命令、构建命令、验证结果和未覆盖风险写入交接日志。

## 交接模板

每个 agent 完成任务后，在 `docs/agents/handoff-log.md` 追加：

```markdown
## YYYY-MM-DD HH:mm - <Agent 名称>

- 领取任务：<执行板任务编号或名称>
- 完成内容：<关键文件和行为变化>
- 验证结果：<命令与结果；未运行需说明原因>
- 遗留问题：<阻塞、风险或后续建议>
- 下一步建议：<建议下一个 agent 领取什么>
```
