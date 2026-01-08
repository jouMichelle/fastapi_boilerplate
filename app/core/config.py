"""应用配置管理模块"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import field_validator
from pydantic_settings import BaseSettings, DotEnvSettingsSource, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类，从环境变量加载配置"""

    model_config = SettingsConfigDict(
        env_file=None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用配置
    APP_NAME: str = "FastAPI App"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "FastAPI App"
    APP_ENV: str = "development"
    DEBUG: bool = False

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False

    # ============================================================
    # 数据库配置（支持分离式配置和直接 URL 配置）
    # ============================================================

    # --- SQLite 配置（分离式） ---
    SQLITE_PATH: str = "./data/app.db"

    # --- PostgreSQL 配置（分离式） ---
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "fastapi_db"

    # --- MySQL 配置（分离式） ---
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DB: str = "fastapi_db"

    # --- 直接 URL 配置（可选，优先级高于分离式配置） ---
    # 如果配置了这些字段，将覆盖分离式配置
    _SQLITE_URL: str | None = None
    _POSTGRES_URL: str | None = None
    _MYSQL_URL: str | None = None

    # --- 默认数据库选择 ---
    DEFAULT_DATABASE: str = "sqlite"  # sqlite | postgres | mysql

    @property
    def SQLITE_URL(self) -> str:
        """
        获取 SQLite 连接 URL

        优先级：直接配置 > 分离式组装
        """
        if self._SQLITE_URL:
            return self._SQLITE_URL
        return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"

    @property
    def POSTGRES_URL(self) -> str:
        """
        获取 PostgreSQL 连接 URL

        优先级：直接配置 > 分离式组装
        """
        if self._POSTGRES_URL:
            return self._POSTGRES_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def MYSQL_URL(self) -> str:
        """
        获取 MySQL 连接 URL

        优先级：直接配置 > 分离式组装
        """
        if self._MYSQL_URL:
            return self._MYSQL_URL
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # 安全配置
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    API_KEY: str = "your-api-key-change-in-production"

    # MinIO 配置
    MINIO_ENDPOINT: str = ""
    MINIO_ACCESS_KEY: str = ""
    MINIO_SECRET_KEY: str = ""

    # CORS 配置
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    CORS_METHODS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True

    # 日志配置
    LOG_LEVEL: str = "INFO"

    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    @field_validator("CORS_ORIGINS", "CORS_METHODS", "CORS_HEADERS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """解析 CORS 配置，支持字符串和列表格式"""
        if isinstance(v, str):
            import json

            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        """自定义配置来源优先级：env > dotenv > secrets > yaml"""
        config = settings_cls.model_config
        env_files = _get_env_files()
        dotenv_source = DotEnvSettingsSource(
            settings_cls,
            env_file=env_files or None,
            env_file_encoding=config.get("env_file_encoding"),
            case_sensitive=config.get("case_sensitive"),
            env_prefix=config.get("env_prefix"),
            env_nested_delimiter=config.get("env_nested_delimiter"),
            env_nested_max_split=config.get("env_nested_max_split"),
            env_ignore_empty=config.get("env_ignore_empty"),
            env_parse_none_str=config.get("env_parse_none_str"),
            env_parse_enums=config.get("env_parse_enums"),
        )
        return init_settings, env_settings, dotenv_source, file_secret_settings, _yaml_settings_source

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.APP_ENV == "production"

    @property
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.APP_ENV == "testing"


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


_ENV_NAME_KEYS = ("APP_ENV", "ENVIRONMENT")
_DEFAULT_ENV_NAME = "development"
_APP_YAML_PATH = Path("configs/app.yaml")
_DOTENV_PATH = Path(".env")


def _read_env_name_from_dotenv(path: Path) -> str | None:
    if not path.exists():
        return None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key not in _ENV_NAME_KEYS:
            continue
        value = value.strip().strip("'").strip('"')
        if value:
            return value
    return None


def _resolve_env_name() -> str:
    env_name = os.getenv("APP_ENV") or os.getenv("ENVIRONMENT")
    if env_name:
        return env_name.strip()
    env_name = _read_env_name_from_dotenv(_DOTENV_PATH)
    if env_name:
        return env_name.strip()
    return _DEFAULT_ENV_NAME


def _get_env_files() -> list[Path]:
    env_files: list[Path] = []
    if _DOTENV_PATH.exists():
        env_files.append(_DOTENV_PATH)
    env_name = _resolve_env_name()
    env_specific = Path(f".env.{env_name}")
    if env_specific.exists():
        env_files.append(env_specific)
    return env_files


def _load_yaml_defaults(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"configs/app.yaml 解析失败: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("configs/app.yaml 内容必须为 dict")

    defaults: dict[str, Any] = {}

    app_cfg = data.get("app", {})
    if isinstance(app_cfg, dict):
        if "name" in app_cfg:
            defaults["APP_NAME"] = app_cfg["name"]
        if "version" in app_cfg:
            defaults["APP_VERSION"] = app_cfg["version"]
        if "description" in app_cfg:
            defaults["APP_DESCRIPTION"] = app_cfg["description"]

    server_cfg = data.get("server", {})
    if isinstance(server_cfg, dict):
        if "host" in server_cfg:
            defaults["HOST"] = server_cfg["host"]
        if "port" in server_cfg:
            defaults["PORT"] = server_cfg["port"]
        if "reload" in server_cfg:
            defaults["RELOAD"] = server_cfg["reload"]

    cors_cfg = data.get("cors", {})
    if isinstance(cors_cfg, dict):
        if "origins" in cors_cfg:
            defaults["CORS_ORIGINS"] = cors_cfg["origins"]
        if "methods" in cors_cfg:
            defaults["CORS_METHODS"] = cors_cfg["methods"]
        if "headers" in cors_cfg:
            defaults["CORS_HEADERS"] = cors_cfg["headers"]
        if "allow_credentials" in cors_cfg:
            defaults["CORS_ALLOW_CREDENTIALS"] = cors_cfg["allow_credentials"]

    pagination_cfg = data.get("pagination", {})
    if isinstance(pagination_cfg, dict):
        if "default_page_size" in pagination_cfg:
            defaults["DEFAULT_PAGE_SIZE"] = pagination_cfg["default_page_size"]
        if "max_page_size" in pagination_cfg:
            defaults["MAX_PAGE_SIZE"] = pagination_cfg["max_page_size"]

    return defaults


def _yaml_settings_source() -> dict[str, Any]:
    return _load_yaml_defaults(_APP_YAML_PATH)


settings = get_settings()
