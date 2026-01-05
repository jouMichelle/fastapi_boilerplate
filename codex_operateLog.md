# Codex 操作日志

## 2026-01-04 11:19:41
- 描述：新增仓库贡献指南 `AGENTS.md`，明确目录约定、开发与提交规范。
- 关键变更：
```diff
+# Repository Guidelines
+## 项目结构与模块组织
+- `app/` 为主应用代码，常见子模块包括 `api/`、`core/`、`models/`、`schemas/`、`services/`、`dal/`、`tasks/`、`utils/`。
+- `tests/` 用于测试，结构包含 `unit/`、`integration/`、`api/`。
+## 构建、测试与本地开发
+- 常见本地启动示例（以实际代码为准）：
+  - `python -m uvicorn app.main:app --reload`
```

## 2026-01-04 16:17:46
- 描述：支持 `configs/app.yaml` 作为默认配置并与 `.env` / `.env.{env}` 叠加覆盖，补齐 CORS 配置字段。
- 关键变更：
```diff
class Settings(BaseSettings):
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "FastAPI App"
    CORS_METHODS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    @classmethod
    def settings_customise_sources(...):
        return init_settings, env_settings, dotenv_source, file_secret_settings, _yaml_settings_source
```

## 2026-01-04 21:29:24
- 描述：新增 `.env` 与 `.env.example`，提供多环境默认与 CORS/数据库示例配置。
- 关键变更：
```diff
+APP_ENV=development
+APP_NAME="FastAPI Boilerplate"
+PORT=8000
+CORS_ORIGINS='["http://localhost:3000","http://localhost:8080"]'
+DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_db"
```

## 2026-01-04 21:30:53
- 描述：新增 `.env.development` 与 `.env.production`，补齐多环境配置示例。
- 关键变更：
```diff
+.env.development
+APP_ENV=development
+DEBUG=true
+
+.env.production
+APP_ENV=production
+PORT=80
```
