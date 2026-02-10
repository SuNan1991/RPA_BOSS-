"""RPA modules"""

# Use lazy imports to avoid failing when optional dependencies (ddddocr, etc.) are missing
try:
    from .login import BossLoginModule
except ImportError:
    BossLoginModule = None

try:
    from .job import JobSearchModule
except ImportError:
    JobSearchModule = None

try:
    from .chat import AutoChatModule
except ImportError:
    AutoChatModule = None

__all__ = ["BossLoginModule", "JobSearchModule", "AutoChatModule"]
