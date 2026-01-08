"""
logger.py

企业级通用日志工具（基于 Loguru）

【设计目标】
1. 单文件工具（可复制、可复用）
2. 不依赖 Web 框架（FastAPI / Flask 等）
3. 显式初始化（import 不产生副作用）
4. 线程安全 + 幂等初始化
5. 支持 console / text file / json file 多种输出
6. 支持结构化日志（extra 字段）

【重要原则】
- logger.py 只提供「能力」
- logging.yaml 只描述「策略」
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import Any, Dict, Mapping

import yaml
from loguru import logger

# ============================================================
# 一、默认日志配置（兜底配置，可直接使用）
# ============================================================

DEFAULT_LOGGING_CONFIG: Dict[str, Any] = {
    # 全局默认日志级别
    "level": "INFO",

    # 文本日志格式（console / text file）
    # ⚠️ component 是推荐字段，但必须允许缺失
    "format": (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{extra[component]}</cyan> | "
        "[{extra[request_id]}] | "
        "{name}:{function}:{line} | "
        "<level>{message}</level>"
    ),

    # 控制台日志
    "console": {
        "enabled": True,
        "level": None,          # None = 使用全局 level
        "colorize": True,
        "backtrace": False,
        "diagnose": False,
    },

    # 普通文本文件日志
    "file": {
        "enabled": True,
        "level": None,
        "filename": "app.log",
        "rotation": "10 MB",
        "retention": "7 days",
        "compression": None,
    },

    # JSON 结构化日志（日志聚合）
    "json": {
        "enabled": False,
        "level": None,
        "filename": "app.json",
        "rotation": "100 MB",
        "retention": "14 days",
        "compression": None,
    },
}

# ============================================================
# 二、YAML 配置加载工具（可选能力）
# ============================================================

def load_logging_config_from_yaml(
    path: str | Path,
    *,
    encoding: str = "utf-8",
) -> Dict[str, Any]:
    """
    从 logging.yaml 文件加载日志配置

    ⚠️ 注意：
    - 这是一个【纯工具函数】
    - 不会被 LoggingManager 自动调用
    - 只负责：yaml -> dict

    Args:
        path: logging.yaml 文件路径
        encoding: 文件编码

    Returns:
        dict：日志配置，可直接传入 LoggingManager.initialize
    """
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"logging.yaml not found: {config_path}")

    with config_path.open("r", encoding=encoding) as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError("logging.yaml 内容必须是一个 dict")

    return data

# ============================================================
# 三、LoggingManager（日志系统初始化管理器）
# ============================================================

class LoggingManager:
    """
    日志系统管理器

    职责：
    - 根据「已经决定好的配置」初始化 Loguru
    - 注册 console / file / json sink
    - 保证初始化只执行一次（线程安全）

    非职责：
    - 不判断环境
    - 不读取配置文件
    - 不引入 request / trace / context
    """

    _initialized: bool = False
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def initialize(
        cls,
        *,
        config: Mapping[str, Any],
        log_dir: str | Path = "logs",
        remove_existing_handlers: bool = True,
    ) -> None:
        """
        初始化日志系统（全局只允许调用一次）

        Args:
            config: 日志配置 dict
            log_dir: 日志文件目录
            remove_existing_handlers: 是否移除 Loguru 默认 handler
        """
        with cls._lock:
            if cls._initialized:
                return

            if remove_existing_handlers:
                logger.remove()

            # 设置默认 extra 字段
            def _patch_extra(record: dict) -> None:
                record["extra"].setdefault("component", "unknown")
                record["extra"].setdefault("request_id", "N/A")

            logger.configure(patcher=_patch_extra)

            # 合并并校验配置
            cfg = _normalize_config(config)

            log_path = Path(log_dir)
            log_path.mkdir(parents=True, exist_ok=True)

            global_level = cfg["level"]
            text_format = cfg["format"]

            # ---------- 控制台日志 ----------
            console_cfg = cfg["console"]
            if console_cfg["enabled"]:
                logger.add(
                    sys.stdout,
                    level=console_cfg["level"] or global_level,
                    format=text_format,
                    colorize=console_cfg["colorize"],
                    backtrace=console_cfg["backtrace"],
                    diagnose=console_cfg["diagnose"],
                )

            # ---------- 文本文件日志 ----------
            file_cfg = cfg["file"]
            if file_cfg["enabled"]:
                logger.add(
                    log_path / file_cfg["filename"],
                    level=file_cfg["level"] or global_level,
                    format=text_format,
                    rotation=file_cfg["rotation"],
                    retention=file_cfg["retention"],
                    compression=file_cfg["compression"],
                    encoding="utf-8",
                    enqueue=True,
                )

            # ---------- JSON 日志 ----------
            json_cfg = cfg["json"]
            if json_cfg["enabled"]:
                logger.add(
                    log_path / json_cfg["filename"],
                    level=json_cfg["level"] or global_level,
                    serialize=True,
                    rotation=json_cfg["rotation"],
                    retention=json_cfg["retention"],
                    compression=json_cfg["compression"],
                    encoding="utf-8",
                    enqueue=True,
                )

            cls._initialized = True

            # 记录一次初始化完成日志
            get_logger("logging").info(
                "Logging initialized | level={} | console={} | file={} | json={}",
                global_level,
                console_cfg["enabled"],
                file_cfg["enabled"],
                json_cfg["enabled"],
            )

    @classmethod
    def reset_for_tests(cls) -> None:
        """
        重置日志系统（仅用于测试）
        """
        with cls._lock:
            logger.remove()
            cls._initialized = False

    @classmethod
    def ensure_initialized(cls) -> None:
        if not cls._initialized:
            raise RuntimeError(
                "LoggingManager is not initialized. "
                "Call LoggingManager.initialize() first."
            )
# ============================================================
# 四、Logger 获取函数（统一入口）
# ============================================================

def init_logger(
    *,
    config: Mapping[str, Any] | None = None,
    log_dir: str = "logs",
) -> None:
    """
    初始化日志系统（便捷函数）

    Args:
        config: 日志配置，默认使用 DEFAULT_LOGGING_CONFIG
        log_dir: 日志文件目录

    使用示例：
        from app.core.logger import init_logger

        # 使用默认配置
        init_logger()

        # 从 YAML 文件加载配置
        config = load_logging_config_from_yaml("configs/logging.yaml")
        init_logger(config=config)
    """
    if config is None:
        config = DEFAULT_LOGGING_CONFIG

    LoggingManager.initialize(config=config, log_dir=log_dir)


def get_logger(component: str):
    """
    获取绑定 component 的 logger

    component 示例：
    - api.user
    - service.auth
    - dal.order
    """
    LoggingManager.ensure_initialized()

    if not component:
        raise ValueError("component 不能为空")

    return logger.bind(component=component)


def get_api_logger(name: str):
    return get_logger(f"api.{name}")


def get_service_logger(name: str):
    return get_logger(f"service.{name}")


def get_dal_logger(name: str):
    return get_logger(f"dal.{name}")


def bind(**extra: Any):
    """
    为 logger 绑定任意结构化字段
    """
    return logger.bind(**extra)

# ============================================================
# 五、内部工具：配置归一化 & 校验
# ============================================================

def _normalize_config(config: Mapping[str, Any]) -> Dict[str, Any]:
    """
    合并用户配置与默认配置，并做基础校验
    """
    base = DEFAULT_LOGGING_CONFIG

    def merge(default: Dict[str, Any], override: Mapping[str, Any] | None):
        result = dict(default)
        if override:
            result.update(override)
        return result

    level = str(config.get("level", base["level"])).upper()
    fmt = config.get("format", base["format"]) or base["format"]

    console = merge(base["console"], config.get("console"))
    file_cfg = merge(base["file"], config.get("file"))
    json_cfg = merge(base["json"], config.get("json"))

    # 级别规范化
    console["level"] = console["level"].upper() if console.get("level") else None
    file_cfg["level"] = file_cfg["level"].upper() if file_cfg.get("level") else None
    json_cfg["level"] = json_cfg["level"].upper() if json_cfg.get("level") else None

    if file_cfg["enabled"] and not file_cfg.get("filename"):
        raise ValueError("file.enabled=True 时必须指定 filename")

    if json_cfg["enabled"] and not json_cfg.get("filename"):
        raise ValueError("json.enabled=True 时必须指定 filename")

    return {
        "level": level,
        "format": fmt,
        "console": console,
        "file": file_cfg,
        "json": json_cfg,
    }
