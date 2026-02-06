"""
任务服务
"""

import json
from datetime import datetime
from typing import Optional

import aiosqlite

from ..core.logging import get_logger
from ..schemas.task import TaskCreate, TaskResponse, TaskUpdate

logger = get_logger("task_service")


class TaskService:
    """任务服务类"""

    def __init__(self, conn: aiosqlite.Connection):
        self.conn = conn

    async def create(self, task: TaskCreate) -> TaskResponse:
        """创建任务"""
        config_json = json.dumps(task.config, ensure_ascii=False)
        now = datetime.now().isoformat()

        cursor = await self.conn.execute(
            """
            INSERT INTO tasks (
                name, task_type, config, status, result,
                error_message, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (task.name, task.task_type, config_json, "pending", None, None, now, now),
        )

        task_id = cursor.lastrowid
        await self.conn.commit()

        logger.info(f"Created task: {task_id}")
        return TaskResponse(
            id=task_id,
            name=task.name,
            task_type=task.task_type,
            config=task.config,
            status="pending",
            result=None,
            error_message=None,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now),
        )

    async def get_by_id(self, task_id: int) -> Optional[TaskResponse]:
        """根据ID获取任务"""
        try:
            cursor = await self.conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = await cursor.fetchone()
            if row:
                return self._row_to_task_response(row)
        except Exception as e:
            logger.error(f"Error getting task: {e}")
        return None

    async def get_list(
        self,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
    ) -> tuple[list[TaskResponse], int]:
        """获取任务列表"""
        query = "SELECT * FROM tasks"
        params = []
        where_clauses = []

        if status:
            where_clauses.append("status = ?")
            params.append(status)

        if task_type:
            where_clauses.append("task_type = ?")
            params.append(task_type)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        try:
            cursor = await self.conn.execute(query, params)
            rows = await cursor.fetchall()

            # 获取总数
            count_query = "SELECT COUNT(*) FROM tasks"
            count_params = []
            if where_clauses:
                count_query += " WHERE " + " AND ".join(where_clauses)
                count_params.extend(params[:-2])  # 排除limit和offset

            count_cursor = await self.conn.execute(count_query, count_params)
            total_row = await count_cursor.fetchone()
            total = total_row[0] if total_row else 0

            result = [self._row_to_task_response(row) for row in rows]
            return result, total
        except Exception as e:
            logger.error(f"Error getting task list: {e}")
            return [], 0

    async def update(self, task_id: int, task: TaskUpdate) -> Optional[TaskResponse]:
        """更新任务"""
        try:
            update_fields = []
            params = []

            if task.status is not None:
                update_fields.append("status = ?")
                params.append(task.status)

            if task.config is not None:
                update_fields.append("config = ?")
                params.append(json.dumps(task.config, ensure_ascii=False))

            if task.result is not None:
                update_fields.append("result = ?")
                params.append(json.dumps(task.result, ensure_ascii=False))

            if not update_fields:
                return await self.get_by_id(task_id)

            update_fields.append("updated_at = ?")
            params.extend([datetime.now().isoformat(), task_id])

            query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
            await self.conn.execute(query, params)
            await self.conn.commit()

            return await self.get_by_id(task_id)
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return None

    async def update_status(
        self, task_id: int, status: str, result: dict = None, error_message: str = None
    ) -> Optional[TaskResponse]:
        """更新任务状态"""
        try:
            update_fields = ["status = ?", "updated_at = ?"]
            params = [status, datetime.now().isoformat()]

            if result is not None:
                update_fields.append("result = ?")
                params.append(json.dumps(result, ensure_ascii=False))

            if error_message is not None:
                update_fields.append("error_message = ?")
                params.append(error_message)

            params.append(task_id)

            query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
            await self.conn.execute(query, params)
            await self.conn.commit()

            logger.info(f"Updated task status: {task_id} -> {status}")
            return await self.get_by_id(task_id)
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            return None

    async def delete(self, task_id: int) -> bool:
        """删除任务"""
        try:
            cursor = await self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            await self.conn.commit()
            deleted_count = cursor.rowcount
            logger.info(f"Deleted task: {task_id}, deleted_count: {deleted_count}")
            return deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return False

    def _row_to_task_response(self, row) -> TaskResponse:
        """将数据库行转换为TaskResponse对象"""
        # row结构:
        # (id, name, task_type, config, status, result,
        #  error_message, created_at, updated_at)
        config = json.loads(row[3]) if row[3] else {}
        result = json.loads(row[5]) if row[5] else None

        return TaskResponse(
            id=row[0],
            name=row[1],
            task_type=row[2],
            config=config,
            status=row[4],
            result=result,
            error_message=row[6],
            created_at=datetime.fromisoformat(row[7]),
            updated_at=datetime.fromisoformat(row[8]),
        )
