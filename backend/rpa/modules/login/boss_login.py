"""
BOSS直聘登录模块
"""

from typing import Any, Optional

from ...app.core.config import settings
from ...app.core.logging import get_logger
from ..core.base import BaseModule
from ..modules.captcha import CaptchaHandler, SlideTrackGenerator

logger = get_logger("boss_login")


class BossLoginModule(BaseModule):
    """BOSS直聘登录模块"""

    def __init__(self):
        super().__init__()
        self.captcha_handler = CaptchaHandler(captcha_type="slide")
        self.track_generator = SlideTrackGenerator()
        self.base_url = settings.BOSS_URL

    def execute(
        self, phone: str, password: str, use_cookie: bool = True, **kwargs
    ) -> dict[str, Any]:
        """
        执行登录

        Args:
            phone: 手机号
            password: 密码
            use_cookie: 是否使用保存的Cookie
            **kwargs: 其他参数

        Returns:
            登录结果字典
        """
        try:
            # 初始化浏览器
            self.init_browser(**kwargs)
            page = self.browser.get_page()

            # 如果启用Cookie，先尝试加载
            if use_cookie:
                if self.browser.load_cookies(url=self.base_url):
                    # 验证Cookie是否有效
                    if self._check_login_status(page):
                        self.logger.info("Login successful via cookie")
                        return {
                            "success": True,
                            "message": "Cookie登录成功",
                            "method": "cookie",
                        }

            # 执行正常登录流程
            return self._login_by_password(page, phone, password)

        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            self.save_screenshot()  # 保存错误截图
            return {"success": False, "message": f"登录失败: {str(e)}", "method": "password"}

    def _login_by_password(self, page, phone: str, password: str) -> dict[str, Any]:
        """
        通过密码登录

        Args:
            page: 浏览器页面对象
            phone: 手机号
            password: 密码

        Returns:
            登录结果
        """
        try:
            # 访问登录页面
            login_url = f"{self.base_url}/web/user/?ka=header-login"
            self.logger.info(f"Navigating to login page: {login_url}")
            page.get(login_url)

            self.wait(1)

            # 切换到密码登录
            password_tab = page.ele("css:.job-seeker-login .pwd-login-wrap", timeout=5)
            if password_tab:
                self.logger.info("Switching to password login mode")
                # 点击密码登录标签
                pwd_tab = page.ele("css:.job-seeker-login .fl-tab-item:nth-child(2)")
                if pwd_tab:
                    pwd_tab.click()
                    self.wait(0.5)

            # 输入手机号
            phone_input = page.ele("css:#phone", timeout=5)
            if not phone_input:
                return {"success": False, "message": "未找到手机号输入框", "method": "password"}

            phone_input.input(phone)
            self.logger.info(f"Phone number entered: {phone}")

            # 输入密码
            password_input = page.ele("css:#pwd", timeout=5)
            if not password_input:
                return {"success": False, "message": "未找到密码输入框", "method": "password"}

            password_input.input(password)
            self.logger.info("Password entered")

            # 点击登录按钮
            login_button = page.ele("css:.job-seeker-login .btn-login", timeout=5)
            if not login_button:
                return {"success": False, "message": "未找到登录按钮", "method": "password"}

            login_button.click()
            self.logger.info("Login button clicked")

            # 等待页面响应
            self.wait(2)

            # 检查是否出现滑块验证码
            if self._check_captcha(page):
                self.logger.info("Captcha detected, handling...")
                if not self._handle_slide_captcha(page):
                    return {
                        "success": False,
                        "message": "滑块验证码处理失败",
                        "method": "password",
                    }

            # 再次等待
            self.wait(2)

            # 检查登录状态
            if self._check_login_status(page):
                # 保存Cookie
                self.browser.save_cookies()
                self.logger.info("Login successful, cookies saved")
                return {"success": True, "message": "登录成功", "method": "password"}
            else:
                # 检查错误提示
                error_msg = self._get_error_message(page)
                return {"success": False, "message": error_msg or "登录失败", "method": "password"}

        except Exception as e:
            self.logger.error(f"Password login error: {e}")
            return {"success": False, "message": f"登录异常: {str(e)}", "method": "password"}

    def _check_captcha(self, page) -> bool:
        """
        检查是否出现验证码

        Args:
            page: 浏览器页面对象

        Returns:
            是否出现验证码
        """
        try:
            # 检查滑块验证码元素
            captcha = page.ele("css:.verify-wrap", timeout=2)
            return captcha is not None
        except Exception:
            return False

    def _handle_slide_captcha(self, page) -> bool:
        """
        处理滑块验证码

        Args:
            page: 浏览器页面对象

        Returns:
            是否处理成功
        """
        try:
            # 等待验证码加载
            self.wait(1)

            # 获取滑块元素
            slider = page.ele("css:.verify-slider img", timeout=5)
            if not slider:
                self.logger.warning("Slider element not found")
                return False

            # 获取背景图
            bg_canvas = page.ele("css:.verify-canvas canvas", timeout=5)
            if not bg_canvas:
                self.logger.warning("Background canvas not found")
                return False

            # 这里需要根据实际页面结构获取验证码图片
            # 简化处理：直接尝试拖动
            track = self.track_generator.generate_curve_track(distance=200)

            # 执行拖动
            slider = page.ele("css:.verify-slider", timeout=5)
            if slider:
                # 使用DrissionPage的拖动功能
                # 这里简化处理，实际需要根据页面结构调整
                for i, (x, y, t) in enumerate(track):
                    if i == 0:
                        slider.hover()
                    else:
                        page.actions.move_to(x, y)
                    self.wait(0.01)

                self.logger.info("Slider captcha handled")
                self.wait(1)
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error handling slide captcha: {e}")
            return False

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

            # 检查是否有用户信息元素
            user_nav = page.ele("css:.user-nav", timeout=5)
            return user_nav is not None

        except Exception as e:
            self.logger.error(f"Error checking login status: {e}")
            return False

    def _get_error_message(self, page) -> Optional[str]:
        """
        获取错误提示信息

        Args:
            page: 浏览器页面对象

        Returns:
            错误信息
        """
        try:
            error_ele = page.ele("css:.job-seeker-login .error-msg", timeout=2)
            if error_ele:
                return error_ele.text
            return None
        except Exception:
            return None
