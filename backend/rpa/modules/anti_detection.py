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
    def get_js_injection_code() -> str:
        """
        生成反检测 JavaScript 注入代码
        在页面加载前执行，隐藏自动化特征

        Returns:
            str: JavaScript 代码字符串
        """
        return """
        // 1. 修复 navigator.webdriver (最关键 - 检测自动化特征)
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
            configurable: true
        });

        // 2. 注入 window.chrome 对象 (真实Chrome必有此对象)
        if (!window.chrome) {
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {},
                webstore: true
            };
        }

        // 3. 模拟真实插件列表
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                { name: 'Chrome PDF Plugin', description: 'Portable Document Format', filename: 'internal-pdf-viewer' },
                { name: 'Chrome PDF Viewer', description: '', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                { name: 'Native Client', description: '', filename: 'internal-nacl-plugin' }
            ],
            configurable: true
        });

        // 4. 修复权限查询 (避免检测到异常的权限API)
        const originalQuery = window.navigator.permissions.query.bind(window.navigator.permissions);
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );

        // 5. 设置语言列表
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en-US', 'en'],
            configurable: true
        });

        // 6. 修复平台信息
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32',
            configurable: true
        });

        // 7. 添加硬件并发数
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8,
            configurable: true
        });

        // 8. 添加设备内存
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8,
            configurable: true
        });

        // 9. 修复 navigator.userAgent (确保是Chrome)
        // 注意：这个通常在启动参数中设置，这里作为备份
        """
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
        Get browser configuration with enhanced anti-detection settings

        Returns:
            ChromiumOptions: Configuration for DrissionPage browser
        """
        try:
            from DrissionPage import ChromiumOptions

            options = ChromiumOptions()

            # === 现有反检测措施 ===
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

            # === 新增增强措施 ===
            # 禁用更多自动化检测特征
            options.set_argument("--disable-features=IsolateOrigins,site-per-process")
            options.set_argument("--disable-site-isolation-trials")
            options.set_argument("--disable-ipc-flooding-protection")
            options.set_argument("--disable-renderer-backgrounding")
            options.set_argument("--disable-backgrounding-occluded-windows")

            # 语言和时区设置
            options.set_argument("--lang=zh-CN")
            options.set_argument("--timezone=Asia/Shanghai")

            # 窗口设置 (避免检测到默认窗口位置)
            options.set_argument("--window-size=1920,1080")
            options.set_argument("--window-position=100,100")
            options.set_argument("--start-maximized")

            # 禁用密码保存提示
            options.set_pref("credentials_enable_service", False)
            options.set_pref("profile.password_manager_enabled", False)

            # 必须显示浏览器 (无头模式容易被检测)
            # Don't set headless, default is to show browser

            logger.info("Enhanced anti-detection configuration applied")
            return options

        except Exception as e:
            logger.error(f"Failed to create anti-detection config: {e}", exc_info=True)
            # Return basic config if anti-detection fails
            try:
                from DrissionPage import ChromiumOptions

                options = ChromiumOptions()
                logger.info("Using basic ChromiumOptions without anti-detection")
                return options
            except Exception as e2:
                logger.error(f"Failed to import ChromiumOptions: {e2}", exc_info=True)
                # Return empty dict instead of None
                # DrissionPage can handle empty dict as default config
                return {}

    @staticmethod
    def inject_anti_detection_scripts(page) -> bool:
        """
        向页面注入反检测脚本
        在导航到目标页面后调用

        Args:
            page: ChromiumPage 实例

        Returns:
            bool: 是否注入成功
        """
        try:
            js_code = AntiDetection.get_js_injection_code()
            page.run_js(js_code)
            logger.info("Anti-detection scripts injected successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to inject anti-detection scripts: {e}")
            return False

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
