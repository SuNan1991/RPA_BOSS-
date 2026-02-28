"""
任务相关API
"""

from typing import Optional

import aiosqlite
from fastapi import APIRouter, BackgroundTasks, Depends, Query

from ..core.database import get_database
from ..core.responses import error_response, success_response
from ..schemas.task import TaskCreate, TaskUpdate
from ..services import TaskService
from ..services.task_executor import TaskExecutor

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("/", response_model=dict)
async def create_task(
    task: TaskCreate,
    background_tasks: BackgroundTasks,
    db: aiosqlite.Connection = Depends(get_database),
):
    """创建任务"""
    service = TaskService(db)
    result = await service.create(task)

    # 如果配置了自动执行，则启动后台任务
    if task.config.get("auto_execute", False):
        executor = TaskExecutor(db)

        async def execute_and_update():
            config_with_type = {**task.config, "task_type": task.task_type}
            await executor.execute_task(result.id, config_with_type)

        background_tasks.add_task(execute_and_update)

    return success_response(data=result.model_dump(), message="任务创建成功")


@router.get("/{task_id}", response_model=dict)
async def get_task(task_id: int, db: aiosqlite.Connection = Depends(get_database)):
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
    db: aiosqlite.Connection = Depends(get_database),
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
    task_id: int,
    task: TaskUpdate,
    db: aiosqlite.Connection = Depends(get_database),
):
    """更新任务"""
    service = TaskService(db)
    result = await service.update(task_id, task)
    if result:
        return success_response(data=result.model_dump(), message="任务更新成功")
    return error_response(message="任务不存在", code=404)


@router.delete("/{task_id}", response_model=dict)
async def delete_task(task_id: int, db: aiosqlite.Connection = Depends(get_database)):
    """删除任务"""
    service = TaskService(db)
    result = await service.delete(task_id)
    if result:
        return success_response(message="任务删除成功")
    return error_response(message="任务不存在", code=404)


@router.post("/{task_id}/execute", response_model=dict)
async def execute_task_endpoint(
    task_id: int,
    background_tasks: BackgroundTasks,
    db: aiosqlite.Connection = Depends(get_database),
):
    """执行任务"""
    service = TaskService(db)
    task = await service.get_by_id(task_id)
    if not task:
        return error_response(message="任务不存在", code=404)

    # 检查任务状态
    if task.status == "running":
        return error_response(message="任务正在执行中", code=400)

    if task.status == "completed":
        return error_response(message="任务已完成", code=400)

    # 更新任务状态为运行中
    await service.update_status(task_id, "running")

    # 创建执行器并执行任务
    executor = TaskExecutor(db)

    async def execute_and_update():
        config_with_type = {**task.config, "task_type": task.task_type}
        await executor.execute_task(task_id, config_with_type)

    background_tasks.add_task(execute_and_update)

    return success_response(message="任务开始执行")
