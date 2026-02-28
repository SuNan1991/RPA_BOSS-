"""
HR 服务层
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Optional

import aiosqlite

# Add backend directory to path for rpa modules import
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from ..core.logging import get_logger
from ..schemas.account import AccountResponse

logger = get_logger("hr_service")


class HRService:
    """HR 账号相关服务"""

    def __init__(self, conn: aiosqlite.Connection):
        self.conn = conn

    async def get_hr_accounts(self) -> list[AccountResponse]:
        """
        获取所有 HR 账号

        Returns:
            HR 账号列表
        """
        try:
            cursor = await self.conn.execute(
                """
                SELECT * FROM accounts
                WHERE account_type = 'hr'
                ORDER BY created_at DESC
            """
            )
            rows = await cursor.fetchall()

            accounts = []
            for row in rows:
                accounts.append(self._row_to_account_response(row))

            return accounts

        except Exception as e:
            logger.error(f"Error getting HR accounts: {e}")
            return []

    async def get_active_account_id(self) -> Optional[int]:
        """
        获取当前活跃的 HR 账户 ID

        Returns:
            活跃账户 ID，如果没有则返回 None
        """
        try:
            from rpa.modules.session_manager import SessionManager

            session_manager = SessionManager()
            return await session_manager.get_active_account_id()

        except Exception as e:
            logger.error(f"Error getting active account: {e}")
            return None

    async def switch_active_account(self, account_id: int) -> dict[str, Any]:
        """
        切换活跃的 HR 账号

        Args:
            account_id: 账户 ID

        Returns:
            切换结果
        """
        try:
            from rpa.modules.session_manager import SessionManager

            # 验证账户存在
            account = await self._get_account_by_id(account_id)
            if not account:
                return {"success": False, "message": "账户不存在"}

            if account.account_type != "hr":
                return {"success": False, "message": "该账户不是 HR 账户"}

            # 切换活跃账户
            session_manager = SessionManager()
            success = await session_manager.set_active_account(account_id)

            if success:
                return {
                    "success": True,
                    "message": f"已切换到账户 {account.username or account.phone}",
                    "account_id": account_id,
                }
            else:
                return {"success": False, "message": "该账户没有有效的会话，请先登录"}

        except Exception as e:
            logger.error(f"Error switching account: {e}")
            return {"success": False, "message": f"切换账户失败: {str(e)}"}

    async def save_candidates(self, hr_account_id: int, candidates: list[dict]) -> dict[str, Any]:
        """
        保存候选人数据到数据库

        Args:
            hr_account_id: HR 账户 ID
            candidates: 候选人数据列表

        Returns:
            保存结果
        """
        try:
            saved_count = 0
            updated_count = 0

            for candidate_data in candidates:
                try:
                    # 检查是否已存在
                    profile_url = candidate_data.get("profile_url", "")
                    if not profile_url:
                        continue

                    # 查询是否已存在
                    cursor = await self.conn.execute(
                        """
                        SELECT id FROM candidates
                        WHERE hr_account_id = ? AND profile_url = ?
                    """,
                        (hr_account_id, profile_url),
                    )
                    existing = await cursor.fetchone()

                    now = datetime.now().isoformat()

                    if existing:
                        # 更新
                        await self.conn.execute(
                            """
                            UPDATE candidates
                            SET name = ?, position = ?, experience = ?, education = ?,
                                expected_salary = ?, recent_company = ?, skills = ?,
                                status = ?, updated_at = ?
                            WHERE id = ?
                        """,
                            (
                                candidate_data.get("name", ""),
                                candidate_data.get("position", ""),
                                candidate_data.get("experience", ""),
                                candidate_data.get("education", ""),
                                candidate_data.get("expected_salary", ""),
                                candidate_data.get("recent_company", ""),
                                candidate_data.get("skills", ""),
                                candidate_data.get("status", "active"),
                                now,
                                existing[0],
                            ),
                        )
                        updated_count += 1
                    else:
                        # 插入
                        await self.conn.execute(
                            """
                            INSERT INTO candidates
                            (name, position, experience, education, expected_salary,
                             recent_company, skills, profile_url, status, hr_account_id,
                             created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                candidate_data.get("name", ""),
                                candidate_data.get("position", ""),
                                candidate_data.get("experience", ""),
                                candidate_data.get("education", ""),
                                candidate_data.get("expected_salary", ""),
                                candidate_data.get("recent_company", ""),
                                candidate_data.get("skills", ""),
                                profile_url,
                                candidate_data.get("status", "active"),
                                hr_account_id,
                                now,
                                now,
                            ),
                        )
                        saved_count += 1

                except Exception as e:
                    logger.warning(f"Error saving candidate: {e}")
                    continue

            await self.conn.commit()

            return {
                "success": True,
                "saved": saved_count,
                "updated": updated_count,
                "total": saved_count + updated_count,
                "message": f"保存完成: 新增{saved_count}个, 更新{updated_count}个",
            }

        except Exception as e:
            logger.error(f"Error saving candidates: {e}")
            return {"success": False, "message": f"保存失败: {str(e)}"}

    async def get_candidates(
        self,
        hr_account_id: int,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """
        获取 HR 账号的候选人列表

        Args:
            hr_account_id: HR 账户 ID
            status: 状态筛选
            page: 页码
            page_size: 每页数量

        Returns:
            候选人列表和分页信息
        """
        try:
            offset = (page - 1) * page_size

            # 构建查询
            query = "SELECT * FROM candidates WHERE hr_account_id = ?"
            params = [hr_account_id]

            if status:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([page_size, offset])

            cursor = await self.conn.execute(query, params)
            rows = await cursor.fetchall()

            # 获取总数
            count_query = "SELECT COUNT(*) FROM candidates WHERE hr_account_id = ?"
            count_params = [hr_account_id]
            if status:
                count_query += " AND status = ?"
                count_params.append(status)

            count_cursor = await self.conn.execute(count_query, count_params)
            total_row = await count_cursor.fetchone()
            total = total_row[0] if total_row else 0

            candidates = []
            for row in rows:
                candidates.append(self._row_to_candidate_response(row))

            return {
                "success": True,
                "data": candidates,
                "total": total,
                "page": page,
                "page_size": page_size,
            }

        except Exception as e:
            logger.error(f"Error getting candidates: {e}")
            return {"success": False, "data": [], "total": 0}

    async def record_communication(
        self,
        hr_account_id: int,
        candidate_id: int,
        message_type: str,
        content: str,
        status: str = "sent",
    ) -> dict[str, Any]:
        """
        记录沟通日志

        Args:
            hr_account_id: HR 账户 ID
            candidate_id: 候选人 ID
            message_type: 消息类型
            content: 消息内容
            status: 状态

        Returns:
            记录结果
        """
        try:
            await self.conn.execute(
                """
                INSERT INTO communications
                (candidate_id, hr_account_id, type, content, direction, status, sent_at)
                VALUES (?, ?, ?, ?, 'outgoing', ?, ?)
            """,
                (candidate_id, hr_account_id, message_type, content, status, datetime.now()),
            )
            await self.conn.commit()

            return {"success": True, "message": "沟通记录已保存"}

        except Exception as e:
            logger.error(f"Error recording communication: {e}")
            return {"success": False, "message": f"保存失败: {str(e)}"}

    async def get_statistics(self, hr_account_id: int, days: int = 7) -> dict[str, Any]:
        """
        获取统计数据

        Args:
            hr_account_id: HR 账户 ID
            days: 统计天数

        Returns:
            统计数据
        """
        try:
            from datetime import timedelta

            cutoff_date = datetime.now() - timedelta(days=days)

            # 候选人数量
            cursor = await self.conn.execute(
                """
                SELECT COUNT(*) FROM candidates
                WHERE hr_account_id = ? AND created_at >= ?
            """,
                (hr_account_id, cutoff_date),
            )
            candidates_viewed = (await cursor.fetchone())[0]

            # 打招呼数量
            cursor = await self.conn.execute(
                """
                SELECT COUNT(*) FROM communications
                WHERE hr_account_id = ? AND type = 'greet' AND sent_at >= ?
            """,
                (hr_account_id, cutoff_date),
            )
            greetings_sent = (await cursor.fetchone())[0]

            # 回复数量
            cursor = await self.conn.execute(
                """
                SELECT COUNT(*) FROM communications
                WHERE hr_account_id = ? AND direction = 'incoming' AND sent_at >= ?
            """,
                (hr_account_id, cutoff_date),
            )
            greetings_replied = (await cursor.fetchone())[0]

            return {
                "success": True,
                "data": {
                    "candidates_viewed": candidates_viewed,
                    "greetings_sent": greetings_sent,
                    "greetings_replied": greetings_replied,
                    "reply_rate": round(greetings_replied / greetings_sent * 100, 1)
                    if greetings_sent > 0
                    else 0,
                    "days": days,
                },
            }

        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"success": False, "message": f"获取统计失败: {str(e)}"}

    async def _get_account_by_id(self, account_id: int) -> Optional[AccountResponse]:
        """根据 ID 获取账户"""
        try:
            cursor = await self.conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = await cursor.fetchone()
            if row:
                return self._row_to_account_response(row)
        except Exception as e:
            logger.error(f"Error getting account: {e}")
        return None

    def _row_to_account_response(self, row) -> AccountResponse:
        """将数据库行转换为 AccountResponse 对象"""
        # row 结构需要根据实际表结构调整
        return AccountResponse(
            id=row[0],
            phone=row[1],
            username=row[2] if len(row) > 2 else None,
            is_active=bool(row[3]) if len(row) > 3 else True,
            cookie_status=row[4] if len(row) > 4 else "none",
            last_login=datetime.fromisoformat(row[5]) if len(row) > 5 and row[5] else None,
            created_at=datetime.fromisoformat(row[6]) if len(row) > 6 else datetime.now(),
            updated_at=datetime.fromisoformat(row[7]) if len(row) > 7 else datetime.now(),
        )

    def _row_to_candidate_response(self, row) -> dict[str, Any]:
        """将数据库行转换为候选人响应对象"""
        return {
            "id": row[0],
            "name": row[1],
            "position": row[2],
            "experience": row[3],
            "education": row[4],
            "expected_salary": row[5],
            "recent_company": row[6],
            "skills": row[7],
            "profile_url": row[8],
            "status": row[9],
            "hr_account_id": row[10],
            "created_at": row[11],
            "updated_at": row[12],
        }
