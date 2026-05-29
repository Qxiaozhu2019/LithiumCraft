# Development

## 目录约定

- `backend-api`：后端 API、Celery、模型、服务、测试。
- `frontend-app`：统一 Vue 内部工作台。
- `deploy`：Docker Compose、Nginx、备份脚本。
- `docs`：中文项目文档。

## 本地开发

### 推荐：分别启动前后端开发服务

在 Windows 本地联调时，优先使用两个可见的 CMD 窗口分别常驻运行后端和前端。不要关闭这两个窗口；关闭后对应服务会停止。

后端 API：

```bat
cd /d E:\工作目录\97_AILearning\11_LithiumCraft\backend-api
set DATABASE_URL=sqlite:///./lithiumcraft-dev.db&& set CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173&& C:\Users\admin\.conda\envs\lithiumcraft-py312\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

前端工作台：

```bat
cd /d E:\工作目录\97_AILearning\11_LithiumCraft\frontend-app
"C:\Program Files\nodejs\npm.cmd" run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

验证：

```bat
netstat -ano | findstr 5173
netstat -ano | findstr 8000
```

访问地址：

- 前端工作台：`http://localhost:5173`
- 后端健康检查：`http://127.0.0.1:8000/health`
- 默认管理员：`admin` / `ChangeMe123!`

前端开发服务已在 `frontend-app/vite.config.ts` 中配置 `/api` 代理到 `http://127.0.0.1:8000`，因此登录请求会从 `http://localhost:5173/api/v1/auth/login` 转发到本地后端。

### Docker Compose

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
