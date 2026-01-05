"""
日期时间工具模块

提供常用的日期时间处理功能：
- 时间戳生成和转换
- 日期时间格式化和解析
- 时区转换
- 时间计算工具
"""

import time
from datetime import UTC, datetime, timedelta

import pytz


def current_timestamp(milliseconds: bool = False) -> int | float:
    """
    获取当前时间戳

    Args:
        milliseconds: 是否返回毫秒级时间戳

    Returns:
        时间戳
    """
    if milliseconds:
        return int(time.time() * 1000)
    return int(time.time())


def utc_now() -> datetime:
    """获取当前UTC时间"""
    return datetime.now(UTC)


def local_now(tz: str | None = None) -> datetime:
    """
    获取本地时间

    Args:
        tz: 时区名称，如 'Asia/Shanghai'

    Returns:
        本地时间
    """
    if tz:
        timezone_obj = pytz.timezone(tz)
        return datetime.now(timezone_obj)
    return datetime.now()


def format_datetime(
    dt: datetime | float | int | str | None = None,
    format_str: str | None = None,
    timezone_name: str | None = None,
) -> str | None:
    """
    格式化日期时间

    Args:
        dt: 日期时间对象、时间戳或字符串，默认为当前时间
        format_str: 格式字符串，默认为ISO格式
        timezone_name: 时区名称

    Returns:
        格式化后的时间字符串，如果dt为None则返回None
    """
    if dt is None:
        return None

    # 默认使用ISO格式，适合API响应
    if format_str is None:
        format_str = "%Y-%m-%dT%H:%M:%S.%fZ"

    if isinstance(dt, int | float):
        dt = datetime.fromtimestamp(dt, tz=UTC)
    elif isinstance(dt, str):
        dt = parse_datetime(dt)
    elif dt.tzinfo is None:
        # 如果没有时区信息，假设为UTC
        dt = dt.replace(tzinfo=UTC)

    if timezone_name:
        dt = timezone_convert(dt, timezone_name)
    elif dt.tzinfo != UTC:
        # 转换到UTC用于API响应
        dt = dt.astimezone(UTC)

    return dt.strftime(format_str)


def parse_datetime(
    date_string: str,
    format_str: str = "%Y-%m-%d %H:%M:%S",
    timezone_name: str | None = None,
) -> datetime:
    """
    解析日期时间字符串

    Args:
        date_string: 日期时间字符串
        format_str: 格式字符串
        timezone_name: 时区名称

    Returns:
        日期时间对象
    """
    dt = datetime.strptime(date_string, format_str)

    if timezone_name:
        tz = pytz.timezone(timezone_name)
        dt = tz.localize(dt)

    return dt


def timezone_convert(dt: datetime, target_timezone: str) -> datetime:
    """
    时区转换

    Args:
        dt: 源日期时间
        target_timezone: 目标时区名称

    Returns:
        转换后的日期时间
    """
    target_tz = pytz.timezone(target_timezone)

    if dt.tzinfo is None:
        # 如果没有时区信息，假设为UTC
        dt = pytz.UTC.localize(dt)

    return dt.astimezone(target_tz)


def timestamp_to_datetime(
    timestamp: int | float, timezone_name: str | None = None
) -> datetime:
    """
    时间戳转日期时间

    Args:
        timestamp: 时间戳
        timezone_name: 时区名称

    Returns:
        日期时间对象
    """
    # 处理毫秒级时间戳
    if timestamp > 1e10:
        timestamp = timestamp / 1000

    dt = datetime.fromtimestamp(timestamp, tz=UTC)

    if timezone_name:
        dt = timezone_convert(dt, timezone_name)

    return dt


def datetime_to_timestamp(dt: datetime, milliseconds: bool = False) -> int | float:
    """
    日期时间转时间戳

    Args:
        dt: 日期时间对象
        milliseconds: 是否返回毫秒级时间戳

    Returns:
        时间戳
    """
    timestamp = dt.timestamp()

    if milliseconds:
        return int(timestamp * 1000)
    return int(timestamp)


def add_time(
    dt: datetime | None = None,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
) -> datetime:
    """
    时间加法

    Args:
        dt: 基础时间，默认为当前时间
        days: 天数
        hours: 小时数
        minutes: 分钟数
        seconds: 秒数

    Returns:
        计算后的时间
    """
    if dt is None:
        dt = utc_now()

    delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return dt + delta


def subtract_time(
    dt: datetime | None = None,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
) -> datetime:
    """
    时间减法

    Args:
        dt: 基础时间，默认为当前时间
        days: 天数
        hours: 小时数
        minutes: 分钟数
        seconds: 秒数

    Returns:
        计算后的时间
    """
    if dt is None:
        dt = utc_now()

    delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return dt - delta


def time_diff(dt1: datetime, dt2: datetime) -> dict:
    """
    计算两个时间的差值

    Args:
        dt1: 时间1
        dt2: 时间2

    Returns:
        时间差值字典
    """
    delta = abs(dt1 - dt2)

    total_seconds = int(delta.total_seconds())
    days = delta.days
    hours = total_seconds // 3600 % 24
    minutes = total_seconds // 60 % 60
    seconds = total_seconds % 60

    return {
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "total_seconds": total_seconds,
    }


def is_business_day(dt: datetime | None = None) -> bool:
    """
    判断是否为工作日

    Args:
        dt: 日期时间，默认为当前时间

    Returns:
        是否为工作日
    """
    if dt is None:
        dt = local_now()

    # 0=Monday, 6=Sunday
    return dt.weekday() < 5


def get_week_start(dt: datetime | None = None) -> datetime:
    """
    获取周开始时间（周一00:00:00）

    Args:
        dt: 日期时间，默认为当前时间

    Returns:
        周开始时间
    """
    if dt is None:
        dt = local_now()

    days_since_monday = dt.weekday()
    week_start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return week_start - timedelta(days=days_since_monday)


def get_month_start(dt: datetime | None = None) -> datetime:
    """
    获取月开始时间（1号00:00:00）

    Args:
        dt: 日期时间，默认为当前时间

    Returns:
        月开始时间
    """
    if dt is None:
        dt = local_now()

    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


# 常用格式化字符串
FORMAT_ISO = "%Y-%m-%dT%H:%M:%S"
FORMAT_DATE = "%Y-%m-%d"
FORMAT_TIME = "%H:%M:%S"
FORMAT_DATETIME = "%Y-%m-%d %H:%M:%S"
FORMAT_TIMESTAMP = "%Y%m%d_%H%M%S"

# 常用时区
TIMEZONE_UTC = "UTC"
TIMEZONE_BEIJING = "Asia/Shanghai"
TIMEZONE_NEW_YORK = "America/New_York"
TIMEZONE_LONDON = "Europe/London"
TIMEZONE_TOKYO = "Asia/Tokyo"


# 导出接口
__all__ = [
    # 主要函数
    "current_timestamp",
    "utc_now",
    "local_now",
    "format_datetime",
    "parse_datetime",
    "timezone_convert",
    "timestamp_to_datetime",
    "datetime_to_timestamp",
    "add_time",
    "subtract_time",
    "time_diff",
    "is_business_day",
    "get_week_start",
    "get_month_start",
    # 常量
    "FORMAT_ISO",
    "FORMAT_DATE",
    "FORMAT_TIME",
    "FORMAT_DATETIME",
    "FORMAT_TIMESTAMP",
    "TIMEZONE_UTC",
    "TIMEZONE_BEIJING",
    "TIMEZONE_NEW_YORK",
    "TIMEZONE_LONDON",
    "TIMEZONE_TOKYO",
]
