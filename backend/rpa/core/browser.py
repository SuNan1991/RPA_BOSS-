"""
浏览器管理模块 - 基于 DrissionPage
"""

import json
import time
from pathlib import Path
from typing import Optional

from DrissionPage import ChromiumOptions, ChromiumPage

from ...app.core.config import settings
from ...app.core.logging import get_logger

logger = get_logger("browser")


class BrowserManager:
    """浏览器管理器"""

    def __init__(self):
        self.page: Optional[ChromiumPage] = None
        self.is_initialized = False

    def init_browser(
        self,
        headless: bool = None,
        user_data_path: str = None,
        proxy: str = None,
    ) -> ChromiumPage:
        """
        初始化浏览器

        Args:
            headless: 是否无头模式
            user_data_path: 用户数据目录路径
            proxy: 代理地址

        Returns:
            ChromiumPage: 浏览器页面对象
        """
        try:
            if self.is_initialized and self.page:
                logger.warning("Browser already initialized")
                return self.page

            # 配置浏览器选项
            co = ChromiumOptions()
            headless = headless if headless is not None else settings.RPA_HEADLESS

            # 设置无头模式
            if headless:
                co.set_argument("--headless")

            # 设置用户数据目录
            if user_data_path:
                co.set_user_data_path(user_data_path)
            else:
                # 使用默认用户数据目录
                default_path = Path(__file__).parent.parent.parent / "data" / "browser_data"
                default_path.mkdir(parents=True, exist_ok=True)
                co.set_user_data_path(str(default_path))

            # 设置代理
            if proxy:
                co.set_proxy(proxy)

            # 禁用自动化检测
            co.set_argument("--disable-blink-features=AutomationControlled")
            co.set_argument("--no-sandbox")
            co.set_argument("--disable-dev-shm-usage")

            # 设置超时
            co.set_timeout(settings.RPA_TIMEOUT)

            # 创建浏览器页面对象
            self.page = ChromiumPage(addr_driver_opts=co)
            self.is_initialized = True

            logger.info("Browser initialized successfully")
            return self.page

        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise

    def close_browser(self):
        """关闭浏览器"""
        try:
            if self.page:
                self.page.quit()
                self.page = None
                self.is_initialized = False
                logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

    def get_page(self) -> ChromiumPage:
        """获取浏览器页面对象"""
        if not self.is_initialized or not self.page:
            raise RuntimeError("Browser not initialized")
        return self.page

    def save_cookies(self, file_path: str = None) -> bool:
        """
        保存Cookie到文件

        Args:
            file_path: Cookie文件路径

        Returns:
            是否保存成功
        """
        try:
            if not self.page:
                logger.error("Browser not initialized")
                return False

            if not file_path:
                file_path = Path(__file__).parent.parent.parent / "data" / "cookies.json"

            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            cookies = self.page.cookies(as_dict=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)

            logger.info(f"Cookies saved to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save cookies: {e}")
            return False

    def load_cookies(self, file_path: str = None, url: str = None) -> bool:
        """
        从文件加载Cookie

        Args:
            file_path: Cookie文件路径
            url: 目标URL，用于设置cookie的作用域

        Returns:
            是否加载成功
        """
        try:
            if not self.page:
                logger.error("Browser not initialized")
                return False

            if not file_path:
                file_path = Path(__file__).parent.parent.parent / "data" / "cookies.json"

            file_path = Path(file_path)
            if not file_path.exists():
                logger.warning(f"Cookie file not found: {file_path}")
                return False

            with open(file_path, encoding="utf-8") as f:
                cookies = json.load(f)

            # 先访问目标域名
            if url:
                self.page.get(url, retry=0, timeout=3)

            # 设置cookies
            for name, value in cookies.items():
                self.page.set.cookie(name, value)

            logger.info(f"Cookies loaded from {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load cookies: {e}")
            return False

    def save_screenshot(self, file_path: str = None) -> bool:
        """
        保存截图

        Args:
            file_path: 截图文件路径

        Returns:
            是否保存成功
        """
        try:
            if not self.page:
                logger.error("Browser not initialized")
                return False

            if not file_path:
                timestamp = int(time.time())
                file_path = (
                    Path(__file__).parent.parent.parent / "logs" / f"screenshot_{timestamp}.png"
                )

            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            self.page.get_screenshot(path=str(file_path))
            logger.info(f"Screenshot saved to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            return False

    def execute_js(self, script: str):
        """
        执行JavaScript脚本

        Args:
            script: JavaScript脚本

        Returns:
            执行结果
        """
        try:
            if not self.page:
                logger.error("Browser not initialized")
                return None

            result = self.page.run_js(script)
            logger.debug(f"Executed JS: {script[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Failed to execute JS: {e}")
            return None


# 全局浏览器管理器实例
browser_manager = BrowserManager()
