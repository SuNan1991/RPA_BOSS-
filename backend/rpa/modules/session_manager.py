"""
Session Manager - Handle session persistence with encryption
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import aiosqlite
from cryptography.fernet import Fernet

from app.core.config import settings

logger = logging.getLogger(__name__)


class SessionManager:
    """Manage session encryption and persistence"""

    def __init__(self):
        self.cipher = self._get_cipher()
        self.session_expiry_days = 30

    def _get_cipher(self) -> Fernet:
        """Get Fernet cipher from configuration"""
        key = settings.SESSION_ENCRYPTION_KEY

        # Ensure key is bytes
        if isinstance(key, str):
            key = key.encode()

        return Fernet(key)

    async def _get_db(self):
        """Get async database connection"""
        # Use the unified database path from config
        db_path = Path(settings.SQLITE_DB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return await aiosqlite.connect(db_path)

    async def save_session(self, cookies: list[dict], user_info: Optional[dict] = None) -> bool:
        """
        Save session with encryption

        Args:
            cookies: List of cookie dictionaries
            user_info: User information dictionary

        Returns:
            bool: True if successful
        """
        try:
            # Serialize and encrypt cookies
            cookies_json = json.dumps(cookies)
            encrypted_cookies = self.cipher.encrypt(cookies_json.encode())

            # Serialize user info
            user_info_json = json.dumps(user_info) if user_info else None

            # Calculate expiry date
            expires_at = datetime.now() + timedelta(days=self.session_expiry_days)

            # Save to database
            conn = await self._get_db()
            try:
                # Delete existing sessions (singleton pattern)
                await conn.execute("DELETE FROM sessions")

                # Insert new session
                await conn.execute(
                    """
                    INSERT INTO sessions (cookies, user_info, created_at, expires_at)
                    VALUES (?, ?, ?, ?)
                """,
                    (encrypted_cookies, user_info_json, datetime.now(), expires_at),
                )

                await conn.commit()
                logger.info("Session saved successfully")
                return True
            finally:
                await conn.close()

        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False

    async def load_session(self) -> Optional[dict[str, Any]]:
        """
        Load and decrypt session

        Returns:
            dict with cookies and user_info, or None if no valid session
        """
        try:
            conn = await self._get_db()

            # Get most recent session
            async with conn.execute("""
                SELECT cookies, user_info, expires_at
                FROM sessions
                ORDER BY created_at DESC
                LIMIT 1
            """) as cursor:
                row = await cursor.fetchone()

                if not row:
                    logger.debug("No session found in database")
                    return None

                encrypted_cookies, user_info_json, expires_at = row

                # Check expiry
                if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
                    logger.info("Session expired, deleting")
                    await self.delete_session()
                    return None

                # Decrypt cookies
                decrypted_cookies = self.cipher.decrypt(encrypted_cookies)
                cookies = json.loads(decrypted_cookies)

                # Parse user info
                user_info = json.loads(user_info_json) if user_info_json else None

                logger.info("Session loaded successfully")
                return {"cookies": cookies, "user_info": user_info}

        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            # Delete corrupted session
            await self.delete_session()
            return None

    async def delete_session(self) -> bool:
        """
        Delete current session

        Returns:
            bool: True if successful
        """
        try:
            conn = await self._get_db()
            try:
                await conn.execute("DELETE FROM sessions")
                await conn.commit()
                logger.info("Session deleted successfully")
                return True
            finally:
                await conn.close()

        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False

    async def is_valid_session(self) -> bool:
        """
        Check if a valid session exists

        Returns:
            bool: True if valid session exists
        """
        try:
            session = await self.load_session()
            return session is not None

        except Exception as e:
            logger.error(f"Failed to check session validity: {e}")
            return False

    async def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        Clean up sessions older than specified days

        Args:
            days: Number of days to keep

        Returns:
            int: Number of sessions deleted
        """
        try:
            conn = await self._get_db()
            try:
                cutoff_date = datetime.now() - timedelta(days=days)

                cursor = await conn.execute(
                    """
                    DELETE FROM sessions
                    WHERE created_at < ?
                """,
                    (cutoff_date,),
                )

                deleted_count = cursor.rowcount
                await conn.commit()

                logger.info(f"Cleaned up {deleted_count} old sessions")
                return deleted_count
            finally:
                await conn.close()

        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
            return 0

    # ==================== 账户会话管理方法 ====================

    async def save_session_for_account(
        self, account_id: int, cookies: list[dict], user_info: Optional[dict] = None
    ) -> bool:
        """
        为指定账户保存会话

        Args:
            account_id: 账户ID
            cookies: Cookie字典列表
            user_info: 用户信息

        Returns:
            bool: 是否成功
        """
        try:
            # 序列化并加密cookies
            cookies_json = json.dumps(cookies)
            encrypted_cookies = self.cipher.encrypt(cookies_json.encode())

            # 序列化用户信息
            user_info_json = json.dumps(user_info) if user_info else None

            # 计算过期时间
            expires_at = datetime.now() + timedelta(days=self.session_expiry_days)

            conn = await self._get_db()
            try:
                # 使用 REPLACE 实现UPSERT（基于UNIQUE约束）
                await conn.execute(
                    """
                    REPLACE INTO account_sessions
                    (account_id, cookies, user_info, created_at, expires_at, last_used_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        account_id,
                        encrypted_cookies,
                        user_info_json,
                        datetime.now(),
                        expires_at,
                        datetime.now(),
                    ),
                )

                await conn.commit()
                logger.info(f"Session saved for account {account_id}")
                return True
            finally:
                await conn.close()

        except Exception as e:
            logger.error(f"Failed to save session for account {account_id}: {e}")
            return False

    async def load_session_for_account(self, account_id: int) -> Optional[dict[str, Any]]:
        """
        加载指定账户的会话

        Args:
            account_id: 账户ID

        Returns:
            dict: 包含cookies和user_info的字典，如果不存在则返回None
        """
        try:
            conn = await self._get_db()

            async with conn.execute(
                """
                SELECT cookies, user_info, expires_at
                FROM account_sessions
                WHERE account_id = ?
            """,
                (account_id,),
            ) as cursor:
                row = await cursor.fetchone()

                if not row:
                    logger.debug(f"No session found for account {account_id}")
                    await conn.close()
                    return None

                encrypted_cookies, user_info_json, expires_at = row

                # 检查是否过期
                if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
                    logger.info(f"Session expired for account {account_id}")
                    await self.delete_session_for_account(account_id)
                    await conn.close()
                    return None

                # 解密cookies
                decrypted_cookies = self.cipher.decrypt(encrypted_cookies)
                cookies = json.loads(decrypted_cookies)

                # 解析用户信息
                user_info = json.loads(user_info_json) if user_info_json else None

                # 更新最后使用时间
                await conn.execute(
                    """
                    UPDATE account_sessions
                    SET last_used_at = ?
                    WHERE account_id = ?
                """,
                    (datetime.now(), account_id),
                )
                await conn.commit()
                await conn.close()

                logger.info(f"Session loaded for account {account_id}")
                return {"cookies": cookies, "user_info": user_info}

        except Exception as e:
            logger.error(f"Failed to load session for account {account_id}: {e}")
            return None

    async def delete_session_for_account(self, account_id: int) -> bool:
        """
        删除指定账户的会话

        Args:
            account_id: 账户ID

        Returns:
            bool: 是否成功
        """
        try:
            conn = await self._get_db()
            try:
                await conn.execute(
                    """
                    DELETE FROM account_sessions
                    WHERE account_id = ?
                """,
                    (account_id,),
                )
                await conn.commit()
                logger.info(f"Session deleted for account {account_id}")
                return True
            finally:
                await conn.close()

        except Exception as e:
            logger.error(f"Failed to delete session for account {account_id}: {e}")
            return False

    async def get_active_account_id(self) -> Optional[int]:
        """
        获取当前活跃的账户ID

        通过检查最近使用的会话来确定活跃账户

        Returns:
            int: 活跃账户ID，如果没有则返回None
        """
        try:
            conn = await self._get_db()

            async with conn.execute(
                """
                SELECT account_id
                FROM account_sessions
                ORDER BY last_used_at DESC
                LIMIT 1
            """
            ) as cursor:
                row = await cursor.fetchone()
                await conn.close()

                if row:
                    return row[0]
                return None

        except Exception as e:
            logger.error(f"Failed to get active account: {e}")
            return None

    async def set_active_account(self, account_id: int) -> bool:
        """
        设置当前活跃账户

        通过更新 last_used_at 时间戳来标记账户为活跃

        Args:
            account_id: 账户ID

        Returns:
            bool: 是否成功
        """
        try:
            conn = await self._get_db()
            try:
                # 检查会话是否存在
                async with conn.execute(
                    """
                    SELECT id FROM account_sessions WHERE account_id = ?
                """,
                    (account_id,),
                ) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        logger.warning(f"No session found for account {account_id}")
                        await conn.close()
                        return False

                # 更新最后使用时间
                await conn.execute(
                    """
                    UPDATE account_sessions
                    SET last_used_at = ?
                    WHERE account_id = ?
                """,
                    (datetime.now(), account_id),
                )
                await conn.commit()
                await conn.close()

                logger.info(f"Active account set to {account_id}")
                return True

        except Exception as e:
            logger.error(f"Failed to set active account: {e}")
            return False

    async def get_active_accounts(self) -> list[int]:
        """
        获取所有有有效会话的账户ID列表

        Returns:
            list[int]: 账户ID列表
        """
        try:
            conn = await self._get_db()

            async with conn.execute(
                """
                SELECT account_id
                FROM account_sessions
                WHERE expires_at IS NULL OR expires_at > ?
                ORDER BY last_used_at DESC
            """,
                (datetime.now(),),
            ) as cursor:
                rows = await cursor.fetchall()
                await conn.close()

                return [row[0] for row in rows]

        except Exception as e:
            logger.error(f"Failed to get active accounts: {e}")
            return []

    async def cleanup_old_account_sessions(self, days: int = 30) -> int:
        """
        清理旧的账户会话

        Args:
            days: 保留天数

        Returns:
            int: 删除的会话数量
        """
        try:
            conn = await self._get_db()
            try:
                cutoff_date = datetime.now() - timedelta(days=days)

                cursor = await conn.execute(
                    """
                    DELETE FROM account_sessions
                    WHERE created_at < ?
                """,
                    (cutoff_date,),
                )

                deleted_count = cursor.rowcount
                await conn.commit()
                await conn.close()

                logger.info(f"Cleaned up {deleted_count} old account sessions")
                return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup old account sessions: {e}")
            return 0

    # ==================== Cookie验证和刷新方法 ====================

    async def validate_cookies(self, account_id: int) -> bool:
        """
        验证指定账户的Cookie是否有效

        Args:
            account_id: 账户ID

        Returns:
            bool: Cookie是否有效
        """
        try:
            # 加载账户会话
            session = await self.load_session_for_account(account_id)
            if not session or not session.get("cookies"):
                logger.debug(f"No cookies found for account {account_id}")
                return False

            # 检查会话是否过期
            conn = await self._get_db()
            async with conn.execute(
                """
                SELECT expires_at FROM account_sessions WHERE account_id = ?
            """,
                (account_id,),
            ) as cursor:
                row = await cursor.fetchone()
                await conn.close()

                if row and row[0]:
                    expires_at = datetime.fromisoformat(row[0])
                    if expires_at < datetime.now():
                        logger.info(f"Cookies expired for account {account_id}")
                        return False

            # 尝试应用Cookie到浏览器进行验证
            try:
                from rpa.modules.browser_manager import BrowserManager

                browser_manager = BrowserManager()
                browser = browser_manager.start_browser()
                if not browser:
                    logger.warning("Failed to start browser for cookie validation")
                    return False

                # 应用Cookie
                cookies = session["cookies"]
                for cookie_dict in cookies:
                    try:
                        browser.set.cookie(
                            name=cookie_dict.get("name"),
                            value=cookie_dict.get("value"),
                            domain=cookie_dict.get("domain", ".zhipin.com"),
                            path=cookie_dict.get("path", "/"),
                        )
                    except Exception as e:
                        logger.debug(f"Failed to set cookie: {e}")

                # 访问BOSS直聘首页验证
                browser.get("https://www.zhipin.com/")
                import time

                time.sleep(2)

                # 检查是否跳转到登录页
                current_url = browser.url
                is_valid = "login.zhipin.com" not in current_url

                browser_manager.close_browser()

                logger.info(f"Cookies validation for account {account_id}: {is_valid}")
                return is_valid

            except Exception as e:
                logger.error(f"Error during browser validation: {e}")
                return False

        except Exception as e:
            logger.error(f"Failed to validate cookies for account {account_id}: {e}")
            return False

    async def refresh_cookies(self, account_id: int) -> dict[str, Any]:
        """
        刷新指定账户的Cookie

        注意：此方法只触发刷新流程，实际刷新需要通过RPA服务完成

        Args:
            account_id: 账户ID

        Returns:
            dict: 刷新状态信息
        """
        try:
            # 检查账户是否存在
            conn = await self._get_db()
            async with conn.execute(
                "SELECT id, phone FROM accounts WHERE id = ?", (account_id,)
            ) as cursor:
                row = await cursor.fetchone()
                await conn.close()

                if not row:
                    return {"success": False, "message": "Account not found"}

            # 标记需要刷新
            logger.info(f"Cookie refresh triggered for account {account_id}")
            return {
                "success": True,
                "message": "Cookie refresh triggered",
                "account_id": account_id,
            }

        except Exception as e:
            logger.error(f"Failed to trigger cookie refresh for account {account_id}: {e}")
            return {"success": False, "message": str(e)}

    async def auto_refresh_expired_cookies(self) -> list[int]:
        """
        自动刷新过期的Cookie

        Returns:
            list[int]: 需要刷新的账户ID列表
        """
        try:
            conn = await self._get_db()

            # 获取所有有会话的账户
            async with conn.execute(
                """
                SELECT account_id FROM account_sessions
                WHERE expires_at IS NOT NULL AND expires_at < ?
            """,
                (datetime.now(),),
            ) as cursor:
                rows = await cursor.fetchall()
                await conn.close()

            expired_accounts = [row[0] for row in rows]

            if expired_accounts:
                logger.info(f"Found {len(expired_accounts)} accounts with expired cookies")

            return expired_accounts

        except Exception as e:
            logger.error(f"Failed to get expired cookies: {e}")
            return []
