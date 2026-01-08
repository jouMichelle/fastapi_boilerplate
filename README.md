# FastAPI Simple Boilerplate

简单的 FastAPI 项目脚手架，适合小型项目快速开发。

## 特性

- **简洁架构** - 扁平化目录结构，易于理解和扩展
- **API Key 鉴权** - 简单的接口保护机制
- **多数据库支持** - SQLite / PostgreSQL / MySQL
- **异步支持** - 全栈异步（FastAPI + SQLAlchemy 2.0）
- **外部服务客户端** - Redis + MinIO 开箱即用
- **日志系统** - Loguru 结构化日志
- **CORS 配置** - 开发/生产环境灵活配置
- **Docker 支持** - 简单的容器化部署

## 项目结构

```
├── app/
│   ├── api/                  # API 路由
│   ├── core/                 # 核心模块
│   │   ├── config.py         # 配置管理
│   │   ├── exceptions.py     # 异常定义
│   │   ├── logger.py         # 日志系统
│   │   ├── response.py       # 统一响应格式
│   │   └── security.py       # API Key 鉴权
│   ├── database/             # 数据库配置
│   ├── models/               # ORM 模型
│   ├── schemas/              # Pydantic 模型
│   ├── services/             # 业务逻辑
│   └── utils/                # 工具函数
├── client/                   # 外部服务客户端
│   ├── redis.py              # Redis 客户端
│   └── minio.py              # MinIO 客户端
├── configs/                  # 配置文件
├── main.py                   # 应用入口
├── Dockerfile
└── docker-compose.yml
```

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 2. 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置
vim .env
```

### 3. 运行应用

```bash
# 开发模式
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问 API

- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health
- 示例接口: http://localhost:8000/api/example

## 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `APP_ENV` | 环境 | `development` |
| `DEBUG` | 调试模式 | `false` |
| `DATABASE_URL` | 数据库连接 | `sqlite+aiosqlite:///./data/app.db` |
| `REDIS_URL` | Redis 连接 | `redis://localhost:6379/0` |
| `API_KEY` | API 密钥 | `your-api-key-change-in-production` |
| `SECRET_KEY` | 应用密钥 | `your-super-secret-key-change-in-production` |

### MinIO 配置

| 变量 | 说明 |
|------|------|
| `MINIO_ENDPOINT` | MinIO 服务地址 |
| `MINIO_ACCESS_KEY` | 访问密钥 |
| `MINIO_SECRET_KEY` | 秘密密钥 |

## API Key 鉴权

在需要保护的接口上使用 `verify_api_key` 依赖：

```python
from fastapi import Depends
from app.core.security import verify_api_key

@router.get("/protected", dependencies=[Depends(verify_api_key)])
async def protected_endpoint():
    return {"message": "OK"}
```

请求时在 Header 中添加：

```
X-API-Key: your-api-key
```

## 数据库操作

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db_session

@router.get("/items")
async def get_items(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Item))
    return result.scalars().all()
```

## 数据库迁移

```bash
# 生成迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```

## Docker 部署

```bash
# 开发环境
docker-compose -f deployment/docker-compose.dev.yml up -d

# 生产环境
docker-compose -f deployment/docker-compose.yml up -d
```

## 与完整版的区别

此简化版移除了：

| 功能 | 简化版 | 完整版 |
|------|--------|--------|
| 用户登录/注册 | ❌ | ✅ |
| JWT 认证 | ❌ | ✅ |
| 用户管理 | ❌ | ✅ |
| DAL 数据访问层 | ❌ | ✅ |
| 依赖注入层 | ❌ | ✅ |
| 中间件（请求ID/访问日志） | ❌ | ✅ |
| Celery 异步任务 | ❌ | ✅ |
| API 版本化 | ❌ | ✅ |

如需完整功能，请切换到 `main` 分支。
