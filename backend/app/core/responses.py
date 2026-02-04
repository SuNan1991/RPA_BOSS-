"""
统一响应模型
"""
from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""

    code: int = Field(default=200, description="状态码")
    message: str = Field(default="success", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": None
            }
        }


class PageResponse(BaseModel, Generic[T]):
    """分页响应模型"""

    code: int = Field(default=200, description="状态码")
    message: str = Field(default="success", description="响应消息")
    data: list[T] = Field(default=[], description="数据列表")
    total: int = Field(default=0, description="总数")
    page: int = Field(default=1, description="当前页")
    page_size: int = Field(default=10, description="每页数量")


def success_response(data: Any = None, message: str = "success", code: int = 200) -> dict:
    """成功响应"""
    return {
        "code": code,
        "message": message,
        "data": data
    }


def error_response(message: str = "error", code: int = 500, data: Any = None) -> dict:
    """错误响应"""
    return {
        "code": code,
        "message": message,
        "data": data
    }
