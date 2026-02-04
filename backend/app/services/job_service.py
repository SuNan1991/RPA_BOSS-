"""
职位服务
"""
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from ..core.logging import get_logger
from ..schemas.job import JobCreate, JobUpdate, JobResponse

logger = get_logger("job_service")


class JobService:
    """职位服务类"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.jobs

    async def create(self, job: JobCreate) -> JobResponse:
        """创建职位"""
        job_dict = job.model_dump()
        job_dict["created_at"] = datetime.now()
        job_dict["updated_at"] = datetime.now()
        job_dict["status"] = "pending"
        job_dict["is_applied"] = False

        result = await self.collection.insert_one(job_dict)
        job_dict["id"] = str(result.inserted_id)

        logger.info(f"Created job: {job_dict['id']}")
        return JobResponse(**job_dict)

    async def get_by_id(self, job_id: str) -> Optional[JobResponse]:
        """根据ID获取职位"""
        try:
            obj_id = ObjectId(job_id)
            job = await self.collection.find_one({"_id": obj_id})
            if job:
                job["id"] = str(job.pop("_id"))
                return JobResponse(**job)
        except Exception as e:
            logger.error(f"Error getting job: {e}")
        return None

    async def get_list(
        self,
        skip: int = 0,
        limit: int = 10,
        filters: dict = None,
    ) -> tuple[List[JobResponse], int]:
        """获取职位列表"""
        query = filters or {}
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        jobs = await cursor.to_list(length=limit)
        total = await self.collection.count_documents(query)

        result = []
        for job in jobs:
            job["id"] = str(job.pop("_id"))
            result.append(JobResponse(**job))

        return result, total

    async def update(self, job_id: str, job: JobUpdate) -> Optional[JobResponse]:
        """更新职位"""
        try:
            obj_id = ObjectId(job_id)
            update_data = {k: v for k, v in job.model_dump().items() if v is not None}
            update_data["updated_at"] = datetime.now()

            await self.collection.update_one({"_id": obj_id}, {"$set": update_data})
            return await self.get_by_id(job_id)
        except Exception as e:
            logger.error(f"Error updating job: {e}")
            return None

    async def delete(self, job_id: str) -> bool:
        """删除职位"""
        try:
            obj_id = ObjectId(job_id)
            result = await self.collection.delete_one({"_id": obj_id})
            logger.info(f"Deleted job: {job_id}, deleted_count: {result.deleted_count}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting job: {e}")
            return False

    async def batch_create(self, jobs: List[JobCreate]) -> int:
        """批量创建职位"""
        if not jobs:
            return 0

        jobs_data = []
        for job in jobs:
            job_dict = job.model_dump()
            job_dict["created_at"] = datetime.now()
            job_dict["updated_at"] = datetime.now()
            job_dict["status"] = "pending"
            job_dict["is_applied"] = False
            jobs_data.append(job_dict)

        result = await self.collection.insert_many(jobs_data)
        logger.info(f"Batch created {len(result.inserted_ids)} jobs")
        return len(result.inserted_ids)
