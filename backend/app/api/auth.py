"""
Authentication API endpoints
"""

import logging
import os

# Import with absolute path handling
import sys

from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.database import db
from app.services.rpa_service import RPAService

logger = logging.getLogger(__name__)

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


class AccountLoginRequest(BaseModel):
    """Account login request model"""

    account_id: int


@router.post("/login/account")
async def login_account(request: AccountLoginRequest):
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
