"""
日志配置
"""

import sys
from pathlib import Path

from loguru import logger

from .config import settings

# 日志路径
log_path = Path(settings.LOG_PATH)
log_path.mkdir(parents=True, exist_ok=True)

# 移除默认处理器
logger.remove()

# 控制台日志
logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    colorize=True,
)

# 文件日志 - 所有日志
logger.add(
    log_path / "app_{time:YYYY-MM-DD}.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="00:00",
    retention="30 days",
    encoding="utf-8",
)

# 文件日志 - 错误日志
logger.add(
    log_path / "error_{time:YYYY-MM-DD}.log",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="00:00",
    retention="30 days",
    encoding="utf-8",
)


def get_logger(name: str = None):
    """获取logger实例"""
    if name:
        return logger.bind(name=name)
    return logger
