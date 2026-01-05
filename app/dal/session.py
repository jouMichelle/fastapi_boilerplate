"""数据库会话管理"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


def _create_engine() -> AsyncEngine:
    """创建数据库引擎，自动适配 SQLite、PostgreSQL、MySQL"""
    url = settings.DATABASE_URL

    if url.startswith("sqlite"):
        # SQLite 不支持连接池参数
        return create_async_engine(
            url,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False},
        )
    elif url.startswith("mysql"):
        # MySQL 配置
        return create_async_engine(
            url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
        )
    else:
        # PostgreSQL 配置（默认）
        return create_async_engine(
            url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
        )


# 创建异步引擎
engine: AsyncEngine = _create_engine()

# 创建异步会话工厂
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（用于依赖注入）"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（上下文管理器）"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """初始化数据库（创建表）"""
    from app.models.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """关闭数据库连接"""
    await engine.dispose()
