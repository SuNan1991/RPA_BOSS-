"""
任务相关数据模型
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """任务基础模型"""

    name: str = Field(..., description="任务名称")
    task_type: str = Field(..., description="任务类型: search_job, auto_apply, auto_chat等")
    config: dict = Field(default_factory=dict, description="任务配置")


class TaskCreate(TaskBase):
    """创建任务"""
    pass


class TaskUpdate(BaseModel):
    """更新任务"""
    status: Optional[str] = Field(None, description="状态")
    config: Optional[dict] = Field(None, description="任务配置")
    result: Optional[dict] = Field(None, description="任务结果")


class TaskResponse(TaskBase):
    """任务响应"""
    id: str = Field(..., description="任务ID")
    status: str = Field(default="pending", description="状态: pending, running, completed, failed")
    result: Optional[dict] = Field(None, description="任务结果")
    error_message: Optional[str] = Field(None, description="错误信息")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123",
                "name": "自动投递任务",
                "task_type": "auto_apply",
                "status": "running",
                "config": {"keyword": "Python", "city": "北京"}
            }
        }
