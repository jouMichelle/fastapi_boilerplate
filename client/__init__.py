"""外部服务客户端"""

from client.redis import RedisClient, get_redis_client
from client.minio import MinioClient, get_minio_client

__all__ = [
    "RedisClient",
    "get_redis_client",
    "MinioClient",
    "get_minio_client",
]
