"""数据库模块（多数据库支持）"""

from app.database.session import (
    # 默认数据库
    get_db_session,
    # SQLite 数据库
    get_sqlite_session,
    sqlite_engine,
    # PostgreSQL 数据库
    get_postgres_session,
    postgres_engine,
    # MySQL 数据库
    get_mysql_session,
    mysql_engine,
    # 数据库初始化和关闭
    init_db,
    close_db,
)

__all__ = [
    # 默认数据库
    "get_db_session",
    # SQLite
    "get_sqlite_session",
    "sqlite_engine",
    # PostgreSQL
    "get_postgres_session",
    "postgres_engine",
    # MySQL
    "get_mysql_session",
    "mysql_engine",
    # 初始化和关闭
    "init_db",
    "close_db",
]
