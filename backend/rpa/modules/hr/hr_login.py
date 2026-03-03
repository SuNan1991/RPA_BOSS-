"""
BOSS直聘招聘者登录模块
"""

from typing import Any, Optional

from app.core.config import settings
from app.core.logging import get_logger
from rpa.core.base import BaseModule

logger = get_logger("hr_login")


class HRLoginModule(BaseModule):
    """BOSS直聘招聘者登录模块"""

    # HR 登录入口 URL
    HR_LOGIN_URL = "https://login.zhipin.com/?ka=header-boss-login"

    def __init__(self):
        super().__init__()
        self.base_url = settings.BOSS_URL

    def execute(self, account_id: int, **kwargs) -> dict[str, Any]:
        """
        执行 HR 账号登录

        Args:
            account_id: 账户ID
            **kwargs: 其他参数

        Returns:
            登录结果字典
        """
        try:
            # 1. 初始化浏览器
            self.init_browser(**kwargs)
            page = self.browser.get_page()

            # 2. 导航到 HR 登录页面
            self.logger.info(f"Navigating to HR login page: {self.HR_LOGIN_URL}")
            page.get(self.HR_LOGIN_URL)
            self.wait(2)

            # 3. 等待用户扫码登录
            # 检查是否已经有有效会话
            session_manager = kwargs.get("session_manager")
            if session_manager:
                # 同步方式获取会话（实际使用时在外部异步处理）
                import asyncio
                loop = asyncio.get_event_loop()
                existing_session = loop.run_until_complete(
                    session_manager.load_session_for_account(account_id)
                )
                if existing_session:
                    # 尝试使用已有会话
                    if self._try_auto_login(page, existing_session["cookies"]):
                        self.logger.info(f"Auto-login successful for account {account_id}")
                        return {
                            "success": True,
                            "message": "自动登录成功",
                            "method": "cookie",
                            "account_id": account_id,
                        }

            # 4. 如果没有有效会话，等待扫码登录
            self.logger.info(f"Waiting for QR code scan for account {account_id}")
            login_result = self._wait_for_qr_code_login(page, account_id)

            return login_result

        except Exception as e:
            self.logger.error(f"HR login failed for account {account_id}: {e}")
            self.save_screenshot()  # 保存错误截图
            return {
                "success": False,
                "message": f"登录失败: {str(e)}",
                "method": "qr_code",
                "account_id": account_id,
            }

    def _try_auto_login(self, page, cookies: list) -> bool:
        """
        尝试使用 Cookie 自动登录

        Args:
            page: 浏览器页面对象
            cookies: Cookie 列表

        Returns:
            是否登录成功
        """
        try:
            # 先访问主域名
            page.get(self.base_url)
            self.wait(1)

            # 设置 cookies
            for cookie in cookies:
                try:
                    page.set.cookie(
                        name=cookie.get("name"),
                        value=cookie.get("value"),
                        domain=cookie.get("domain", ".zhipin.com"),
                        path=cookie.get("path", "/"),
                    )
                except Exception as e:
                    self.logger.debug(f"Failed to set cookie: {e}")
                    continue

            # 刷新页面验证登录状态
            page.get(self.base_url)
            self.wait(2)

            # 检查是否登录成功
            return self._check_login_status(page)

        except Exception as e:
            self.logger.error(f"Auto-login error: {e}")
            return False

    def _wait_for_qr_code_login(self, page, account_id: int, timeout: int = 300) -> dict[str, Any]:
        """
        等待扫码登录

        Args:
            page: 浏览器页面对象
            account_id: 账户ID
            timeout: 超时时间（秒）

        Returns:
            登录结果
        """
        import time

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                current_url = page.url

                # 检查是否跳转出登录页（登录成功的标志）
                if "login.zhipin.com" not in current_url:
                    self.logger.info(f"Login successful, redirected to {current_url}")

                    # 检查登录状态
                    if self._check_login_status(page):
                        return {
                            "success": True,
                            "message": "扫码登录成功",
                            "method": "qr_code",
                            "account_id": account_id,
                        }

                # 等待一段时间再检查
                self.wait(2)

            except Exception as e:
                self.logger.error(f"Error during QR code login wait: {e}")
                self.wait(2)

        # 超时
        self.logger.warning(f"QR code login timeout for account {account_id}")
        return {
            "success": False,
            "message": "扫码登录超时",
            "method": "qr_code",
            "account_id": account_id,
        }

    def _check_login_status(self, page) -> bool:
        """
        检查登录状态

        Args:
            page: 浏览器页面对象

        Returns:
            是否已登录
        """
        try:
            # 访问首页检查登录状态
            page.get(self.base_url, retry=1, timeout=10)
            self.wait(1)

            # HR 登录后的页面元素检查
            # 优先检查 HR 特有的元素
            hr_selectors = [
                ".nav-boss-user",  # HR 用户导航
                ".boss-nav-user",  # 另一种 HR 导航
                ".user-nav",  # 通用用户导航
            ]

            for selector in hr_selectors:
                try:
                    element = page.ele(f"css:{selector}", timeout=3)
                    if element:
                        self.logger.debug(f"Login status confirmed via {selector}")
                        return True
                except Exception:
                    continue

            return False

        except Exception as e:
            self.logger.error(f"Error checking login status: {e}")
            return False

    def extract_user_info(self, page) -> Optional[dict[str, Any]]:
        """
        从页面提取用户信息

        Args:
            page: 浏览器页面对象

        Returns:
            用户信息字典
        """
        try:
            user_info = {}

            # 尝试获取用户名
            username_selectors = [
                ".nav-boss-user-name",
                ".boss-nav-user-name",
                ".user-name",
            ]

            for selector in username_selectors:
                try:
                    element = page.ele(f"css:{selector}", timeout=2)
                    if element:
                        user_info["username"] = element.text.strip()
                        break
                except Exception:
                    continue

            # 尝试获取头像 URL
            avatar_selectors = [
                ".nav-boss-user-pic img",
                ".boss-nav-user-pic img",
                ".user-avatar img",
            ]

            for selector in avatar_selectors:
                try:
                    element = page.ele(f"css:{selector}", timeout=2)
                    if element:
                        user_info["avatar"] = element.attr("src")
                        break
                except Exception:
                    continue

            self.logger.info(f"Extracted user info: {user_info}")
            return user_info if user_info else None

        except Exception as e:
            self.logger.error(f"Failed to extract user info: {e}")
            return None
