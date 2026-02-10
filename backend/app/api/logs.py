"""
日志管理 API - Log Query, Configuration, Statistics, Export
"""

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel

from app.core.logging import get_logger, log_manager

logger = get_logger(__name__)
router = APIRouter(prefix="/api/logs", tags=["logs"])


class LogLevelUpdate(BaseModel):
    """日志级别更新请求"""

    level: str


class LogStats(BaseModel):
    """日志统计信息"""

    connected_clients: int
    buffer_size: int
    logs_sent: int
    log_file_count: int
    log_file_size_bytes: int
    log_file_size_mb: float


@router.get("/", response_model=list[dict])
async def query_logs(
    limit: int = Query(100, ge=1, le=1000, description="返回的日志条数"),
    offset: int = Query(0, ge=0, description="偏移量"),
    level: Optional[str] = Query(None, description="日志级别过滤"),
    module: Optional[str] = Query(None, description="模块过滤"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    hours: Optional[int] = Query(None, description="最近N小时的日志"),
):
    """
    查询日志文件

    返回日志列表，支持分页、过滤和搜索
    """
    try:
        logs = []
        log_dir = Path("backend/logs")

        # 确定要查询的日志文件
        if hours:
            # 查询最近N小时的日志
            cutoff_time = datetime.now() - timedelta(hours=hours)
            log_files = [
                f
                for f in log_dir.glob("app_*.log")
                if datetime.fromtimestamp(f.stat().st_mtime) > cutoff_time
            ]
        else:
            # 查询所有日志文件（按时间倒序）
            log_files = sorted(log_dir.glob("app_*.log"), reverse=True)

        # 读取并解析日志文件
        for log_file in log_files:
            try:
                with open(log_file, encoding="utf-8") as f:
                    for line in f:
                        # 简单解析日志行
                        # 格式: 2025-02-07 10:30:45.123 | INFO     | module | function:line | message
                        if line.strip():
                            parsed = _parse_log_line(line)
                            if parsed:
                                # 应用过滤条件
                                if level and parsed.get("level") != level:
                                    continue
                                if module and parsed.get("module") != module:
                                    continue
                                if (
                                    keyword
                                    and keyword.lower() not in parsed.get("message", "").lower()
                                ):
                                    continue

                                logs.append(parsed)

                                # 达到限制数量
                                if len(logs) >= limit:
                                    break

                if len(logs) >= limit:
                    break

            except Exception as e:
                logger.error(f"Error reading log file {log_file}: {e}")

        # 应用偏移量
        logs = logs[offset : offset + limit]

        return logs

    except Exception as e:
        logger.error(f"Error querying logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _parse_log_line(line: str) -> Optional[dict]:
    """
    解析单行日志

    Args:
        line: 日志文本行

    Returns:
        解析后的日志字典
    """
    try:
        # 正则匹配日志格式
        # 格式: 2025-02-07 10:30:45.123 | INFO     | module | function:line | message
        pattern = r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d+)\s+\|\s+(\w+)\s+\|\s+(\S+)\s+\|\s+([^|]+)\|\s+(.+)$"
        match = re.match(pattern, line)

        if match:
            timestamp, level, module, function_line, message = match.groups()
            return {
                "timestamp": timestamp,
                "level": level.strip(),
                "module": module,
                "function_line": function_line.strip(),
                "message": message.strip(),
                "raw": line,
            }

        return {"raw": line, "message": line.strip()}

    except Exception:
        return {"raw": line, "message": line.strip()}


@router.put("/level/{module}")
async def set_log_level(module: str, request: LogLevelUpdate):
    """
    动态设置日志级别

    - **module**: "global" 表示全局级别，或指定模块名
    - **level**: TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
    """
    try:
        target_module = None if module == "global" else module
        success = log_manager.set_log_level(target_module, request.level)

        if not success:
            raise HTTPException(status_code=400, detail="Invalid log level")

        logger.info(f"Log level changed: module={module}, level={request.level}")

        return {"status": "success", "module": module, "level": request.level}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting log level: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=LogStats)
async def get_log_statistics():
    """获取日志系统统计信息"""
    try:
        return log_manager.get_log_stats()
    except Exception as e:
        logger.error(f"Error getting log stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_logs(
    format: str = Query("json", pattern="^(json|csv)$", description="导出格式"),
    hours: int = Query(24, ge=1, le=168, description="导出最近N小时的日志"),
):
    """
    导出日志文件

    支持 JSON 和 CSV 格式
    """
    try:
        # 查询日志
        logs = await query_logs(limit=10000, offset=0, hours=hours)

        if format == "json":
            # JSON 导出
            from fastapi.responses import JSONResponse

            return JSONResponse(content=logs)

        elif format == "csv":
            # CSV 导出
            import csv
            import io

            output = io.StringIO()
            writer = csv.DictWriter(
                output, fieldnames=["timestamp", "level", "module", "function_line", "message"]
            )
            writer.writeheader()
            writer.writerows(logs)

            # 返回文件
            output.seek(0)
            content = output.getvalue()

            return Response(
                content=content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                },
            )

    except Exception as e:
        logger.error(f"Error exporting logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_old_logs(days: int = Query(30, ge=1, le=365, description="删除N天前的日志")):
    """
    手动清理旧日志文件

    返回删除的文件列表和释放的空间
    """
    try:
        log_dir = Path("backend/logs")
        cutoff_date = datetime.now() - timedelta(days=days)

        deleted_files = []
        space_freed = 0

        # 查找并删除旧日志
        for log_file in log_dir.glob("*.log") + log_dir.glob("*.zip"):
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    file_size = log_file.stat().st_size
                    log_file.unlink()
                    deleted_files.append(log_file.name)
                    space_freed += file_size
            except Exception as e:
                logger.error(f"Error deleting file {log_file}: {e}")

        logger.info(f"Cleaned up {len(deleted_files)} log files, freed {space_freed} bytes")

        return {
            "status": "success",
            "deleted_files": deleted_files,
            "files_deleted": len(deleted_files),
            "space_freed_bytes": space_freed,
            "space_freed_mb": round(space_freed / 1024 / 1024, 2),
        }

    except Exception as e:
        logger.error(f"Error cleaning up logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
