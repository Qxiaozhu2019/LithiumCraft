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

如果代码已经上传到服务器，也可以在项目目录内运行：

```bash
bash deploy/scripts/bootstrap-alinux.sh
```

脚本会安装基础工具、Docker Engine，启用 Docker 服务，并在没有 swap 时创建 2GB `/swapfile`。

## 首次部署

推荐部署目录：

```bash
mkdir -p /opt/lithiumcraft
cd /opt/lithiumcraft
git clone <your-repository-url> .
```

没有远程仓库时，可以本地打包上传：

```bash
scp lithiumcraft.tar.gz root@139.224.223.234:/opt/
ssh root@139.224.223.234
cd /opt
tar -xzf lithiumcraft.tar.gz
mv 11_LithiumCraft lithiumcraft
cd /opt/lithiumcraft
```

创建生产环境配置：

```bash
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

升级：

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
