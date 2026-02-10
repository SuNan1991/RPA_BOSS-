"""
API路由
"""

from fastapi import APIRouter

from .accounts import router as accounts_router
from .auth import router as auth_router
from .jobs import router as jobs_router
from .logs import router as logs_router
from .tasks import router as tasks_router

api_router = APIRouter()

api_router.include_router(jobs_router)
api_router.include_router(tasks_router)
api_router.include_router(accounts_router)
api_router.include_router(auth_router)
api_router.include_router(logs_router)
