"""
Authentication API endpoints
"""

import os

# Import with absolute path handling
import sys

from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.database import db
from app.core.logging import get_logger
from app.services.rpa_service import RPAService

logger = get_logger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

rpa_service = RPAService()


class LoginRequest(BaseModel):
    """Login request model"""

    pass  # No parameters needed for RPA login


class StatusResponse(BaseModel):
    """Status response model"""

    is_logged_in: bool
    user_info: dict | None
    browser_status: str | None
    browser_opened: bool = False
    login_in_progress: bool


class LogResponse(BaseModel):
    """Login log response"""

    id: int
    username: str | None
    success: bool
    failure_reason: str | None
    timestamp: str


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get current authentication status"""
    try:
        status = await rpa_service.get_status()
        return status

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def login(request: LoginRequest, background_tasks: BackgroundTasks):
    """Start RPA login process"""
    try:
        # Check if Chrome is installed
        import os
        import platform

        system = platform.system()

        # Simple Chrome check
        chrome_paths = {
            "Windows": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            ],
            "Darwin": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
            "Linux": ["/usr/bin/google-chrome", "/usr/bin/chrome", "/usr/bin/chromium"],
        }

        chrome_found = False
        for path in chrome_paths.get(system, []):
            if os.path.exists(path):
                chrome_found = True
                break

        if not chrome_found:
            raise HTTPException(
                status_code=400, detail="Chrome browser not found. Please install Google Chrome."
            )

        # Start login
        result = await rpa_service.start_login()

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        # 启动后台监控任务，不阻塞响应
        if result["status"] == "browser_opened":
            background_tasks.add_task(monitor_and_broadcast_login)
            logger.info("Background login monitoring task started")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting login: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout():
    """Logout and clear session"""
    try:
        result = rpa_service.logout()

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging out: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore-browser")
async def restore_browser():
    """手动恢复浏览器会话（当自动恢复失败时）"""
    try:
        result = await rpa_service.restore_browser_session()

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restoring browser: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class AccountLoginRequest(BaseModel):
    """Account login request model"""

    account_id: int


@router.post("/login/account")
async def login_account(request: AccountLoginRequest, background_tasks: BackgroundTasks):
    """Start RPA login process for a specific account"""
    try:
        # Check if Chrome is installed
        import platform

        system = platform.system()

        # Simple Chrome check
        chrome_paths = {
            "Windows": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            ],
            "Darwin": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
            "Linux": ["/usr/bin/google-chrome", "/usr/bin/chrome", "/usr/bin/chromium"],
        }

        chrome_found = False
        for path in chrome_paths.get(system, []):
            if os.path.exists(path):
                chrome_found = True
                break

        if not chrome_found:
            raise HTTPException(
                status_code=400, detail="Chrome browser not found. Please install Google Chrome."
            )

        # Start login for specific account
        result = await rpa_service.start_login_for_account(request.account_id)

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        # 启动后台监控任务，不阻塞响应
        if result["status"] == "browser_opened":
            background_tasks.add_task(monitor_and_broadcast_account_login, request.account_id)
            logger.info(f"Background account login monitoring task started for account {request.account_id}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting account login: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accounts/{account_id}/switch")
async def switch_account(account_id: int):
    """Switch to a specific account as active"""
    try:
        from app.services.account_service import AccountService

        conn = await db.get_connection()
        account_service = AccountService(conn)

        # Verify account exists
        account = await account_service.get_by_id(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Set as active account
        session_manager = rpa_service.session_manager
        success = await session_manager.set_active_account(account_id)

        if success:
            # Broadcast account switch event
            await manager.broadcast(
                {
                    "type": "account_switched",
                    "data": {
                        "account_id": account_id,
                        "account_info": account.model_dump(),
                        "timestamp": rpa_service.get_now_iso(),
                    },
                }
            )

            return {"status": "success", "message": f"Switched to account {account_id}", "account_id": account_id}
        else:
            raise HTTPException(status_code=400, detail="No valid session found for this account")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error switching account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accounts/{account_id}/restore-browser")
async def restore_browser_for_account(account_id: int):
    """为指定账号恢复浏览器会话"""
    try:
        result = await rpa_service.restore_browser_session_for_account(account_id)

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restoring browser for account {account_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs", response_model=list[LogResponse])
async def get_login_logs(limit: int = 50, offset: int = 0):
    """Get login history (admin only)"""
    try:
        conn = await db.get_connection()

        async with conn.execute(
            """
            SELECT id, username, success, failure_reason, timestamp
            FROM login_logs
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """,
            (limit, offset),
        ) as cursor:
            rows = await cursor.fetchall()

        logs = []
        for row in rows:
            logs.append(
                {
                    "id": row[0],
                    "username": row[1],
                    "success": bool(row[2]),
                    "failure_reason": row[3],
                    "timestamp": row[4],
                }
            )

        return logs

    except Exception as e:
        logger.error(f"Error getting login logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket connection manager
class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register new connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time status updates"""
    await manager.connect(websocket)

    try:
        # Send initial status
        initial_status = await rpa_service.get_status()
        await websocket.send_json(initial_status)

        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()

            # Handle ping/heartbeat
            if data == "ping":
                # Get current status and send it back
                status = await rpa_service.get_status()
                await websocket.send_json({"type": "status", "data": status})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_status(status: dict):
    """Helper function to broadcast status updates"""
    await manager.broadcast({"type": "status_update", "data": status})


async def monitor_and_broadcast_login():
    """后台任务：监控登录过程并广播结果"""
    try:
        logger.info("Login monitoring: Starting to monitor login process...")
        result = await rpa_service.monitor_login()
        logger.info(f"Login monitoring: Result = {result}")

        # 登录成功后广播状态
        if result["status"] == "success":
            status = await rpa_service.get_status()
            logger.info(f"Login monitoring: Broadcasting success status: {status}")

            # ========== 新增：包含账号同步信息 ==========
            status["account_id"] = result.get("account_id")
            status["is_new_account"] = result.get("is_new_account")
            status["sync_message"] = result.get("sync_message")

            if result.get("account_id"):
                logger.info(f"Login monitoring: Account synced - ID: {result.get('account_id')}, New: {result.get('is_new_account')}")
            # =============================================

            await broadcast_status(status)
        elif result["status"] == "timeout":
            logger.warning("Login monitoring: Login timed out after 5 minutes")
            # 广播超时状态
            await broadcast_status(await rpa_service.get_status())
        elif result["status"] == "error":
            logger.error(f"Login monitoring: Error during login: {result.get('message')}")
        else:
            logger.info(f"Login monitoring: Login ended with status: {result['status']}")

    except Exception as e:
        logger.error(f"Login monitoring: Exception occurred: {e}", exc_info=True)


async def monitor_and_broadcast_account_login(account_id: int):
    """后台任务：监控账号登录过程并广播结果"""
    try:
        from app.services.account_service import AccountService

        logger.info(f"Account login monitoring: Starting to monitor login for account {account_id}...")
        result = await rpa_service.monitor_login_for_account(account_id)
        logger.info(f"Account login monitoring: Result = {result}")

        if result["status"] == "success":
            # 获取账号信息
            conn = await db.get_connection()
            account_service = AccountService(conn)
            account = await account_service.get_by_id(account_id)

            # 广播登录成功
            await manager.broadcast({
                "type": "account_login_success",
                "data": {
                    "account_id": account_id,
                    "account_name": account.username if account else "Unknown",
                    "user_info": result.get("user_info"),
                    "timestamp": rpa_service.get_now_iso()
                }
            })
            logger.info(f"Account login monitoring: Broadcasted success for account {account_id}")

        elif result["status"] == "timeout":
            logger.warning(f"Account login monitoring: Login timeout for account {account_id}")
            # 广播超时状态
            await manager.broadcast({
                "type": "account_login_failed",
                "data": {
                    "account_id": account_id,
                    "reason": "Login timeout (5 minutes)"
                }
            })

        elif result["status"] == "cancelled":
            logger.info(f"Account login monitoring: Login cancelled for account {account_id}")
            await manager.broadcast({
                "type": "account_login_failed",
                "data": {
                    "account_id": account_id,
                    "reason": "Browser was closed"
                }
            })

        elif result["status"] == "error":
            error_msg = result.get("message", "Unknown error")
            logger.error(f"Account login monitoring: Error during login for account {account_id}: {error_msg}")
            await manager.broadcast({
                "type": "account_login_failed",
                "data": {
                    "account_id": account_id,
                    "reason": error_msg
                }
            })
        else:
            logger.info(f"Account login monitoring: Login ended with status: {result['status']}")

    except Exception as e:
        logger.error(f"Account login monitoring: Exception occurred for account {account_id}: {e}", exc_info=True)
        await manager.broadcast({
            "type": "account_login_failed",
            "data": {
                "account_id": account_id,
                "reason": str(e)
            }
        })
