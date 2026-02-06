"""
RPA功能模块
"""

from .chat import AutoChatModule
from .job import JobSearchModule
from .login import BossLoginModule

__all__ = ["BossLoginModule", "JobSearchModule", "AutoChatModule"]
