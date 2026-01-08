"""MinIO 客户端"""

from io import BytesIO
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from app.core.config import settings
from app.core.logger import logger


class MinioClient:
    """MinIO 客户端封装"""

    def __init__(
        self,
        endpoint: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        secure: bool = False,
    ):
        self.endpoint = endpoint or settings.MINIO_ENDPOINT
        self.access_key = access_key or settings.MINIO_ACCESS_KEY
        self.secret_key = secret_key or settings.MINIO_SECRET_KEY
        self.secure = secure
        self._client: Minio | None = None

    def connect(self) -> None:
        """建立连接"""
        if not all([self.endpoint, self.access_key, self.secret_key]):
            logger.warning("MinIO 配置不完整，跳过连接")
            return

        try:
            self._client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure,
            )
            logger.info("MinIO 客户端初始化成功")
        except Exception as e:
            logger.error(f"MinIO 客户端初始化失败: {e}")
            self._client = None

    @property
    def client(self) -> Minio | None:
        """获取客户端实例"""
        return self._client

    def ensure_bucket(self, bucket_name: str) -> bool:
        """确保 bucket 存在"""
        if not self._client:
            return False

        try:
            if not self._client.bucket_exists(bucket_name):
                self._client.make_bucket(bucket_name)
                logger.info(f"创建 bucket: {bucket_name}")
            return True
        except S3Error as e:
            logger.error(f"创建 bucket 失败: {e}")
            return False

    def upload_file(
        self,
        bucket_name: str,
        object_name: str,
        file_path: str,
        content_type: str = "application/octet-stream",
    ) -> bool:
        """上传文件"""
        if not self._client:
            return False

        try:
            self._client.fput_object(
                bucket_name,
                object_name,
                file_path,
                content_type=content_type,
            )
            logger.info(f"文件上传成功: {bucket_name}/{object_name}")
            return True
        except S3Error as e:
            logger.error(f"文件上传失败: {e}")
            return False

    def upload_bytes(
        self,
        bucket_name: str,
        object_name: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> bool:
        """上传字节数据"""
        if not self._client:
            return False

        try:
            self._client.put_object(
                bucket_name,
                object_name,
                BytesIO(data),
                length=len(data),
                content_type=content_type,
            )
            logger.info(f"数据上传成功: {bucket_name}/{object_name}")
            return True
        except S3Error as e:
            logger.error(f"数据上传失败: {e}")
            return False

    def download_file(
        self,
        bucket_name: str,
        object_name: str,
        file_path: str,
    ) -> bool:
        """下载文件"""
        if not self._client:
            return False

        try:
            self._client.fget_object(bucket_name, object_name, file_path)
            logger.info(f"文件下载成功: {bucket_name}/{object_name}")
            return True
        except S3Error as e:
            logger.error(f"文件下载失败: {e}")
            return False

    def get_object(
        self,
        bucket_name: str,
        object_name: str,
    ) -> BinaryIO | None:
        """获取对象"""
        if not self._client:
            return None

        try:
            response = self._client.get_object(bucket_name, object_name)
            return response
        except S3Error as e:
            logger.error(f"获取对象失败: {e}")
            return None

    def delete_object(
        self,
        bucket_name: str,
        object_name: str,
    ) -> bool:
        """删除对象"""
        if not self._client:
            return False

        try:
            self._client.remove_object(bucket_name, object_name)
            logger.info(f"对象删除成功: {bucket_name}/{object_name}")
            return True
        except S3Error as e:
            logger.error(f"对象删除失败: {e}")
            return False

    def get_presigned_url(
        self,
        bucket_name: str,
        object_name: str,
        expires: int = 3600,
    ) -> str | None:
        """获取预签名 URL"""
        if not self._client:
            return None

        try:
            from datetime import timedelta

            url = self._client.presigned_get_object(
                bucket_name,
                object_name,
                expires=timedelta(seconds=expires),
            )
            return url
        except S3Error as e:
            logger.error(f"获取预签名 URL 失败: {e}")
            return None


# 全局客户端实例
_minio_client: MinioClient | None = None


def get_minio_client() -> MinioClient:
    """获取 MinIO 客户端"""
    global _minio_client
    if _minio_client is None:
        _minio_client = MinioClient()
        _minio_client.connect()
    return _minio_client
