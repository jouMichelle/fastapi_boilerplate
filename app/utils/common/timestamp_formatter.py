#!/usr/bin/env python3
"""
时间格式化工具模块
提供统一的时间格式化功能，支持多种格式配置
"""

import os
from datetime import UTC, datetime
from enum import Enum


class TimestampFormat(str, Enum):
    """时间格式枚举"""

    # 默认格式：2025-07-23 08:25:09.231
    DEFAULT = "default"
    # 连字符格式：2025-07-23-08-25-09.231
    HYPHEN = "hyphen"
    # ISO 8601格式：2025-07-23T08:25:09.231Z
    ISO8601 = "iso8601"


class TimestampFormatter:
    """时间格式化器"""

    def __init__(self, format_type: TimestampFormat = TimestampFormat.DEFAULT):
        self.format_type = format_type

    def format_timestamp(self, timestamp: datetime) -> str:
        """
        根据配置的格式类型格式化时间戳

        Args:
            timestamp: 要格式化的datetime对象

        Returns:
            格式化后的时间字符串
        """
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)

        # 转换为本地时间
        local_time = timestamp.astimezone()

        if self.format_type == TimestampFormat.DEFAULT:
            # 默认格式：2025-07-23 08:25:09.231
            return local_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        if self.format_type == TimestampFormat.HYPHEN:
            # 连字符格式：2025-07-23-08-25-09.231
            return local_time.strftime("%Y-%m-%d-%H-%M-%S.%f")[:-3]

        if self.format_type == TimestampFormat.ISO8601:
            # ISO 8601格式：2025-07-23T08:25:09.231Z
            utc_time = timestamp.astimezone(UTC)
            return utc_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        # 兜底到默认格式
        return local_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


# 全局格式化器实例
def get_timestamp_formatter() -> TimestampFormatter:
    """获取时间格式化器实例"""
    # 从环境变量读取格式配置
    format_env = os.getenv("TIMESTAMP_FORMAT", "default").lower()

    try:
        format_type = TimestampFormat(format_env)
    except ValueError:
        # 如果环境变量值无效，使用默认格式
        format_type = TimestampFormat.DEFAULT

    return TimestampFormatter(format_type)


# 便捷函数
def format_timestamp(timestamp: datetime | None = None) -> str:
    """
    格式化时间戳的便捷函数

    Args:
        timestamp: 要格式化的datetime对象，如果为None则使用当前时间

    Returns:
        格式化后的时间字符串
    """
    if timestamp is None:
        timestamp = datetime.now()

    formatter = get_timestamp_formatter()
    return formatter.format_timestamp(timestamp)


if __name__ == "__main__":
    """演示不同时间格式"""
    import os

    now = datetime.now()
    print("🕒 时间格式化演示")
    print("=" * 50)

    # 演示默认格式
    print("\n1. 默认格式 (TIMESTAMP_FORMAT=default)")
    os.environ["TIMESTAMP_FORMAT"] = "default"
    formatter = get_timestamp_formatter()
    print(f"   {formatter.format_timestamp(now)}")

    # 演示连字符格式
    print("\n2. 连字符格式 (TIMESTAMP_FORMAT=hyphen)")
    os.environ["TIMESTAMP_FORMAT"] = "hyphen"
    formatter = get_timestamp_formatter()
    print(f"   {formatter.format_timestamp(now)}")

    # 演示ISO 8601格式
    print("\n3. ISO 8601格式 (TIMESTAMP_FORMAT=iso8601)")
    os.environ["TIMESTAMP_FORMAT"] = "iso8601"
    formatter = get_timestamp_formatter()
    print(f"   {formatter.format_timestamp(now)}")

    # 演示便捷函数
    print("\n4. 便捷函数演示")
    os.environ["TIMESTAMP_FORMAT"] = "default"
    print(f"   format_timestamp(): {format_timestamp()}")
    print(f"   format_timestamp(now): {format_timestamp(now)}")
