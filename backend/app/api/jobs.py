"""
职位相关API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.database import get_database
from ..core.responses import PageResponse, success_response, error_response
from ..schemas.job import JobCreate, JobUpdate, JobResponse, JobFilter
from ..services import JobService

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/", response_model=dict)
async def create_job(
    job: JobCreate, db: AsyncIOMotorDatabase = Depends(get_database)
):
    """创建职位"""
    service = JobService(db)
    result = await service.create(job)
    return success_response(data=result.model_dump(), message="职位创建成功")


@router.get("/{job_id}", response_model=dict)
async def get_job(
    job_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
):
    """获取职位详情"""
    service = JobService(db)
    result = await service.get_by_id(job_id)
    if result:
        return success_response(data=result.model_dump())
    return error_response(message="职位不存在", code=404)


@router.get("/", response_model=dict)
async def get_jobs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    city: Optional[str] = Query(None, description="城市"),
    keyword: Optional[str] = Query(None, description="关键词"),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """获取职位列表"""
    skip = (page - 1) * page_size
    filters = {}
    if city:
        filters["city"] = city
    if keyword:
        filters["$or"] = [
            {"job_name": {"$regex": keyword, "$options": "i"}},
            {"company_name": {"$regex": keyword, "$options": "i"}},
        ]

    service = JobService(db)
    jobs, total = await service.get_list(skip=skip, limit=page_size, filters=filters)

    return {
        "code": 200,
        "message": "success",
        "data": [job.model_dump() for job in jobs],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.put("/{job_id}", response_model=dict)
async def update_job(
    job_id: str,
    job: JobUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """更新职位"""
    service = JobService(db)
    result = await service.update(job_id, job)
    if result:
        return success_response(data=result.model_dump(), message="职位更新成功")
    return error_response(message="职位不存在", code=404)


@router.delete("/{job_id}", response_model=dict)
async def delete_job(
    job_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
):
    """删除职位"""
    service = JobService(db)
    result = await service.delete(job_id)
    if result:
        return success_response(message="职位删除成功")
    return error_response(message="职位不存在", code=404)


@router.post("/batch", response_model=dict)
async def batch_create_jobs(
    jobs: list[JobCreate], db: AsyncIOMotorDatabase = Depends(get_database)
):
    """批量创建职位"""
    service = JobService(db)
    count = await service.batch_create(jobs)
    return success_response(data={"count": count}, message=f"成功创建{count}个职位")
