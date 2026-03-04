"""
WebSocket 日志流 - 实时推送后端日志到前端
"""

import asyncio
import json
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect

from app.core.logging import get_logger, log_manager

logger_ws = get_logger("websocket_logs")


async def _log_broadcaster(websocket: WebSocket, stop_event: asyncio.Event):
    """后台任务：定期轮询缓冲区并发送日志"""
    while not stop_event.is_set():
        try:
                # 检查缓冲区是否有日志
                if log_manager._ws_buffer:
                    # 复制并清空缓冲区
                    logs_to_send = log_manager._ws_buffer.copy()
                    log_manager._ws_buffer.clear()
                    log_manager._ws_last_flush = datetime.now()

                    # 发送日志
                    message = json.dumps(logs_to_send)
                    await websocket.send_text(message)

                # 等待一段时间再检查
                await asyncio.sleep(0.1)  # 100ms

        except WebSocketDisconnect:
            break
        except Exception as e:
            logger_ws.error(f"Error in log broadcaster: {e}")
            break


@logger_ws.catch
async def websocket_log_stream(websocket: WebSocket):
    """
    WebSocket 端点 - 实时日志流

    连接到 /ws/logs 接收实时日志推送
    """
    stop_event = asyncio.Event()

    try:
        await websocket.accept()

        # 发送连接确认
        await websocket.send_json(
            {
                "type": "connected",
                "message": "WebSocket log stream connected",
                "timestamp": datetime.now().isoformat(),
            }
        )

        # 添加到连接管理器
        log_manager.add_websocket_connection(websocket)

        # 启动后台广播任务
        broadcaster_task = asyncio.create_task(
            _log_broadcaster(websocket, stop_event)
        )

        # 保持连接，处理客户端消息
        while True:
            data = await websocket.receive_text()

            # 处理心跳/命令
            if data == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
            elif data == "pause":
                # 暂停发送日志
                stop_event.set()
                await websocket.send_json(
                    {
                        "type": "paused",
                        "message": "Log streaming paused",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            elif data == "resume":
                # 恢复发送日志
                stop_event.clear()
                await websocket.send_json(
                    {
                        "type": "resumed",
                        "message": "Log streaming resumed",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            else:
                # 未知命令
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": f"Unknown command: {data}",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

    except WebSocketDisconnect:
        logger_ws.info("WebSocket log client disconnected")
    except Exception as e:
        logger_ws.error(f"WebSocket error: {e}")
    finally:
        # 停止广播任务
        stop_event.set()
        # 从连接管理器移除
        log_manager.remove_websocket_connection(websocket)
