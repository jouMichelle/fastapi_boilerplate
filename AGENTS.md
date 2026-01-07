# Repository Guidelines

## 项目结构与模块组织
- `app/` 为主应用代码，含 `api/`、`core/`、`services/`、`dal/`、`models/`、`schemas/`、`tasks/`、`utils/`。
- `tests/` 存放测试，建议按 `unit/`、`integration/`、`api/` 划分；`migrations/` 为 Alembic 迁移脚本。
- `configs/` 放应用与日志配置，`deployment/` 放 Docker 与环境示例，`static/` 放静态资源。
- 约定目录：正式文档 `docs/`，讨论方案 `discuss/`，脚本 `scripts/*.sh`，日志 `logs/`，示例 `examples/`。

## 构建、测试与本地开发
- 安装依赖：`uv sync` 或 `pip install -e .`。
- 本地运行：`python run.py` 或 `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`。
- Docker 启动：`docker-compose -f deployment/docker-compose.dev.yml up -d`，生产使用 `deployment/docker-compose.yml`。
- 数据库迁移：`alembic revision --autogenerate -m "描述"`，`alembic upgrade head`。

## 编码风格与命名约定
- Python 4 空格缩进；变量/函数用 `snake_case`，类用 `PascalCase`。
- 业务逻辑放 `app/services/`，数据访问放 `app/dal/`，避免跨层耦合。
- 质量工具：`ruff check .`（lint），`mypy app/`（类型检查），行宽 120。

## 测试指南
- 测试框架：`pytest` + `pytest-asyncio`，入口为 `tests/`。
- 文件命名 `test_*.py`，建议按模块目录组织测试。
- 运行：`pytest tests/` 或 `pytest tests/api`。

## 提交与 PR 指南
- 提交信息遵循 Conventional Commits：`type(scope): subject`。
- PR 需包含变更说明、关联问题、配置/迁移说明、测试结果；影响接口时附示例或截图。

## 安全与配置
- 参考 `configs/secrets.example.yaml` 与 `deployment/env.example` 配置本地环境，不提交真实密钥。
- 运行日志统一输出到 `logs/`。

## 协作与自动化
- 完成代码创建/修改/重构后，追加记录到 `codex_operateLog.md`，包含日期、简述与关键 diff 片段。
