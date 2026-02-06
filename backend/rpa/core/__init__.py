"""
RPA核心模块
"""

from .base import BaseModule
from .browser import BrowserManager, browser_manager

__all__ = ["BrowserManager", "browser_manager", "BaseModule"]
