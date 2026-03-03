"""
Browser Manager - Singleton pattern for managing browser instance
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from DrissionPage import ChromiumPage

# Use absolute import to avoid relative import issues
from rpa.modules.anti_detection import AntiDetection

logger = logging.getLogger(__name__)


class BrowserManager:
    """Singleton browser manager with anti-detection and timeout"""

    _instance: Optional["BrowserManager"] = None
    _browser: Optional[ChromiumPage] = None
    _start_time: Optional[datetime] = None
    _timeout_task: Optional[asyncio.Task] = None
    _timeout_seconds = 300  # 5 minutes

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def start_browser(self) -> ChromiumPage:
        """Start browser with anti-detection configuration"""
        try:
            # Close existing browser if any
            if self._browser is not None:
                self.close_browser()

            # Get anti-detection configuration
            co = AntiDetection.get_config()
            logger.info(f"Anti-detection config: {co}")

            if co is None:
                logger.warning("Anti-detection config returned None, using defaults")

            # Create browser instance with page
            logger.info("Creating ChromiumPage instance...")
            self._browser = ChromiumPage(addr_or_opts=co)
            self._start_time = datetime.now()

            # 立即注入反检测脚本
            AntiDetection.inject_anti_detection_scripts(self._browser)

            logger.info("Browser started successfully with anti-detection scripts")
            return self._browser

        except Exception as e:
            logger.error(f"Failed to start browser: {e}", exc_info=True)
            raise

    def close_browser(self) -> bool:
        """Close browser and cleanup resources"""
        try:
            if self._browser is not None:
                # Quit the browser
                self._browser.quit()
                self._browser = None
                self._start_time = None

                # Cancel timeout task if running
                if self._timeout_task and not self._timeout_task.done():
                    self._timeout_task.cancel()

                logger.info("Browser closed successfully")
                return True

            return False

        except Exception as e:
            logger.error(f"Error closing browser: {e}")
            self._browser = None
            return False

    def get_browser(self) -> Optional[ChromiumPage]:
        """Get current browser instance"""
        return self._browser

    def is_browser_running(self) -> bool:
        """Check if browser is running"""
        return self._browser is not None

    def get_elapsed_time(self) -> Optional[timedelta]:
        """Get time elapsed since browser started"""
        if self._start_time is None:
            return None
        return datetime.now() - self._start_time

    def is_timeout_exceeded(self) -> bool:
        """Check if timeout has been exceeded"""
        if self._start_time is None:
            return False
        elapsed = datetime.now() - self._start_time
        return elapsed.total_seconds() > self._timeout_seconds

    async def start_timeout_check(self):
        """Start timeout check task"""
        self._timeout_task = asyncio.create_task(self._timeout_check())

    async def _timeout_check(self):
        """Check for timeout and close browser if exceeded"""
        try:
            await asyncio.sleep(self._timeout_seconds)

            if self.is_timeout_exceeded():
                logger.warning("Browser timeout exceeded, closing browser")
                self.close_browser()

        except asyncio.CancelledError:
            logger.debug("Timeout check cancelled")

    async def health_check(self) -> dict:
        """Perform health check on browser instance"""
        if self._browser is None:
            return {"status": "not_running", "healthy": False}

        try:
            # Check if browser process is still alive
            elapsed = self.get_elapsed_time()
            return {
                "status": "running",
                "healthy": True,
                "elapsed_seconds": elapsed.total_seconds() if elapsed else 0,
                "timeout_remaining": max(0, self._timeout_seconds - elapsed.total_seconds())
                if elapsed
                else self._timeout_seconds,
            }

        except Exception as e:
            logger.error(f"Browser health check failed: {e}")
            return {"status": "error", "healthy": False, "error": str(e)}
