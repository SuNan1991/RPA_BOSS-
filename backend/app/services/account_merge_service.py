"""
账号合并服务
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime

import aiosqlite
from pydantic import BaseModel

from ..core.logging import get_logger
from .account_service import AccountService

logger = get_logger("account_merge_service")


class DuplicateGroup(BaseModel):
    """重复账号组"""
    type: str  # 'phone' or 'username'
    value: str  # 重复的值
    account_ids: List[int]
    count: int


class MergePreview(BaseModel):
    """合并预览"""
    source: Dict[str, Any]
    target: Dict[str, Any]
    sessions_to_migrate: int
    logs_to_migrate: int
    conflicts: List[str]


class MergeResult(BaseModel):
    """合并结果"""
    success: bool
    message: str
    target_id: int


class AccountMergeService:
    """账号合并服务 - 检测和合并重复账号"""

    def __init__(self, conn: aiosqlite.Connection):
        self.conn = conn
        self.account_service = AccountService(conn)

    async def detect_duplicates(self) -> List[DuplicateGroup]:
        """
        检测重复账号

        策略：
        1. 按手机号分组（完全匹配）
        2. 按用户名分组（完全匹配，排除默认值"BOSS用户"）
        3. 返回分组列表，每组包含重复的账号信息
        """
        duplicates = []

        # 1. 手机号重复
        cursor = await self.conn.execute("""
            SELECT phone, GROUP_CONCAT(id) as ids, COUNT(*) as count
            FROM accounts
            WHERE phone IS NOT NULL AND phone != '' AND phone NOT LIKE 'auto_%'
            GROUP BY phone
            HAVING count > 1
        """)

        rows = await cursor.fetchall()
        for row in rows:
            duplicates.append(DuplicateGroup(
                type="phone",
                value=row[0],
                account_ids=[int(id) for id in row[1].split(',')],
                count=row[2]
            ))

        # 2. 用户名重复（排除默认值）
        cursor = await self.conn.execute("""
            SELECT username, GROUP_CONCAT(id) as ids, COUNT(*) as count
            FROM accounts
            WHERE username IS NOT NULL
              AND username != ''
              AND username != 'BOSS用户'
            GROUP BY username
            HAVING count > 1
        """)

        rows = await cursor.fetchall()
        for row in rows:
            duplicates.append(DuplicateGroup(
                type="username",
                value=row[0],
                account_ids=[int(id) for id in row[1].split(',')],
                count=row[2]
            ))

        logger.info(f"Detected {len(duplicates)} duplicate groups")
        return duplicates

    async def preview_merge(self, source_id: int, target_id: int) -> MergePreview:
        """
        预览合并结果

        显示：
        - 两个账号的详细信息对比
        - 将要迁移的数据（sessions、logs）
        - 合并后的最终状态
        """
        source = await self.account_service.get_by_id(source_id)
        target = await self.account_service.get_by_id(target_id)

        if not source or not target:
            raise ValueError("Source or target account not found")

        # 统计将要迁移的数据
        sessions_count = await self._count_sessions(source_id)
        logs_count = await self._count_logs(source_id)

        # 检测冲突
        conflicts = self._detect_conflicts(source.dict(), target.dict())

        return MergePreview(
            source=source.dict(),
            target=target.dict(),
            sessions_to_migrate=sessions_count,
            logs_to_migrate=logs_count,
            conflicts=conflicts
        )

    async def merge_accounts(
        self,
        source_id: int,
        target_id: int,
        strategy: str = "keep_target"
    ) -> MergeResult:
        """
        执行账号合并

        策略：
        1. 使用事务保护
        2. 迁移所有关联数据（sessions、logs）
        3. 根据策略处理冲突字段
        4. 删除源账号

        Args:
            source_id: 源账号ID（将被删除）
            target_id: 目标账号ID（将被保留）
            strategy: 合并策略
                - keep_target: 保留目标账号的字段值（默认）
                - keep_source: 保留源账号的字段值
                - keep_newer: 保留更新的账号的字段值
        """
        if source_id == target_id:
            return MergeResult(
                success=False,
                message="不能合并同一个账号",
                target_id=target_id
            )

        # 开始事务
        await self.conn.execute("BEGIN IMMEDIATE TRANSACTION")

        try:
            # 1. 获取账号信息
            source = await self.account_service.get_by_id(source_id)
            target = await self.account_service.get_by_id(target_id)

            if not source or not target:
                raise ValueError("Source or target account not found")

            logger.info(f"Merging account {source_id} into {target_id} with strategy: {strategy}")

            # 2. 迁移sessions
            await self.conn.execute("""
                UPDATE account_sessions
                SET account_id = ?
                WHERE account_id = ?
            """, (target_id, source_id))

            # 3. 迁移操作日志
            await self.conn.execute("""
                UPDATE account_operation_logs
                SET account_id = ?
                WHERE account_id = ?
            """, (target_id, source_id))

            # 4. 根据策略更新目标账号字段
            if strategy == "keep_source":
                # 用source的非空字段更新target
                await self._update_target_from_source(source_id, target_id)
            elif strategy == "keep_newer":
                # 比较updated_at，保留更新的
                await self._update_target_keep_newer(source_id, target_id)
            # keep_target: 不需要更新，保持target原样

            # 5. 更新目标账号的统计信息
            await self._update_target_stats(target_id)

            # 6. 删除源账号（级联删除会自动清理关联数据）
            await self.conn.execute(
                "DELETE FROM accounts WHERE id = ?",
                (source_id,)
            )

            await self.conn.commit()

            logger.info(f"Merge completed: account {source_id} merged into {target_id}")

            return MergeResult(
                success=True,
                message=f"账号合并成功，已将 {source.username} 合并到 {target.username}",
                target_id=target_id
            )

        except Exception as e:
            await self.conn.execute("ROLLBACK")
            logger.error(f"Merge failed: {e}", exc_info=True)
            raise

    async def _count_sessions(self, account_id: int) -> int:
        """统计账号的session数量"""
        cursor = await self.conn.execute(
            "SELECT COUNT(*) FROM account_sessions WHERE account_id = ?",
            (account_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else 0

    async def _count_logs(self, account_id: int) -> int:
        """统计账号的操作日志数量"""
        cursor = await self.conn.execute(
            "SELECT COUNT(*) FROM account_operation_logs WHERE account_id = ?",
            (account_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else 0

    def _detect_conflicts(self, source: Dict, target: Dict) -> List[str]:
        """检测字段冲突"""
        conflicts = []

        # 检查关键字段是否不同
        if source.get("phone") != target.get("phone"):
            conflicts.append(f"手机号不同: {source.get('phone')} vs {target.get('phone')}")

        if source.get("username") != target.get("username"):
            conflicts.append(f"用户名不同: {source.get('username')} vs {target.get('username')}")

        if source.get("cookie_status") != target.get("cookie_status"):
            conflicts.append(f"Cookie状态不同: {source.get('cookie_status')} vs {target.get('cookie_status')}")

        return conflicts

    async def _update_target_from_source(self, source_id: int, target_id: int):
        """用源账号的字段更新目标账号"""
        source = await self.account_service.get_by_id(source_id)

        # 更新目标账号，使用源账号的非空字段
        await self.conn.execute("""
            UPDATE accounts
            SET username = COALESCE(?, username),
                phone = COALESCE(?, phone),
                notes = COALESCE(?, notes),
                updated_at = ?
            WHERE id = ?
        """, (
            source.username if source.username else None,
            source.phone if source.phone and not source.phone.startswith('auto_') else None,
            source.notes if source.notes else None,
            datetime.now().isoformat(),
            target_id
        ))

    async def _update_target_keep_newer(self, source_id: int, target_id: int):
        """保留更新的账号的字段"""
        cursor = await self.conn.execute("""
            SELECT id, username, phone, updated_at
            FROM accounts
            WHERE id IN (?, ?)
            ORDER BY updated_at DESC
            LIMIT 1
        """, (source_id, target_id))

        newer = await cursor.fetchone()
        if newer and newer[0] == source_id:
            # 源账号更新，用它更新目标
            await self._update_target_from_source(source_id, target_id)

    async def _update_target_stats(self, target_id: int):
        """更新目标账号的统计信息"""
        # 更新登录次数（合并）
        await self.conn.execute("""
            UPDATE accounts
            SET login_count = (
                SELECT SUM(login_count)
                FROM accounts
                WHERE id = ? OR id IN (
                    SELECT account_id FROM account_sessions WHERE account_id = ?
                )
            ),
            updated_at = ?
            WHERE id = ?
        """, (target_id, target_id, datetime.now().isoformat(), target_id))
