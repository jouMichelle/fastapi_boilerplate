# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 **FastAPI 简化版脚手架**（当前分支：`simple`），适合小型项目快速开发。

**核心技术栈：**
- Python 3.11+
- FastAPI 0.115+
- SQLAlchemy 2.0 (异步)
- Alembic (数据库迁移)
- Pydantic 2.10+ (数据验证)
- Redis (缓存)
- MinIO (对象存储)
- Loguru (日志系统)

**与完整版区别：** 本项目移除了用户认证、DAL 层、中间件、Celery 等复杂功能，保留核心特性。如需完整功能，请切换到 `main` 分支。

## 核心架构

```
app/
├── api/              # API 路由层
│   ├── __init__.py  # 路由注册
│   └── example.py   # 示例路由
├── core/             # 核心功能
│   ├── config.py    # 配置管理（环境变量 + YAML）
│   ├── constants.py # 常量定义
│   ├── exceptions.py # 自定义异常类
│   ├── logger.py    # 企业级日志系统
│   ├── response.py  # 统一响应格式
│   └── security.py  # API Key 鉴权
├── database/         # 数据库模块
│   └── session.py   # 数据库会话管理
├── models/           # ORM 模型
│   └── base.py      # 模型基类（时间戳、软删除）
├── schemas/          # Pydantic 模型
│   └── common.py    # 通用 Schema
├── services/         # 业务逻辑层
└── utils/            # 工具函数
```

**关键入口点：**
- `main.py` - 应用入口
- `app/api/__init__.py` - 路由注册
- `app/core/config.py` - 配置管理（支持环境变量覆盖）

## 开发命令

```bash
# 切换 conda 环境（必需）
source /opt/anaconda3/bin/activate agent_v1_3.11
# 或
conda activate agent_v1_3.11

# 运行应用（开发模式）
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 数据库迁移
alembic revision --autogenerate -m "描述"
alembic upgrade head
alembic downgrade -1

# 运行测试
pytest tests/
pytest tests/unit/           # 单元测试
pytest tests/integration/    # 集成测试
pytest tests/api/            # API 测试
pytest -xvs tests/path/to/test_file.py::test_function  # 单个测试

# 代码质量检查
ruff check .       # 代码检查
ruff format .      # 代码格式化
mypy app/          # 类型检查

# Docker 部署
docker-compose -f deployment/docker-compose.dev.yml up -d    # 开发
docker-compose -f deployment/docker-compose.yml up -d        # 生产
```

## 配置管理

**配置文件：**
- `configs/app.yaml` - 应用配置（YAML 格式）
- `.env` - 环境变量（复制自 `.env.example`）

**配置加载优先级：** 环境变量 > .env 文件 > YAML 配置

**关键配置项：**
```python
DATABASE_URL      # 数据库连接（支持 SQLite/PostgreSQL/MySQL）
REDIS_URL         # Redis 连接
API_KEY           # API 鉴权密钥
SECRET_KEY        # 应用密钥
MINIO_ENDPOINT    # MinIO 服务地址
CORS_ORIGINS      # CORS 允许的源
```

## 分层架构开发规范

简化版采用三层架构（无 DAL 层）：

```
API 层
    ↓
Schema 层
    ↓
Service 层
    ↓
Model 层 (SQLAlchemy ORM)
```

**依赖方向：** API → Service → Model

**新增功能开发流程：**
1. 在 `app/models/` 定义 SQLAlchemy ORM 模型
2. 在 `app/schemas/` 定义请求/响应 Pydantic 模型
3. 在 `app/services/` 实现业务逻辑
4. 在 `app/api/` 定义路由和端点

## API Key 鉴权

使用 `app/core/security.py` 中的 `verify_api_key` 依赖保护接口：

```python
from fastapi import Depends
from app.core.security import verify_api_key

@router.get("/protected", dependencies=[Depends(verify_api_key)])
async def protected_endpoint():
    return {"message": "OK"}
```

**请求 Header：**
```
X-API-Key: your-api-key
```

## 数据库操作

**数据库会话依赖：**
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db_session

@router.get("/items")
async def get_items(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Item))
    return result.scalars().all()
```

**模型基类特性：**
- `id` - 主键
- `created_at` / `updated_at` - 自动时间戳
- `is_deleted` / `deleted_at` - 软删除支持
- `to_dict()` - 转换为字典方法

## 统一响应格式

**使用 `app/core/response.py` 中的工具函数：**
```python
from app.core.response import success, error, paginate

# 成功响应
return success(data={"key": "value"}, message="操作成功")

# 错误响应
return error(code=400, message="参数错误")

# 分页响应
return paginate(data=items, total=100, page=1, page_size=20)
```

## 外部服务客户端

**Redis 客户端：** `client/redis.py`
```python
redis_client = await get_redis_client()
await redis_client.set("key", "value", ex=3600)
value = await redis_client.get("key")
```

**MinIO 客户端：** `client/minio.py`
```python
minio_client = get_minio_client()
minio_client.upload_file(bucket, object_name, file_path)
url = minio_client.get_presigned_url(bucket, object_name, expires=3600)
```

## 异常处理

**预定义异常类：** `app/core/exceptions.py`
- `BadRequestError` (400)
- `UnauthorizedError` (401)
- `ForbiddenError` (403)
- `NotFoundError` (404)
- `ConflictError` (409)
- `ValidationError` (422)
- `InternalServerError` (500)

## 与完整版 (main 分支) 的区别

| 功能 | 简化版 (simple) | 完整版 (main) |
|------|-----------------|---------------|
| 用户登录/注册 | ❌ | ✅ |
| JWT 认证 | ❌ | ✅ |
| 用户管理 | ❌ | ✅ |
| DAL 数据访问层 | ❌ | ✅ |
| 依赖注入层 | ❌ | ✅ |
| 中间件（访问日志） | ✅ | ✅ |
| Celery 异步任务 | ❌ | ✅ |
| API 版本化 | ❌ | ✅ |
| 多数据库支持 | ✅ | ❌ |
| API Key 鉴权 | ✅ | ✅ |
| 数据库支持 | ✅ | ✅ |
| Redis/MinIO | ✅ | ✅ |
| 日志系统 | ✅ | ✅ |

**何时切换到 main 分支：**
- 需要完整的用户认证系统
- 需要复杂的业务逻辑和大型应用
- 需要异步任务队列
- 需要请求追踪和访问日志
