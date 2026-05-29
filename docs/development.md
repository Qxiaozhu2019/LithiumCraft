# Development

## 目录约定

- `backend-api`：后端 API、Celery、模型、服务、测试。
- `frontend-app`：Vue 前台首页与管理工作台。
- `deploy`：Docker Compose、Nginx、备份脚本。
- `docs`：中文项目文档。

## 本地开发

### 推荐：分别启动前后端开发服务

在 Windows 本地联调时，优先使用两个可见的 CMD 窗口分别常驻运行后端和前端。不要关闭这两个窗口；关闭后对应服务会停止。后端必须带 `--reload` 启动；前端使用 Vite dev server 并固定 `--host 0.0.0.0 --port 5173 --strictPort`，Vite 会自动热更新。后续代码修改后让服务自动热重启/热更新，不要反复手动开关 CMD。

后端 API：

```bat
cd /d E:\工作目录\97_AILearning\11_LithiumCraft\backend-api
set DATABASE_URL=sqlite:///./lithiumcraft-dev.db&& set CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173&& C:\Users\admin\.conda\envs\lithiumcraft-py312\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
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

- 公开首页：`http://localhost:5173`
- 管理入口：`http://localhost:5173/admin/crawl-logs`
- 后端健康检查：`http://127.0.0.1:8000/health`
- 默认管理员：`admin` / `ChangeMe123!`

前端开发服务已在 `frontend-app/vite.config.ts` 中配置 `/api` 代理到 `http://127.0.0.1:8000`，因此登录请求会从 `http://localhost:5173/api/v1/auth/login` 转发到本地后端。

后端 `--reload` 会在 Python 文件变更后自动重启；前端 Vite dev server 会在 Vue/TypeScript/CSS 变更后自动热更新页面。只有 `.env`、启动命令、依赖安装或端口异常这类非代码变更，才需要手动重启对应 CMD。

### 后台抓取进程

手动抓取和每日 7 点自动抓取依赖 Redis、Celery worker 和 Celery beat。只验证页面和 API 时可以先不启动；需要真实入队和执行抓取时需额外启动。

Redis 可使用本机服务或 Docker，例如：

```bat
docker run --name lithiumcraft-redis -p 6379:6379 redis:7-alpine
```

Celery worker（Windows 建议使用 `solo` pool）：

```bat
cd /d E:\工作目录\97_AILearning\11_LithiumCraft\backend-api
set DATABASE_URL=sqlite:///./lithiumcraft-dev.db&& set REDIS_URL=redis://127.0.0.1:6379/0&& C:\Users\admin\.conda\envs\lithiumcraft-py312\python.exe -m celery -A app.tasks.celery_app.celery_app worker --loglevel=info --pool=solo
```

Celery beat：

```bat
cd /d E:\工作目录\97_AILearning\11_LithiumCraft\backend-api
set DATABASE_URL=sqlite:///./lithiumcraft-dev.db&& set REDIS_URL=redis://127.0.0.1:6379/0&& C:\Users\admin\.conda\envs\lithiumcraft-py312\python.exe -m celery -A app.tasks.celery_app.celery_app beat --loglevel=info
```

### Docker Compose

```bash
cp .env.example .env
docker compose -f deploy/docker-compose.yml --env-file .env up --build
```

## 测试

后端使用 pytest。前端使用 TypeScript 构建检查。提交前至少运行：

```bat
cd /d E:\工作目录\97_AILearning\11_LithiumCraft\backend-api
C:\Users\admin\.conda\envs\lithiumcraft-py312\python.exe -m pytest tests -q -o cache_dir=C:\Users\admin\AppData\Local\Temp\lithiumcraft-pytest-cache
C:\Users\admin\.conda\envs\lithiumcraft-py312\python.exe -m ruff check app tests --config line-length=100 --no-cache
cd /d E:\工作目录\97_AILearning\11_LithiumCraft\frontend-app
"C:\Program Files\nodejs\npm.cmd" run build
```

## 新增来源流程

1. 确认来源公开可访问且合规。
2. 检查 `robots.txt` 和网站使用条款。
3. 配置来源类型、URL、域名、频率和上限。
4. 默认候选来源使用 `manual_only`，可手动测试但不会参与每天 7 点“全部启用来源”自动抓取。
5. 检查抓取日志、入库条目和 blocked 原因。
6. 确认无异常后启用来源。

## 提交规范

提交信息可使用英文，例如 `docs: update requirements`、`feat(api): add intelligence endpoints`、`test(crawler): block disabled source`。
