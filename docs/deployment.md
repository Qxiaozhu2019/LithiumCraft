# Deployment

## 阿里云 ECS

第一期使用单台 ECS。安装 Docker 和 Docker Compose，配置域名、HTTPS 证书和安全组。生产环境必须修改 `.env` 中的密码和 JWT secret。

## Docker Compose

```bash
cp .env.example .env
docker compose -f deploy/docker-compose.yml --env-file .env up -d --build
```

## Nginx

Nginx 作为统一入口，`/api/` 转发到 FastAPI，`/` 转发到 Vue 工作台。生产环境启用 HTTPS。

## 备份

使用 `deploy/scripts/backup-postgres.sh` 定期备份 PostgreSQL，并将备份复制到安全目录或 OSS。

## 排障

- API 健康检查：`/health`。
- 查看日志：`docker compose -f deploy/docker-compose.yml logs -f`。
- 重启服务：`docker compose -f deploy/docker-compose.yml restart <service>`。
- 异常来源应先禁用，再查看抓取日志和 robots/限频配置。
