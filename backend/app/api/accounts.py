"""
账户相关API
"""

from datetime import datetime
from typing import Optional

import aiosqlite
from fastapi import APIRouter, Depends, Query

from ..core.database import get_database
from ..core.responses import error_response, success_response
from ..schemas.account import (
    AccountCreate,
    AccountUpdate,
    BatchOperationRequest,
)
from ..services import AccountService

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.post("/", response_model=dict)
async def create_account(account: AccountCreate, db: aiosqlite.Connection = Depends(get_database)):
    """创建账户"""
    service = AccountService(db)

    # 检查手机号是否已存在
    existing = await service.get_by_phone(account.phone)
    if existing:
        return error_response(message="该手机号已注册", code=400)

    result = await service.create(account)
    return success_response(data=result.model_dump(), message="账户创建成功")


# ==================== 账号合并相关API ====================


@router.get("/duplicates", response_model=dict)
async def detect_duplicate_accounts(db: aiosqlite.Connection = Depends(get_database)):
    """检测重复账号"""
    from ..services.account_merge_service import AccountMergeService

    service = AccountMergeService(db)
    duplicates = await service.detect_duplicates()

    return success_response({
        "duplicates": [dup.model_dump() for dup in duplicates],
        "total_groups": len(duplicates),
        "message": f"检测到 {len(duplicates)} 组重复账号"
    })


@router.get("/{source_id}/merge-preview/{target_id}", response_model=dict)
async def preview_merge_accounts(
    source_id: int,
    target_id: int,
    db: aiosqlite.Connection = Depends(get_database)
):
    """预览账号合并结果"""
    from ..services.account_merge_service import AccountMergeService

    if source_id == target_id:
        return error_response(message="不能合并到同一个账号", code=400)

    service = AccountMergeService(db)
    preview = await service.preview_merge(source_id, target_id)

    return success_response({
        "preview": preview.model_dump(),
        "message": "预览生成成功"
    })


@router.post("/{source_id}/merge", response_model=dict)
async def merge_accounts(
    source_id: int,
    target_id: int,
    strategy: str = "keep_target",
    db: aiosqlite.Connection = Depends(get_database)
):
    """
    合并账号

    Args:
        source_id: 源账号ID（将被合并）
        target_id: 目标账号ID（将保留）
        strategy: 合并策略 (keep_target/keep_source/keep_newer)
    """
    from ..services.account_merge_service import AccountMergeService

    if source_id == target_id:
        return error_response(message="不能合并到同一个账号", code=400)

    if strategy not in ["keep_target", "keep_source", "keep_newer"]:
        return error_response(message="无效的合并策略", code=400)

    service = AccountMergeService(db)
    result = await service.merge_accounts(source_id, target_id, strategy)

    if result.success:
        return success_response({
            "target_id": result.target_id,
            "message": result.message
        })
    else:
        return error_response(message=result.message, code=500)


# ==================== 基础CRUD API ====================


@router.get("/{account_id}", response_model=dict)
async def get_account(account_id: int, db: aiosqlite.Connection = Depends(get_database)):
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
    account_type: Optional[str] = Query(None, description="账户类型: hr 或 seeker"),
    db: aiosqlite.Connection = Depends(get_database),
):
    """获取账户列表"""
    skip = (page - 1) * page_size

    service = AccountService(db)
    accounts, total = await service.get_list(skip=skip, limit=page_size, is_active=is_active, account_type=account_type)

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
    account_id: int,
    account: AccountUpdate,
    db: aiosqlite.Connection = Depends(get_database),
):
    """更新账户"""
    service = AccountService(db)
    result = await service.update(account_id, account)
    if result:
        return success_response(data=result.model_dump(), message="账户更新成功")
    return error_response(message="账户不存在", code=404)


@router.delete("/{account_id}", response_model=dict)
async def delete_account(account_id: int, db: aiosqlite.Connection = Depends(get_database)):
    """删除账户"""
    service = AccountService(db)
    result = await service.delete(account_id)
    if result:
        return success_response(message="账户删除成功")
    return error_response(message="账户不存在", code=404)


@router.post("/{account_id}/refresh-cookie", response_model=dict)
async def refresh_cookie(account_id: int, db: aiosqlite.Connection = Depends(get_database)):
    """刷新Cookie"""
    service = AccountService(db)
    account = await service.get_by_id(account_id)
    if not account:
        return error_response(message="账户不存在", code=404)

    # 调用RPA服务刷新Cookie
    from ..services.rpa_service import RPAService

    rpa_service = RPAService()

    # 检查是否已有登录在进行中
    if rpa_service.is_login_in_progress():
        return error_response(message="已有登录正在进行中，请稍后再试", code=400)

    # 启动登录流程
    result = await rpa_service.start_login_for_account(account_id)

    if result.get("status") == "browser_opened":
        return success_response(
            data={"account_id": account_id, "status": "browser_opened"},
            message="浏览器已打开，请扫码或密码登录",
        )
    else:
        return error_response(message=result.get("message", "刷新Cookie失败"), code=500)


@router.get("/{account_id}/validate", response_model=dict)
async def validate_cookie(account_id: int, db: aiosqlite.Connection = Depends(get_database)):
    """验证Cookie是否有效"""
    service = AccountService(db)
    account = await service.get_by_id(account_id)
    if not account:
        return error_response(message="账户不存在", code=404)

    # 调用会话管理器验证Cookie
    from rpa.modules.session_manager import SessionManager

    session_manager = SessionManager()
    is_valid = await session_manager.validate_cookies(account_id)

    # 更新Cookie状态
    new_status = "valid" if is_valid else "invalid"
    await service.update_cookie_status(account_id, new_status)

    return success_response(data={"valid": is_valid, "status": new_status}, message="Cookie验证完成")


# ============================================================================
# Enhanced API Endpoints
# ============================================================================

@router.get("/statistics/overview", response_model=dict)
async def get_statistics(db: aiosqlite.Connection = Depends(get_database)):
    """获取账号统计概览"""
    service = AccountService(db)
    stats = await service.get_statistics()
    return success_response(data=stats.model_dump())


@router.post("/batch", response_model=dict)
async def batch_operation(
    request: BatchOperationRequest,
    db: aiosqlite.Connection = Depends(get_database),
):
    """批量操作账号"""
    if not request.account_ids:
        return error_response(message="账号ID列表不能为空", code=400)

    if request.action not in ["activate", "deactivate", "delete", "refresh_cookies"]:
        return error_response(message=f"不支持的操作类型: {request.action}", code=400)

    service = AccountService(db)
    result = await service.batch_operation(request)

    return success_response(
        data={
            "success_count": result.success_count,
            "failed_count": result.failed_count,
            "details": result.details,
        },
        message=f"批量{request.action}完成",
    )


@router.get("/{account_id}/logs", response_model=dict)
async def get_operation_logs(
    account_id: int,
    operation_type: Optional[str] = Query(None, description="操作类型"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: aiosqlite.Connection = Depends(get_database),
):
    """获取账号操作日志"""
    service = AccountService(db)

    # 验证账号是否存在
    account = await service.get_by_id(account_id)
    if not account:
        return error_response(message="账户不存在", code=404)

    logs, total = await service.get_operation_logs(
        account_id=account_id,
        operation_type=operation_type,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )

    return {
        "code": 200,
        "message": "success",
        "data": [log.model_dump() for log in logs],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/group/{group_id}", response_model=dict)
async def get_accounts_by_group(
    group_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: aiosqlite.Connection = Depends(get_database),
):
    """获取分组下的账号列表"""
    from ..services.account_group_service import AccountGroupService

    group_service = AccountGroupService(db)
    group = await group_service.get_by_id(group_id)
    if not group:
        return error_response(message="分组不存在", code=404)

    accounts = await group_service.get_accounts_by_group(group_id)

    # Simple pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated_accounts = accounts[start:end]

    return {
        "code": 200,
        "message": "success",
        "data": [account.model_dump() for account in paginated_accounts],
        "total": len(accounts),
        "page": page,
        "page_size": page_size,
        "group": group.model_dump(),
    }

