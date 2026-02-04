"""
账户相关API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.database import get_database
from ..core.responses import success_response, error_response
from ..schemas.account import AccountCreate, AccountUpdate, AccountResponse
from ..services import AccountService

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.post("/", response_model=dict)
async def create_account(
    account: AccountCreate, db: AsyncIOMotorDatabase = Depends(get_database)
):
    """创建账户"""
    service = AccountService(db)

    # 检查手机号是否已存在
    existing = await service.get_by_phone(account.phone)
    if existing:
        return error_response(message="该手机号已注册", code=400)

    result = await service.create(account)
    return success_response(data=result.model_dump(), message="账户创建成功")


@router.get("/{account_id}", response_model=dict)
async def get_account(
    account_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
):
    """获取账户详情"""
    service = AccountService(db)
    result = await service.get_by_id(account_id)
    if result:
        return success_response(data=result.model_dump())
    return error_response(message="账户不存在", code=404)


@router.get("/", response_model=dict)
async def get_accounts(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """获取账户列表"""
    skip = (page - 1) * page_size

    service = AccountService(db)
    accounts, total = await service.get_list(
        skip=skip, limit=page_size, is_active=is_active
    )

    return {
        "code": 200,
        "message": "success",
        "data": [account.model_dump() for account in accounts],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.put("/{account_id}", response_model=dict)
async def update_account(
    account_id: str,
    account: AccountUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """更新账户"""
    service = AccountService(db)
    result = await service.update(account_id, account)
    if result:
        return success_response(data=result.model_dump(), message="账户更新成功")
    return error_response(message="账户不存在", code=404)


@router.delete("/{account_id}", response_model=dict)
async def delete_account(
    account_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
):
    """删除账户"""
    service = AccountService(db)
    result = await service.delete(account_id)
    if result:
        return success_response(message="账户删除成功")
    return error_response(message="账户不存在", code=404)


@router.post("/{account_id}/refresh-cookie", response_model=dict)
async def refresh_cookie(
    account_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
):
    """刷新Cookie"""
    service = AccountService(db)
    account = await service.get_by_id(account_id)
    if not account:
        return error_response(message="账户不存在", code=404)

    # TODO: 调用RPA模块刷新Cookie
    # 这里需要调用RPA模块的登录功能获取新Cookie

    return success_response(message="Cookie刷新成功")
