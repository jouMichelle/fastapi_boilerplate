# 项目上下文 (GEMINI.md)

本文档为 Gemini 提供关于 `fastapi_boilerplate` 项目的上下文信息、架构设计及开发规范。

## 1. 项目概述

**项目名称**: fastapi_boilerplate
**类型**: Python / FastAPI 后端项目
**状态**: 开发中 (脚手架/模板)
**核心技术**:
- **Web 框架**: FastAPI (>=0.115.0)
- **数据库 ORM**: SQLAlchemy 2.0 (Async)
- **数据库驱动**: asyncpg (PostgreSQL), aiosqlite (SQLite), aiomysql (MySQL)
- **数据验证**: Pydantic v2
- **迁移工具**: Alembic
- **任务队列**: Celery + Redis
- **认证授权**: JWT (python-jose), Passlib (bcrypt)
- **日志系统**: Loguru
- **包管理**: uv (推荐) 或 pip (pyproject.toml)

本项目采用严格的分层架构，旨在提供一个结构清晰、可扩展且符合生产标准的 FastAPI 应用模板。

## 2. 核心架构与目录结构

项目遵循严格的单向依赖分层架构：

```
app/
├── api/             # 接口层：处理 HTTP 请求与响应
│   └── v1/          # 版本化接口 (auth, user, etc.)
├── bootstrap/       # 启动层：应用工厂、生命周期管理、中间件注册
├── core/            # 核心层：全局配置、异常处理、日志、安全工具
├── dal/             # 数据访问层 (Data Access Layer)：Repository 模式，直接操作数据库
├── deps/            # 依赖层：FastAPI 依赖注入 (Auth, DB session, Rate limit)
├── http_middleware/ # 中间件：处理请求/响应拦截 (Access Log, Request ID, Security Headers)
├── models/          # 模型层：SQLAlchemy ORM 模型定义
├── schemas/         # 结构层：Pydantic 数据验证与序列化模型 (DTO)
├── services/        # 服务层：核心业务逻辑实现 (调用 DAL)
├── tasks/           # 任务层：Celery 异步后台任务
└── utils/           # 工具层：通用辅助函数
```

**配置与部署:**
- `configs/`: YAML 配置文件 (`app.yaml`, `logging.yaml`, `models.yaml`, `secrets.yaml`).
- `deployment/`: Docker 部署相关文件 (`docker-compose*.yml`, `Dockerfile`).
- `migrations/`: Alembic 数据库迁移脚本.
- `scripts/`: 维护脚本 (如 `init_db.py`).
- `tests/`: 测试用例 (`unit`, `integration`, `api`).

## 3. 开发规范

### 3.1 分层依赖原则
开发新功能时，必须严格遵守单向依赖原则，禁止跨层反向调用：
`API Layer` -> `Service Layer` -> `DAL (Repository)` -> `Models`

1.  **API 层 (`app/api`)**: 仅负责参数解析、依赖注入、调用 Service、返回响应。**禁止**在此层直接操作数据库。
2.  **Service 层 (`app/services`)**: 处理业务逻辑、事务控制、复杂计算。调用 DAL 层获取数据。
3.  **DAL 层 (`app/dal`)**: 封装所有数据库查询与操作 (CRUD)。返回 ORM 模型或标量。
4.  **Schemas (`app/schemas`)**: 用于 API 输入输出的数据传输对象 (DTO)。Service 层和 API 层之间通常通过 Model 或 Schema 传递数据。

### 3.2 代码风格与规范
-   **类型注解**: 所有函数参数和返回值必须包含 Python 类型注解 (Type Hints)。
-   **Linting**: 使用 `ruff` 进行代码检查和格式化。
-   **Testing**: 使用 `pytest` 编写测试，尽量覆盖核心业务逻辑。

## 4. 常用开发命令

*   **安装依赖**:
    ```bash
    uv sync  # 使用 uv
    # 或
    pip install -e .[dev]
    ```

*   **启动开发服务器**:
    ```bash
    # 使用 Python 脚本
    python run.py
    # 或直接使用 uvicorn
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

*   **代码质量检查**:
    ```bash
    ruff check .   # Linting
    mypy app/      # 类型检查
    ```

*   **测试**:
    ```bash
    pytest tests/
    ```

*   **数据库迁移 (Alembic)**:
    ```bash
    # 生成迁移脚本
    alembic revision --autogenerate -m "描述你的变更"
    # 执行迁移
    alembic upgrade head
    ```

*   **Docker 启动**:
    ```bash
    docker-compose -f deployment/docker-compose.dev.yml up -d
    ```

## 5. 配置文件

配置文件位于 `configs/` 目录，通过 `app.core.config.settings` 加载。
-   `app.yaml`: 应用主配置 (Server, CORS, Pagination, Rate Limit, Upload).
-   `logging.yaml`: 日志详细配置.
-   `models.yaml`: 数据库模型相关配置.
-   `secrets.yaml`: **敏感配置** (Key, DB URL, Passwords). **不要提交此文件**. 请复制 `secrets.example.yaml` 创建。

## 6. 注意事项

-   **环境变量**: 项目支持 `.env` 文件，但主要配置建议通过 `configs/*.yaml` 管理。
-   **异步编程**: 项目全栈异步 (FastAPI + Async SQLAlchemy)，请确保所有 I/O 操作使用 `await`。
-   **安全**: 生产环境部署时，务必修改 `secrets.yaml` 中的 `SECRET_KEY` 并确保 `DEBUG=False`。
