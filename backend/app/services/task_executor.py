"""
任务执行器
负责执行各种类型的后台任务
"""

import asyncio
from datetime import datetime
from typing import Any, Optional

import aiosqlite

from app.core.logging import get_logger
from rpa.modules.hr.batch_greet import BatchGreetModule
from rpa.modules.hr.candidate_search import CandidateSearchModule

logger = get_logger("task_executor")


class TaskExecutor:
    """任务执行器"""

    def __init__(self, db: aiosqlite.Connection):
        self.db = db
        self.running_tasks: dict[int, bool] = {}

    async def execute_task(self, task_id: int, task_config: dict[str, Any]) -> dict[str, Any]:
        """
        执行任务的入口方法

        Args:
            task_id: 任务ID
            task_config: 任务配置

        Returns:
            执行结果
        """
        task_type = task_config.get("task_type", "")

        # 标记任务为运行中
        self.running_tasks[task_id] = True

        try:
            logger.info(f"Executing task {task_id} of type: {task_type}")

            if task_type == "search_candidate":
                result = await self._execute_search_candidate(task_config)
            elif task_type == "batch_greet":
                result = await self._execute_batch_greet(task_config)
            elif task_type == "auto_chat":
                result = await self._execute_auto_chat(task_config)
            else:
                result = {
                    "success": False,
                    "message": f"Unknown task type: {task_type}",
                    "data": {},
                }

            # 更新任务状态
            if result["success"]:
                await self._update_task_status(task_id, "completed", result=result["data"])
            else:
                await self._update_task_status(task_id, "failed", error_message=result.get("message", "Unknown error"))

            return result

        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            await self._update_task_status(task_id, "failed", error_message=str(e))
            return {
                "success": False,
                "message": str(e),
                "data": {},
            }
        finally:
            # 清除运行标记
            self.running_tasks.pop(task_id, None)

    async def _execute_search_candidate(self, config: dict[str, Any]) -> dict[str, Any]:
        """
        执行候选人搜索任务

        Args:
            config: 搜索配置

        Returns:
            搜索结果
        """
        try:
            # 提取搜索参数
            keyword = config.get("keyword", "")
            city = config.get("city", "全国")
            experience = config.get("experience")
            education = config.get("education")
            salary = config.get("salary")
            age = config.get("age")
            gender = config.get("gender")
            max_pages = config.get("max_pages", 1)
            hr_account_id = config.get("hr_account_id")

            # 创建搜索模块
            module = CandidateSearchModule()

            # 执行搜索（在单独的线程中运行同步代码）
            loop = asyncio.get_event_loop()
            search_result = await loop.run_in_executor(
                None,
                lambda: module.execute(
                    keyword=keyword,
                    city=city,
                    experience=experience,
                    education=education,
                    salary=salary,
                    age=age,
                    gender=gender,
                    max_pages=max_pages,
                    hr_account_id=hr_account_id,
                ),
            )

            # 如果搜索成功，保存候选人到数据库
            if search_result.get("success") and search_result.get("data"):
                await self._save_candidates(search_result["data"], hr_account_id)

            return search_result

        except Exception as e:
            logger.error(f"Search candidate task failed: {e}")
            return {
                "success": False,
                "message": f"候选人搜索失败: {str(e)}",
                "data": {},
            }

    async def _execute_batch_greet(self, config: dict[str, Any]) -> dict[str, Any]:
        """
        执行批量打招呼任务

        Args:
            config: 打招呼配置

        Returns:
            打招呼结果
        """
        try:
            # 提取参数
            candidate_ids = config.get("candidate_ids", [])
            template = config.get("template")
            rate_limit = config.get("rate_limit")
            hr_account_id = config.get("hr_account_id")

            # 获取候选人数据
            candidates_data = []
            if candidate_ids:
                candidates_data = await self._get_candidates_by_ids(candidate_ids)

            # 创建打招呼模块
            module = BatchGreetModule()

            # 执行批量打招呼
            loop = asyncio.get_event_loop()
            greet_result = await loop.run_in_executor(
                None,
                lambda: module.execute(
                    candidate_ids=candidate_ids,
                    candidates_data=candidates_data,
                    template=template,
                    rate_limit=rate_limit,
                    hr_account_id=hr_account_id,
                ),
            )

            # 记录沟通日志
            if greet_result.get("success"):
                await self._save_communications(greet_result["data"], hr_account_id)

            return greet_result

        except Exception as e:
            logger.error(f"Batch greet task failed: {e}")
            return {
                "success": False,
                "message": f"批量打招呼失败: {str(e)}",
                "data": {},
            }

    async def _execute_auto_chat(self, config: dict[str, Any]) -> dict[str, Any]:
        """
        执行自动聊天任务

        Args:
            config: 聊天配置

        Returns:
            聊天结果
        """
        try:
            # 自动聊天功能待实现
            logger.info("Auto chat task - to be implemented")

            return {
                "success": False,
                "message": "自动聊天功能待实现",
                "data": {},
            }

        except Exception as e:
            logger.error(f"Auto chat task failed: {e}")
            return {
                "success": False,
                "message": f"自动聊天失败: {str(e)}",
                "data": {},
            }

    async def _save_candidates(self, candidates: list[dict], hr_account_id: Optional[int]) -> int:
        """
        保存候选人到数据库

        Args:
            candidates: 候选人列表
            hr_account_id: HR账户ID

        Returns:
            保存数量
        """
        try:
            saved_count = 0
            now = datetime.now().isoformat()

            for candidate in candidates:
                try:
                    # 检查是否已存在
                    profile_url = candidate.get("profile_url", "")
                    if not profile_url:
                        continue

                    cursor = await self.db.execute(
                        "SELECT id FROM candidates WHERE profile_url = ?", (profile_url,)
                    )
                    existing = await cursor.fetchone()

                    if existing:
                        # 更新现有候选人
                        await self.db.execute(
                            """
                            UPDATE candidates SET
                                name = ?, position = ?, experience = ?, education = ?,
                                expected_salary = ?, recent_company = ?, skills = ?,
                                status = 'pending', updated_at = ?
                            WHERE profile_url = ?
                            """,
                            (
                                candidate.get("name", ""),
                                candidate.get("position", ""),
                                candidate.get("experience", ""),
                                candidate.get("education", ""),
                                candidate.get("expected_salary", ""),
                                candidate.get("recent_company", ""),
                                candidate.get("skills", ""),
                                now,
                                profile_url,
                            ),
                        )
                    else:
                        # 插入新候选人
                        await self.db.execute(
                            """
                            INSERT INTO candidates (
                                hr_account_id, name, position, experience, education,
                                expected_salary, recent_company, skills, profile_url,
                                status, created_at, updated_at
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                hr_account_id,
                                candidate.get("name", ""),
                                candidate.get("position", ""),
                                candidate.get("experience", ""),
                                candidate.get("education", ""),
                                candidate.get("expected_salary", ""),
                                candidate.get("recent_company", ""),
                                candidate.get("skills", ""),
                                profile_url,
                                "pending",
                                now,
                                now,
                            ),
                        )
                        saved_count += 1

                except Exception as e:
                    logger.warning(f"Error saving candidate: {e}")
                    continue

            await self.db.commit()
            logger.info(f"Saved {saved_count} new candidates")
            return saved_count

        except Exception as e:
            logger.error(f"Error saving candidates: {e}")
            return 0

    async def _get_candidates_by_ids(self, candidate_ids: list[int]) -> list[dict]:
        """
        根据ID列表获取候选人数据

        Args:
            candidate_ids: 候选人ID列表

        Returns:
            候选人数据列表
        """
        try:
            if not candidate_ids:
                return []

            placeholders = ",".join("?" * len(candidate_ids))
            query = f"SELECT * FROM candidates WHERE id IN ({placeholders})"

            cursor = await self.db.execute(query, candidate_ids)
            rows = await cursor.fetchall()

            candidates = []
            for row in rows:
                # row结构需要根据实际表结构调整
                candidates.append({
                    "id": row[0],
                    "name": row[2] if len(row) > 2 else "",
                    "profile_url": row[9] if len(row) > 9 else "",
                })

            return candidates

        except Exception as e:
            logger.error(f"Error getting candidates by IDs: {e}")
            return []

    async def _save_communications(self, result: dict, hr_account_id: Optional[int]):
        """
        保存沟通记录

        Args:
            result: 打招呼结果
            hr_account_id: HR账户ID
        """
        try:
            now = datetime.now().isoformat()

            for detail in result.get("details", []):
                if detail.get("success"):
                    await self.db.execute(
                        """
                        INSERT INTO communications (
                            hr_account_id, candidate_id, type, message,
                            status, created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            hr_account_id,
                            detail.get("candidate_id"),
                            "greet",
                            "",
                            "sent",
                            now,
                        ),
                    )

            await self.db.commit()

        except Exception as e:
            logger.error(f"Error saving communications: {e}")

    async def _update_task_status(
        self,
        task_id: int,
        status: str,
        result: Optional[dict] = None,
        error_message: Optional[str] = None,
    ):
        """
        更新任务状态

        Args:
            task_id: 任务ID
            status: 状态
            result: 结果数据
            error_message: 错误消息
        """
        try:
            import json

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
            await self.db.execute(query, params)
            await self.db.commit()

            logger.info(f"Updated task status: {task_id} -> {status}")

        except Exception as e:
            logger.error(f"Error updating task status: {e}")

    def is_task_running(self, task_id: int) -> bool:
        """
        检查任务是否正在运行

        Args:
            task_id: 任务ID

        Returns:
            是否正在运行
        """
        return self.running_tasks.get(task_id, False)

    async def stop_task(self, task_id: int) -> bool:
        """
        停止任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功停止
        """
        if task_id in self.running_tasks:
            self.running_tasks[task_id] = False
            await self._update_task_status(task_id, "cancelled")
            return True
        return False
