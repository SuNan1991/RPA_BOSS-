"""
账户相关数据模型
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AccountBase(BaseModel):
    """账户基础模型"""

    phone: str = Field(..., description="手机号")
    username: Optional[str] = Field(None, description="用户名")
    is_active: bool = Field(default=True, description="是否激活")


class AccountCreate(AccountBase):
    """创建账户"""
    password: str = Field(..., description="密码")


class AccountUpdate(BaseModel):
    """更新账户"""
    username: Optional[str] = None
    is_active: Optional[bool] = None
    cookie_status: Optional[str] = None


class AccountResponse(AccountBase):
    """账户响应"""
    id: str = Field(..., description="账户ID")
    cookie_status: str = Field(default="none", description="Cookie状态: none, valid, invalid")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123",
                "phone": "13800138000",
                "username": "张三",
                "is_active": True,
                "cookie_status": "valid"
            }
        }


class LoginRequest(BaseModel):
    """登录请求"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")
