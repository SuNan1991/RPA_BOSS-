"""
FastAPI 主应用
"""

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .api import (
    api_router,
    auth,  # Import auth router
)
from .api.websocket_logs import websocket_log_stream
from .core.config import settings
from .core.database import db, init_database
from .core.logging import get_logger, setup_logging

# Setup logging first (before any other imports that might log)
setup_logging()
logger = get_logger(__name__)

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Starting up...")
    await db.connect()
    await init_database()

    # Run database migrations
    try:
        import os

        migration_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "migrations")

        # Get async connection
        conn = await db.get_connection()
        cursor = await conn.cursor()

        # Create migrations table if not exists
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS _migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Get applied migrations
        await cursor.execute("SELECT filename FROM _migrations")
        rows = await cursor.fetchall()
        applied = {row[0] for row in rows}

        # Apply new migrations
        if os.path.exists(migration_dir):
            for filename in sorted(os.listdir(migration_dir)):
                if filename.endswith(".sql") and filename not in applied:
                    filepath = os.path.join(migration_dir, filename)
                    logger.info(f"Applying migration: {filename}")

                    with open(filepath, encoding="utf-8") as f:
                        sql = f.read()
                        await cursor.executescript(sql)

                    await cursor.execute(
                        "INSERT INTO _migrations (filename) VALUES (?)", (filename,)
                    )
                    await conn.commit()

        await cursor.close()
        logger.info("Database migrations completed")

    except Exception as e:
        logger.error(f"Error running migrations: {e}")

    yield
    # 关闭时
    logger.info("Shutting down...")
    await db.close()


# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    description="BOSS直聘自动化招聘系统",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router)
app.include_router(auth.router)  # Add auth router with WebSocket


# WebSocket endpoint for log streaming
@app.websocket("/ws/logs")
async def websocket_logs_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time log streaming"""
    await websocket_log_stream(websocket)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "BOSS RPA API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
