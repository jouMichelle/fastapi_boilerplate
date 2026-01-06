# Docker 部署指南

本文档介绍如何使用 Docker 部署 FastAPI 应用。

## 目录结构

```
deployment/
├── docker/
│   ├── Dockerfile        # 生产环境镜像
│   ├── Dockerfile.dev    # 开发环境镜像
│   ├── entrypoint.sh     # 启动脚本
│   └── .dockerignore     # 构建排除文件
├── docker-compose.yml     # 生产环境编排
├── docker-compose.dev.yml # 开发环境编排
├── env.example           # 环境变量模板
└── README.md             # 本文档
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
cp deployment/env.example deployment/.env
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

### 方式一：使用 Docker Compose（推荐）

适合单机部署，包含完整的服务栈。

```bash
# 生产环境
docker-compose -f deployment/docker-compose.yml up -d

# 启用 Celery Worker（可选）
docker-compose -f deployment/docker-compose.yml --profile worker up -d
```

### 方式二：导出镜像部署

适合无法访问 Git 仓库的服务器。

```bash
# 本地构建镜像
docker build -t fastapi-app:latest -f deployment/docker/Dockerfile .

# 导出镜像文件
docker save fastapi-app:latest | gzip > fastapi-app.tar.gz

# 传输到服务器
scp fastapi-app.tar.gz user@server:/path/to/

# 服务器上加载镜像
docker load < fastapi-app.tar.gz

# 启动容器
docker run -d \
  --name fastapi-app \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/dbname \
  -e SECRET_KEY=your-secret-key \
  fastapi-app:latest
```

### 方式三：服务器上构建

适合有 Git 访问权限的服务器。

```bash
# 克隆代码
git clone https://github.com/your/repo.git
cd repo

# 构建并启动
docker-compose -f deployment/docker-compose.yml up -d --build
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `APP_ENV` | 运行环境 | production |
| `DEBUG` | 调试模式 | false |
| `DATABASE_URL` | 数据库连接 | - |
| `REDIS_URL` | Redis 连接 | - |
| `SECRET_KEY` | JWT 密钥 | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间 | 30 |

## 服务说明

### 生产环境服务

| 服务 | 端口 | 说明 |
|------|------|------|
| app | 8000 | FastAPI 应用（Gunicorn + Uvicorn） |
| db | 5432 | PostgreSQL 数据库 |
| redis | 6379 | Redis 缓存 |
| worker | - | Celery Worker（可选） |

### 开发环境服务

| 服务 | 端口 | 说明 |
|------|------|------|
| app | 8000 | FastAPI 应用（热重载模式） |

## 常用命令

```bash
# 查看运行状态
docker-compose -f deployment/docker-compose.yml ps

# 查看日志
docker-compose -f deployment/docker-compose.yml logs -f [service]

# 进入容器
docker-compose -f deployment/docker-compose.yml exec app bash

# 重启服务
docker-compose -f deployment/docker-compose.yml restart app

# 重新构建
docker-compose -f deployment/docker-compose.yml up -d --build

# 清理资源
docker-compose -f deployment/docker-compose.yml down -v --rmi local
```

## 数据库迁移

```bash
# 进入容器执行迁移
docker-compose -f deployment/docker-compose.yml exec app alembic upgrade head

# 或设置环境变量自动迁移
RUN_MIGRATIONS=true docker-compose -f deployment/docker-compose.yml up -d
```

## 健康检查

应用提供健康检查端点：

```bash
curl http://localhost:8000/health
# {"status": "healthy", "app": "FastAPI Boilerplate"}
```

Docker 会自动检查服务健康状态，不健康时自动重启。

## 日志管理

生产环境日志存储在 Docker Volume 中：

```bash
# 查看日志位置
docker volume inspect fastapi_app_logs

# 导出日志
docker cp fastapi-app:/app/logs ./logs_backup
```

## 注意事项

1. **生产环境必须修改 SECRET_KEY**
2. **PostgreSQL 密码应使用强密码**
3. **建议使用 HTTPS 反向代理（如 Nginx）**
4. **定期备份数据库数据**
