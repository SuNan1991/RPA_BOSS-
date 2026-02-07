"""
RPA自动化模块
"""

# Use lazy imports to avoid failing when optional dependencies are missing
# Modules can be imported directly: from rpa.modules.browser_manager import BrowserManager

try:
    from .core import BaseModule, browser_manager
except ImportError:
    BaseModule = None
    browser_manager = None

try:
    from .modules import AutoChatModule, BossLoginModule, JobSearchModule
except ImportError:
    BossLoginModule = None
    JobSearchModule = None
    AutoChatModule = None

__all__ = [
    "BaseModule",
    "browser_manager",
    "BossLoginModule",
    "JobSearchModule",
    "AutoChatModule",
]
