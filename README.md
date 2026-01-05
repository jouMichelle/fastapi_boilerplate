# FastAPI Boilerplate

一个生产级 FastAPI 项目脚手架，采用分层架构设计，开箱即用。

## 特性

- **分层架构** - Router → Service → DAL → Model 清晰分层
- **认证授权** - JWT Bearer Token 认证，支持登录/注册/刷新令牌
- **多数据库支持** - SQLite / PostgreSQL / MySQL 无缝切换
- **日志系统** - Loguru + Request ID 请求追踪
- **统一响应** - 标准化 API 响应格式和错误码
- **通用工具** - 日期时间、ID 生成器等常用工具
- **中间件** - 访问日志、请求追踪、安全响应头
- **Docker 部署** - 完整的 Docker Compose 配置

## 快速开始

### 环境要求

- Python 3.11+
- uv (推荐) 或 pip

### 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 运行应用

```bash
# 开发模式
python run.py

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档。

## 项目结构

```
app/
├── api/v1/              # API 路由
│   ├── auth/            # 认证接口（登录/注册/刷新令牌）
│   └── user/            # 用户 CRUD 接口
├── bootstrap/           # 应用启动引导
│   ├── app_factory.py   # 应用工厂
│   ├── lifespan.py      # 生命周期管理
│   └── router.py        # 路由注册
├── core/                # 核心功能
│   ├── config.py        # 配置管理
│   ├── exceptions.py    # 异常定义
│   ├── logger.py        # 日志配置
│   ├── response.py      # 响应格式
│   └── security.py      # 安全工具（JWT/密码）
├── dal/                 # 数据访问层
│   ├── base.py          # Repository 基类
│   ├── session.py       # 数据库会话
│   └── user/            # 用户 Repository
├── deps/                # 依赖注入
│   ├── auth.py          # 认证依赖
│   ├── db.py            # 数据库依赖
│   └── context.py       # 请求上下文
├── http_middleware/     # HTTP 中间件
├── models/              # ORM 模型
├── schemas/             # Pydantic Schema
├── services/            # 业务逻辑层
│   ├── auth/            # 认证服务
│   └── user/            # 用户服务
├── tasks/               # Celery 异步任务
└── utils/               # 工具函数
    └── common/          # 通用工具
```

## API 接口

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录 |
| POST | `/api/v1/auth/refresh` | 刷新令牌 |

### 用户接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/users` | 创建用户 | 否 |
| GET | `/api/v1/users` | 用户列表 | 是 |
| GET | `/api/v1/users/me` | 当前用户 | 是 |
| GET | `/api/v1/users/{id}` | 用户详情 | 是 |
| PUT | `/api/v1/users/{id}` | 更新用户 | 是 |
| DELETE | `/api/v1/users/{id}` | 删除用户 | 是 |

## 配置说明

### 环境变量

```bash
# 应用配置
APP_NAME=FastAPI Boilerplate
DEBUG=true

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./data/app.db

# JWT 配置
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 多数据库支持

```bash
# SQLite（开发环境）
DATABASE_URL=sqlite+aiosqlite:///./data/app.db

# PostgreSQL（生产环境）
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname

# MySQL
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/dbname
```

## 开发命令

```bash
# 运行测试
pytest tests/

# 代码检查
ruff check .

# 类型检查
mypy app/

# 数据库迁移
alembic revision --autogenerate -m "描述"
alembic upgrade head
```

## Docker 部署

```bash
# 开发环境
docker-compose -f deployment/docker-compose.dev.yml up -d

# 生产环境
docker-compose -f deployment/docker-compose.yml up -d
```

## 技术栈

| 组件 | 技术 |
|------|------|
| Web 框架 | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| 数据验证 | Pydantic v2 |
| 认证 | python-jose (JWT) |
| 密码哈希 | passlib + bcrypt |
| 日志 | Loguru |
| 任务队列 | Celery + Redis |
| 数据库迁移 | Alembic |

## 许可证

Apache License 2.0
