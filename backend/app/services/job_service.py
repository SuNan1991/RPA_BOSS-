"""
职位服务
"""

from datetime import datetime
from typing import Optional

import aiosqlite

from ..core.logging import get_logger
from ..schemas.job import JobCreate, JobResponse, JobUpdate

logger = get_logger("job_service")


class JobService:
    """职位服务类"""

    def __init__(self, conn: aiosqlite.Connection):
        self.conn = conn

    async def create(self, job: JobCreate) -> JobResponse:
        """创建职位"""
        job_dict = {
            "job_name": job.job_name,
            "company_name": job.company_name,
            "salary": job.salary,
            "city": job.city,
            "area": job.area,
            "experience": job.experience,
            "education": job.education,
            "company_size": job.company_size,
            "industry": job.industry,
            "job_url": job.job_url,
            "boss_title": job.boss_title,
            "status": "pending",
            "is_applied": False,
            "notes": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        cursor = await self.conn.execute(
            """
            INSERT INTO jobs (job_name, company_name, salary, city, area, experience,
                             education, company_size, industry, job_url, boss_title,
                             status, is_applied, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_dict["job_name"],
                job_dict["company_name"],
                job_dict["salary"],
                job_dict["city"],
                job_dict["area"],
                job_dict["experience"],
                job_dict["education"],
                job_dict["company_size"],
                job_dict["industry"],
                job_dict["job_url"],
                job_dict["boss_title"],
                job_dict["status"],
                job_dict["is_applied"],
                job_dict["notes"],
                job_dict["created_at"],
                job_dict["updated_at"],
            ),
        )

        job_id = cursor.lastrowid
        await self.conn.commit()
        job_dict["id"] = job_id

        logger.info(f"Created job: {job_id}")
        return JobResponse(**job_dict)

    async def get_by_id(self, job_id: int) -> Optional[JobResponse]:
        """根据ID获取职位"""
        try:
            cursor = await self.conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            row = await cursor.fetchone()
            if row:
                return self._row_to_job_response(row)
        except Exception as e:
            logger.error(f"Error getting job: {e}")
        return None

    async def get_list(
        self,
        skip: int = 0,
        limit: int = 10,
        filters: dict = None,
    ) -> tuple[list[JobResponse], int]:
        """获取职位列表"""
        query = "SELECT * FROM jobs"
        params = []
        where_clauses = []

        if filters:
            if "status" in filters and filters["status"]:
                where_clauses.append("status = ?")
                params.append(filters["status"])

            if "city" in filters and filters["city"]:
                where_clauses.append("city = ?")
                params.append(filters["city"])

            if "company_name" in filters and filters["company_name"]:
                where_clauses.append("company_name LIKE ?")
                params.append(f"%{filters['company_name']}%")

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        try:
            cursor = await self.conn.execute(query, params)
            rows = await cursor.fetchall()

            # 获取总数
            count_query = "SELECT COUNT(*) FROM jobs"
            count_params = []
            if where_clauses:
                count_query += " WHERE " + " AND ".join(where_clauses)
                count_params.extend(params[:-2])  # 排除limit和offset

            count_cursor = await self.conn.execute(count_query, count_params)
            total_row = await count_cursor.fetchone()
            total = total_row[0] if total_row else 0

            result = [self._row_to_job_response(row) for row in rows]
            return result, total
        except Exception as e:
            logger.error(f"Error getting job list: {e}")
            return [], 0

    async def update(self, job_id: int, job: JobUpdate) -> Optional[JobResponse]:
        """更新职位"""
        try:
            update_fields = []
            params = []

            if job.status is not None:
                update_fields.append("status = ?")
                params.append(job.status)

            if job.is_applied is not None:
                update_fields.append("is_applied = ?")
                params.append(job.is_applied)

            if job.notes is not None:
                update_fields.append("notes = ?")
                params.append(job.notes)

            if not update_fields:
                return await self.get_by_id(job_id)

            update_fields.append("updated_at = ?")
            params.extend([datetime.now().isoformat(), job_id])

            query = f"UPDATE jobs SET {', '.join(update_fields)} WHERE id = ?"
            await self.conn.execute(query, params)
            await self.conn.commit()

            return await self.get_by_id(job_id)
        except Exception as e:
            logger.error(f"Error updating job: {e}")
            return None

    async def delete(self, job_id: int) -> bool:
        """删除职位"""
        try:
            cursor = await self.conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
            await self.conn.commit()
            deleted_count = cursor.rowcount
            logger.info(f"Deleted job: {job_id}, deleted_count: {deleted_count}")
            return deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting job: {e}")
            return False

    async def batch_create(self, jobs: list[JobCreate]) -> int:
        """批量创建职位"""
        if not jobs:
            return 0

        now = datetime.now().isoformat()
        jobs_data = []
        for job in jobs:
            jobs_data.append(
                (
                    job.job_name,
                    job.company_name,
                    job.salary,
                    job.city,
                    job.area,
                    job.experience,
                    job.education,
                    job.company_size,
                    job.industry,
                    job.job_url,
                    job.boss_title,
                    "pending",
                    False,
                    None,
                    now,
                    now,
                )
            )

        try:
            await self.conn.executemany(
                """
                INSERT INTO jobs (job_name, company_name, salary, city, area, experience,
                                 education, company_size, industry, job_url, boss_title,
                                 status, is_applied, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                jobs_data,
            )
            await self.conn.commit()
            created_count = len(jobs_data)
            logger.info(f"Batch created {created_count} jobs")
            return created_count
        except Exception as e:
            logger.error(f"Error batch creating jobs: {e}")
            await self.conn.rollback()
            return 0

    def _row_to_job_response(self, row) -> JobResponse:
        """将数据库行转换为JobResponse对象"""
        # row结构: (id, job_name, company_name, salary, city, area, experience,
        #            education, company_size, industry, job_url, boss_title,
        #            status, is_applied, notes, created_at, updated_at)
        return JobResponse(
            id=row[0],
            job_name=row[1],
            company_name=row[2],
            salary=row[3],
            city=row[4],
            area=row[5],
            experience=row[6],
            education=row[7],
            company_size=row[8],
            industry=row[9],
            job_url=row[10],
            boss_title=row[11],
            status=row[12],
            is_applied=bool(row[13]),
            notes=row[14],
            created_at=datetime.fromisoformat(row[15]),
            updated_at=datetime.fromisoformat(row[16]),
        )
