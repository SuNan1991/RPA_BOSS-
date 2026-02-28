"""
BOSS直聘批量打招呼模块
"""

import random
from typing import Any, Optional

from app.core.config import settings
from app.core.logging import get_logger
from rpa.core.base import BaseModule

logger = get_logger("batch_greet")


class BatchGreetModule(BaseModule):
    """批量打招呼模块"""

    # 默认打招呼模板
    DEFAULT_TEMPLATES = [
        "您好，看了您的简历觉得很匹配，方便沟通一下吗？",
        "您好，我们这边有合适的职位，了解一下？",
        "您好，看到您的经验很丰富，想和您聊聊",
        "您好，看了您的背景很不错，期待与您进一步交流",
    ]

    # 可配置频率限制（默认安全值）
    DEFAULT_RATE_LIMIT = {
        "max_per_hour": 30,  # 每小时最多30次
        "min_delay": 3,  # 最小延迟3秒
        "max_delay": 8,  # 最大延迟8秒
    }

    def __init__(self):
        super().__init__()
        self.base_url = settings.BOSS_URL
        self.greeted_count = 0
        self.failed_count = 0

    def execute(
        self,
        candidate_ids: list[int],
        candidates_data: list[dict],
        template: Optional[str] = None,
        rate_limit: Optional[dict] = None,
        hr_account_id: Optional[int] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        批量打招呼

        Args:
            candidate_ids: 候选人ID列表
            candidates_data: 候选人数据列表 (包含 profile_url 等)
            template: 打招呼模板（为空则随机选择）
            rate_limit: 频率限制配置
            hr_account_id: HR账户ID
            **kwargs: 其他参数

        Returns:
            执行结果
        """
        try:
            # 确保浏览器已初始化
            if not self.browser.is_initialized:
                self.init_browser(**kwargs)

            # 使用提供的配置或默认配置
            config = rate_limit or self.DEFAULT_RATE_LIMIT
            min_delay = config.get("min_delay", self.DEFAULT_RATE_LIMIT["min_delay"])
            max_delay = config.get("max_delay", self.DEFAULT_RATE_LIMIT["max_delay"])

            page = self.browser.get_page()
            results = {
                "success": 0,
                "failed": 0,
                "total": len(candidate_ids),
                "details": [],
            }

            # 选择模板
            greet_template = template or random.choice(self.DEFAULT_TEMPLATES)

            self.logger.info(f"Starting batch greet for {len(candidate_ids)} candidates")
            self.logger.info(f"Template: {greet_template}")
            self.logger.info(f"Rate limit: min_delay={min_delay}s, max_delay={max_delay}s")

            for i, candidate_id in enumerate(candidate_ids):
                try:
                    # 获取候选人数据
                    candidate_data = None
                    for cand in candidates_data:
                        if cand.get("id") == candidate_id or cand.get("profile_url"):
                            candidate_data = cand
                            break

                    if not candidate_data:
                        self.logger.warning(f"Candidate {candidate_id} data not found")
                        results["failed"] += 1
                        results["details"].append(
                            {"candidate_id": candidate_id, "success": False, "error": "Data not found"}
                        )
                        continue

                    # 频率限制检查
                    if not self._check_rate_limit(config):
                        wait_time = self._get_wait_time(config)
                        self.logger.warning(f"Rate limit reached, waiting {wait_time}s")
                        self.wait(wait_time)

                    # 随机延迟
                    delay = random.uniform(min_delay, max_delay)
                    self.logger.debug(f"Waiting {delay:.2f}s before greeting candidate {candidate_id}")
                    self.wait(delay)

                    # 执行打招呼
                    greet_result = self._greet_candidate(page, candidate_data, greet_template)

                    if greet_result["success"]:
                        results["success"] += 1
                        self.greeted_count += 1
                        self.logger.info(f"Successfully greeted candidate {candidate_id}")
                    else:
                        results["failed"] += 1
                        self.failed_count += 1
                        self.logger.warning(f"Failed to greet candidate {candidate_id}: {greet_result['error']}")

                    results["details"].append(
                        {
                            "candidate_id": candidate_id,
                            "success": greet_result["success"],
                            "error": greet_result.get("error"),
                        }
                    )

                    # 更新频率限制记录
                    self._record_operation(config)

                except Exception as e:
                    self.logger.error(f"Error greeting candidate {candidate_id}: {e}")
                    results["failed"] += 1
                    results["details"].append(
                        {"candidate_id": candidate_id, "success": False, "error": str(e)}
                    )

            self.logger.info(
                f"Batch greet completed: {results['success']} succeeded, {results['failed']} failed"
            )

            return {
                "success": True,
                "data": results,
                "message": f"批量打招呼完成: 成功{results['success']}个, 失败{results['failed']}个",
                "hr_account_id": hr_account_id,
            }

        except Exception as e:
            self.logger.error(f"Batch greet failed: {e}")
            self.save_screenshot()
            return {
                "success": False,
                "data": {},
                "message": f"批量打招呼失败: {str(e)}",
                "hr_account_id": hr_account_id,
            }

    def _greet_candidate(self, page, candidate_data: dict, template: str) -> dict[str, Any]:
        """
        向单个候选人打招呼

        Args:
            page: 浏览器页面对象
            candidate_data: 候选人数据
            template: 打招呼模板

        Returns:
            打招呼结果
        """
        try:
            profile_url = candidate_data.get("profile_url", "")
            if not profile_url:
                return {"success": False, "error": "No profile URL"}

            # 访问候选人主页
            if not profile_url.startswith("http"):
                profile_url = self.base_url + profile_url

            page.get(profile_url, retry=2, timeout=15)
            self.wait(1)

            # 查找打招呼按钮
            # 可能的选择器
            greet_button_selectors = [
                "css:.btn-greet",
                "css:.btn-startchat",
                "css:.greet-btn",
                "css:button:contains('立即沟通')",
                "css:button:contains('打招呼')",
            ]

            greet_button = None
            for selector in greet_button_selectors:
                try:
                    greet_button = page.ele(selector, timeout=2)
                    if greet_button:
                        break
                except Exception:
                    continue

            if not greet_button:
                return {"success": False, "error": "Greet button not found"}

            # 点击打招呼按钮
            greet_button.click()
            self.wait(1)

            # 如果弹出对话框，输入消息
            message_input = page.ele("css:.chat-input, textarea, .message-input", timeout=2)
            if message_input:
                message_input.input(template)
                self.wait(0.5)

                # 查找发送按钮
                send_button = page.ele("css:.btn-send, .send-btn, button:contains('发送')", timeout=2)
                if send_button:
                    send_button.click()
                    self.wait(1)

            return {"success": True}

        except Exception as e:
            self.logger.error(f"Error greeting candidate: {e}")
            return {"success": False, "error": str(e)}

    def _check_rate_limit(self, config: dict) -> bool:
        """
        检查是否超过频率限制

        Args:
            config: 频率限制配置

        Returns:
            是否可以继续操作
        """
        max_per_hour = config.get("max_per_hour", self.DEFAULT_RATE_LIMIT["max_per_hour"])

        # 简单实现：检查当前小时内的操作次数
        from datetime import datetime, timedelta

        now = datetime.now()
        if not hasattr(self, "_operation_history"):
            self._operation_history = []

        # 清理超过1小时的记录
        cutoff = now - timedelta(hours=1)
        self._operation_history = [t for t in self._operation_history if t > cutoff]

        return len(self._operation_history) < max_per_hour

    def _record_operation(self, config: dict):
        """
        记录操作时间

        Args:
            config: 频率限制配置
        """
        from datetime import datetime

        if not hasattr(self, "_operation_history"):
            self._operation_history = []

        self._operation_history.append(datetime.now())

    def _get_wait_time(self, config: dict) -> float:
        """
        获取需要等待的时间

        Args:
            config: 频率限制配置

        Returns:
            等待时间（秒）
        """
        max_per_hour = config.get("max_per_hour", self.DEFAULT_RATE_LIMIT["max_per_hour"])

        if not hasattr(self, "_operation_history"):
            return 60.0

        if len(self._operation_history) < max_per_hour:
            return 0.0

        # 计算最早的记录何时过期
        from datetime import datetime, timedelta

        now = datetime.now()
        cutoff = now - timedelta(hours=1)

        if self._operation_history and self._operation_history[0] > cutoff:
            # 需要等到最早的记录过期
            wait_until = self._operation_history[0] + timedelta(hours=1)
            wait_seconds = (wait_until - now).total_seconds()
            return max(0, wait_seconds)

        return 0.0

    def reset_counters(self):
        """重置计数器"""
        self.greeted_count = 0
        self.failed_count = 0
        self._operation_history = []
