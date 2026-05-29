# Development

## 目录约定

- `backend-api`：后端 API、Celery、模型、服务、测试。
- `frontend-app`：统一 Vue 内部工作台。
- `deploy`：Docker Compose、Nginx、备份脚本。
- `docs`：中文项目文档。

## 本地开发

```bash
cp .env.example .env
docker compose -f deploy/docker-compose.yml --env-file .env up --build
```

## 测试

后端使用 pytest。前端使用 TypeScript 构建检查。提交前至少运行后端测试和前端构建。

## 新增来源流程

1. 确认来源公开可访问且合规。
2. 检查 `robots.txt` 和网站使用条款。
3. 配置来源类型、URL、域名、频率和上限。
4. 先禁用自动抓取，手动触发一次测试。
5. 检查抓取日志、入库条目和 blocked 原因。
6. 确认无异常后启用来源。

## 提交规范

提交信息可使用英文，例如 `docs: update requirements`、`feat(api): add intelligence endpoints`、`test(crawler): block disabled source`。
