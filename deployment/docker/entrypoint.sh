#!/bin/bash
set -e

# 等待数据库就绪（如果配置了 PostgreSQL/MySQL）
wait_for_db() {
    if [[ "$DATABASE_URL" == *"postgresql"* ]]; then
        echo "Waiting for PostgreSQL..."
        while ! python -c "
import asyncio
import asyncpg
async def check():
    try:
        conn = await asyncpg.connect('$DATABASE_URL'.replace('+asyncpg', ''))
        await conn.close()
        return True
    except:
        return False
print(asyncio.run(check()))
" | grep -q "True"; do
            echo "PostgreSQL is unavailable - sleeping"
            sleep 2
        done
        echo "PostgreSQL is up!"
    elif [[ "$DATABASE_URL" == *"mysql"* ]]; then
        echo "Waiting for MySQL..."
        sleep 5  # 简单等待
        echo "MySQL should be up!"
    fi
}

# 等待 Redis 就绪（如果配置了）
wait_for_redis() {
    if [ -n "$REDIS_URL" ]; then
        echo "Waiting for Redis..."
        while ! python -c "
import redis
r = redis.from_url('$REDIS_URL')
r.ping()
print('ok')
" 2>/dev/null | grep -q "ok"; do
            echo "Redis is unavailable - sleeping"
            sleep 2
        done
        echo "Redis is up!"
    fi
}

# 主流程
echo "Starting FastAPI application..."
echo "Environment: ${APP_ENV:-production}"

# 等待依赖服务
wait_for_db
wait_for_redis

# 运行数据库迁移（可选）
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    alembic upgrade head
fi

# 执行传入的命令
exec "$@"
