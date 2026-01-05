# 项目上下文 (GEMINI.md)

本文档旨在为 Gemini 提供关于本项目的上下文信息、架构设计及开发规范。

## 1. 项目概述

**项目名称**: fastapi_boilerplate
**类型**: Python / FastAPI 后端项目
**状态**: 初始脚手架（目前大部分源文件为空，处于待实现状态）
**核心技术**:
- **Web 框架**: FastAPI
- **数据库 ORM**: SQLAlchemy (预计)
- **迁移工具**: Alembic
- **任务队列**: Celery (根据 `app/tasks` 目录推断)
- **容器化**: Docker & Docker Compose

本项目采用分层架构设计，旨在提供一个结构清晰、可扩展的 FastAPI 应用模板。

## 2. 核心架构与目录结构

项目遵循严格的分层架构，各层职责如下：

```
app/
├── api/             # 接口层：处理 HTTP 请求与响应
│   └── v1/          # 版本化接口 (admin, system, user)
├── bootstrap/       # 启动层：应用工厂、生命周期管理、中间件注册
├── core/            # 核心层：全局配置、异常处理、日志、安全工具
├── dal/             # 数据访问层 (Data Access Layer)：Repository 模式，直接操作数据库
├── deps/            # 依赖层：FastAPI 依赖注入 (Auth, DB session, Rate limit)
├── http_middleware/ # 中间件：处理请求/响应拦截 (日志, Request ID, 安全头)
├── models/          # 模型层：数据库 ORM 模型定义
├── schemas/         # 结构层：Pydantic 数据验证与序列化模型
├── services/        # 服务层：核心业务逻辑实现
├── tasks/           # 任务层：异步后台任务
└── utils/           # 工具层：通用辅助函数
```

**配置与部署:**
- `configs/`: 存放 YAML 格式的配置文件。
- `deployment/`: Docker 部署相关文件。
- `scripts/`: 数据库初始化等维护脚本。
- `migrations/`: Alembic 数据库迁移脚本。

## 3. 开发规范

### 3.1 分层依赖原则
开发新功能时，请严格遵守单向依赖原则：
`API Layer` -> `Service Layer` -> `DAL (Repository)` -> `Models`

1. **API 层** (`app/api`): 仅负责参数解析、调用 Service、返回响应。不含复杂业务逻辑。
2. **Service 层** (`app/services`): 处理业务逻辑、事务控制。调用 DAL 层获取数据。
3. **DAL 层** (`app/dal`): 封装所有数据库查询与操作。
4. **Schemas** (`app/schemas`): 用于 API 输入输出的数据传输对象 (DTO)。

### 3.2 常用开发命令 (参考)

由于项目尚处于初始化阶段，以下命令基于目录结构和常见实践推断：

*   **启动开发服务器**:
    ```bash
    # 使用 uvicorn 直接启动
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    # 或使用运行脚本 (需确认 run.py 内容)
    python run.py
    ```

*   **数据库迁移 (Alembic)**:
    ```bash
    # 生成迁移脚本
    alembic revision --autogenerate -m "描述"
    # 执行迁移
    alembic upgrade head
    ```

*   **初始化数据**:
    ```bash
    python scripts/init_db.py
    ```

*   **测试**:
    ```bash
    pytest tests/
    ```

## 4. 配置文件

配置文件位于 `configs/` 目录：
- `app.yaml`: 应用主配置
- `logging.yaml`: 日志配置
- `models.yaml`: 模型相关配置
- `secrets.example.yaml`: 敏感信息模板 (需复制为 `secrets.yaml`)

## 5. 注意事项

- 当前 `pyproject.toml`, `app/main.py` 等关键文件为空，需要优先完成项目的基础依赖安装和入口代码编写。
- 在编写代码时，请参考 `CLAUDE.md` 中定义的详细规范。
