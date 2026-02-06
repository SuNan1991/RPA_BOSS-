"""
账户服务
"""

from datetime import datetime
from typing import Optional

import aiosqlite

from ..core.logging import get_logger
from ..schemas.account import AccountCreate, AccountResponse, AccountUpdate

logger = get_logger("account_service")


class AccountService:
    """账户服务类"""

    def __init__(self, conn: aiosqlite.Connection):
        self.conn = conn

    async def create(self, account: AccountCreate) -> AccountResponse:
        """创建账户"""
        account_dict = {
            "phone": account.phone,
            "username": account.username,
            "is_active": account.is_active,
            "cookie_status": "none",
            "last_login": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        cursor = await self.conn.execute(
            """
            INSERT INTO accounts (
                phone, username, is_active, cookie_status,
                last_login, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                account_dict["phone"],
                account_dict["username"],
                account_dict["is_active"],
                account_dict["cookie_status"],
                account_dict["last_login"],
                account_dict["created_at"],
                account_dict["updated_at"],
            ),
        )

        account_id = cursor.lastrowid
        await self.conn.commit()
        account_dict["id"] = account_id

        logger.info(f"Created account: {account_id}")
        return AccountResponse(**account_dict)

    async def get_by_id(self, account_id: int) -> Optional[AccountResponse]:
        """根据ID获取账户"""
        try:
            cursor = await self.conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = await cursor.fetchone()
            if row:
                return self._row_to_account_response(row)
        except Exception as e:
            logger.error(f"Error getting account: {e}")
        return None

    async def get_by_phone(self, phone: str) -> Optional[AccountResponse]:
        """根据手机号获取账户"""
        try:
            cursor = await self.conn.execute("SELECT * FROM accounts WHERE phone = ?", (phone,))
            row = await cursor.fetchone()
            if row:
                return self._row_to_account_response(row)
        except Exception as e:
            logger.error(f"Error getting account by phone: {e}")
        return None

    async def get_list(
        self, skip: int = 0, limit: int = 10, is_active: Optional[bool] = None
    ) -> tuple[list[AccountResponse], int]:
        """获取账户列表"""
        query = "SELECT * FROM accounts"
        params = []

        if is_active is not None:
            query += " WHERE is_active = ?"
            params.append(is_active)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        try:
            cursor = await self.conn.execute(query, params)
            rows = await cursor.fetchall()

            # 获取总数
            count_query = "SELECT COUNT(*) FROM accounts"
            count_params = []
            if is_active is not None:
                count_query += " WHERE is_active = ?"
                count_params.append(is_active)

            count_cursor = await self.conn.execute(count_query, count_params)
            total_row = await count_cursor.fetchone()
            total = total_row[0] if total_row else 0

            result = [self._row_to_account_response(row) for row in rows]
            return result, total
        except Exception as e:
            logger.error(f"Error getting account list: {e}")
            return [], 0

    async def update(self, account_id: int, account: AccountUpdate) -> Optional[AccountResponse]:
        """更新账户"""
        try:
            update_fields = []
            params = []

            if account.username is not None:
                update_fields.append("username = ?")
                params.append(account.username)

            if account.is_active is not None:
                update_fields.append("is_active = ?")
                params.append(account.is_active)

            if account.cookie_status is not None:
                update_fields.append("cookie_status = ?")
                params.append(account.cookie_status)

            if not update_fields:
                return await self.get_by_id(account_id)

            update_fields.append("updated_at = ?")
            params.extend([datetime.now().isoformat(), account_id])

            query = f"UPDATE accounts SET {', '.join(update_fields)} WHERE id = ?"
            await self.conn.execute(query, params)
            await self.conn.commit()

            return await self.get_by_id(account_id)
        except Exception as e:
            logger.error(f"Error updating account: {e}")
            return None

    async def update_cookie_status(
        self, account_id: int, cookie_status: str
    ) -> Optional[AccountResponse]:
        """更新Cookie状态"""
        try:
            if cookie_status == "valid":
                await self.conn.execute(
                    """
                    UPDATE accounts
                    SET cookie_status = ?, last_login = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        cookie_status,
                        datetime.now().isoformat(),
                        datetime.now().isoformat(),
                        account_id,
                    ),
                )
            else:
                await self.conn.execute(
                    """
                    UPDATE accounts
                    SET cookie_status = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (cookie_status, datetime.now().isoformat(), account_id),
                )

            await self.conn.commit()
            logger.info(f"Updated cookie status: {account_id} -> {cookie_status}")
            return await self.get_by_id(account_id)
        except Exception as e:
            logger.error(f"Error updating cookie status: {e}")
            return None

    async def delete(self, account_id: int) -> bool:
        """删除账户"""
        try:
            cursor = await self.conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
            await self.conn.commit()
            deleted_count = cursor.rowcount
            logger.info(f"Deleted account: {account_id}, deleted_count: {deleted_count}")
            return deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting account: {e}")
            return False

    def _row_to_account_response(self, row) -> AccountResponse:
        """将数据库行转换为AccountResponse对象"""
        # row结构:
        # (id, phone, username, is_active, cookie_status, last_login, created_at, updated_at)
        return AccountResponse(
            id=row[0],
            phone=row[1],
            username=row[2],
            is_active=bool(row[3]),
            cookie_status=row[4],
            last_login=datetime.fromisoformat(row[5]) if row[5] else None,
            created_at=datetime.fromisoformat(row[6]),
            updated_at=datetime.fromisoformat(row[7]),
        )
