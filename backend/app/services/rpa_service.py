"""
RPA Service - Handle RPA login operations
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Any, Optional

# Add backend directory to path for rpa modules import
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.logging import get_logger

logger = get_logger(__name__)


class RPAService:
    """Service for managing RPA login operations"""

    def __init__(self):
        # Lazy initialization to avoid import issues
        self._browser_manager = None
        self._session_manager = None
        self._login_in_progress = False

    @property
    def browser_manager(self):
        """Lazy load browser manager"""
        if self._browser_manager is None:
            from rpa.modules.browser_manager import BrowserManager

            self._browser_manager = BrowserManager()
        return self._browser_manager

    @property
    def session_manager(self):
        """Lazy load session manager"""
        if self._session_manager is None:
            from rpa.modules.session_manager import SessionManager

            self._session_manager = SessionManager()
        return self._session_manager

    async def start_login(self) -> dict[str, Any]:
        """
        Start RPA login process

        Returns:
            dict with status and message
        """
        if self._login_in_progress:
            return {"status": "error", "message": "Login already in progress"}

        try:
            self._login_in_progress = True

            # Start browser (已包含反检测脚本注入)
            browser = self.browser_manager.start_browser()

            # Navigate to BOSS Zhipin login page
            login_url = "https://login.zhipin.com/"
            browser.get(login_url)

            logger.info(f"Navigated to {login_url}")

            # 等待页面加载
            await asyncio.sleep(2)

            # 再次注入反检测脚本（确保在新页面生效）
            from rpa.modules.anti_detection import AntiDetection
            AntiDetection.inject_anti_detection_scripts(browser)

            logger.info("Anti-detection scripts re-injected after page load")

            # Log login attempt
            await self._log_login_attempt(None, success=False, failure_reason="Login started")

            return {
                "status": "browser_opened",
                "message": "Browser opened, waiting for user to login",
            }

        except Exception as e:
            logger.error(f"Failed to start login: {e}")
            self._login_in_progress = False
            await self._log_login_attempt(None, success=False, failure_reason=str(e))

            return {"status": "error", "message": f"Failed to start login: {str(e)}"}

    async def monitor_login(self) -> dict[str, Any]:
        """
        Monitor login process by polling URL

        Returns:
            dict with login status
        """
        try:
            browser = self.browser_manager.get_browser()

            if not browser:
                return {"status": "error", "message": "Browser not running"}

            # Poll URL to detect login success
            max_attempts = 150  # 5 minutes with 2 second intervals
            for attempt in range(max_attempts):
                if not self.browser_manager.is_browser_running():
                    return {"status": "cancelled", "message": "Browser was closed"}

                current_url = browser.url

                # Check if URL changed (login successful)
                if "login.zhipin.com" not in current_url:
                    logger.info(f"Login successful, redirected to {current_url}")
                    return await self._handle_login_success(browser)

                # Wait before next check
                await asyncio.sleep(2)

            # Timeout
            logger.warning("Login timeout after 5 minutes")
            self.browser_manager.close_browser()
            self._login_in_progress = False

            return {"status": "timeout", "message": "Login timeout (5 minutes)"}

        except Exception as e:
            logger.error(f"Error monitoring login: {e}")
            self._login_in_progress = False
            return {"status": "error", "message": f"Error monitoring login: {str(e)}"}

    async def _handle_login_success(self, browser) -> dict[str, Any]:
        """Handle successful login"""
        try:
            # Extract cookies
            cookies = self.extract_cookies(browser)

            # Extract user info
            user_info = self.extract_user_info(browser)

            # ========== 新增：自动同步到账号系统 ==========
            from app.services.account_sync_service import AccountSyncService
            from app.core.database import db

            try:
                conn = await db.get_connection()
                sync_service = AccountSyncService(conn)
                sync_result = await sync_service.sync_account_from_login(
                    cookies=cookies,
                    user_info=user_info
                )

                logger.info(f"[Account Sync] Result: {sync_result.message} (ID: {sync_result.account_id})")

            except Exception as sync_error:
                logger.error(f"[Account Sync] Failed: {sync_error}", exc_info=True)
                # 同步失败不影响登录，使用默认值
                sync_result = {
                    "account_id": None,
                    "is_new_account": False,
                    "message": "同步失败，但登录成功"
                }
            # =============================================

            # 保留原有的保存到 sessions 表（向后兼容）
            await self.session_manager.save_session(cookies, user_info)

            # Log successful login
            username = user_info.get("username") if user_info else "Unknown"
            await self._log_login_attempt(username, success=True)

            # 保持浏览器打开，方便用户继续操作
            # 浏览器将在用户登出或应用退出时关闭
            self._login_in_progress = False

            logger.info("Login successful, browser kept open for user operations")

            # 返回增强的结果，包含 account_id
            return {
                "status": "success",
                "message": "Login successful",
                "user_info": user_info,
                "account_id": sync_result.account_id,
                "is_new_account": sync_result.is_new_account,
                "sync_message": sync_result.message
            }

        except Exception as e:
            logger.error(f"Error handling login success: {e}")
            self._login_in_progress = False
            return {"status": "error", "message": f"Error saving session: {str(e)}"}

    def extract_cookies(self, browser) -> list:
        """
        Extract cookies from browser

        Returns:
            list of cookie dictionaries
        """
        try:
            # DrissionPage 4.x: cookies() 返回列表，使用 all_domains=True 获取所有域的 cookies
            cookies = browser.cookies(all_domains=True, all_info=True)

            # Filter for zhipin.com domain
            zhipin_cookies = [
                cookie for cookie in cookies if "zhipin.com" in str(cookie.get("domain", ""))
            ]

            logger.info(f"Extracted {len(zhipin_cookies)} cookies from zhipin.com")
            return zhipin_cookies

        except Exception as e:
            logger.error(f"Failed to extract cookies: {e}")
            return []

    def extract_user_info(self, browser) -> Optional[dict[str, Any]]:
        """
        Extract user information from page

        使用多种方式获取用户信息:
        1. CSS 选择器（按优先级尝试多个选择器）
        2. JavaScript 执行（从 localStorage/window 对象获取）
        3. API 响应数据（如果有）

        Returns:
            dict with user info or None
        """
        try:
            user_info = {}

            # ==================== 方式1: CSS 选择器获取用户名 ====================
            # BOSS直聘登录后会跳转到主页或个人中心
            # 按优先级尝试多个选择器
            username_selectors = [
                # BOSS直聘导航栏用户名（最常见）
                ".nav-figure-text",      # 导航栏右侧用户名
                ".nav-figure .name",     # 导航栏结构中的名字
                ".nav-figure span",      # 导航栏结构中的 span

                # 个人中心页面
                ".info-primary-name",    # 个人中心主名称
                ".info-primary .name",   # 个人中心名称区域

                # 通用选择器
                ".user-name",
                ".nav-user-name",
                ".username",
                "[class*='user-name']",
                "[class*='userName']",

                # 数据属性
                '[data-selector="user-name"]',
                "[data-user-name]",
            ]

            for selector in username_selectors:
                try:
                    element = browser.find(selector)
                    if element:
                        text = element.text
                        if text:
                            text = text.strip()
                            # 合理的用户名长度检查
                            if 1 < len(text) < 30 and text not in ["登录", "注册", "登录/注册"]:
                                user_info["username"] = text
                                logger.info(f"通过选择器 '{selector}' 提取到用户名: {text}")
                                break
                except Exception as e:
                    logger.debug(f"选择器 '{selector}' 查找失败: {e}")
                    continue

            # ==================== 方式2: CSS 选择器获取头像 ====================
            avatar_selectors = [
                # BOSS直聘导航栏头像
                ".nav-figure img",
                ".nav-avatar img",
                ".nav-figure-box img",

                # 个人中心头像
                ".info-primary img",
                ".user-avatar img",

                # 通用选择器
                "[class*='avatar'] img",
                "[class*='user-img']",
            ]

            for selector in avatar_selectors:
                try:
                    element = browser.find(selector)
                    if element:
                        src = element.attr("src")
                        if src and len(src) > 10:
                            user_info["avatar"] = src
                            logger.info(f"通过选择器 '{selector}' 提取到头像")
                            break
                except Exception as e:
                    logger.debug(f"选择器 '{selector}' 查找失败: {e}")
                    continue

            # ==================== 方式3: JavaScript 获取额外信息 ====================
            # 很多网站会在 localStorage 或 window 对象中存储用户信息
            try:
                js_user_info = browser.run_js("""
                    () => {
                        const result = {};

                        // 检查 localStorage 中的用户信息
                        for (let i = 0; i < localStorage.length; i++) {
                            const key = localStorage.key(i);
                            if (key && (
                                key.includes('user') ||
                                key.includes('userInfo') ||
                                key.includes('account') ||
                                key.includes('geek') ||
                                key.includes('boss')
                            )) {
                                try {
                                    const value = localStorage.getItem(key);
                                    // 尝试解析 JSON
                                    try {
                                        result[key] = JSON.parse(value);
                                    } catch {
                                        result[key] = value;
                                    }
                                } catch (e) {}
                            }
                        }

                        // 检查常见的 window 对象
                        if (window.__INITIAL_STATE__) {
                            result.__INITIAL_STATE__ = window.__INITIAL_STATE__;
                        }
                        if (window.__NUXT__) {
                            result.__NUXT__ = window.__NUXT__;
                        }
                        if (window.pageData) {
                            result.pageData = window.pageData;
                        }
                        if (window.userInfo) {
                            result.userInfo = window.userInfo;
                        }

                        return result;
                    }
                """)

                if js_user_info:
                    logger.debug(f"JavaScript 获取到数据: {list(js_user_info.keys()) if isinstance(js_user_info, dict) else 'non-dict'}")

                    # 从 JavaScript 结果中提取用户名
                    if not user_info.get("username"):
                        user_info["username"] = self._extract_username_from_js_result(js_user_info)

                    # 从 JavaScript 结果中提取头像
                    if not user_info.get("avatar"):
                        user_info["avatar"] = self._extract_avatar_from_js_result(js_user_info)

            except Exception as e:
                logger.debug(f"JavaScript 获取用户信息失败: {e}")

            # ==================== 方式4: 从页面 URL 或其他元数据获取 ====================
            # 如果仍然没有用户名，尝试从页面标题或其他地方获取
            if not user_info.get("username"):
                try:
                    # 尝试从页面标题获取
                    title = browser.title
                    if title and "-" in title:
                        # BOSS直聘的标题通常是 "用户名 - BOSS直聘"
                        possible_name = title.split("-")[0].strip()
                        if possible_name and possible_name not in ["BOSS直聘", "BOSS", "直聘"]:
                            user_info["username"] = possible_name
                            logger.info(f"从页面标题提取到用户名: {possible_name}")
                except Exception as e:
                    logger.debug(f"从标题获取用户名失败: {e}")

            # ==================== 验证结果 ====================
            if user_info:
                logger.info(f"成功提取用户信息: {user_info}")
                return user_info
            else:
                logger.warning("未能提取到任何用户信息，可能页面结构已变化")
                # 返回一个包含默认值的字典，而不是 None
                # 这样可以避免 session 被视为无效
                return {"username": "BOSS用户", "source": "default"}

        except Exception as e:
            logger.error(f"提取用户信息失败: {e}")
            # 返回默认值而不是 None
            return {"username": "BOSS用户", "source": "default", "error": str(e)}

    def _extract_username_from_js_result(self, js_result: dict) -> Optional[str]:
        """从 JavaScript 结果中提取用户名"""
        if not isinstance(js_result, dict):
            return None

        # 递归搜索用户名
        def find_username(obj, depth=0):
            if depth > 5:  # 限制递归深度
                return None

            if isinstance(obj, dict):
                # 直接检查常见的用户名字段
                for key in ["name", "username", "nickname", "realName", "userName", "displayName"]:
                    if obj.get(key) and isinstance(obj[key], str) and len(obj[key]) < 30:
                        return obj[key]

                # 递归检查嵌套对象
                for value in obj.values():
                    result = find_username(value, depth + 1)
                    if result:
                        return result

            elif isinstance(obj, list):
                for item in obj:
                    result = find_username(item, depth + 1)
                    if result:
                        return result

            return None

        return find_username(js_result)

    def _extract_avatar_from_js_result(self, js_result: dict) -> Optional[str]:
        """从 JavaScript 结果中提取头像 URL"""
        if not isinstance(js_result, dict):
            return None

        # 递归搜索头像
        def find_avatar(obj, depth=0):
            if depth > 5:
                return None

            if isinstance(obj, dict):
                # 直接检查常见的头像字段
                for key in ["avatar", "avatarUrl", "headImg", "photo", "headUrl", "avatarSmall"]:
                    if obj.get(key) and isinstance(obj[key], str) and obj[key].startswith("http"):
                        return obj[key]

                # 递归检查嵌套对象
                for value in obj.values():
                    result = find_avatar(value, depth + 1)
                    if result:
                        return result

            elif isinstance(obj, list):
                for item in obj:
                    result = find_avatar(item, depth + 1)
                    if result:
                        return result

            return None

        return find_avatar(js_result)

    async def apply_session_to_browser(self) -> bool:
        """
        Apply saved cookies to browser for auto-login

        Returns:
            bool: True if session was applied successfully
        """
        try:
            # Load session from database
            session = await self.session_manager.load_session()
            if not session or not session.get("cookies"):
                logger.debug("No session found to apply")
                return False

            # Start browser
            browser = self.browser_manager.start_browser()
            if not browser:
                logger.error("Failed to start browser for session application")
                return False

            # Apply cookies to browser
            cookies = session["cookies"]
            for cookie_dict in cookies:
                try:
                    # Set cookie for the correct domain
                    browser.set.cookie(
                        name=cookie_dict.get("name"),
                        value=cookie_dict.get("value"),
                        domain=cookie_dict.get("domain", ".zhipin.com"),
                        path=cookie_dict.get("path", "/"),
                    )
                except Exception as e:
                    logger.warning(f"Failed to set cookie {cookie_dict.get('name')}: {e}")

            logger.info(f"Applied {len(cookies)} cookies to browser")

            # Navigate to BOSS Zhipin to verify login
            await asyncio.sleep(1)
            browser.get("https://www.zhipin.com/")
            await asyncio.sleep(2)

            # Check if login was successful
            current_url = browser.url
            if "login.zhipin.com" not in current_url:
                logger.info("Auto-login successful using saved cookies")
                return True
            else:
                logger.warning("Auto-login failed, cookies may be expired")
                return False

        except Exception as e:
            logger.error(f"Failed to apply session to browser: {e}")
            return False

    def logout(self) -> dict[str, Any]:
        """
        Logout user and clear session

        Returns:
            dict with status
        """
        try:
            # Close browser if running
            if self.browser_manager.is_browser_running():
                self.browser_manager.close_browser()

            # Delete session
            self.session_manager.delete_session()

            logger.info("Logout successful")
            return {"status": "success", "message": "Logged out successfully"}

        except Exception as e:
            logger.error(f"Failed to logout: {e}")
            return {"status": "error", "message": f"Logout failed: {str(e)}"}

    async def get_status(self) -> dict[str, Any]:
        """
        Get current RPA and login status

        Returns:
            dict with status information
        """
        try:
            # Check if DrissionPage is available
            import importlib.util

            if not importlib.util.find_spec("DrissionPage"):
                return {
                    "is_logged_in": False,
                    "user_info": None,
                    "browser_status": "not_available",
                    "login_in_progress": False,
                    "timestamp": datetime.now().isoformat(),
                }

            session = await self.session_manager.load_session()
            browser_health = await self.browser_manager.health_check()

            # 防御性验证：同时检查 session 和 user_info 是否存在
            user_info = session.get("user_info") if session else None
            is_logged_in = session is not None and user_info is not None and bool(user_info)

            return {
                "is_logged_in": is_logged_in,
                "user_info": user_info,
                "browser_status": browser_health.get("status"),
                "browser_opened": self.browser_manager.is_browser_running(),
                "login_in_progress": self._login_in_progress,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {
                "is_logged_in": False,
                "user_info": None,
                "browser_status": "error",
                "login_in_progress": False,
                "timestamp": datetime.now().isoformat(),
            }

    async def _log_login_attempt(
        self, username: Optional[str], success: bool, failure_reason: Optional[str] = None
    ):
        """Log login attempt to database"""
        try:
            from app.core.database import db

            conn = await db.get_connection()
            await conn.execute(
                """
                INSERT INTO login_logs (username, success, failure_reason, timestamp)
                VALUES (?, ?, ?, ?)
            """,
                (username, success, failure_reason, datetime.now()),
            )
            await conn.commit()

        except Exception as e:
            logger.error(f"Failed to log login attempt: {e}")

    def is_login_in_progress(self) -> bool:
        """Check if login is currently in progress"""
        return self._login_in_progress

    def set_login_progress(self, in_progress: bool):
        """Set login progress flag"""
        self._login_in_progress = in_progress

    async def restore_browser_session(self) -> dict[str, Any]:
        """
        恢复浏览器会话（手动恢复）

        用于前端手动恢复浏览器的场景

        Returns:
            dict: 恢复结果
        """
        try:
            from rpa.modules.browser_restorer import browser_restorer

            result = await browser_restorer.restore_browser_only()
            return result

        except Exception as e:
            logger.error(f"Failed to restore browser session: {e}")
            return {
                "status": "error",
                "message": str(e),
                "browser_opened": False
            }

    # ==================== 账户登录方法 ====================

    async def start_login_for_account(self, account_id: int) -> dict[str, Any]:
        """
        Start RPA login process for a specific account

        Args:
            account_id: 账户ID

        Returns:
            dict with status and message
        """
        if self._login_in_progress:
            return {"status": "error", "message": "Login already in progress"}

        try:
            self._login_in_progress = True

            # 获取账户信息
            from app.core.database import db
            from app.services.account_service import AccountService

            conn = await db.get_connection()
            account_service = AccountService(conn)
            account = await account_service.get_by_id(account_id)

            if not account:
                self._login_in_progress = False
                return {"status": "error", "message": f"Account {account_id} not found"}

            # 检查账户类型
            account_type = getattr(account, "account_type", "seeker")

            # 启动浏览器
            browser = self.browser_manager.start_browser()

            # 根据账户类型选择登录模块
            if account_type == "hr":
                login_url = "https://login.zhipin.com/?ka=header-boss-login"
            else:
                login_url = "https://login.zhipin.com/"

            browser.get(login_url)
            logger.info(f"Navigated to {login_url} for account {account_id}")

            # 记录登录尝试
            await self._log_login_attempt(
                account.username, success=False, failure_reason=f"Login started for account {account_id}"
            )

            return {
                "status": "browser_opened",
                "message": "Browser opened, waiting for user to login",
                "account_id": account_id,
            }

        except Exception as e:
            logger.error(f"Failed to start login for account {account_id}: {e}")
            self._login_in_progress = False
            await self._log_login_attempt(None, success=False, failure_reason=str(e))

            return {"status": "error", "message": f"Failed to start login: {str(e)}"}

    async def monitor_login_for_account(self, account_id: int) -> dict[str, Any]:
        """
        Monitor login process for a specific account

        Args:
            account_id: 账户ID

        Returns:
            dict with login status
        """
        try:
            browser = self.browser_manager.get_browser()

            if not browser:
                return {"status": "error", "message": "Browser not running"}

            # 轮询 URL 检测登录成功
            max_attempts = 150  # 5分钟，2秒间隔
            for attempt in range(max_attempts):
                if not self.browser_manager.is_browser_running():
                    return {"status": "cancelled", "message": "Browser was closed"}

                current_url = browser.url

                # 检查 URL 变化（登录成功）
                if "login.zhipin.com" not in current_url:
                    logger.info(f"Login successful for account {account_id}, redirected to {current_url}")
                    return await self._handle_login_success_for_account(browser, account_id)

                # 等待下次检查
                await asyncio.sleep(2)

            # 超时
            logger.warning(f"Login timeout for account {account_id} after 5 minutes")
            self.browser_manager.close_browser()
            self._login_in_progress = False

            return {"status": "timeout", "message": "Login timeout (5 minutes)", "account_id": account_id}

        except Exception as e:
            logger.error(f"Error monitoring login for account {account_id}: {e}")
            self._login_in_progress = False
            return {"status": "error", "message": f"Error monitoring login: {str(e)}"}

    async def _handle_login_success_for_account(self, browser, account_id: int) -> dict[str, Any]:
        """
        处理账户登录成功

        Args:
            browser: 浏览器对象
            account_id: 账户ID

        Returns:
            登录结果
        """
        try:
            # 提取 cookies
            cookies = self.extract_cookies(browser)

            # 提取用户信息
            user_info = self.extract_user_info(browser)

            # 保存会话到指定账户
            await self.session_manager.save_session_for_account(account_id, cookies, user_info)

            # 更新账户状态
            from app.core.database import db
            from app.services.account_service import AccountService

            conn = await db.get_connection()
            account_service = AccountService(conn)
            await account_service.update_cookie_status(account_id, "valid")

            # 记录成功登录
            username = user_info.get("username") if user_info else "Unknown"
            await self._log_login_attempt(username, success=True)

            # 保持浏览器打开，方便用户继续操作
            self._login_in_progress = False

            logger.info(f"Login successful for account {account_id}, browser kept open")
            return {
                "status": "success",
                "message": "Login successful",
                "user_info": user_info,
                "account_id": account_id,
            }

        except Exception as e:
            logger.error(f"Error handling login success for account {account_id}: {e}")
            self._login_in_progress = False
            return {"status": "error", "message": f"Error saving session: {str(e)}"}

    async def get_active_account_status(self) -> dict[str, Any]:
        """
        获取活跃账户的状态

        Returns:
            dict with status information
        """
        try:
            active_account_id = await self.session_manager.get_active_account_id()

            if not active_account_id:
                return {
                    "is_logged_in": False,
                    "active_account_id": None,
                    "user_info": None,
                    "timestamp": datetime.now().isoformat(),
                }

            # 加载活跃账户的会话
            session = await self.session_manager.load_session_for_account(active_account_id)

            return {
                "is_logged_in": session is not None,
                "active_account_id": active_account_id,
                "user_info": session.get("user_info") if session else None,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get active account status: {e}")
            return {
                "is_logged_in": False,
                "active_account_id": None,
                "user_info": None,
                "timestamp": datetime.now().isoformat(),
            }

    @staticmethod
    def get_now_iso() -> str:
        """获取当前时间的 ISO 格式字符串"""
        return datetime.now().isoformat()

    async def restore_browser_session_for_account(self, account_id: int) -> dict[str, Any]:
        """
        为指定账号恢复浏览器会话

        Args:
            account_id: 账户ID

        Returns:
            dict: 恢复结果
        """
        try:
            # 1. 验证账号存在
            from app.core.database import db
            from app.services.account_service import AccountService

            conn = await db.get_connection()
            account_service = AccountService(conn)
            account = await account_service.get_by_id(account_id)

            if not account:
                return {
                    "status": "error",
                    "message": f"Account {account_id} not found",
                    "browser_opened": False
                }

            # 2. 加载该账号的session
            session = await self.session_manager.load_session_for_account(account_id)

            if not session or not session.get("cookies"):
                return {
                    "status": "error",
                    "message": f"No valid session found for account {account_id}",
                    "browser_opened": False
                }

            # 3. 检查浏览器是否已运行
            if self.browser_manager.is_browser_running():
                # 如果浏览器已运行，先关闭
                logger.info(f"Closing existing browser before restoring for account {account_id}")
                self.browser_manager.close_browser()
                await asyncio.sleep(1)  # 等待浏览器完全关闭

            # 4. 启动浏览器
            browser = self.browser_manager.start_browser()

            # 5. 注入反检测脚本
            from rpa.modules.anti_detection import AntiDetection
            AntiDetection.inject_anti_detection_scripts(browser)

            # 6. 注入cookies (DrissionPage 4.x 使用 browser.cookies() 批量设置)
            cookies = session["cookies"]
            try:
                browser.cookies(cookies)
                logger.info(f"Cookies injected for account {account_id}")
            except Exception as e:
                logger.warning(f"Failed to inject some cookies: {e}")

            # 7. 导航到BOSS首页
            browser.get("https://www.zhipin.com")
            await asyncio.sleep(2)

            # 8. 设置该账号为活跃账号
            await self.session_manager.set_active_account(account_id)

            # 9. 更新最后使用时间
            await account_service.update_last_operation(account_id)

            logger.info(f"Browser session restored for account {account_id}")

            return {
                "status": "success",
                "message": f"Browser session restored for account {account_id}",
                "browser_opened": True,
                "account_id": account_id,
                "user_info": session.get("user_info")
            }

        except Exception as e:
            logger.error(f"Failed to restore browser for account {account_id}: {e}")
            return {
                "status": "error",
                "message": str(e),
                "browser_opened": False
            }
