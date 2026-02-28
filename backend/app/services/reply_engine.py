"""
自动回复规则引擎
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Any, Optional

import aiosqlite

from app.core.logging import get_logger
from rpa.modules.hr.batch_greet import BatchGreetModule

logger = get_logger("reply_engine")


class ReplyRule:
    """回复规则数据类"""

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.hr_account_id = kwargs.get("hr_account_id")
        self.trigger_keywords = kwargs.get("trigger_keywords", "")
        self.reply_template = kwargs.get("reply_template", "")
        self.auto_invite = kwargs.get("auto_invite", False)
        self.priority = kwargs.get("priority", 0)
        self.is_active = kwargs.get("is_active", True)

    def get_keywords(self) -> list[str]:
        """获取关键词列表"""
        try:
            if isinstance(self.trigger_keywords, str):
                return [k.strip() for k in self.trigger_keywords.split(",") if k.strip()]
            return self.trigger_keywords or []
        except Exception:
            return []

    def match(self, message: str) -> bool:
        """
        检查消息是否匹配规则

        Args:
            message: 收到的消息

        Returns:
            bool: 是否匹配
        """
        if not self.is_active:
            return False

        keywords = self.get_keywords()
        message_lower = message.lower()

        for keyword in keywords:
            if keyword.lower() in message_lower:
                return True

        return False

    def format_reply(self, context: dict) -> str:
        """
        格式化回复模板

        Args:
            context: 上下文变量

        Returns:
            格式化后的回复
        """
        reply = self.reply_template
        for key, value in context.items():
            reply = reply.replace(f"{{{key}}}", str(value))
        return reply


class ReplyEngine:
    """自动回复引擎"""

    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def match_rule(
        self, message: str, hr_account_id: int
    ) -> Optional[ReplyRule]:
        """
        根据消息匹配最佳回复规则

        Args:
            message: 收到的消息
            hr_account_id: HR账户ID

        Returns:
            匹配的规则，如果没有匹配则返回None
        """
        try:
            # 获取该账户的所有活跃规则，按优先级排序
            cursor = await self.db.execute(
                """
                SELECT * FROM auto_reply_rules
                WHERE hr_account_id = ? AND is_active = 1
                ORDER BY priority DESC, id ASC
            """,
                (hr_account_id,),
            )
            rows = await cursor.fetchall()

            if not rows:
                logger.debug(f"No active reply rules found for account {hr_account_id}")
                return None

            # 查找第一个匹配的规则
            for row in rows:
                rule = ReplyRule(
                    id=row[0],
                    hr_account_id=row[1],
                    trigger_keywords=row[2],
                    reply_template=row[3],
                    auto_invite=bool(row[4]),
                    priority=row[5],
                    is_active=bool(row[6]),
                )

                if rule.match(message):
                    logger.info(f"Matched reply rule {rule.id} for message: {message[:50]}...")
                    return rule

            logger.debug(f"No matching reply rule for message: {message[:50]}...")
            return None

        except Exception as e:
            logger.error(f"Error matching reply rule: {e}")
            return None

    async def execute_rule(
        self, rule: ReplyRule, context: dict
    ) -> dict[str, Any]:
        """
        执行回复规则

        Args:
            rule: 回复规则
            context: 上下文变量（候选人信息等）

        Returns:
            执行结果
        """
        try:
            # 格式化回复消息
            reply_message = rule.format_reply(context)

            result = {
                "success": True,
                "rule_id": rule.id,
                "reply_message": reply_message,
                "auto_invite": rule.auto_invite,
            }

            # 如果设置了自动打招呼，触发打招呼
            if rule.auto_invite and context.get("candidate_id"):
                await self._send_auto_greet(
                    rule.hr_account_id, context["candidate_id"], reply_message
                )

            logger.info(f"Executed reply rule {rule.id}")
            return result

        except Exception as e:
            logger.error(f"Error executing reply rule: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def auto_reply(self, message_data: dict) -> dict[str, Any]:
        """
        自动回复消息

        Args:
            message_data: 消息数据，包含 message, candidate_id, hr_account_id 等

        Returns:
            回复结果
        """
        try:
            message = message_data.get("message", "")
            hr_account_id = message_data.get("hr_account_id")
            candidate_id = message_data.get("candidate_id")
            candidate_name = message_data.get("candidate_name", "候选人")

            if not hr_account_id:
                return {"success": False, "error": "Missing hr_account_id"}

            # 匹配规则
            rule = await self.match_rule(message, hr_account_id)
            if not rule:
                return {"success": False, "error": "No matching rule"}

            # 准备上下文
            context = {
                "candidate_name": candidate_name,
                "candidate_id": candidate_id,
                "message": message,
            }

            # 执行规则
            result = await self.execute_rule(rule, context)

            # 记录回复
            await self._log_reply(
                hr_account_id,
                candidate_id,
                message,
                result.get("reply_message", ""),
                rule.id,
            )

            return result

        except Exception as e:
            logger.error(f"Error in auto_reply: {e}")
            return {"success": False, "error": str(e)}

    async def _send_auto_greet(
        self, hr_account_id: int, candidate_id: int, message: str
    ):
        """
        发送自动打招呼

        Args:
            hr_account_id: HR账户ID
            candidate_id: 候选人ID
            message: 消息内容
        """
        try:
            # 这里可以集成打招呼模块
            logger.info(
                f"Auto greet triggered for candidate {candidate_id} with message: {message[:50]}..."
            )

        except Exception as e:
            logger.error(f"Error sending auto greet: {e}")

    async def _log_reply(
        self,
        hr_account_id: int,
        candidate_id: Optional[int],
        received_message: str,
        reply_message: str,
        rule_id: int,
    ):
        """
        记录自动回复

        Args:
            hr_account_id: HR账户ID
            candidate_id: 候选人ID
            received_message: 收到的消息
            reply_message: 回复消息
            rule_id: 规则ID
        """
        try:
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
                    candidate_id,
                    "auto_reply",
                    f"Received: {received_message}\nReplied: {reply_message}\nRule: {rule_id}",
                    "sent",
                    datetime.now(),
                ),
            )
            await self.db.commit()

        except Exception as e:
            logger.error(f"Error logging reply: {e}")


class ReplyRuleService:
    """回复规则服务"""

    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create(
        self,
        hr_account_id: int,
        trigger_keywords: str,
        reply_template: str,
        auto_invite: bool = False,
        priority: int = 0,
        is_active: bool = True,
    ) -> ReplyRule:
        """
        创建回复规则

        Args:
            hr_account_id: HR账户ID
            trigger_keywords: 触发关键词（逗号分隔）
            reply_template: 回复模板
            auto_invite: 是否自动打招呼
            priority: 优先级
            is_active: 是否启用

        Returns:
            创建的规则
        """
        try:
            cursor = await self.db.execute(
                """
                INSERT INTO auto_reply_rules
                (hr_account_id, trigger_keywords, reply_template, auto_invite, priority, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    hr_account_id,
                    trigger_keywords,
                    reply_template,
                    1 if auto_invite else 0,
                    priority,
                    1 if is_active else 0,
                    datetime.now(),
                ),
            )
            rule_id = cursor.lastrowid
            await self.db.commit()

            logger.info(f"Created reply rule {rule_id}")
            return await self.get_by_id(rule_id)

        except Exception as e:
            logger.error(f"Error creating reply rule: {e}")
            raise

    async def get_by_id(self, rule_id: int) -> Optional[ReplyRule]:
        """根据ID获取规则"""
        try:
            cursor = await self.db.execute(
                "SELECT * FROM auto_reply_rules WHERE id = ?", (rule_id,)
            )
            row = await cursor.fetchone()
            if row:
                return ReplyRule(
                    id=row[0],
                    hr_account_id=row[1],
                    trigger_keywords=row[2],
                    reply_template=row[3],
                    auto_invite=bool(row[4]),
                    priority=row[5],
                    is_active=bool(row[6]),
                )
            return None

        except Exception as e:
            logger.error(f"Error getting reply rule: {e}")
            return None

    async def get_list(
        self, hr_account_id: Optional[int] = None, is_active: Optional[bool] = None
    ) -> list[ReplyRule]:
        """获取规则列表"""
        try:
            query = "SELECT * FROM auto_reply_rules WHERE 1=1"
            params = []

            if hr_account_id is not None:
                query += " AND hr_account_id = ?"
                params.append(hr_account_id)

            if is_active is not None:
                query += " AND is_active = ?"
                params.append(1 if is_active else 0)

            query += " ORDER BY priority DESC, created_at DESC"

            cursor = await self.db.execute(query, params)
            rows = await cursor.fetchall()

            return [
                ReplyRule(
                    id=row[0],
                    hr_account_id=row[1],
                    trigger_keywords=row[2],
                    reply_template=row[3],
                    auto_invite=bool(row[4]),
                    priority=row[5],
                    is_active=bool(row[6]),
                )
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Error getting reply rules: {e}")
            return []

    async def update(
        self,
        rule_id: int,
        trigger_keywords: Optional[str] = None,
        reply_template: Optional[str] = None,
        auto_invite: Optional[bool] = None,
        priority: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[ReplyRule]:
        """更新规则"""
        try:
            updates = []
            params = []

            if trigger_keywords is not None:
                updates.append("trigger_keywords = ?")
                params.append(trigger_keywords)
            if reply_template is not None:
                updates.append("reply_template = ?")
                params.append(reply_template)
            if auto_invite is not None:
                updates.append("auto_invite = ?")
                params.append(1 if auto_invite else 0)
            if priority is not None:
                updates.append("priority = ?")
                params.append(priority)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)

            if updates:
                params.append(rule_id)
                await self.db.execute(
                    f"UPDATE auto_reply_rules SET {', '.join(updates)} WHERE id = ?",
                    params,
                )
                await self.db.commit()

            return await self.get_by_id(rule_id)

        except Exception as e:
            logger.error(f"Error updating reply rule: {e}")
            return None

    async def delete(self, rule_id: int) -> bool:
        """删除规则"""
        try:
            await self.db.execute("DELETE FROM auto_reply_rules WHERE id = ?", (rule_id,))
            await self.db.commit()
            logger.info(f"Deleted reply rule {rule_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting reply rule: {e}")
            return False
