"""
账户相关数据模型
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class AccountBase(BaseModel):
    """账户基础模型"""

    phone: str = Field(..., description="手机号")
    username: Optional[str] = Field(None, description="用户名")
    is_active: bool = Field(default=True, description="是否激活")


class AccountCreate(AccountBase):
    """创建账户"""

    password: Optional[str] = Field(None, description="密码（可选，不存储）")
    account_type: str = Field(default="hr", description="账户类型: hr 或 seeker")
    group_id: Optional[int] = Field(None, description="分组ID")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    notes: Optional[str] = Field(None, description="备注")
    quota_limit: int = Field(default=100, description="每日配额限制")


class AccountUpdate(BaseModel):
    """更新账户"""

    username: Optional[str] = None
    is_active: Optional[bool] = None
    cookie_status: Optional[str] = None
    account_type: Optional[str] = None
    group_id: Optional[int] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    quota_limit: Optional[int] = None


class AccountResponse(AccountBase):
    """账户响应"""

    id: int = Field(..., description="账户ID")
    account_type: str = Field(default="hr", description="账户类型: hr 或 seeker")
    cookie_status: str = Field(default="none", description="Cookie状态: none, valid, invalid")
    group_id: Optional[int] = Field(None, description="分组ID")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    notes: Optional[str] = Field(None, description="备注")
    login_count: int = Field(default=0, description="登录次数")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    last_operation_at: Optional[datetime] = Field(None, description="最后操作时间")
    quota_limit: int = Field(default=100, description="每日配额限制")
    quota_used: int = Field(default=0, description="今日已用配额")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "phone": "13800138000",
                "username": "张三",
                "is_active": True,
                "cookie_status": "valid",
                "group_id": 1,
                "tags": ["VIP", "活跃"],
                "notes": "重要客户",
                "login_count": 10,
                "quota_limit": 100,
                "quota_used": 30,
            }
        }


# ============================================================================
# Account Group Schemas
# ============================================================================

class AccountGroupBase(BaseModel):
    """账户分组基础模型"""

    name: str = Field(..., description="分组名称")
    description: Optional[str] = Field(None, description="分组描述")
    parent_id: Optional[int] = Field(None, description="父分组ID")


class AccountGroupCreate(AccountGroupBase):
    """创建分组"""

    pass


class AccountGroupUpdate(BaseModel):
    """更新分组"""

    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None


class AccountGroupResponse(AccountGroupBase):
    """分组响应"""

    id: int = Field(..., description="分组ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "VIP客户",
                "description": "重要客户分组",
                "parent_id": None,
            }
        }


# ============================================================================
# Statistics and Operation Log Schemas
# ============================================================================

class AccountStatistics(BaseModel):
    """账户统计"""

    total_accounts: int = Field(..., description="总账号数")
    active_accounts: int = Field(..., description="活跃账号数")
    valid_cookies: int = Field(..., description="有效Cookie数")
    invalid_cookies: int = Field(..., description="无效Cookie数")
    none_cookies: int = Field(..., description="未登录账号数")


class BatchOperationRequest(BaseModel):
    """批量操作请求"""

    action: str = Field(..., description="操作类型: activate, deactivate, delete, refresh_cookies")
    account_ids: List[int] = Field(..., description="账号ID列表")


class BatchOperationResult(BaseModel):
    """批量操作结果"""

    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")
    details: List[dict] = Field(default_factory=list, description="详细信息")


class OperationLogResponse(BaseModel):
    """操作日志响应"""

    id: int = Field(..., description="日志ID")
    account_id: int = Field(..., description="账号ID")
    operation_type: str = Field(..., description="操作类型")
    operation_detail: Optional[str] = Field(None, description="操作详情")
    success: bool = Field(..., description="是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")
    duration_ms: Optional[int] = Field(None, description="耗时(毫秒)")
    created_at: datetime = Field(..., description="创建时间")


class LoginRequest(BaseModel):
    """登录请求"""

    phone: str = Field(..., description="手机号")
    password: Optional[str] = Field(None, description="密码（可选，不存储）")
