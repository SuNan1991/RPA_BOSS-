"""
账户服务
"""

import json
import time
from datetime import datetime, timedelta
from typing import Optional, List

import aiosqlite

from ..core.logging import get_logger
from ..schemas.account import (
    AccountCreate,
    AccountResponse,
    AccountUpdate,
    AccountStatistics,
    BatchOperationRequest,
    BatchOperationResult,
    OperationLogResponse,
)

logger = get_logger("account_service")


class AccountService:
    """账户服务类"""

    def __init__(self, conn: aiosqlite.Connection):
        self.conn = conn

    async def create(self, account: AccountCreate) -> AccountResponse:
        """创建账户"""
        now = datetime.now().isoformat()
        # Debug: 打印 account 对象的所有属性
        logger.info(f"Creating account with data: {account.model_dump()}")
        logger.info(f"Account type from request: {account.account_type}")

        account_dict = {
            "phone": account.phone,
            "username": account.username,
            "is_active": account.is_active,
            "cookie_status": "none",
            "account_type": account.account_type,  # 直接使用 account.account_type
            "group_id": account.group_id,
            "tags": json.dumps(account.tags) if account.tags else None,
            "notes": account.notes,
            "login_count": 0,
            "last_login": None,
            "last_operation_at": None,
            "quota_limit": account.quota_limit,
            "quota_used": 0,
            "created_at": now,
            "updated_at": now,
        }

        cursor = await self.conn.execute(
            """
            INSERT INTO accounts (
                phone, username, is_active, cookie_status, account_type, group_id, tags, notes,
                login_count, last_login, last_operation_at, quota_limit, quota_used,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                account_dict["created_at"],
                account_dict["updated_at"],
            ),
        )

        account_id = cursor.lastrowid
        await self.conn.commit()
        account_dict["id"] = account_id

        # Parse tags back to list for response
        if account_dict["tags"]:
            account_dict["tags"] = json.loads(account_dict["tags"])

        logger.info(f"Created account: {account_id}")
        return self._dict_to_account_response(account_dict)

    async def get_by_id(self, account_id: int) -> Optional[AccountResponse]:
        """根据ID获取账户"""
        try:
            cursor = await self.conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = await cursor.fetchone()
            if row:
                return await self._row_to_account_response(row)
        except Exception as e:
            logger.error(f"Error getting account: {e}")
        return None

    async def get_by_phone(self, phone: str) -> Optional[AccountResponse]:
        """根据手机号获取账户"""
        try:
            cursor = await self.conn.execute("SELECT * FROM accounts WHERE phone = ?", (phone,))
            row = await cursor.fetchone()
            if row:
                return await self._row_to_account_response(row)
        except Exception as e:
            logger.error(f"Error getting account by phone: {e}")
        return None

    async def get_list(
        self, skip: int = 0, limit: int = 10, is_active: Optional[bool] = None, account_type: Optional[str] = None
    ) -> tuple[list[AccountResponse], int]:
        """获取账户列表"""
        # 重置过期配额（超过24小时未操作）
        await self._reset_expired_quotas()
        
        query = "SELECT * FROM accounts WHERE 1=1"
        params = []

        if is_active is not None:
            query += " AND is_active = ?"
            params.append(is_active)

        if account_type is not None:
            query += " AND account_type = ?"
            params.append(account_type)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        try:
            cursor = await self.conn.execute(query, params)
            rows = await cursor.fetchall()

            # 获取总数
            count_query = "SELECT COUNT(*) FROM accounts WHERE 1=1"
            count_params = []
            if is_active is not None:
                count_query += " AND is_active = ?"
                count_params.append(is_active)

            if account_type is not None:
                count_query += " AND account_type = ?"
                count_params.append(account_type)

            count_cursor = await self.conn.execute(count_query, count_params)
            total_row = await count_cursor.fetchone()
            total = total_row[0] if total_row else 0

            result = [await self._row_to_account_response(row) for row in rows]
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

            if account.group_id is not None:
                update_fields.append("group_id = ?")
                params.append(account.group_id)

            if account.tags is not None:
                update_fields.append("tags = ?")
                params.append(json.dumps(account.tags))

            if account.notes is not None:
                update_fields.append("notes = ?")
                params.append(account.notes)

            if account.quota_limit is not None:
                update_fields.append("quota_limit = ?")
                params.append(account.quota_limit)

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

    async def _row_to_account_response(self, row) -> AccountResponse:
        """将数据库行转换为AccountResponse对象（使用列名映射，避免索引错误）"""
        # 使用 PRAGMA table_info 获取列名
        cursor = await self.conn.execute("PRAGMA table_info(accounts)")
        columns_info = await cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        row_dict = dict(zip(column_names, row))

        # 解析 tags
        tags = None
        if row_dict.get("tags"):
            try:
                tags = json.loads(row_dict["tags"])
            except (json.JSONDecodeError, TypeError):
                tags = None

        return AccountResponse(
            id=row_dict["id"],
            phone=row_dict["phone"],
            username=row_dict.get("username"),
            is_active=bool(row_dict.get("is_active", True)),
            cookie_status=row_dict.get("cookie_status", "none"),
            account_type=row_dict.get("account_type", "hr"),
            group_id=row_dict.get("group_id"),
            tags=tags,
            notes=row_dict.get("notes"),
            login_count=row_dict.get("login_count", 0),
            last_login=self._parse_datetime(row_dict.get("last_login")),
            last_operation_at=self._parse_datetime(row_dict.get("last_operation_at")),
            quota_limit=row_dict.get("quota_limit", 100),
            quota_used=row_dict.get("quota_used", 0),
            created_at=self._parse_datetime(row_dict.get("created_at")) or datetime.now(),
            updated_at=self._parse_datetime(row_dict.get("updated_at")) or datetime.now(),
        )

    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        """解析日期时间字符串"""
        if value:
            try:
                return datetime.fromisoformat(value)
            except (ValueError, TypeError):
                pass
        return None

    async def _reset_expired_quotas(self):
        """重置过期配额（超过24小时未操作的账号）"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            await self.conn.execute(
                "UPDATE accounts SET quota_used = 0, updated_at = ? WHERE quota_used > 0 AND last_operation_at < ? AND last_operation_at IS NOT NULL",
                (datetime.now().isoformat(), cutoff_time.isoformat())
            )
            await self.conn.commit()
        except Exception as e:
            logger.error(f"Error resetting expired quotas: {e}")

    def _dict_to_account_response(self, data: dict) -> AccountResponse:
        """将字典转换为AccountResponse对象"""
        return AccountResponse(
            id=data["id"],
            phone=data["phone"],
            username=data.get("username"),
            is_active=data.get("is_active", True),
            cookie_status=data.get("cookie_status", "none"),
            account_type=data.get("account_type", "hr"),
            group_id=data.get("group_id"),
            tags=data.get("tags"),
            notes=data.get("notes"),
            login_count=data.get("login_count", 0),
            last_login=self._parse_datetime(data.get("last_login")),
            last_operation_at=self._parse_datetime(data.get("last_operation_at")),
            quota_limit=data.get("quota_limit", 100),
            quota_used=data.get("quota_used", 0),
            created_at=self._parse_datetime(data.get("created_at")) or datetime.now(),
            updated_at=self._parse_datetime(data.get("updated_at")) or datetime.now(),
        )

    # ========================================================================
    # Statistics Methods
    # ========================================================================

    async def get_statistics(self) -> AccountStatistics:
        """获取账号统计概览"""
        try:
            # Total accounts
            cursor = await self.conn.execute("SELECT COUNT(*) FROM accounts")
            total_row = await cursor.fetchone()
            total_accounts = total_row[0] if total_row else 0

            # Active accounts
            cursor = await self.conn.execute("SELECT COUNT(*) FROM accounts WHERE is_active = 1")
            active_row = await cursor.fetchone()
            active_accounts = active_row[0] if active_row else 0

            # Valid cookies
            cursor = await self.conn.execute("SELECT COUNT(*) FROM accounts WHERE cookie_status = 'valid'")
            valid_row = await cursor.fetchone()
            valid_cookies = valid_row[0] if valid_row else 0

            # Invalid cookies
            cursor = await self.conn.execute("SELECT COUNT(*) FROM accounts WHERE cookie_status = 'invalid'")
            invalid_row = await cursor.fetchone()
            invalid_cookies = invalid_row[0] if invalid_row else 0

            # None cookies
            cursor = await self.conn.execute("SELECT COUNT(*) FROM accounts WHERE cookie_status = 'none'")
            none_row = await cursor.fetchone()
            none_cookies = none_row[0] if none_row else 0

            return AccountStatistics(
                total_accounts=total_accounts,
                active_accounts=active_accounts,
                valid_cookies=valid_cookies,
                invalid_cookies=invalid_cookies,
                none_cookies=none_cookies,
            )
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return AccountStatistics(
                total_accounts=0,
                active_accounts=0,
                valid_cookies=0,
                invalid_cookies=0,
                none_cookies=0,
            )

    # ========================================================================
    # Batch Operations
    # ========================================================================

    async def batch_operation(self, request: BatchOperationRequest) -> BatchOperationResult:
        """批量操作（带事务保护）"""
        success_count = 0
        failed_count = 0
        details = []

        # 开始事务
        await self.conn.execute("BEGIN IMMEDIATE TRANSACTION")

        try:
            for account_id in request.account_ids:
                try:
                    if request.action == "activate":
                        await self.conn.execute(
                            "UPDATE accounts SET is_active = 1, updated_at = ? WHERE id = ?",
                            (datetime.now().isoformat(), account_id)
                        )
                        success_count += 1
                        details.append({"account_id": account_id, "status": "success", "message": "Activated"})

                    elif request.action == "deactivate":
                        await self.conn.execute(
                            "UPDATE accounts SET is_active = 0, updated_at = ? WHERE id = ?",
                            (datetime.now().isoformat(), account_id)
                        )
                        success_count += 1
                        details.append({"account_id": account_id, "status": "success", "message": "Deactivated"})

                    elif request.action == "delete":
                        # 直接执行删除，不调用 self.delete() 避免其内部 commit
                        cursor = await self.conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
                        if cursor.rowcount > 0:
                            success_count += 1
                            details.append({"account_id": account_id, "status": "success", "message": "Deleted"})
                        else:
                            failed_count += 1
                            details.append({"account_id": account_id, "status": "failed", "message": "Account not found"})

                    elif request.action == "refresh_cookies":
                        await self.conn.execute(
                            "UPDATE accounts SET cookie_status = 'none', updated_at = ? WHERE id = ?",
                            (datetime.now().isoformat(), account_id)
                        )
                        success_count += 1
                        details.append({"account_id": account_id, "status": "success", "message": "Cookie status reset"})

                    else:
                        failed_count += 1
                        details.append({"account_id": account_id, "status": "failed", "message": f"Unknown action: {request.action}"})

                except Exception as e:
                    failed_count += 1
                    details.append({"account_id": account_id, "status": "failed", "message": str(e)})
                    logger.error(f"Batch operation failed for account {account_id}: {e}")

            # 所有操作完成，提交事务
            await self.conn.commit()
            logger.info(f"Batch operation '{request.action}': success={success_count}, failed={failed_count}")

        except Exception as e:
            # 发生严重错误，回滚事务
            await self.conn.execute("ROLLBACK")
            logger.error(f"Batch operation rolled back due to error: {e}")
            raise

        return BatchOperationResult(
            success_count=success_count,
            failed_count=failed_count,
            details=details,
        )

    # ========================================================================
    # Operation Logs
    # ========================================================================

    async def record_operation(
        self,
        account_id: int,
        operation_type: str,
        operation_detail: Optional[dict] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
    ) -> bool:
        """记录操作日志"""
        try:
            await self.conn.execute(
                """
                INSERT INTO account_operation_logs (
                    account_id, operation_type, operation_detail, success,
                    error_message, duration_ms, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    account_id,
                    operation_type,
                    json.dumps(operation_detail) if operation_detail else None,
                    success,
                    error_message,
                    duration_ms,
                    datetime.now().isoformat(),
                ),
            )

            # Update last_operation_at
            await self.conn.execute(
                "UPDATE accounts SET last_operation_at = ? WHERE id = ?",
                (datetime.now().isoformat(), account_id),
            )

            await self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error recording operation: {e}")
            return False

    async def get_operation_logs(
        self,
        account_id: Optional[int] = None,
        operation_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[OperationLogResponse], int]:
        """获取操作日志"""
        query = "SELECT * FROM account_operation_logs WHERE 1=1"
        params = []

        if account_id is not None:
            query += " AND account_id = ?"
            params.append(account_id)

        if operation_type:
            query += " AND operation_type = ?"
            params.append(operation_type)

        if start_date:
            query += " AND created_at >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND created_at <= ?"
            params.append(end_date.isoformat())

        # Get total count
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        count_cursor = await self.conn.execute(count_query, params)
        total_row = await count_cursor.fetchone()
        total = total_row[0] if total_row else 0

        # Add pagination
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([page_size, (page - 1) * page_size])

        try:
            cursor = await self.conn.execute(query, params)
            rows = await cursor.fetchall()

            logs = []
            for row in rows:
                logs.append(OperationLogResponse(
                    id=row[0],
                    account_id=row[1],
                    operation_type=row[2],
                    operation_detail=row[3],
                    success=bool(row[4]),
                    error_message=row[5],
                    duration_ms=row[6],
                    created_at=datetime.fromisoformat(row[7]) if row[7] else datetime.now(),
                ))

            return logs, total
        except Exception as e:
            logger.error(f"Error getting operation logs: {e}")
            return [], 0

    # ========================================================================
    # Account Login Tracking
    # ========================================================================

    async def increment_login_count(self, account_id: int) -> bool:
        """增加登录次数"""
        try:
            await self.conn.execute(
                """
                UPDATE accounts
                SET login_count = login_count + 1,
                    last_login = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (datetime.now().isoformat(), datetime.now().isoformat(), account_id),
            )
            await self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error incrementing login count: {e}")
            return False

    async def update_last_operation(self, account_id: int) -> bool:
        """更新最后操作时间"""
        try:
            await self.conn.execute(
                "UPDATE accounts SET last_operation_at = ?, updated_at = ? WHERE id = ?",
                (datetime.now().isoformat(), datetime.now().isoformat(), account_id),
            )
            await self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating last operation: {e}")
            return False
