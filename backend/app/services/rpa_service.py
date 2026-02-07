"""
RPA Service - Handle RPA login operations
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Any, Optional

# Add backend directory to path for rpa modules import
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

logger = logging.getLogger(__name__)


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

            # Start browser
            browser = self.browser_manager.start_browser()

            # Navigate to BOSS Zhipin login page
            login_url = "https://login.zhipin.com/"
            browser.get(login_url)

            logger.info(f"Navigated to {login_url}")

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

            # Save session
            await self.session_manager.save_session(cookies, user_info)

            # Log successful login
            username = user_info.get("username") if user_info else "Unknown"
            await self._log_login_attempt(username, success=True)

            # Close browser
            self.browser_manager.close_browser()
            self._login_in_progress = False

            return {"status": "success", "message": "Login successful", "user_info": user_info}

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
            cookies = browser.cookies(as_dict=True)

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

        Returns:
            dict with user info or None
        """
        try:
            # Try to get username from page
            # This will depend on the actual page structure
            user_info = {}

            # Attempt to find user name (selectors may vary)
            try:
                # Common selectors for user info on BOSS Zhipin
                selectors = [
                    ".user-name",
                    ".nav-user-name",
                    '[data-selector="user-name"]',
                    ".info-nav-user-name",
                ]

                for selector in selectors:
                    try:
                        element = browser.find(selector)
                        if element:
                            user_info["username"] = element.text
                            break
                    except Exception:
                        continue

            except Exception as e:
                logger.debug(f"Could not extract username: {e}")

            # Try to get avatar URL
            try:
                avatar_selectors = [
                    ".user-avatar img",
                    ".nav-user-pic img",
                    '[data-selector="user-avatar"] img',
                ]

                for selector in avatar_selectors:
                    try:
                        element = browser.find(selector)
                        if element:
                            user_info["avatar"] = element.attr("src")
                            break
                    except Exception:
                        continue

            except Exception as e:
                logger.debug(f"Could not extract avatar: {e}")

            logger.info(f"Extracted user info: {user_info}")
            return user_info if user_info else None

        except Exception as e:
            logger.error(f"Failed to extract user info: {e}")
            return None

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

            return {
                "is_logged_in": session is not None,
                "user_info": session.get("user_info") if session else None,
                "browser_status": browser_health.get("status"),
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
