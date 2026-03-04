"""
工业级日志管理系统 - Centralized Logging Manager
基于 loguru 实现统一日志管理、文件持久化、WebSocket 实时流、结构化日志
"""

import asyncio
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import WebSocket
from loguru import logger


class LogManager:
    """统一日志管理器 - 提供全局日志配置和 logger 工厂"""

    def __init__(self):
        self._log_level = "INFO"
        self._module_levels: dict[str, str] = {}
        self._websocket_connections: list[WebSocket] = []
        self._ws_buffer: list[dict[str, Any]] = []
        self._ws_buffer_size = 10  # 降低缓冲区大小，加快响应速度
        self._ws_last_flush = datetime.now()
        self._ws_flush_interval = 0.5  # second，降低刷新间隔
        self._connection_manager = None
        # 使用 asyncio.Queue 来传递日志消息（线程安全）
        self._log_queue: asyncio.Queue = None
        self._queue_task: asyncio.Task = None

    def setup(self):
        """初始化全局日志配置"""
        # Remove default handler
        logger.remove()

        # Create logs directory
        self._create_log_directory()

        # Add handlers
        self._add_console_handler()
        self._add_file_handler()
        self._add_websocket_handler()

        logger.info("Logging system initialized", extra={"module": "LogManager"})

    def get_logger(self, module_name: str) -> logger:
        """
        获取模块专属 logger

        Args:
            module_name: 模块名称（通常使用 __name__）

        Returns:
            绑定了模块名的 logger
        """
        return logger.bind(module=module_name)

    def set_log_level(self, module: Optional[str], level: str) -> bool:
        """
        动态调整日志级别

        Args:
            module: 模块名，None 表示全局级别
            level: 日志级别 (TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL)

        Returns:
            是否设置成功
        """
        valid_levels = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]
        if level not in valid_levels:
            logger.error(f"Invalid log level: {level}. Must be one of {valid_levels}")
            return False

        if module is None:
            self._log_level = level
            logger.info(f"Global log level set to {level}")
        else:
            self._module_levels[module] = level
            logger.info(f"Module '{module}' log level set to {level}")

        return True

    def _create_log_directory(self):
        """创建日志目录结构"""
        # 使用相对于 backend 目录的路径
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        archive_dir = log_dir / "archive"
        archive_dir.mkdir(exist_ok=True)

        logger.debug(f"Log directory created: {log_dir}")

    def _add_console_handler(self):
        """添加控制台处理器（彩色输出）"""
        logger.add(
            sys.stdout,
            level=self._log_level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            ),
            colorize=True,
            filter=self._sensitive_data_filter,
        )

    def _add_file_handler(self):
        """添加文件处理器（轮转、压缩、保留）"""
        # 使用相对于 backend 目录的路径
        log_dir = Path(__file__).parent.parent.parent / "logs"

        # Application log (all levels)
        logger.add(
            log_dir / "app_{time:YYYY-MM-DD}.log",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name} | {function}:{line} | {message}",
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            enqueue=True,  # Async write
            filter=self._sensitive_data_filter,
            backtrace=True,
            diagnose=True,
        )

        # Error log (ERROR and CRITICAL only)
        logger.add(
            log_dir / "error_{time:YYYY-MM-DD}.log",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name} | {function}:{line} | {message}",
            rotation="100 MB",
            retention="90 days",  # Keep error logs longer
            compression="zip",
            enqueue=True,
            filter=self._sensitive_data_filter,
        )

    def _add_websocket_handler(self):
        """
        添加 WebSocket 自定义处理器
        将日志实时推送到所有连接的 WebSocket 客户端
        """
        def websocket_sink(message):
            """自定义 sink 函数，将日志广播到 WebSocket"""
            record = message.record

            # 构建日志条目
            log_entry = {
                "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "level": record["level"].name,
                "module": record["extra"].get("module", record["name"]),
                "function_line": f"{record['function']}:{record['line']}",
                "message": record["message"],
            }

            # 如果有异常信息
            if record.get("exception"):
                log_entry["exception"] = str(record["exception"])

            # 广播到 WebSocket
            self._broadcast_to_websocket(log_entry)

        # 添加自定义处理器，只推送 INFO 及以上级别的日志
        logger.add(
            websocket_sink,
            level="INFO",
            format="{message}",
            filter=self._sensitive_data_filter,
        )

    def _sensitive_data_filter(self, record) -> bool:
        """
        过滤日志中的敏感信息

        Args:
            record: loguru record

        Returns:
            是否应该记录这条日志
        """
        message = record["message"]

        # 定义敏感字段列表
        sensitive_patterns = [
            (r'password["\']?\s*=\s*[^\\s]+', "password=***"),
            (r'token["\']?\s*=\s*[^\\s]+', "token=***"),
            (r'cookie["\']?\s*=\s*[^\\s]+', "cookie=***"),
            (r'secret["\']?\s*=\s*[^\\s]+', "secret=***"),
            (r'api_key["\']?\s*=\s*[^\\s]+', "api_key=***"),
            (r'authorization["\']?\s*=\s*Bearer\s+[A-Za-z0-9\.\-]+', "authorization=Bearer ***"),
        ]

        for pattern, replacement in sensitive_patterns:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)

        record["message"] = message
        return True

    def add_websocket_connection(self, websocket: WebSocket):
        """添加 WebSocket 连接"""
        if websocket not in self._websocket_connections:
            self._websocket_connections.append(websocket)
            logger.info(
                f"WebSocket log client connected. Total: {len(self._websocket_connections)}"
            )

    def remove_websocket_connection(self, websocket: WebSocket):
        """移除 WebSocket 连接"""
        if websocket in self._websocket_connections:
            self._websocket_connections.remove(websocket)
            logger.info(
                f"WebSocket log client disconnected. Total: {len(self._websocket_connections)}"
            )

    def _broadcast_to_websocket(self, record: dict[str, Any]):
        """广播日志到所有 WebSocket 连接 - 只添加到缓冲区，实际发送由 WebSocket 端点处理"""
        if not self._websocket_connections:
            return

        # Add to buffer (线程安全)
        self._ws_buffer.append(record)
        self._ws_last_flush = datetime.now()

    def get_log_stats(self) -> dict[str, Any]:
        """获取日志统计信息"""
        # 使用相对于 backend 目录的路径
        log_dir = Path(__file__).parent.parent.parent / "logs"

        # Calculate total log file size
        total_size = sum(f.stat().st_size for f in log_dir.glob("*.log") if f.is_file())

        # Count log files
        log_files = list(log_dir.glob("*.log"))

        return {
            "connected_clients": len(self._websocket_connections),
            "buffer_size": len(self._ws_buffer),
            "logs_sent": 0,  # Could be tracked
            "log_file_count": len(log_files),
            "log_file_size_bytes": total_size,
            "log_file_size_mb": round(total_size / 1024 / 1024, 2),
        }


# Global LogManager instance
log_manager = LogManager()


def setup_logging():
    """设置全局日志系统（应用启动时调用）"""
    log_manager.setup()


def get_logger(module_name: str = None) -> logger:
    """
    获取 logger 实例（便捷函数）

    Args:
        module_name: 模块名称

    Returns:
        绑定了模块名的 logger
    """
    return log_manager.get_logger(module_name or "__main__")


# 导出 logger 供直接使用
__all__ = ["LogManager", "setup_logging", "get_logger", "log_manager", "logger"]
