#!/usr/bin/env python3
"""
专门的用户ID生成工具
提供多种用户友好的ID生成策略
"""

import secrets
import time
from enum import Enum


class UserIDType(str, Enum):
    """用户ID类型枚举"""

    # 紧凑型：8位，如 'A3K9M2X7'
    COMPACT = "compact"
    # 前缀型：u + 7位，如 'u7A3K9M'
    PREFIX = "prefix"
    # 数字型：纯数字，如 '12345678'
    NUMERIC = "numeric"
    # 混合型：字母数字混合，如 'user123ABC'
    MIXED = "mixed"


class UserIDGenerator:
    """专门的用户ID生成器"""

    # 安全字符集（去除容易混淆的字符）
    SAFE_CHARS = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"  # 32个字符，去除0,1,I,O
    NUMBERS = "23456789"  # 去除0,1
    LETTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ"  # 去除I,O

    @classmethod
    def generate_compact_id(cls, length: int = 8) -> str:
        """
        生成紧凑型用户ID

        Args:
            length: ID长度，默认8位

        Returns:
            str: 紧凑型用户ID，如 'A3K9M2X7'

        特点：
        - 8位随机字符
        - 去除易混淆字符
        - 全大写字母和数字
        - 碰撞概率极低
        """
        return "".join(secrets.choice(cls.SAFE_CHARS) for _ in range(length))

    @classmethod
    def generate_prefix_id(cls, prefix: str = "u", length: int = 7) -> str:
        """
        生成前缀型用户ID

        Args:
            prefix: 前缀，默认'u'
            length: 随机部分长度，默认7位

        Returns:
            str: 前缀型用户ID，如 'u7A3K9M'

        特点：
        - 有意义的前缀
        - 易于识别用户ID
        - 支持自定义前缀
        """
        random_part = "".join(secrets.choice(cls.SAFE_CHARS) for _ in range(length))
        return f"{prefix}{random_part}"

    @classmethod
    def generate_numeric_id(cls, length: int = 8) -> str:
        """
        生成纯数字用户ID

        Args:
            length: ID长度，默认8位

        Returns:
            str: 纯数字用户ID，如 '23456789'

        特点：
        - 纯数字，易于输入
        - 去除0和1，避免混淆
        - 适合需要数字ID的场景
        """
        # 第一位不能是0，从NUMBERS中选择
        first_digit = secrets.choice(cls.NUMBERS)
        rest_digits = "".join(secrets.choice(cls.NUMBERS) for _ in range(length - 1))
        return first_digit + rest_digits

    @classmethod
    def generate_mixed_id(cls, prefix: str = "user", suffix_length: int = 6) -> str:
        """
        生成混合型用户ID

        Args:
            prefix: 前缀，默认'user'
            suffix_length: 后缀长度，默认6位

        Returns:
            str: 混合型用户ID，如 'user2A3K9M'

        特点：
        - 可读性强的前缀
        - 随机后缀保证唯一性
        - 适合需要语义化的场景
        """
        suffix = "".join(secrets.choice(cls.SAFE_CHARS) for _ in range(suffix_length))
        return f"{prefix}{suffix}"

    @classmethod
    def generate_timestamp_based_id(cls, prefix: str = "u") -> str:
        """
        生成基于时间戳的用户ID

        Args:
            prefix: 前缀，默认'u'

        Returns:
            str: 基于时间戳的用户ID，如 'u1A2B3C'

        特点：
        - 包含时间信息
        - 有一定的时序性
        - 适合需要按时间排序的场景
        """
        # 使用36进制时间戳（更紧凑）
        timestamp = int(time.time() * 1000) % (36**4)  # 取最后4位36进制
        timestamp_str = cls._to_base36(timestamp).zfill(4)

        # 添加3位随机字符
        random_part = "".join(secrets.choice(cls.SAFE_CHARS) for _ in range(3))

        return f"{prefix}{timestamp_str}{random_part}"

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

    @classmethod
    def validate_user_id(
        cls, user_id: str, id_type: UserIDType = UserIDType.COMPACT
    ) -> bool:
        """
        验证用户ID格式

        Args:
            user_id: 要验证的用户ID
            id_type: ID类型

        Returns:
            bool: 是否符合格式要求
        """
        if not user_id:
            return False

        if id_type == UserIDType.COMPACT:
            return len(user_id) == 8 and all(
                c in cls.SAFE_CHARS for c in user_id.upper()
            )

        if id_type == UserIDType.PREFIX:
            return (
                len(user_id) >= 2
                and user_id[0].isalpha()
                and all(c in cls.SAFE_CHARS for c in user_id[1:].upper())
            )

        if id_type == UserIDType.NUMERIC:
            return (
                user_id.isdigit()
                and len(user_id) >= 6
                and all(c in cls.NUMBERS for c in user_id)
            )

        if id_type == UserIDType.MIXED:
            return len(user_id) >= 4 and user_id.replace("_", "").isalnum()

        return False


def generate_user_id(id_type: UserIDType = UserIDType.COMPACT, **kwargs) -> str:
    """
    生成用户ID的便捷函数

    Args:
        id_type: ID类型
        **kwargs: 其他参数

    Returns:
        str: 生成的用户ID
    """
    if id_type == UserIDType.COMPACT:
        return UserIDGenerator.generate_compact_id(**kwargs)
    if id_type == UserIDType.PREFIX:
        return UserIDGenerator.generate_prefix_id(**kwargs)
    if id_type == UserIDType.NUMERIC:
        return UserIDGenerator.generate_numeric_id(**kwargs)
    if id_type == UserIDType.MIXED:
        return UserIDGenerator.generate_mixed_id(**kwargs)
    return UserIDGenerator.generate_compact_id(**kwargs)


def generate_short_user_id() -> str:
    """生成短用户ID（推荐）"""
    return UserIDGenerator.generate_compact_id(8)


def generate_readable_user_id() -> str:
    """生成可读性强的用户ID"""
    return UserIDGenerator.generate_prefix_id("u", 7)


def generate_numeric_user_id() -> str:
    """生成数字用户ID"""
    return UserIDGenerator.generate_numeric_id(8)


def is_valid_user_id(user_id: str) -> bool:
    """验证是否为有效的用户ID"""
    # 尝试匹配各种格式
    for id_type in UserIDType:
        if UserIDGenerator.validate_user_id(user_id, id_type):
            return True
    return False


if __name__ == "__main__":
    """演示各种用户ID生成"""
    print("🆔 用户ID生成器演示")
    print("=" * 50)

    print("\n1. 紧凑型ID (推荐用于新系统)")
    for _ in range(5):
        print(f"   {UserIDGenerator.generate_compact_id()}")

    print("\n2. 前缀型ID (用户友好)")
    for _ in range(5):
        print(f"   {UserIDGenerator.generate_prefix_id()}")

    print("\n3. 数字型ID (易于输入)")
    for _ in range(5):
        print(f"   {UserIDGenerator.generate_numeric_id()}")

    print("\n4. 混合型ID (语义化)")
    for _ in range(3):
        print(f"   {UserIDGenerator.generate_mixed_id()}")
        print(f"   {UserIDGenerator.generate_mixed_id('customer', 4)}")

    print("\n5. 时间戳型ID (有时序性)")
    for _ in range(5):
        print(f"   {UserIDGenerator.generate_timestamp_based_id()}")

    print("\n6. ID验证演示")
    test_ids = [
        "A3K9M2X7",  # 有效的紧凑型
        "u7A3K9M",  # 有效的前缀型
        "23456789",  # 有效的数字型
        "user2A3K9M",  # 有效的混合型
        "invalid",  # 无效ID
        "01234567",  # 包含0和1，无效
    ]

    for test_id in test_ids:
        is_valid = is_valid_user_id(test_id)
        print(f"   {test_id}: {'✅ 有效' if is_valid else '❌ 无效'}")
