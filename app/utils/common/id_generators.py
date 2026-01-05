"""
ID生成器工具模块

提供多种ID生成策略：UUID、短ID、雪花算法等
整合原有的id_generator.py功能并进行优化
"""

import secrets
import string
import threading
import time
import uuid
from abc import ABC, abstractmethod

# 避免循环导入，移除对旧模块的依赖
_legacy_generate_uuid = None
_legacy_generate_short_id = None


class BaseIDGenerator(ABC):
    """ID生成器基类"""

    @abstractmethod
    def generate(self) -> str:
        """生成ID"""
        pass


class UUIDGenerator(BaseIDGenerator):
    """UUID生成器"""

    def __init__(self, version: int = 4, namespace: uuid.UUID | None = None):
        """
        初始化UUID生成器

        Args:
            version: UUID版本 (1, 3, 4, 5)
            namespace: 命名空间 (用于版本3和5)
        """
        self.version = version
        self.namespace = namespace

    def generate(self) -> str:
        """生成UUID"""
        if self.version == 1:
            return str(uuid.uuid1())
        if self.version == 3:
            if not self.namespace:
                raise ValueError("Namespace required for UUID version 3")
            return str(uuid.uuid3(self.namespace, str(time.time())))
        if self.version == 4:
            return str(uuid.uuid4())
        if self.version == 5:
            if not self.namespace:
                raise ValueError("Namespace required for UUID version 5")
            return str(uuid.uuid5(self.namespace, str(time.time())))
        raise ValueError(f"Unsupported UUID version: {self.version}")


class ShortIDGenerator(BaseIDGenerator):
    """短ID生成器"""

    def __init__(self, length: int = 8, alphabet: str | None = None):
        """
        初始化短ID生成器

        Args:
            length: ID长度
            alphabet: 字符集
        """
        self.length = length
        self.alphabet = alphabet or (string.ascii_letters + string.digits)

    def generate(self) -> str:
        """生成短ID"""
        return "".join(secrets.choice(self.alphabet) for _ in range(self.length))


class SnowflakeGenerator(BaseIDGenerator):
    """雪花算法ID生成器"""

    def __init__(self, datacenter_id: int = 1, worker_id: int = 1):
        """
        初始化雪花算法生成器

        Args:
            datacenter_id: 数据中心ID (0-31)
            worker_id: 工作节点ID (0-31)
        """
        self.datacenter_id = datacenter_id & 0x1F  # 5位
        self.worker_id = worker_id & 0x1F  # 5位
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

        # 基准时间戳 (2020-01-01 00:00:00)
        self.epoch = 1577836800000

    def generate(self) -> str:
        """生成雪花ID"""
        with self.lock:
            timestamp = int(time.time() * 1000)

            if timestamp < self.last_timestamp:
                raise Exception("Clock moved backwards")

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & 0xFFF  # 12位
                if self.sequence == 0:
                    # 等待下一毫秒
                    timestamp = self._wait_next_millis(timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            # 组合ID: 1位符号位 + 41位时间戳 + 5位数据中心 + 5位工作节点 + 12位序列号
            snowflake_id = (
                ((timestamp - self.epoch) << 22)
                | (self.datacenter_id << 17)
                | (self.worker_id << 12)
                | self.sequence
            )

            return str(snowflake_id)

    def _wait_next_millis(self, last_timestamp: int) -> int:
        """等待下一毫秒"""
        timestamp = int(time.time() * 1000)
        while timestamp <= last_timestamp:
            timestamp = int(time.time() * 1000)
        return timestamp


# 默认生成器实例
_default_uuid_generator = UUIDGenerator()
_default_short_id_generator = ShortIDGenerator()
_default_snowflake_generator = SnowflakeGenerator()


def generate_uuid(version: int = 4, namespace: str | uuid.UUID | None = None) -> str:
    """
    生成UUID

    Args:
        version: UUID版本
        namespace: 命名空间

    Returns:
        UUID字符串
    """
    # 向后兼容检查
    if version == 4 and namespace is None and _legacy_generate_uuid:
        return _legacy_generate_uuid()

    if isinstance(namespace, str):
        namespace = uuid.uuid5(uuid.NAMESPACE_DNS, namespace)

    generator = UUIDGenerator(version, namespace)
    return generator.generate()


def generate_short_id(length: int = 8, alphabet: str | None = None) -> str:
    """
    生成短ID

    Args:
        length: ID长度
        alphabet: 字符集

    Returns:
        短ID字符串
    """
    # 向后兼容检查
    if length == 8 and alphabet is None and _legacy_generate_short_id:
        return _legacy_generate_short_id()

    generator = ShortIDGenerator(length, alphabet)
    return generator.generate()


def generate_snowflake_id(datacenter_id: int = 1, worker_id: int = 1) -> str:
    """
    生成雪花算法ID

    Args:
        datacenter_id: 数据中心ID
        worker_id: 工作节点ID

    Returns:
        雪花ID字符串
    """
    generator = SnowflakeGenerator(datacenter_id, worker_id)
    return generator.generate()


class CompactIDGenerator:
    """紧凑型ID生成器 - 提供多种简短ID方案"""

    # 自定义字符集（去除容易混淆的字符）
    SAFE_CHARS = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"  # 32个字符，去除0,1,I,O
    NUMBERS = "0123456789"
    LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    @classmethod
    def generate_nano_id(cls, length: int = 8) -> str:
        """生成8位纳米ID（默认）

        Args:
            length: ID长度，默认8位

        Returns:
            str: 8位随机ID，如 'A3K9M2X7'
        """
        return "".join(secrets.choice(cls.SAFE_CHARS) for _ in range(length))

    @classmethod
    def generate_timestamp_id(cls, prefix: str = "") -> str:
        """生成基于时间戳的短ID

        Args:
            prefix: 可选前缀

        Returns:
            str: 时间戳+随机数ID，如 'u7A3K9' 或 '7A3K9M'（6位）
        """
        # 使用36进制时间戳（更紧凑）
        timestamp = int(time.time() * 1000) % (36**4)  # 取最后4位36进制
        timestamp_str = cls._to_base36(timestamp).zfill(4)

        # 添加2位随机字符
        random_part = "".join(secrets.choice(cls.SAFE_CHARS) for _ in range(2))

        if prefix:
            return f"{prefix}{timestamp_str}{random_part}"
        return f"{timestamp_str}{random_part}"

    @classmethod
    def generate_sequential_id(cls, prefix: str = "u") -> str:
        """生成序列化短ID（适合高并发）

        Args:
            prefix: ID前缀

        Returns:
            str: 序列化短ID
        """
        # 使用当前时间和随机数
        timestamp = int(time.time() * 1000) % (36**3)
        random_num = secrets.randbelow(36**2)

        return f"{prefix}{cls._to_base36(timestamp)}{cls._to_base36(random_num)}"

    @classmethod
    def _to_base36(cls, num: int) -> str:
        """转换为36进制字符串"""
        if num == 0:
            return "0"

        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        result = ""
        while num > 0:
            result = chars[num % 36] + result
            num //= 36
        return result


def generate_session_id() -> str:
    """生成会话ID（兼容函数）"""
    return CompactIDGenerator.generate_timestamp_id("s")


def create_id_generator(generator_type: str = "uuid", **kwargs) -> BaseIDGenerator:
    """
    创建ID生成器工厂函数

    Args:
        generator_type: 生成器类型 ('uuid', 'short', 'snowflake')
        **kwargs: 生成器参数

    Returns:
        ID生成器实例
    """
    if generator_type.lower() == "uuid":
        return UUIDGenerator(**kwargs)
    if generator_type.lower() == "short":
        return ShortIDGenerator(**kwargs)
    if generator_type.lower() == "snowflake":
        return SnowflakeGenerator(**kwargs)
    raise ValueError(f"Unknown generator type: {generator_type}")


# 便捷函数
def uuid4() -> str:
    """生成UUID v4"""
    return generate_uuid(4)


def uuid1() -> str:
    """生成UUID v1"""
    return generate_uuid(1)


def short_id(length: int = 8) -> str:
    """生成短ID"""
    return generate_short_id(length)


def snowflake_id() -> str:
    """生成雪花ID"""
    return generate_snowflake_id()


def generate_user_id() -> str:
    """生成用户ID（兼容性函数）"""
    return generate_uuid()


def generate_compact_user_id(length: int = 8, use_prefix: bool = True) -> str:
    """生成紧凑型用户ID

    Args:
        length: ID长度，默认8位
        use_prefix: 是否使用'u'前缀，默认True

    Returns:
        str: 紧凑型用户ID，如 'u7A3K9M2' 或 'A3K9M2X7'

    Examples:
        >>> generate_compact_user_id()  # 'u7A3K9M2'
        >>> generate_compact_user_id(6, False)  # 'A3K9M2'
    """
    if use_prefix:
        return CompactIDGenerator.generate_sequential_id("u")
    return CompactIDGenerator.generate_nano_id(length)


def generate_user_friendly_id() -> str:
    """生成用户友好的短ID（推荐用于新用户）

    Returns:
        str: 8位用户友好ID，如 'A3K9M2X7'
    """
    return CompactIDGenerator.generate_nano_id(8)


def generate_session_id() -> str:
    """生成会话ID（兼容性函数）"""
    return generate_uuid()


# 导出接口
__all__ = [
    # 类
    "BaseIDGenerator",
    "UUIDGenerator",
    "ShortIDGenerator",
    "SnowflakeGenerator",
    "CompactIDGenerator",
    # 主要函数
    "generate_uuid",
    "generate_short_id",
    "generate_snowflake_id",
    "create_id_generator",
    # 便捷函数
    "uuid4",
    "uuid1",
    "short_id",
    "snowflake_id",
    # 用户ID生成函数
    "generate_user_id",
    "generate_compact_user_id",
    "generate_user_friendly_id",
    # 兼容性函数
    "generate_session_id",
]
