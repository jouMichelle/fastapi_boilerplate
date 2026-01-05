"""应用生命周期管理"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.core.config import settings
from app.core.logger import (
    DEFAULT_LOGGING_CONFIG,
    LoggingManager,
    get_logger,
    load_logging_config_from_yaml,
)
from app.dal.session import close_db, init_db


def _init_logging() -> None:
    """初始化日志系统"""
    config_path = Path("configs/logging.yaml")

    if config_path.exists():
        config = load_logging_config_from_yaml(config_path)
    else:
        # 使用默认配置
        config = DEFAULT_LOGGING_CONFIG

    LoggingManager.initialize(config=config, log_dir="logs")


# 在模块加载时初始化日志（确保最早执行）
_init_logging()

logger = get_logger("bootstrap.lifespan")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理器"""
    await on_startup()
    yield
    await on_shutdown()


async def on_startup() -> None:
    """应用启动时执行"""
    logger.info("Application starting up...")

    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database: {}", str(e))
        # 开发模式下允许数据库连接失败
        if not settings.DEBUG:
            raise
        logger.warning("Running without database connection (DEBUG mode)")

    logger.info("Application started successfully")


async def on_shutdown() -> None:
    """应用关闭时执行"""
    logger.info("Application shutting down...")

    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error("Error closing database: {}", str(e))

    logger.info("Application shutdown complete")
