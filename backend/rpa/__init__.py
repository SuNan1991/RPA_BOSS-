"""
RPA自动化模块
"""
from .core import BaseModule, browser_manager
from .modules import BossLoginModule, JobSearchModule, AutoChatModule

__all__ = [
    "BaseModule",
    "browser_manager",
    "BossLoginModule",
    "JobSearchModule",
    "AutoChatModule",
]
