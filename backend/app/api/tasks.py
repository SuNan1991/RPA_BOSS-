"""
任务相关API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.database import get_database
from ..core.responses import success_response, error_response
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse
from ..services import TaskService

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("/", response_model=dict)
async def create_task(
    task: TaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """创建任务"""
    service = TaskService(db)
    result = await service.create(task)

    # 添加后台任务执行逻辑
    # background_tasks.add_task(execute_task, result.id, task.config, db)

    return success_response(data=result.model_dump(), message="任务创建成功")


@router.get("/{task_id}", response_model=dict)
async def get_task(
    task_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
):
    """获取任务详情"""
    service = TaskService(db)
    result = await service.get_by_id(task_id)
    if result:
        return success_response(data=result.model_dump())
    return error_response(message="任务不存在", code=404)


@router.get("/", response_model=dict)
async def get_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态"),
    task_type: Optional[str] = Query(None, description="任务类型"),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """获取任务列表"""
    skip = (page - 1) * page_size

    service = TaskService(db)
    tasks, total = await service.get_list(
        skip=skip, limit=page_size, status=status, task_type=task_type
    )

    return {
        "code": 200,
        "message": "success",
        "data": [task.model_dump() for task in tasks],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.put("/{task_id}", response_model=dict)
async def update_task(
    task_id: str,
    task: TaskUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """更新任务"""
    service = TaskService(db)
    result = await service.update(task_id, task)
    if result:
        return success_response(data=result.model_dump(), message="任务更新成功")
    return error_response(message="任务不存在", code=404)


@router.delete("/{task_id}", response_model=dict)
async def delete_task(
    task_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
):
    """删除任务"""
    service = TaskService(db)
    result = await service.delete(task_id)
    if result:
        return success_response(message="任务删除成功")
    return error_response(message="任务不存在", code=404)


@router.post("/{task_id}/execute", response_model=dict)
async def execute_task_endpoint(
    task_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """执行任务"""
    service = TaskService(db)
    task = await service.get_by_id(task_id)
    if not task:
        return error_response(message="任务不存在", code=404)

    # 更新任务状态为运行中
    await service.update_status(task_id, "running")

    # 添加后台任务执行逻辑
    # background_tasks.add_task(execute_task, task_id, task.config, db)

    return success_response(message="任务开始执行")
