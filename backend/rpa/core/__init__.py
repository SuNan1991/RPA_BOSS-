"""
RPA核心模块
"""
from .browser import BrowserManager, browser_manager
from .base import BaseModule

__all__ = ["BrowserManager", "browser_manager", "BaseModule"]
