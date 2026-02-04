"""
任务服务
"""
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from ..core.logging import get_logger
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse

logger = get_logger("task_service")


class TaskService:
    """任务服务类"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.tasks

    async def create(self, task: TaskCreate) -> TaskResponse:
        """创建任务"""
        task_dict = task.model_dump()
        task_dict["created_at"] = datetime.now()
        task_dict["updated_at"] = datetime.now()
        task_dict["status"] = "pending"

        result = await self.collection.insert_one(task_dict)
        task_dict["id"] = str(result.inserted_id)

        logger.info(f"Created task: {task_dict['id']}")
        return TaskResponse(**task_dict)

    async def get_by_id(self, task_id: str) -> Optional[TaskResponse]:
        """根据ID获取任务"""
        try:
            obj_id = ObjectId(task_id)
            task = await self.collection.find_one({"_id": obj_id})
            if task:
                task["id"] = str(task.pop("_id"))
                return TaskResponse(**task)
        except Exception as e:
            logger.error(f"Error getting task: {e}")
        return None

    async def get_list(
        self,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
    ) -> tuple[List[TaskResponse], int]:
        """获取任务列表"""
        query = {}
        if status:
            query["status"] = status
        if task_type:
            query["task_type"] = task_type

        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        tasks = await cursor.to_list(length=limit)
        total = await self.collection.count_documents(query)

        result = []
        for task in tasks:
            task["id"] = str(task.pop("_id"))
            result.append(TaskResponse(**task))

        return result, total

    async def update(self, task_id: str, task: TaskUpdate) -> Optional[TaskResponse]:
        """更新任务"""
        try:
            obj_id = ObjectId(task_id)
            update_data = {k: v for k, v in task.model_dump().items() if v is not None}
            update_data["updated_at"] = datetime.now()

            await self.collection.update_one({"_id": obj_id}, {"$set": update_data})
            return await self.get_by_id(task_id)
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return None

    async def update_status(
        self, task_id: str, status: str, result: dict = None, error_message: str = None
    ) -> Optional[TaskResponse]:
        """更新任务状态"""
        try:
            obj_id = ObjectId(task_id)
            update_data = {"status": status, "updated_at": datetime.now()}
            if result is not None:
                update_data["result"] = result
            if error_message is not None:
                update_data["error_message"] = error_message

            await self.collection.update_one({"_id": obj_id}, {"$set": update_data})
            logger.info(f"Updated task status: {task_id} -> {status}")
            return await self.get_by_id(task_id)
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            return None

    async def delete(self, task_id: str) -> bool:
        """删除任务"""
        try:
            obj_id = ObjectId(task_id)
            result = await self.collection.delete_one({"_id": obj_id})
            logger.info(f"Deleted task: {task_id}, deleted_count: {result.deleted_count}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return False
