"""
账户分组服务
"""

import json
from datetime import datetime
from typing import Optional, List

import aiosqlite

from ..core.logging import get_logger
from ..schemas.account import (
    AccountGroupCreate,
    AccountGroupResponse,
    AccountGroupUpdate,
    AccountResponse,
)

logger = get_logger("account_group_service")


class AccountGroupService:
    """账户分组服务类"""

    def __init__(self, conn: aiosqlite.Connection):
        self.conn = conn

    async def create(self, group: AccountGroupCreate) -> AccountGroupResponse:
        """创建分组"""
        now = datetime.now().isoformat()

        cursor = await self.conn.execute(
            """
            INSERT INTO account_groups (name, description, parent_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (group.name, group.description, group.parent_id, now, now),
        )

        group_id = cursor.lastrowid
        await self.conn.commit()

        logger.info(f"Created account group: {group_id}")
        return await self.get_by_id(group_id)

    async def get_by_id(self, group_id: int) -> Optional[AccountGroupResponse]:
        """根据ID获取分组"""
        try:
            cursor = await self.conn.execute(
                "SELECT * FROM account_groups WHERE id = ?",
                (group_id,),
            )
            row = await cursor.fetchone()
            if row:
                return self._row_to_group_response(row)
        except Exception as e:
            logger.error(f"Error getting group: {e}")
        return None

    async def get_list(self) -> List[AccountGroupResponse]:
        """获取所有分组列表"""
        try:
            cursor = await self.conn.execute(
                "SELECT * FROM account_groups ORDER BY created_at ASC"
            )
            rows = await cursor.fetchall()
            return [self._row_to_group_response(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting group list: {e}")
            return []

    async def get_tree(self) -> List[dict]:
        """获取分组树结构"""
        groups = await self.get_list()

        # Build tree structure
        group_map = {g.id: {"id": g.id, "name": g.name, "description": g.description, "parent_id": g.parent_id, "children": []} for g in groups}

        tree = []
        for group in group_map.values():
            parent_id = group["parent_id"]
            if parent_id and parent_id in group_map:
                group_map[parent_id]["children"].append(group)
            else:
                tree.append(group)

        return tree

    async def update(self, group_id: int, group: AccountGroupUpdate) -> Optional[AccountGroupResponse]:
        """更新分组"""
        try:
            update_fields = []
            params = []

            if group.name is not None:
                update_fields.append("name = ?")
                params.append(group.name)

            if group.description is not None:
                update_fields.append("description = ?")
                params.append(group.description)

            if group.parent_id is not None:
                # Prevent circular reference
                if group.parent_id == group_id:
                    logger.error("Cannot set parent_id to self")
                    return None
                update_fields.append("parent_id = ?")
                params.append(group.parent_id)

            if not update_fields:
                return await self.get_by_id(group_id)

            update_fields.append("updated_at = ?")
            params.extend([datetime.now().isoformat(), group_id])

            query = f"UPDATE account_groups SET {', '.join(update_fields)} WHERE id = ?"
            await self.conn.execute(query, params)
            await self.conn.commit()

            return await self.get_by_id(group_id)
        except Exception as e:
            logger.error(f"Error updating group: {e}")
            return None

    async def delete(self, group_id: int) -> bool:
        """删除分组"""
        try:
            # Set accounts in this group to have no group
            await self.conn.execute(
                "UPDATE accounts SET group_id = NULL WHERE group_id = ?",
                (group_id,),
            )

            # Set children's parent_id to NULL
            await self.conn.execute(
                "UPDATE account_groups SET parent_id = NULL WHERE parent_id = ?",
                (group_id,),
            )

            # Delete the group
            cursor = await self.conn.execute(
                "DELETE FROM account_groups WHERE id = ?",
                (group_id,),
            )
            await self.conn.commit()

            deleted_count = cursor.rowcount
            logger.info(f"Deleted account group: {group_id}, deleted_count: {deleted_count}")
            return deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting group: {e}")
            return False

    async def get_accounts_by_group(self, group_id: int) -> List[AccountResponse]:
        """获取分组下的账号"""
        try:
            cursor = await self.conn.execute(
                "SELECT * FROM accounts WHERE group_id = ? ORDER BY created_at DESC",
                (group_id,),
            )
            rows = await cursor.fetchall()

            # Import here to avoid circular dependency
            from .account_service import AccountService
            account_service = AccountService(self.conn)
            return [account_service._row_to_account_response(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting accounts by group: {e}")
            return []

    async def get_account_count_by_group(self, group_id: int) -> int:
        """获取分组下的账号数量"""
        try:
            cursor = await self.conn.execute(
                "SELECT COUNT(*) FROM accounts WHERE group_id = ?",
                (group_id,),
            )
            row = await cursor.fetchone()
            return row[0] if row else 0
        except Exception as e:
            logger.error(f"Error getting account count: {e}")
            return 0

    def _row_to_group_response(self, row) -> AccountGroupResponse:
        """将数据库行转换为AccountGroupResponse对象"""
        # row结构:
        # (id, name, description, parent_id, created_at, updated_at)
        return AccountGroupResponse(
            id=row[0],
            name=row[1],
            description=row[2],
            parent_id=row[3],
            created_at=datetime.fromisoformat(row[4]) if row[4] else datetime.now(),
            updated_at=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
        )
