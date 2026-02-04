"""
RPA功能模块
"""
from .login import BossLoginModule
from .job import JobSearchModule
from .chat import AutoChatModule

__all__ = ["BossLoginModule", "JobSearchModule", "AutoChatModule"]
