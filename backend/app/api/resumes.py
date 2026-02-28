"""
简历接收与管理相关API
"""

from datetime import datetime
from typing import Optional

import aiosqlite
from fastapi import APIRouter, Depends, Query

from ..core.database import get_database
from ..core.responses import error_response, success_response

router = APIRouter(prefix="/api/hr/resumes", tags=["resumes"])


@router.get("/", response_model=dict)
async def get_resumes(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态筛选"),
    hr_job_id: Optional[int] = Query(None, description="职位ID"),
    db: aiosqlite.Connection = Depends(get_database),
):
    """获取收到的简历列表"""
    try:
        skip = (page - 1) * page_size

        # 构建查询
        query = "SELECT * FROM received_resumes WHERE 1=1"
        params = []
        count_query = "SELECT COUNT(*) FROM received_resumes WHERE 1=1"
        count_params = []

        if status:
            query += " AND status = ?"
            params.append(status)
            count_query += " AND status = ?"
            count_params.append(status)

        if hr_job_id:
            query += " AND hr_job_id = ?"
            params.append(hr_job_id)
            count_query += " AND hr_job_id = ?"
            count_params.append(hr_job_id)

        # 获取总数
        cursor = await db.execute(count_query, count_params)
        total_row = await cursor.fetchone()
        total = total_row[0] if total_row else 0

        # 获取分页数据
        query += " ORDER BY received_at DESC LIMIT ? OFFSET ?"
        params.extend([page_size, skip])

        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()

        # 格式化结果
        resumes = []
        for row in rows:
            resumes.append({
                "id": row[0],
                "hr_job_id": row[1],
                "candidate_id": row[2],
                "resume_url": row[3],
                "status": row[4],
                "match_score": row[5],
                "notes": row[6],
                "received_at": row[7],
                "updated_at": row[8],
            })

        return {
            "code": 200,
            "message": "success",
            "data": resumes,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    except Exception as e:
        return error_response(message=f"获取失败: {str(e)}", code=500)


@router.get("/{resume_id}", response_model=dict)
async def get_resume(resume_id: int, db: aiosqlite.Connection = Depends(get_database)):
    """获取简历详情"""
    try:
        cursor = await db.execute(
            "SELECT * FROM received_resumes WHERE id = ?",
            (resume_id,)
        )
        row = await cursor.fetchone()

        if not row:
            return error_response(message="简历不存在", code=404)

        return success_response(data={
            "id": row[0],
            "hr_job_id": row[1],
            "candidate_id": row[2],
            "resume_url": row[3],
            "status": row[4],
            "match_score": row[5],
            "notes": row[6],
            "received_at": row[7],
            "updated_at": row[8],
        })

    except Exception as e:
        return error_response(message=f"获取失败: {str(e)}", code=500)


@router.put("/{resume_id}/status", response_model=dict)
async def update_resume_status(
    resume_id: int,
    status: str = Query(..., description="新状态: pending/contacted/rejected/hired"),
    notes: Optional[str] = Query(None, description="备注"),
    db: aiosqlite.Connection = Depends(get_database),
):
    """更新简历状态"""
    try:
        updates = ["status = ?", "updated_at = ?"]
        params = [status, datetime.now()]

        if notes is not None:
            updates.append("notes = ?")
            params.append(notes)

        params.append(resume_id)

        await db.execute(
            f"UPDATE received_resumes SET {', '.join(updates)} WHERE id = ?",
            params
        )
        await db.commit()

        return success_response(message="状态更新成功")

    except Exception as e:
        return error_response(message=f"更新失败: {str(e)}", code=500)


@router.get("/{resume_id}/download", response_model=dict)
async def download_resume(resume_id: int, db: aiosqlite.Connection = Depends(get_database)):
    """
    获取简历下载链接

    注意：实际下载需要通过RPA模块实现
    """
    try:
        cursor = await db.execute(
            "SELECT resume_url, candidate_id FROM received_resumes WHERE id = ?",
            (resume_id,)
        )
        row = await cursor.fetchone()

        if not row:
            return error_response(message="简历不存在", code=404)

        resume_url, candidate_id = row

        if not resume_url:
            return error_response(message="简历URL不存在", code=400)

        # TODO: 通过RPA模块下载简历
        return success_response(
            data={
                "resume_url": resume_url,
                "candidate_id": candidate_id,
                "message": "简历下载功能需要通过RPA模块实现"
            },
            message="获取简历信息成功"
        )

    except Exception as e:
        return error_response(message=f"获取失败: {str(e)}", code=500)


@router.post("/sync", response_model=dict)
async def sync_resumes(
    hr_job_id: Optional[int] = Query(None, description="职位ID，为空则同步所有"),
    db: aiosqlite.Connection = Depends(get_database),
):
    """
    同步收到的简历

    注意：实际同步需要通过RPA模块实现
    """
    try:
        # TODO: 调用RPA模块获取新简历
        return success_response(
            data={
                "hr_job_id": hr_job_id,
                "synced_count": 0,
                "message": "简历同步功能需要通过RPA模块实现"
            },
            message="同步任务已创建"
        )

    except Exception as e:
        return error_response(message=f"同步失败: {str(e)}", code=500)


@router.get("/statistics/summary", response_model=dict)
async def get_resume_statistics(
    db: aiosqlite.Connection = Depends(get_database),
):
    """获取简历统计信息"""
    try:
        # 按状态统计
        cursor = await db.execute("""
            SELECT status, COUNT(*) as count
            FROM received_resumes
            GROUP BY status
        """)
        status_rows = await cursor.fetchall()

        stats_by_status = {row[0]: row[1] for row in status_rows}

        # 总数
        cursor = await db.execute("SELECT COUNT(*) FROM received_resumes")
        total_row = await cursor.fetchone()
        total = total_row[0] if total_row else 0

        # 今日新增
        cursor = await db.execute("""
            SELECT COUNT(*) FROM received_resumes
            WHERE DATE(received_at) = DATE('now')
        """)
        today_row = await cursor.fetchone()
        today_count = today_row[0] if today_row else 0

        return success_response(data={
            "total": total,
            "today_count": today_count,
            "by_status": stats_by_status,
        })

    except Exception as e:
        return error_response(message=f"获取统计失败: {str(e)}", code=500)
