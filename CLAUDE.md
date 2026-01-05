# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 FastAPI 项目样板，采用分层架构设计。基于 Apache License 2.0 开源。

## 核心架构

```
app/
├── api/v1/          # RESTful API 端点（admin、system、user 模块）
├── bootstrap/       # 应用启动引导（工厂模式）
├── core/            # 核心功能（配置、异常、日志、安全）
├── dal/             # 数据访问层 (Repository Pattern)
├── deps/            # FastAPI 依赖注入
├── http_middleware/ # HTTP 中间件
├── models/          # SQLAlchemy ORM 模型
├── schemas/         # Pydantic 数据验证模式
├── services/        # 业务逻辑层
├── tasks/           # 异步任务 (Celery)
└── utils/           # 工具函数
```

**关键入口点：**
- `app/bootstrap/app_factory.py` - FastAPI 应用工厂
- `app/bootstrap/router.py` - 路由注册
- `app/bootstrap/lifespan.py` - 应用生命周期
- `run.py` - 主运行入口

## 开发命令

```bash
# 运行应用（开发模式）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 run.py
python run.py

# 数据库迁移
alembic revision --autogenerate -m "描述"
alembic upgrade head
alembic downgrade -1

# 初始化数据库
python scripts/init_db.py

# 运行测试
pytest tests/
pytest tests/unit/           # 单元测试
pytest tests/integration/    # 集成测试
pytest tests/api/            # API 测试
pytest -xvs tests/path/to/test_file.py::test_function  # 单个测试

# Docker 部署
docker-compose -f deployment/docker-compose.yml up -d        # 生产
docker-compose -f deployment/docker-compose.dev.yml up -d    # 开发
```

## 配置管理

- `configs/app.yaml` - 应用配置
- `configs/logging.yaml` - 日志配置
- `configs/models.yaml` - 模型配置
- `configs/secrets.example.yaml` - 密钥模板（复制为 secrets.yaml 使用）
- `deployment/env.example` - 环境变量模板

## 分层架构开发规范

新增功能时遵循以下分层结构：

1. **API 层** (`app/api/v1/`): 定义路由和端点
2. **Schema 层** (`app/schemas/`): 定义请求/响应 Pydantic 模型
3. **Service 层** (`app/services/`): 实现业务逻辑
4. **DAL 层** (`app/dal/`): 实现数据访问操作
5. **Model 层** (`app/models/`): 定义 SQLAlchemy ORM 模型

依赖方向：API → Service → DAL → Model

## 中间件

- `access_log.py` - 访问日志记录
- `request_id.py` - 请求追踪 ID
- `security_headers.py` - 安全响应头

## 依赖注入

`app/deps/` 提供可复用的 FastAPI 依赖：
- `auth.py` - 认证相关依赖
- `db.py` - 数据库会话依赖
- `rate_limit.py` - 速率限制依赖
- `context.py` - 请求上下文依赖
