# Deployment

## 部署目标

LithiumCraft 第一版推荐部署在单台阿里云 Linux ECS 上，使用 Docker Compose 管理全部服务：

- `frontend`：Vue 3 + Vite 构建后的静态前端，由容器内 Nginx 托管。
- `api`：FastAPI + Python 3.12 后端，提供 `/api/v1` 业务接口和 `/health` 健康检查。
- `postgres`：PostgreSQL 16，保存业务数据。
- `redis`：Redis 7，作为 Celery broker/result backend。
- `worker`：Celery worker，执行抓取和摘要任务。
- `beat`：Celery beat，按 `Asia/Shanghai` 时间调度自动任务。
- `nginx`：统一入口，`/api/` 转发到后端，其他路径转发到前端。

## 服务器初始化

阿里云安全组建议只开放：

- `22`：SSH，仅放行你的办公 IP。
- `80`：HTTP，第一阶段公网访问。
- `443`：HTTPS，绑定域名和证书后使用。
- `8888`：如果继续使用宝塔面板，仅临时放行你的办公 IP。

不要公网开放 `5432`、`6379`、`8000`、`5173`。

空服务器可先运行初始化脚本：

```bash
curl -fsSL https://raw.githubusercontent.com/<your-org>/<your-repo>/<branch>/deploy/scripts/bootstrap-alinux.sh -o bootstrap-alinux.sh
bash bootstrap-alinux.sh
```

如果服务器不能访问 GitHub，先按“首次部署”的打包上传方式把项目传到 `/opt/lithiumcraft`，再在项目目录内运行：

```bash
cd /opt/lithiumcraft
find deploy/scripts -maxdepth 1 -type f -name '*.sh' -exec sed -i 's/\r$//' {} +
find deploy/scripts -maxdepth 1 -type f -name '*.sh' -exec chmod +x {} +
bash deploy/scripts/bootstrap-alinux.sh
```

脚本会安装基础工具、Docker Engine，启用 Docker 服务，并在没有 swap 时创建 2GB `/swapfile`。

## 首次部署

推荐部署目录：

```bash
mkdir -p /opt/lithiumcraft
```

当前推荐从本地打包上传，不要求服务器能访问 GitHub：

```bash
# 在本地项目根目录执行，排除 Git、依赖、生产 .env、备份和本地开发数据库
tar --exclude='.git' \
  --exclude='node_modules' \
  --exclude='frontend-app/node_modules' \
  --exclude='.env' \
  --exclude='backend-api/lithiumcraft-dev.db' \
  --exclude='deploy/backups' \
  -czf lithiumcraft-deploy.tar.gz .

scp lithiumcraft-deploy.tar.gz root@139.224.223.234:/tmp/
```

服务器解压：

```bash
ssh root@139.224.223.234
mkdir -p /opt/lithiumcraft
tar -xzf /tmp/lithiumcraft-deploy.tar.gz -C /opt/lithiumcraft
find /opt/lithiumcraft/deploy/scripts -maxdepth 1 -type f -name '*.sh' -exec sed -i 's/\r$//' {} +
find /opt/lithiumcraft/deploy/scripts -maxdepth 1 -type f -name '*.sh' -exec chmod +x {} +
```

创建生产环境配置：

```bash
cd /opt/lithiumcraft
cp deploy/env.production.example .env
vim .env
```

必须替换这些值：

- `POSTGRES_PASSWORD`
- `DATABASE_URL` 中的 PostgreSQL 密码
- `JWT_SECRET_KEY`
- `ADMIN_PASSWORD`
- `CORS_ORIGINS`
- `CRAWLER_USER_AGENT` 中的站点地址和联系邮箱

第一阶段直接用公网 IP 暴露 HTTP：

```env
CORS_ORIGINS=http://139.224.223.234
CRAWLER_USER_AGENT=LithiumCraftBot/0.1 (+http://139.224.223.234; compliance contact: ops@example.com)
PUBLIC_HTTP_BIND=0.0.0.0
PUBLIC_HTTP_PORT=80
```

启动：

```bash
bash deploy/scripts/deploy.sh
```

等镜像构建和容器启动后验证：

```bash
BASE_URL=http://127.0.0.1 bash deploy/scripts/verify.sh
```

浏览器访问：

- `http://139.224.223.234/`
- `http://139.224.223.234/login`
- `http://139.224.223.234/docs`

## 宝塔 HTTPS 反代

如果使用宝塔面板管理域名和证书，推荐让 Docker Nginx 只监听本机端口：

```env
PUBLIC_HTTP_BIND=127.0.0.1
PUBLIC_HTTP_PORT=8080
CORS_ORIGINS=https://你的域名,http://你的域名
CRAWLER_USER_AGENT=LithiumCraftBot/0.1 (+https://你的域名; compliance contact: ops@example.com)
```

然后在宝塔站点里配置反向代理：

```text
http://127.0.0.1:8080
```

验证命令改为：

```bash
BASE_URL=http://127.0.0.1:8080 bash deploy/scripts/verify.sh
```

## 运维命令

查看状态：

```bash
docker compose -f deploy/docker-compose.yml --env-file .env ps
```

查看日志：

```bash
docker compose -f deploy/docker-compose.yml --env-file .env logs -f
docker compose -f deploy/docker-compose.yml --env-file .env logs -f api
docker compose -f deploy/docker-compose.yml --env-file .env logs -f worker
docker compose -f deploy/docker-compose.yml --env-file .env logs -f beat
docker compose -f deploy/docker-compose.yml --env-file .env logs -f nginx
```

重启服务：

```bash
docker compose -f deploy/docker-compose.yml --env-file .env restart api
docker compose -f deploy/docker-compose.yml --env-file .env restart worker
docker compose -f deploy/docker-compose.yml --env-file .env restart beat
docker compose -f deploy/docker-compose.yml --env-file .env restart nginx
```

## 同步与热更新

生产环境没有真正的前后端热更新：前端需要重新构建静态资源，后端镜像需要重新构建或重启容器。这里的“热更新”指在不重装服务器、不删除数据库 volume、不改 `.env` 的情况下，把新代码同步到 `/opt/lithiumcraft`，然后滚动式重建相关容器。

### 推荐方式：本地打包上传

服务器不要求安装 Git，也不要求能访问 GitHub。日常更新使用本地打包上传：

本地电脑是 Windows、服务器是 Linux 时，推荐直接在本地运行项目自带的一键热更新脚本：

```powershell
Set-Location 'E:\工作目录\97_AILearning\11_LithiumCraft'
powershell -ExecutionPolicy Bypass -File deploy\scripts\hot-update.ps1 -HostName 139.224.223.234 -UserName root
```

脚本会自动完成：

- 本地打包并排除 `.git`、`.env`、依赖、本地 SQLite 和备份目录。
- 上传包到服务器 `/tmp/lithiumcraft-deploy.tar.gz`。
- 如果当前 PostgreSQL 容器正在运行，先执行一次 PostgreSQL 备份。
- 在服务器解压到 `/tmp` 临时目录，确认包结构正确且不包含 `.env`。
- 清理 `/opt/lithiumcraft` 中旧代码并复制新代码，避免几个月后热更新时残留已删除文件。
- 校验 `/opt/lithiumcraft/.env` 未被覆盖。
- 修复 shell 脚本 LF 换行和可执行权限。
- 运行 `deploy.sh` 重建需要更新的容器。
- 运行 `verify.sh` 验证首页和 API。

如果确认不需要更新前备份，可追加 `-SkipBackup`：

```powershell
powershell -ExecutionPolicy Bypass -File deploy\scripts\hot-update.ps1 -HostName 139.224.223.234 -UserName root -SkipBackup
```

如果不用 PowerShell 脚本，也可以手动执行：

```bash
# 本地项目根目录
tar --exclude='.git' \
  --exclude='node_modules' \
  --exclude='frontend-app/node_modules' \
  --exclude='.env' \
  --exclude='backend-api/lithiumcraft-dev.db' \
  --exclude='deploy/backups' \
  -czf lithiumcraft-deploy.tar.gz .

scp lithiumcraft-deploy.tar.gz root@139.224.223.234:/tmp/

# 服务器 Linux
ssh root@139.224.223.234
cd /opt/lithiumcraft

before_env_sum=$(sha256sum .env | awk '{print $1}')
env_copy=$(mktemp /tmp/lithiumcraft-env.XXXXXX)
staging_dir=$(mktemp -d /tmp/lithiumcraft-release.XXXXXX)
trap 'rm -rf "$staging_dir" "$env_copy"' EXIT
cp .env "$env_copy"

find deploy/scripts -maxdepth 1 -type f -name '*.sh' -exec sed -i 's/\r$//' {} +
find deploy/scripts -maxdepth 1 -type f -name '*.sh' -exec chmod +x {} +
if docker compose -f deploy/docker-compose.yml --env-file .env ps --services --status running 2>/dev/null | grep -qx postgres; then
  bash deploy/scripts/backup-postgres.sh
else
  echo "PostgreSQL container is not running; skip pre-update backup."
fi

tar -xzf /tmp/lithiumcraft-deploy.tar.gz -C "$staging_dir"
if [ -f "$staging_dir/.env" ]; then
  echo "Package unexpectedly contains .env; abort."
  exit 1
fi
if [ ! -f "$staging_dir/deploy/scripts/deploy.sh" ]; then
  echo "Package does not look like a LithiumCraft project root; abort."
  exit 1
fi

find "$staging_dir/deploy/scripts" -maxdepth 1 -type f -name '*.sh' -exec sed -i 's/\r$//' {} +
find "$staging_dir/deploy/scripts" -maxdepth 1 -type f -name '*.sh' -exec chmod +x {} +
if [ -d deploy/backups ]; then
  mkdir -p "$staging_dir/deploy"
  cp -a deploy/backups "$staging_dir/deploy/backups"
fi

find /opt/lithiumcraft -mindepth 1 -maxdepth 1 ! -name '.env' -exec rm -rf -- {} +
cp -a "$staging_dir/." /opt/lithiumcraft/
cp "$env_copy" /opt/lithiumcraft/.env

after_env_sum=$(sha256sum .env | awk '{print $1}')
if [ "$before_env_sum" != "$after_env_sum" ]; then
  echo ".env changed unexpectedly; abort."
  exit 1
fi

bash deploy/scripts/deploy.sh
bash deploy/scripts/verify.sh
```

一键脚本和手动流程都会清理旧代码文件，但会保留：

- `/opt/lithiumcraft/.env`
- PostgreSQL volume：`deploy_postgres_data`
- Redis volume：`deploy_redis_data`
- 备份目录：`deploy/backups`

注意：上传包必须排除 `.env`，否则会丢生产密码和密钥。不要执行 `docker compose down -v` 或 `docker volume prune`，否则可能删除数据库 volume。

### 可选方式：服务器 Git 工作树

只有在服务器已安装 Git 且能访问 GitHub 时，才使用 `git pull` 更新：

```bash
cd /opt/lithiumcraft
git pull
bash deploy/scripts/deploy.sh
bash deploy/scripts/verify.sh
```

清理无用镜像：

```bash
docker image prune -f
```

不要执行 `docker volume prune`，避免误删 PostgreSQL 或 Redis 数据卷。

## 备份

手动备份 PostgreSQL：

```bash
cd /opt/lithiumcraft
bash deploy/scripts/backup-postgres.sh
```

安装每日 02:30 自动备份：

```bash
bash deploy/scripts/install-backup-cron.sh
```

备份文件默认写入：

```text
/opt/lithiumcraft/deploy/backups/
```

建议定期把备份复制到本地或 OSS。升级前先手动执行一次备份。

## 验收标准

部署完成后确认：

- `/health` 返回 `{"status":"ok","service":"lithiumcraft-api"}`。
- `/api/v1/categories` 返回 JSON。
- 首页、`/login`、`/docs` 可以从浏览器打开。
- `worker` 和 `beat` 日志没有 PostgreSQL/Redis 连接错误。
- 管理后台可以登录。
- 手动触发抓取后，抓取日志能写入数据库。
- 执行备份脚本后生成 `.sql.gz` 文件。
