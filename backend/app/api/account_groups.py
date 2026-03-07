"""
账户分组API
"""

import aiosqlite
from fastapi import APIRouter, Depends

from ..core.database import get_database
from ..core.responses import error_response, success_response
from ..schemas.account import AccountGroupCreate, AccountGroupUpdate
from ..services.account_group_service import AccountGroupService

router = APIRouter(prefix="/api/account-groups", tags=["account-groups"])


@router.post("/", response_model=dict)
async def create_group(
    group: AccountGroupCreate,
    db: aiosqlite.Connection = Depends(get_database),
):
    """创建分组"""
    service = AccountGroupService(db)

    # 如果指定了父分组，检查父分组是否存在
    if group.parent_id:
        parent = await service.get_by_id(group.parent_id)
        if not parent:
            return error_response(message="父分组不存在", code=400)

    result = await service.create(group)
    return success_response(data=result.model_dump(), message="分组创建成功")


@router.get("/", response_model=dict)
async def get_groups(db: aiosqlite.Connection = Depends(get_database)):
    """获取所有分组列表"""
    service = AccountGroupService(db)
    groups = await service.get_list()

    # 添加每个分组的账号数量
    groups_with_count = []
    for group in groups:
        count = await service.get_account_count_by_group(group.id)
        group_dict = group.model_dump()
        group_dict["account_count"] = count
        groups_with_count.append(group_dict)

    return success_response(data=groups_with_count)


@router.get("/tree", response_model=dict)
async def get_group_tree(db: aiosqlite.Connection = Depends(get_database)):
    """获取分组树结构"""
    service = AccountGroupService(db)
    tree = await service.get_tree()
    return success_response(data=tree)


@router.get("/{group_id}", response_model=dict)
async def get_group(
    group_id: int,
    db: aiosqlite.Connection = Depends(get_database),
):
    """获取分组详情"""
    service = AccountGroupService(db)
    group = await service.get_by_id(group_id)
    if not group:
        return error_response(message="分组不存在", code=404)

    # 添加账号数量
    count = await service.get_account_count_by_group(group_id)
    group_dict = group.model_dump()
    group_dict["account_count"] = count

    return success_response(data=group_dict)


@router.put("/{group_id}", response_model=dict)
async def update_group(
    group_id: int,
    group: AccountGroupUpdate,
    db: aiosqlite.Connection = Depends(get_database),
):
    """更新分组"""
    service = AccountGroupService(db)

    # 检查分组是否存在
    existing = await service.get_by_id(group_id)
    if not existing:
        return error_response(message="分组不存在", code=404)

    # 如果要更新父分组，检查父分组是否存在
    if group.parent_id is not None and group.parent_id != 0:
        if group.parent_id == group_id:
            return error_response(message="不能将自己设为父分组", code=400)
        parent = await service.get_by_id(group.parent_id)
        if not parent:
            return error_response(message="父分组不存在", code=400)

    result = await service.update(group_id, group)
    if result:
        return success_response(data=result.model_dump(), message="分组更新成功")
    return error_response(message="更新失败", code=500)


@router.delete("/{group_id}", response_model=dict)
async def delete_group(
    group_id: int,
    db: aiosqlite.Connection = Depends(get_database),
):
    """删除分组"""
    service = AccountGroupService(db)

    # 检查分组是否存在
    existing = await service.get_by_id(group_id)
    if not existing:
        return error_response(message="分组不存在", code=404)

    # 检查是否有子分组
    groups = await service.get_list()
    has_children = any(g.parent_id == group_id for g in groups)
    if has_children:
        return error_response(message="该分组下有子分组，无法删除", code=400)

    # 检查是否有账号
    count = await service.get_account_count_by_group(group_id)
    if count > 0:
        return error_response(message=f"该分组下有 {count} 个账号，无法删除", code=400)

    result = await service.delete(group_id)
    if result:
        return success_response(message="分组删除成功")
    return error_response(message="删除失败", code=500)


@router.get("/{group_id}/accounts", response_model=dict)
async def get_group_accounts(
    group_id: int,
    db: aiosqlite.Connection = Depends(get_database),
):
    """获取分组下的所有账号"""
    service = AccountGroupService(db)

    # 检查分组是否存在
    group = await service.get_by_id(group_id)
    if not group:
        return error_response(message="分组不存在", code=404)

    accounts = await service.get_accounts_by_group(group_id)
    return success_response(
        data=[account.model_dump() for account in accounts],
        meta={"group": group.model_dump(), "total": len(accounts)},
    )
