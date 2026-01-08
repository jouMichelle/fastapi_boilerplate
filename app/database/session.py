"""
数据库会话管理（多数据库支持）

支持同时使用 SQLite、PostgreSQL、MySQL 三种数据库。
开发者可以根据需要明确选择使用哪个数据库的会话。

使用示例：
    # 方式一：使用默认数据库
    async with get_db_session() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()

    # 方式二：明确使用 SQLite
    async with get_sqlite_session() as db:
        user = User(name="张三")
        db.add(user)
        await db.commit()

    # 方式三：明确使用 PostgreSQL
    async with get_postgres_session() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()

    # 方式四：明确使用 MySQL
    async with get_mysql_session() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()

注意：
- 不再使用 FastAPI 的 Depends(get_db_session) 模式
- 改为直接调用函数获取会话
- 每个数据库都有独立的引擎和会话工厂
- 会话会在上下文管理器退出时自动提交或回滚
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.logger import logger


def _create_engine(database_url: str) -> AsyncEngine:
    """
    创建异步数据库引擎

    Args:
        database_url: 数据库连接 URL

    Returns:
        AsyncEngine: SQLAlchemy 异步引擎
    """
    # SQLite 不支持连接池参数
    if database_url.startswith("sqlite"):
        return create_async_engine(
            database_url,
            echo=settings.DEBUG,
        )

    # PostgreSQL / MySQL 支持连接池
    return create_async_engine(
        database_url,
        echo=settings.DEBUG,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )


# ============================================================
# SQLite 数据库
# ============================================================

sqlite_engine = _create_engine(settings.SQLITE_URL)
sqlite_session_factory = async_sessionmaker(
    bind=sqlite_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_sqlite_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取 SQLite 数据库会话

    使用示例：
        from app.database.session import get_sqlite_session

        async with get_sqlite_session() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
    """
    async with sqlite_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ============================================================
# PostgreSQL 数据库
# ============================================================

postgres_engine = _create_engine(settings.POSTGRES_URL)
postgres_session_factory = async_sessionmaker(
    bind=postgres_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取 PostgreSQL 数据库会话

    使用示例：
        from app.database.session import get_postgres_session

        async with get_postgres_session() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
    """
    async with postgres_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ============================================================
# MySQL 数据库
# ============================================================

mysql_engine = _create_engine(settings.MYSQL_URL)
mysql_session_factory = async_sessionmaker(
    bind=mysql_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_mysql_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取 MySQL 数据库会话

    使用示例：
        from app.database.session import get_mysql_session

        async with get_mysql_session() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
    """
    async with mysql_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ============================================================
# 默认数据库会话
# ============================================================

# 根据 DEFAULT_DATABASE 配置选择默认引擎
_db_engines = {
    "sqlite": sqlite_engine,
    "postgres": postgres_engine,
    "mysql": mysql_engine,
}

_db_session_factories = {
    "sqlite": sqlite_session_factory,
    "postgres": postgres_session_factory,
    "mysql": mysql_session_factory,
}

# 获取默认引擎和会话工厂
default_engine = _db_engines.get(settings.DEFAULT_DATABASE.lower(), sqlite_engine)
default_session_factory = _db_session_factories.get(
    settings.DEFAULT_DATABASE.lower(), sqlite_session_factory
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取默认数据库会话（由 DEFAULT_DATABASE 配置决定）

    使用示例：
        from app.database.session import get_db_session

        async with get_db_session() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()

    注意：
        - 这是快捷方法，实际使用哪个数据库由 DEFAULT_DATABASE 配置决定
        - 如需明确指定数据库，请使用：
          * get_sqlite_session()
          * get_postgres_session()
          * get_mysql_session()
    """
    async with default_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ============================================================
# 数据库初始化和关闭
# ============================================================

async def init_db() -> None:
    """
    初始化所有数据库（创建表）

    注意：会为所有配置的数据库创建表结构
    """
    from app.models import Base

    # 初始化 SQLite
    async with sqlite_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("SQLite 数据库初始化完成")

    # 初始化 PostgreSQL
    async with postgres_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("PostgreSQL 数据库初始化完成")

    # 初始化 MySQL
    async with mysql_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("MySQL 数据库初始化完成")


async def close_db() -> None:
    """关闭所有数据库连接"""
    await sqlite_engine.dispose()
    logger.info("SQLite 数据库连接已关闭")

    await postgres_engine.dispose()
    logger.info("PostgreSQL 数据库连接已关闭")

    await mysql_engine.dispose()
    logger.info("MySQL 数据库连接已关闭")
