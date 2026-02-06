"""
职位相关数据模型
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class JobBase(BaseModel):
    """职位基础模型"""

    job_name: str = Field(..., description="职位名称")
    company_name: str = Field(..., description="公司名称")
    salary: str = Field(..., description="薪资范围")
    city: str = Field(..., description="城市")
    area: Optional[str] = Field(None, description="区域")
    experience: Optional[str] = Field(None, description="经验要求")
    education: Optional[str] = Field(None, description="学历要求")
    company_size: Optional[str] = Field(None, description="公司规模")
    industry: Optional[str] = Field(None, description="行业")
    job_url: str = Field(..., description="职位链接")
    boss_title: Optional[str] = Field(None, description="BOSS职位")


class JobCreate(JobBase):
    """创建职位"""

    pass


class JobUpdate(BaseModel):
    """更新职位"""

    status: Optional[str] = Field(None, description="状态")
    is_applied: Optional[bool] = Field(None, description="是否已投递")
    notes: Optional[str] = Field(None, description="备注")


class JobResponse(JobBase):
    """职位响应"""

    id: int = Field(..., description="职位ID")
    status: str = Field(default="pending", description="状态")
    is_applied: bool = Field(default=False, description="是否已投递")
    notes: Optional[str] = Field(None, description="备注")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "job_name": "Python开发工程师",
                "company_name": "科技公司",
                "salary": "15-25K",
                "city": "北京",
                "status": "pending",
                "is_applied": False,
            }
        }


class JobFilter(BaseModel):
    """职位筛选"""

    city: Optional[str] = None
    keyword: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
