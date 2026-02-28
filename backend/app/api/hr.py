"""
HR 功能 API 端点
"""

import logging
import os

# Import with absolute path handling
import sys

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.database import db
from app.services.hr_service import HRService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/hr", tags=["hr"])


# ==================== 请求/响应模型 ====================


class CandidateSearchRequest(BaseModel):
    """候选人搜索请求"""

    keyword: str
    city: str = "全国"
    experience: str | None = None
    education: str | None = None
    salary: str | None = None
    age: str | None = None
    gender: str | None = None
    max_pages: int = 1


class BatchGreetRequest(BaseModel):
    """批量打招呼请求"""

    candidate_ids: list[int]
    template: str | None = None
    rate_limit: dict | None = None


class BatchGreetWithDataRequest(BaseModel):
    """批量打招呼请求（带候选人数据）"""

    candidate_ids: list[int]
    candidates_data: list[dict]
    template: str | None = None
    rate_limit: dict | None = None


# ==================== API 端点 ====================


@router.get("/accounts")
async def get_hr_accounts():
    """获取 HR 账号列表"""
    try:
        conn = await db.get_connection()
        service = HRService(conn)

        accounts = await service.get_hr_accounts()

        return {
            "code": 200,
            "message": "success",
            "data": [acc.model_dump() for acc in accounts],
        }

    except Exception as e:
        logger.error(f"Error getting HR accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts/active")
async def get_active_account():
    """获取当前活跃的 HR 账户"""
    try:
        conn = await db.get_connection()
        service = HRService(conn)

        active_account_id = await service.get_active_account_id()

        if active_account_id:
            account = await service._get_account_by_id(active_account_id)
            if account:
                return {
                    "code": 200,
                    "message": "success",
                    "data": account.model_dump(),
                }

        return {
            "code": 404,
            "message": "No active account found",
            "data": None,
        }

    except Exception as e:
        logger.error(f"Error getting active account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/candidates/search")
async def search_candidates(request: CandidateSearchRequest, background_tasks: BackgroundTasks):
    """搜索候选人（后台任务）"""
    try:
        # 获取当前活跃账户
        conn = await db.get_connection()
        service = HRService(conn)
        active_account_id = await service.get_active_account_id()

        if not active_account_id:
            raise HTTPException(status_code=400, detail="没有活跃的 HR 账户，请先登录")

        # 在后台执行搜索
        background_tasks.add_task(
            _execute_candidate_search,
            active_account_id,
            request.keyword,
            request.city,
            request.experience,
            request.education,
            request.salary,
            request.age,
            request.gender,
            request.max_pages,
        )

        return {
            "code": 200,
            "message": "候选人搜索已启动，请稍候...",
            "data": {"account_id": active_account_id},
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting candidate search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/greetings/batch")
async def batch_greet(request: BatchGreetWithDataRequest, background_tasks: BackgroundTasks):
    """批量打招呼（后台任务）"""
    try:
        # 获取当前活跃账户
        conn = await db.get_connection()
        service = HRService(conn)
        active_account_id = await service.get_active_account_id()

        if not active_account_id:
            raise HTTPException(status_code=400, detail="没有活跃的 HR 账户，请先登录")

        if not request.candidate_ids:
            raise HTTPException(status_code=400, detail="请选择要打招呼的候选人")

        # 在后台执行批量打招呼
        background_tasks.add_task(
            _execute_batch_greet,
            active_account_id,
            request.candidate_ids,
            request.candidates_data,
            request.template,
            request.rate_limit,
        )

        return {
            "code": 200,
            "message": f"正在向 {len(request.candidate_ids)} 位候选人打招呼...",
            "data": {"total": len(request.candidate_ids), "account_id": active_account_id},
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting batch greet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/candidates")
async def get_candidates(
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    """获取候选人列表"""
    try:
        conn = await db.get_connection()
        service = HRService(conn)

        active_account_id = await service.get_active_account_id()

        if not active_account_id:
            raise HTTPException(status_code=400, detail="没有活跃的 HR 账户")

        result = await service.get_candidates(active_account_id, status, page, page_size)

        return {
            "code": 200,
            "message": "success",
            "data": result.get("data", []),
            "total": result.get("total", 0),
            "page": page,
            "page_size": page_size,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_statistics(days: int = 7):
    """获取统计数据"""
    try:
        conn = await db.get_connection()
        service = HRService(conn)

        active_account_id = await service.get_active_account_id()

        if not active_account_id:
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "candidates_viewed": 0,
                    "greetings_sent": 0,
                    "greetings_replied": 0,
                    "reply_rate": 0,
                    "days": days,
                },
            }

        result = await service.get_statistics(active_account_id, days)

        return {
            "code": 200,
            "message": "success",
            "data": result.get("data", {}),
        }

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 后台任务函数 ====================


async def _execute_candidate_search(
    hr_account_id: int,
    keyword: str,
    city: str,
    experience: str | None,
    education: str | None,
    salary: str | None,
    age: str | None,
    gender: str | None,
    max_pages: int,
):
    """执行候选人搜索（后台任务）"""
    try:
        from rpa.modules.hr import CandidateSearchModule

        logger.info(f"Starting candidate search for account {hr_account_id}")

        # 加载账户会话
        from rpa.modules.session_manager import SessionManager

        session_manager = SessionManager()
        session = await session_manager.load_session_for_account(hr_account_id)

        if not session:
            logger.error(f"No session found for account {hr_account_id}")
            return

        # 创建搜索模块并执行
        module = CandidateSearchModule()
        result = module.execute(
            keyword=keyword,
            city=city,
            experience=experience,
            education=education,
            salary=salary,
            age=age,
            gender=gender,
            max_pages=max_pages,
            hr_account_id=hr_account_id,
        )

        if result.get("success"):
            # 保存候选人到数据库
            conn = await db.get_connection()
            service = HRService(conn)
            await service.save_candidates(hr_account_id, result.get("data", []))
            logger.info(f"Candidate search completed for account {hr_account_id}")
        else:
            logger.error(f"Candidate search failed: {result.get('message')}")

    except Exception as e:
        logger.error(f"Error in candidate search background task: {e}")


async def _execute_batch_greet(
    hr_account_id: int,
    candidate_ids: list[int],
    candidates_data: list[dict],
    template: str | None,
    rate_limit: dict | None,
):
    """执行批量打招呼（后台任务）"""
    try:
        from rpa.modules.hr import BatchGreetModule

        logger.info(f"Starting batch greet for account {hr_account_id}")

        # 加载账户会话
        from rpa.modules.session_manager import SessionManager

        session_manager = SessionManager()
        session = await session_manager.load_session_for_account(hr_account_id)

        if not session:
            logger.error(f"No session found for account {hr_account_id}")
            return

        # 创建批量打招呼模块并执行
        module = BatchGreetModule()
        result = module.execute(
            candidate_ids=candidate_ids,
            candidates_data=candidates_data,
            template=template,
            rate_limit=rate_limit,
            hr_account_id=hr_account_id,
        )

        if result.get("success"):
            data = result.get("data", {})
            # 记录沟通日志
            conn = await db.get_connection()
            service = HRService(conn)

            for detail in data.get("details", []):
                if detail.get("success"):
                    await service.record_communication(
                        hr_account_id=hr_account_id,
                        candidate_id=detail.get("candidate_id"),
                        message_type="greet",
                        content=template or "默认打招呼",
                        status="sent",
                    )

            logger.info(
                f"Batch greet completed for account {hr_account_id}: "
                f"{data.get('success')} succeeded, {data.get('failed')} failed"
            )
        else:
            logger.error(f"Batch greet failed: {result.get('message')}")

    except Exception as e:
        logger.error(f"Error in batch greet background task: {e}")


# ==================== HR职位管理 ====================


@router.get("/jobs")
async def get_hr_jobs(
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    """获取HR职位列表"""
    try:
        conn = await db.get_connection()
        active_account_id = None

        # 尝试获取活跃账户
        service = HRService(conn)
        active_account_id = await service.get_active_account_id()

        skip = (page - 1) * page_size

        # 构建查询
        query = "SELECT * FROM hr_jobs WHERE 1=1"
        params = []
        count_query = "SELECT COUNT(*) FROM hr_jobs WHERE 1=1"
        count_params = []

        if active_account_id:
            query += " AND hr_account_id = ?"
            params.append(active_account_id)
            count_query += " AND hr_account_id = ?"
            count_params.append(active_account_id)

        if status:
            query += " AND status = ?"
            params.append(status)
            count_query += " AND status = ?"
            count_params.append(status)

        # 获取总数
        count_cursor = await conn.execute(count_query, count_params)
        total_row = await count_cursor.fetchone()
        total = total_row[0] if total_row else 0

        # 获取分页数据
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([page_size, skip])

        cursor = await conn.execute(query, params)
        rows = await cursor.fetchall()

        jobs = []
        for row in rows:
            jobs.append({
                "id": row[0],
                "hr_account_id": row[1],
                "job_name": row[2],
                "department": row[3],
                "salary_range": row[4],
                "experience_requirement": row[5],
                "education_requirement": row[6],
                "description": row[7],
                "requirements": row[8],
                "benefits": row[9],
                "status": row[10],
                "boss_job_id": row[11],
                "refresh_count": row[12],
                "view_count": row[13],
                "applicant_count": row[14],
                "published_at": row[15],
                "created_at": row[16],
            })

        return {
            "code": 200,
            "message": "success",
            "data": jobs,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    except Exception as e:
        logger.error(f"Error getting HR jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs")
async def create_hr_job(
    job_name: str,
    department: str | None = None,
    salary_range: str | None = None,
    experience_requirement: str | None = None,
    education_requirement: str | None = None,
    description: str | None = None,
    requirements: str | None = None,
    benefits: str | None = None,
):
    """创建HR职位"""
    try:
        conn = await db.get_connection()
        service = HRService(conn)
        active_account_id = await service.get_active_account_id()

        if not active_account_id:
            raise HTTPException(status_code=400, detail="没有活跃的 HR 账户")

        from datetime import datetime

        cursor = await conn.execute(
            """
            INSERT INTO hr_jobs (
                hr_account_id, job_name, department, salary_range,
                experience_requirement, education_requirement, description,
                requirements, benefits, status, published_at, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?)
            """,
            (
                active_account_id,
                job_name,
                department,
                salary_range,
                experience_requirement,
                education_requirement,
                description,
                requirements,
                benefits,
                datetime.now(),
                datetime.now(),
                datetime.now(),
            ),
        )
        job_id = cursor.lastrowid
        await conn.commit()

        return {
            "code": 200,
            "message": "职位创建成功",
            "data": {"id": job_id, "job_name": job_name},
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating HR job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs/{job_id}/refresh")
async def refresh_hr_job(job_id: int, background_tasks: BackgroundTasks):
    """刷新HR职位"""
    try:
        # 在后台执行刷新
        background_tasks.add_task(_execute_job_refresh, job_id)

        return {
            "code": 200,
            "message": "职位刷新已启动",
            "data": {"job_id": job_id},
        }

    except Exception as e:
        logger.error(f"Error starting job refresh: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _execute_job_refresh(job_id: int):
    """执行职位刷新（后台任务）"""
    try:
        from rpa.modules.hr.job_manager import JobManagerModule

        logger.info(f"Starting job refresh for job {job_id}")

        conn = await db.get_connection()
        service = HRService(conn)
        active_account_id = await service.get_active_account_id()

        if not active_account_id:
            logger.error("No active account for job refresh")
            return

        # 加载会话
        from rpa.modules.session_manager import SessionManager

        session_manager = SessionManager()
        session = await session_manager.load_session_for_account(active_account_id)

        if not session:
            logger.error(f"No session found for account {active_account_id}")
            return

        # 创建职位管理模块并执行刷新
        module = JobManagerModule()
        result = module.refresh_job(job_id)

        if result.get("success"):
            # 更新刷新次数
            await conn.execute(
                "UPDATE hr_jobs SET refresh_count = refresh_count + 1, updated_at = ? WHERE id = ?",
                (datetime.now(), job_id),
            )
            await conn.commit()
            logger.info(f"Job {job_id} refreshed successfully")
        else:
            logger.error(f"Job refresh failed: {result.get('message')}")

    except Exception as e:
        logger.error(f"Error in job refresh background task: {e}")


@router.put("/jobs/{job_id}/status")
async def update_job_status(
    job_id: int,
    status: str,  # active, paused, closed
):
    """更新职位状态"""
    try:
        conn = await db.get_connection()
        await conn.execute(
            "UPDATE hr_jobs SET status = ?, updated_at = ? WHERE id = ?",
            (status, datetime.now(), job_id),
        )
        await conn.commit()

        return {
            "code": 200,
            "message": "职位状态更新成功",
        }

    except Exception as e:
        logger.error(f"Error updating job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
