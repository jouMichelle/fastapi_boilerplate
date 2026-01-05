# Repository Guidelines

## 项目结构与模块组织
- `app/` 为主应用代码，常见子模块包括 `api/`、`core/`、`models/`、`schemas/`、`services/`、`dal/`、`tasks/`、`utils/`。
- `tests/` 用于测试，结构包含 `unit/`、`integration/`、`api/`。
- `configs/` 存放应用与日志等配置（如 `app.yaml`、`logging.yaml`、`models.yaml`、`secrets.example.yaml`）。
- `migrations/` 为 Alembic 迁移脚本，`deployment/` 保存容器与环境示例，`static/` 放静态资源。
- 约定：正式文档放 `docs/`，讨论方案放 `discuss/`，脚本放 `scripts/`（Shell 脚本使用 `scripts/*.sh`），日志放 `logs/`，示例放 `examples/`。

## 构建、测试与本地开发
- 当前仓库未提供统一入口脚本，请先确认 `app/main.py` 与 `deployment/docker-compose*.yml` 的实际内容。
- 常见本地启动示例（以实际代码为准）：
  - `python -m uvicorn app.main:app --reload`
  - `docker compose -f deployment/docker-compose.yml up -d`
- 数据库初始化脚本位于 `scripts/init_db.py`，执行前需核对配置与参数。

## 编码风格与命名约定
- Python 采用 4 空格缩进；变量/函数使用 `snake_case`，类使用 `PascalCase`。
- 业务逻辑放在 `services/`，数据访问放在 `dal/`，避免模块职责混杂。
- 文档命名使用 `YYYY-MM-DD-HH-MM-SS-描述.md`，按目录约定归档。

## 测试指南
- 测试统一放在 `tests/`，按 `unit/`、`integration/`、`api/` 细分。
- 目前未发现测试框架配置，建议使用 `pytest` 并采用 `test_*.py` 命名。
- 关键修复或新增功能应补充最小可复现测试。

## 提交与 PR 规范
- Git 历史显示采用 Conventional Commits：`type(scope): subject`（如 `chore(config): ...`）。
- PR 建议包含：变更说明、关联问题/需求、配置或迁移说明、测试结果或截图（如影响接口/页面）。

## 安全与配置
- 不提交真实密钥或敏感信息，优先基于 `configs/secrets.example.yaml` 与 `deployment/env.example` 创建本地配置。
