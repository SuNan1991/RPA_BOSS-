"""
账号同步服务
"""

import json
from datetime import datetime
from typing import Optional

import aiosqlite
from pydantic import BaseModel

from ..core.logging import get_logger
from .account_service import AccountService

logger = get_logger("account_sync_service")


class SyncResult(BaseModel):
    """同步结果"""
    account_id: Optional[int]
    is_new_account: bool
    message: str


class AccountSyncService:
    """账号同步服务 - 登录成功后自动同步到账号管理系统"""

    def __init__(self, conn: aiosqlite.Connection):
        self.conn = conn
        self.account_service = AccountService(conn)

    async def identify_account(self, user_info: dict) -> Optional[int]:
        """
        识别账号 - 判断是新账号还是已有账号

        策略优先级：
        1. 通过手机号匹配（优先级最高）
        2. 通过用户名匹配（次优先级）
        3. 返回None表示新账号

        Args:
            user_info: 用户信息字典

        Returns:
            账号ID或None
        """
        # 策略1：手机号匹配
        phone = user_info.get("phone")
        if phone:
            cursor = await self.conn.execute(
                "SELECT id FROM accounts WHERE phone = ?",
                (phone,)
            )
            row = await cursor.fetchone()
            if row:
                logger.info(f"Account identified by phone: {phone} -> ID: {row[0]}")
                return row[0]

        # 策略2：用户名匹配
        username = user_info.get("username")
        if username and username != "BOSS用户":  # 排除默认值
            cursor = await self.conn.execute(
                "SELECT id FROM accounts WHERE username = ?",
                (username,)
            )
            row = await cursor.fetchone()
            if row:
                logger.info(f"Account identified by username: {username} -> ID: {row[0]}")
                return row[0]

        logger.info("No existing account found, will create new account")
        return None

    async def sync_account_from_login(
        self,
        cookies: list[dict],
        user_info: dict
    ) -> SyncResult:
        """
        从登录信息同步账号

        Args:
            cookies: 浏览器提取的cookies
            user_info: 用户信息（包含username等）

        Returns:
            SyncResult: 包含 account_id, is_new_account, message
        """
        try:
            # 验证 user_info
            if not user_info or not user_info.get("username"):
                # 使用默认值
                user_info = {
                    "username": "BOSS用户",
                    "source": "default",
                    "auto_created": True
                }
                logger.warning("Using default user info due to missing data")

            # 1. 识别账号
            account_id = await self.identify_account(user_info)

            # 2. 创建或更新账号
            if account_id:
                # 更新已有账号
                await self._update_account(account_id, user_info, cookies)
                is_new = False
                message = "账号已更新"
                logger.info(f"Updated existing account: {account_id}")
            else:
                # 创建新账号
                account_id = await self._create_auto_account(user_info, cookies)
                is_new = True
                message = "新账号已自动添加"
                logger.info(f"Created new account: {account_id}")

            # 3. 保存到 account_sessions 表
            await self._save_session_for_account(account_id, cookies, user_info)

            return SyncResult(
                account_id=account_id,
                is_new_account=is_new,
                message=message
            )

        except Exception as e:
            logger.error(f"Account sync failed: {e}", exc_info=True)
            # 降级：返回None但不影响登录
            return SyncResult(
                account_id=None,
                is_new_account=False,
                message="同步失败，但登录成功"
            )

    async def _create_auto_account(self, user_info: dict, cookies: list[dict]) -> int:
        """
        创建自动账号

        Args:
            user_info: 用户信息
            cookies: Cookie数据

        Returns:
            新创建的账号ID
        """
        now = datetime.now().isoformat()

        # 生成唯一手机号（如果user_info中没有）
        phone = user_info.get("phone")
        if not phone:
            # 生成临时手机号避免冲突
            import time
            timestamp = int(time.time() * 1000)
            phone = f"auto_{timestamp}"

        username = user_info.get("username", "BOSS用户")

        # 判断账号类型（根据来源URL或其他信息）
        account_type = "hr"  # 默认为HR
        if user_info.get("account_type"):
            account_type = user_info["account_type"]

        account_dict = {
            "phone": phone,
            "username": username,
            "is_active": True,
            "cookie_status": "valid",
            "account_type": account_type,
            "group_id": None,
            "tags": json.dumps(["自动创建"]) if user_info.get("auto_created") else None,
            "notes": "通过登录自动创建" if user_info.get("auto_created") else None,
            "login_count": 1,
            "last_login": now,
            "last_operation_at": now,
            "quota_limit": 100,
            "quota_used": 0,
            "auto_created": 1,
            "last_sync_at": now,
            "sync_source": "auto_login",
            "created_at": now,
            "updated_at": now,
        }

        cursor = await self.conn.execute(
            """
            INSERT INTO accounts (
                phone, username, is_active, cookie_status, account_type, group_id, tags, notes,
                login_count, last_login, last_operation_at, quota_limit, quota_used,
                auto_created, last_sync_at, sync_source,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                account_dict["phone"],
                account_dict["username"],
                account_dict["is_active"],
                account_dict["cookie_status"],
                account_dict["account_type"],
                account_dict["group_id"],
                account_dict["tags"],
                account_dict["notes"],
                account_dict["login_count"],
                account_dict["last_login"],
                account_dict["last_operation_at"],
                account_dict["quota_limit"],
                account_dict["quota_used"],
                account_dict["auto_created"],
                account_dict["last_sync_at"],
                account_dict["sync_source"],
                account_dict["created_at"],
                account_dict["updated_at"],
            ),
        )

        account_id = cursor.lastrowid
        await self.conn.commit()

        logger.info(f"Created auto account: {account_id} ({username})")
        return account_id

    async def _update_account(self, account_id: int, user_info: dict, cookies: list[dict]):
        """
        更新已有账号

        Args:
            account_id: 账号ID
            user_info: 用户信息
            cookies: Cookie数据
        """
        now = datetime.now().isoformat()
        username = user_info.get("username", "BOSS用户")

        # 更新账号信息
        await self.conn.execute(
            """
            UPDATE accounts
            SET username = ?,
                cookie_status = 'valid',
                last_login = ?,
                last_sync_at = ?,
                login_count = login_count + 1,
                updated_at = ?
            WHERE id = ?
            """,
            (username, now, now, now, account_id)
        )

        await self.conn.commit()
        logger.info(f"Updated account {account_id}: last_login={now}")

    async def _save_session_for_account(self, account_id: int, cookies: list[dict], user_info: dict):
        """
        保存session到account_sessions表

        Args:
            account_id: 账号ID
            cookies: Cookie数据
            user_info: 用户信息
        """
        from rpa.modules.session_manager import SessionManager

        # 创建临时的 SessionManager 实例
        session_manager = SessionManager()

        # 使用 SessionManager 的保存方法
        await session_manager.save_session_for_account(
            account_id=account_id,
            cookies=cookies,
            user_info=user_info
        )

        logger.info(f"Saved session for account {account_id}")
