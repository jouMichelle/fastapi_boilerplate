"""Redis 客户端"""

from typing import Any

import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import settings
from app.core.logger import logger


class RedisClient:
    """Redis 客户端封装"""

    def __init__(self, url: str | None = None):
        self.url = url or settings.REDIS_URL
        self._client: Redis | None = None

    async def connect(self) -> None:
        """建立连接"""
        if not self.url:
            logger.warning("Redis URL 未配置，跳过连接")
            return

        try:
            self._client = redis.from_url(
                self.url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._client.ping()
            logger.info("Redis 连接成功")
        except Exception as e:
            logger.error(f"Redis 连接失败: {e}")
            self._client = None

    async def disconnect(self) -> None:
        """断开连接"""
        if self._client:
            await self._client.close()
            logger.info("Redis 连接已关闭")

    @property
    def client(self) -> Redis | None:
        """获取客户端实例"""
        return self._client

    async def get(self, key: str) -> str | None:
        """获取值"""
        if not self._client:
            return None
        return await self._client.get(key)

    async def set(
        self,
        key: str,
        value: Any,
        ex: int | None = None,
    ) -> bool:
        """设置值"""
        if not self._client:
            return False
        await self._client.set(key, value, ex=ex)
        return True

    async def delete(self, key: str) -> bool:
        """删除键"""
        if not self._client:
            return False
        await self._client.delete(key)
        return True

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self._client:
            return False
        return await self._client.exists(key) > 0


# 全局客户端实例
_redis_client: RedisClient | None = None


async def get_redis_client() -> RedisClient:
    """获取 Redis 客户端"""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
        await _redis_client.connect()
    return _redis_client


async def close_redis_client() -> None:
    """关闭 Redis 客户端"""
    global _redis_client
    if _redis_client:
        await _redis_client.disconnect()
        _redis_client = None
