"""
Anti-Detection Module - Configure browser to avoid bot detection
"""

from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from DrissionPage import ChromiumPage

logger = logging.getLogger(__name__)


class AntiDetection:
    """Anti-detection browser configuration"""

    # Real user agents from Chrome on different OS
    USER_AGENTS = [
        # Windows Chrome
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        # Mac Chrome
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    ]

    @staticmethod
    def get_config():
        """
        Get browser configuration with anti-detection settings

        Returns:
            ChromiumOptions: Configuration for DrissionPage browser
        """
        try:
            from DrissionPage import ChromiumOptions

            options = ChromiumOptions()

            # Set random user agent
            user_agent = random.choice(AntiDetection.USER_AGENTS)
            options.set_user_agent(user_agent=user_agent)

            # Disable automation flags
            options.set_argument("--disable-blink-features=AutomationControlled")
            options.remove_argument("--enable-automation")
            options.set_argument("--disable-infobars")
            options.set_argument("--disable-extensions")
            options.set_argument("--no-first-run")
            options.set_argument("--disable-default-apps")
            options.set_argument("--disable-sync")

            # Set realistic window size
            options.set_argument("--window-size=1920,1080")
            options.set_argument("--start-maximized")

            # Set preferences to hide automation
            options.set_pref("credentials_enable_service", False)
            options.set_pref("profile.password_manager_enabled", False)

            # Disable headless mode (must show browser)
            # Don't set headless, default is to show browser

            logger.info("Anti-detection configuration applied")
            return options

        except Exception as e:
            logger.error(f"Failed to create anti-detection config: {e}")
            # Return basic config if anti-detection fails
            try:
                from DrissionPage import ChromiumOptions

                return ChromiumOptions()
            except Exception:
                # If even importing fails, return None
                return None

    @staticmethod
    def verify_detection(page: ChromiumPage) -> dict:
        """
        Verify if anti-detection is working

        Args:
            page: ChromiumPage instance to check

        Returns:
            dict: Verification results
        """
        try:
            results = {}

            # Check navigator.webdriver
            webdriver_value = page.run_js("return navigator.webdriver")
            results["navigator.webdriver"] = webdriver_value
            results["webdriver_hidden"] = webdriver_value is None or webdriver_value is False

            # Check plugins
            plugins = page.run_js("return navigator.plugins.length")
            results["plugins_count"] = plugins
            results["has_plugins"] = plugins > 0

            # Check user agent
            user_agent = page.run_js("return navigator.userAgent")
            results["user_agent"] = user_agent
            results["has_chrome_ua"] = "Chrome" in user_agent

            # Overall detection risk
            results["detection_risk"] = (
                "low"
                if all(
                    [results["webdriver_hidden"], results["has_plugins"], results["has_chrome_ua"]]
                )
                else "high"
            )

            logger.info(f"Anti-detection verification: {results}")
            return results

        except Exception as e:
            logger.error(f"Failed to verify anti-detection: {e}")
            return {"error": str(e), "detection_risk": "unknown"}
