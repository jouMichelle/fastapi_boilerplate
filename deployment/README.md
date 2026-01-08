# Docker 部署指南

本文档介绍如何使用 Docker 部署 FastAPI 应用。

## 目录结构

```
deployment/
├── docker/
│   ├── Dockerfile         # 生产环境镜像
│   ├── Dockerfile.dev     # 开发环境镜像
│   ├── entrypoint.sh      # 启动脚本
│   └── .dockerignore      # 构建排除文件
├── docker-compose.yml      # 生产环境编排（需要构建）
├── docker-compose.prod.yml # 生产环境编排（使用预构建镜像）
├── docker-compose.dev.yml  # 开发环境编排
├── env.example            # 环境变量模板
└── README.md              # 本文档
```

## 快速开始

### 开发环境

```bash
# 1. 启动开发环境（使用 SQLite，支持热重载）
docker-compose -f deployment/docker-compose.dev.yml up -d

# 2. 查看日志
docker-compose -f deployment/docker-compose.dev.yml logs -f app

# 3. 停止服务
docker-compose -f deployment/docker-compose.dev.yml down
```

访问 http://localhost:8000/docs 查看 API 文档。

### 生产环境

```bash
# 1. 复制并配置环境变量
cp deployment/..env.example deployment/.env
vim deployment/.env  # 修改 SECRET_KEY 等配置

# 2. 构建并启动（包含 PostgreSQL + Redis）
docker-compose -f deployment/docker-compose.yml up -d --build

# 3. 查看服务状态
docker-compose -f deployment/docker-compose.yml ps

# 4. 查看日志
docker-compose -f deployment/docker-compose.yml logs -f app

# 5. 停止服务
docker-compose -f deployment/docker-compose.yml down
```

## 部署方式

### 方式一：服务器上构建部署

适合服务器可以访问 Git 仓库的场景。

```bash
# 1. 克隆代码到服务器
git clone https://github.com/your/repo.git
cd repo

# 2. 配置环境变量
cp deployment/..env.example deployment/.env
vim deployment/.env

# 3. 构建并启动
docker-compose -f deployment/docker-compose.yml up -d --build

# 4. 启用 Celery Worker（可选）
docker-compose -f deployment/docker-compose.yml --profile worker up -d
```

### 方式二：导出镜像部署（推荐）

适合服务器无法访问 Git 仓库，或需要统一镜像版本的场景。

> **注意**：此方式只部署应用容器，需要自行准备外部数据库（PostgreSQL/MySQL）和缓存（Redis）服务。

#### 前置要求

- 外部 PostgreSQL 或 MySQL 数据库
- 外部 Redis 服务（可选，用于缓存和 Celery）

#### 步骤 1：本地构建并导出镜像

```bash
# 进入项目根目录
cd /path/to/fastapi_boilerplate

# 构建生产镜像
docker build -t fastapi-app:latest -f deployment/docker/Dockerfile .

# 导出镜像为压缩文件
docker save fastapi-app:latest | gzip > fastapi-app.tar.gz

# 查看镜像大小
ls -lh fastapi-app.tar.gz
```

#### 步骤 2：准备部署文件

需要传输到服务器的文件：
```
fastapi-app.tar.gz          # 镜像文件
deployment/docker-compose.prod.yml  # 编排文件
deployment/env.example      # 环境变量模板
```

#### 步骤 3：传输到服务器

```bash
# 创建服务器目录
ssh user@server "mkdir -p /opt/fastapi-app"

# 传输文件
scp fastapi-app.tar.gz user@server:/opt/fastapi-app/
scp deployment/docker-compose.prod.yml user@server:/opt/fastapi-app/docker-compose.yml
scp deployment/..env.example user@server:/opt/fastapi-app/.env
```

#### 步骤 4：服务器上部署

```bash
# 登录服务器
ssh user@server
cd /opt/fastapi-app

# 加载镜像
docker load < fastapi-app.tar.gz

# 验证镜像已加载
docker images | grep fastapi-app

# 修改环境变量（重要！）
vim .env
# 必须配置：
# - DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
# - SECRET_KEY=<生成一个强密码>
# - REDIS_URL=redis://host:6379/0  (可选)

# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app
```

#### 步骤 5：验证部署

```bash
# 健康检查
curl http://localhost:8000/health

# 查看 API 文档
# 浏览器访问 http://your-server-ip:8000/docs
```

#### 更新部署

```bash
# 本地重新构建镜像
docker build -t fastapi-app:latest -f deployment/docker/Dockerfile .
docker save fastapi-app:latest | gzip > fastapi-app.tar.gz

# 传输到服务器
scp fastapi-app.tar.gz user@server:/opt/fastapi-app/

# 服务器上更新
ssh user@server
cd /opt/fastapi-app
docker load < fastapi-app.tar.gz
docker-compose up -d --force-recreate
```

### 方式三：单容器运行

适合简单场景或已有外部数据库。

```bash
# 加载镜像
docker load < fastapi-app.tar.gz

# 运行容器
docker run -d \
  --name fastapi-app \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname \
  -e SECRET_KEY=your-secret-key \
  -e REDIS_URL=redis://host:6379/0 \
  -v /data/app/logs:/app/logs \
  fastapi-app:latest

# 查看日志
docker logs -f fastapi-app
```

## 环境变量

| 变量 | 说明 | 默认值 | 必填 |
|------|------|--------|------|
| `DATABASE_URL` | 数据库连接字符串 | - | ✅ |
| `SECRET_KEY` | JWT 密钥 | - | ✅ |
| `REDIS_URL` | Redis 连接字符串 | - | 可选 |
| `APP_PORT` | 应用端口 | 8000 | |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间（分钟） | 30 | |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 刷新 Token 过期时间（天） | 7 | |

### 数据库连接字符串格式

```bash
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# MySQL
DATABASE_URL=mysql+aiomysql://user:password@host:3306/dbname

# SQLite（仅开发环境）
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
```

### 生成安全的 SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 服务说明

### 生产环境服务

**docker-compose.prod.yml**（使用预构建镜像）

| 服务 | 端口 | 说明 |
|------|------|------|
| app | 8000 | FastAPI 应用（Gunicorn + Uvicorn） |

**docker-compose.yml**（服务器上构建）

| 服务 | 端口 | 说明 |
|------|------|------|
| app | 8000 | FastAPI 应用（Gunicorn + Uvicorn） |

> 两种生产配置都需要外部提供数据库和 Redis 服务

### 开发环境服务（docker-compose.dev.yml）

| 服务 | 端口 | 说明 |
|------|------|------|
| app | 8000 | FastAPI 应用（热重载模式，默认 SQLite） |

> 开发环境默认使用 SQLite，如需连接外部数据库可通过环境变量配置

## 常用命令

```bash
# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f [service]

# 进入容器
docker-compose exec app bash

# 重启服务
docker-compose restart app

# 停止并删除容器
docker-compose down

# 停止并删除容器、数据卷
docker-compose down -v

# 清理未使用的镜像
docker image prune -f
```

## 数据库迁移

```bash
# 进入容器执行迁移
docker-compose exec app alembic upgrade head

# 或设置环境变量自动迁移
RUN_MIGRATIONS=true docker-compose up -d
```

## 健康检查

应用提供健康检查端点：

```bash
curl http://localhost:8000/health
# {"status": "healthy", "app": "FastAPI Boilerplate"}
```

Docker 会自动检查服务健康状态，不健康时自动重启。

## 日志管理

```bash
# 查看应用日志
docker-compose logs -f app

# 导出日志文件
docker cp fastapi-app:/app/logs ./logs_backup

# 查看 Docker Volume
docker volume ls
docker volume inspect <volume_name>
```

## 数据备份

```bash
# 备份 PostgreSQL 数据库
docker-compose exec db pg_dump -U postgres fastapi_db > backup.sql

# 恢复数据库
cat backup.sql | docker-compose exec -T db psql -U postgres fastapi_db
```

## 注意事项

1. **生产环境必须修改 SECRET_KEY** - 使用强随机密钥
2. **PostgreSQL 密码应使用强密码** - 不要使用默认值
3. **建议使用 HTTPS 反向代理** - 如 Nginx + Let's Encrypt
4. **定期备份数据库数据** - 设置定时任务
5. **监控服务状态** - 配置告警通知
