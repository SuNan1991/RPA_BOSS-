"""
Browser Restorer - 自动恢复浏览器会话

职责：
1. 服务启动时检查数据库中的 session
2. 如果 session 有效，自动打开浏览器并恢复会话
3. 如果 session 无效或不存在，返回 False 等待用户手动登录

设计原则：
- 单一职责：只负责恢复浏览器会话
- 幂等性：多次调用不会重复打开浏览器
- 优雅降级：恢复失败不影响服务启动
- 可观测性：每个步骤都有日志记录
"""

import asyncio
from typing import Optional

from app.core.logging import get_logger
from rpa.modules.anti_detection import AntiDetection
from rpa.modules.browser_manager import BrowserManager
from rpa.modules.session_manager import SessionManager

logger = get_logger(__name__)


class BrowserRestorer:
    """浏览器会话恢复器 - 服务启动时自动恢复登录状态"""

    _instance: Optional["BrowserRestorer"] = None
    _restore_in_progress: bool = False
    _last_restore_result: Optional[bool] = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化恢复器"""
        if not hasattr(self, "_initialized"):
            self.browser_manager = BrowserManager()
            self.session_manager = SessionManager()
            self._initialized = True
            logger.debug("BrowserRestorer initialized")

    async def restore_if_valid_session(self) -> bool:
        """
        检查并恢复浏览器会话

        调用时机：服务启动时调用一次

        Returns:
            True: 恢复成功，浏览器已打开
            False: 无有效 session，需要用户手动登录
        """
        # 防止并发恢复
        if self._restore_in_progress:
            logger.warning("Restore already in progress, waiting...")
            # 等待当前恢复完成
            while self._restore_in_progress:
                await asyncio.sleep(0.1)
            return self._last_restore_result or False

        self._restore_in_progress = True

        try:
            logger.info("Starting browser session restoration...")

            # 步骤1: 检查浏览器是否已经运行
            if self.browser_manager.is_browser_running():
                logger.info("Browser already running, skipping restoration")
                self._last_restore_result = True
                return True

            # 步骤2: 加载 session
            logger.info("Loading session from database...")
            session = await self.session_manager.load_session()

            if not session:
                logger.info("No valid session found, waiting for user login")
                self._last_restore_result = False
                return False

            cookies = session.get("cookies", [])
            user_info = session.get("user_info", {})

            if not cookies:
                logger.warning("Session has no cookies, cannot restore")
                self._last_restore_result = False
                return False

            logger.info(f"Valid session found for user: {user_info.get('username', 'Unknown')}")

            # 步骤3: 启动浏览器
            logger.info("Starting browser...")
            browser = self.browser_manager.start_browser()

            if not browser:
                logger.error("Failed to start browser")
                self._last_restore_result = False
                return False

            # 步骤4: 注入反检测脚本
            logger.info("Injecting anti-detection scripts...")
            try:
                AntiDetection.inject_anti_detection_scripts(browser)
            except Exception as e:
                logger.warning(f"Failed to inject anti-detection scripts: {e}")
                # 继续执行，反检测脚本注入失败不阻止恢复

            # 步骤5: 注入 cookies
            logger.info(f"Injecting {len(cookies)} cookies...")
            try:
                # DrissionPage 的 cookies 方法
                browser.cookies(cookies)
                logger.info("Cookies injected successfully")
            except Exception as e:
                logger.error(f"Failed to inject cookies: {e}")
                self.browser_manager.close_browser()
                self._last_restore_result = False
                return False

            # 步骤6: 导航到 BOSS 首页
            logger.info("Navigating to BOSS homepage...")
            try:
                browser.get("https://www.zhipin.com")
                logger.info(f"Navigated to: {browser.url}")
            except Exception as e:
                logger.error(f"Failed to navigate: {e}")
                self.browser_manager.close_browser()
                self._last_restore_result = False
                return False

            # 步骤7: 验证登录状态
            logger.info("Verifying login status...")
            is_logged_in = await self._verify_login_status(browser)

            if is_logged_in:
                logger.info("Browser session restored successfully!")
                self._last_restore_result = True
                return True
            else:
                logger.warning("Login verification failed, session may be expired")
                # 不关闭浏览器，让用户可以看到当前页面状态
                self._last_restore_result = False
                return False

        except Exception as e:
            logger.error(f"Error during browser restoration: {e}", exc_info=True)
            self._last_restore_result = False
            return False

        finally:
            self._restore_in_progress = False

    async def _verify_login_status(self, browser) -> bool:
        """
        验证浏览器登录状态

        通过检查页面元素来判断是否已登录

        Args:
            browser: ChromiumPage 实例

        Returns:
            bool: 是否已登录
        """
        try:
            # 等待页面加载
            await asyncio.sleep(2)

            current_url = browser.url
            logger.debug(f"Current URL: {current_url}")

            # 如果在登录页，说明未登录
            if "login.zhipin.com" in current_url:
                logger.info("On login page, not logged in")
                return False

            # 检查是否有用户信息元素（多个选择器尝试）
            user_selectors = [
                ".nav-figure-text",      # 导航栏用户名
                ".info-primary-name",    # 个人中心
                ".user-name",            # 通用
                "[class*='user-name']",  # 模糊匹配
            ]

            for selector in user_selectors:
                try:
                    element = browser.find(selector)
                    if element:
                        text = element.text.strip() if element.text else ""
                        if text and len(text) > 1:
                            logger.info(f"Found user element with selector '{selector}': {text}")
                            return True
                except Exception:
                    continue

            # 如果找不到用户元素，但不在登录页，可能还在加载
            # 给予宽限，返回 True（后续操作会验证）
            if "zhipin.com" in current_url and "login" not in current_url:
                logger.info("On BOSS site but user element not found, assuming logged in")
                return True

            return False

        except Exception as e:
            logger.error(f"Error verifying login status: {e}")
            return False

    async def restore_browser_only(self) -> dict:
        """
        仅恢复浏览器（不重新检查 session）

        用于前端手动恢复浏览器的场景

        Returns:
            dict: 恢复结果
        """
        try:
            # 如果浏览器已经运行，直接返回成功
            if self.browser_manager.is_browser_running():
                return {
                    "status": "success",
                    "message": "Browser already running",
                    "browser_opened": True
                }

            # 重新执行完整恢复流程
            restored = await self.restore_if_valid_session()

            if restored:
                return {
                    "status": "success",
                    "message": "Browser restored successfully",
                    "browser_opened": True
                }
            else:
                return {
                    "status": "error",
                    "message": "No valid session found, please login first",
                    "browser_opened": False
                }

        except Exception as e:
            logger.error(f"Error in restore_browser_only: {e}")
            return {
                "status": "error",
                "message": str(e),
                "browser_opened": False
            }

    def get_status(self) -> dict:
        """
        获取恢复器状态

        Returns:
            dict: 状态信息
        """
        return {
            "browser_running": self.browser_manager.is_browser_running(),
            "restore_in_progress": self._restore_in_progress,
            "last_restore_result": self._last_restore_result
        }


# 全局单例
browser_restorer = BrowserRestorer()
