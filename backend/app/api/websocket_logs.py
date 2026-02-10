"""
WebSocket 日志流 - 实时推送后端日志到前端
"""

from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect

from app.core.logging import get_logger, log_manager

logger_ws = get_logger("websocket_logs")


@logger_ws.catch
async def websocket_log_stream(websocket: WebSocket):
    """
    WebSocket 端点 - 实时日志流

    连接到 /ws/logs 接收实时日志推送
    """
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

    try:
        # 保持连接，处理客户端消息
        while True:
            data = await websocket.receive_text()

            # 处理心跳/命令
            if data == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
            elif data == "pause":
                # 暂停发送日志
                await websocket.send_json(
                    {
                        "type": "paused",
                        "message": "Log streaming paused",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            elif data == "resume":
                # 恢复发送日志
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
        # 从连接管理器移除
        log_manager.remove_websocket_connection(websocket)
