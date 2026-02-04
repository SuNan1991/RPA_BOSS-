"""
RPA基础模块类
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from .browser import browser_manager
from ...app.core.logging import get_logger

logger = get_logger("base_module")


class BaseModule(ABC):
    """RPA基础模块类"""

    def __init__(self):
        self.browser = browser_manager
        self.logger = logger

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行模块功能

        Args:
            **kwargs: 模块参数

        Returns:
            执行结果字典
        """
        pass

    def init_browser(self, **kwargs) -> bool:
        """
        初始化浏览器

        Args:
            **kwargs: 浏览器配置参数

        Returns:
            是否初始化成功
        """
        try:
            if not self.browser.is_initialized:
                self.browser.init_browser(**kwargs)
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            return False

    def close_browser(self) -> bool:
        """
        关闭浏览器

        Returns:
            是否关闭成功
        """
        try:
            self.browser.close_browser()
            return True
        except Exception as e:
            self.logger.error(f"Failed to close browser: {e}")
            return False

    def save_screenshot(self, file_path: str = None) -> bool:
        """
        保存截图

        Args:
            file_path: 截图文件路径

        Returns:
            是否保存成功
        """
        return self.browser.save_screenshot(file_path)

    def wait(self, seconds: float):
        """
        等待指定秒数

        Args:
            seconds: 等待秒数
        """
        import time
        self.logger.debug(f"Waiting {seconds} seconds...")
        time.sleep(seconds)
