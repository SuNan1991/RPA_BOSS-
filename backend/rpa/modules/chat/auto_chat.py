"""
BOSS直聘自动聊天模块
"""

from typing import Any, Optional

from ...app.core.config import settings
from ...app.core.logging import get_logger
from ..core.base import BaseModule

logger = get_logger("auto_chat")


class AutoChatModule(BaseModule):
    """自动聊天模块"""

    def __init__(self):
        super().__init__()
        self.base_url = settings.BOSS_URL

    def execute(
        self,
        job_url: str,
        message: str,
        **kwargs,
    ) -> dict[str, Any]:
        """
        发送聊天消息

        Args:
            job_url: 职位链接或聊天链接
            message: 消息内容
            **kwargs: 其他参数

        Returns:
            发送结果
        """
        try:
            if not self.browser.is_initialized:
                self.init_browser(**kwargs)

            page = self.browser.get_page()

            # 访问职位页面并打开聊天
            if not job_url.startswith("http"):
                job_url = self.base_url + job_url

            page.get(job_url, retry=2, timeout=15)
            self.wait(1)

            # 点击立即沟通按钮
            chat_button = page.ele("css:.btn-startchat", timeout=5)
            if chat_button:
                chat_button.click()
                self.wait(1)
            else:
                # 检查是否已经在聊天界面
                chat_input = page.ele("css:.chat-input", timeout=2)
                if not chat_input:
                    return {"success": False, "message": "未找到聊天入口"}

            # 输入消息
            result = self._send_message(page, message)

            if result:
                return {"success": True, "message": "消息发送成功"}
            else:
                return {"success": False, "message": "消息发送失败"}

        except Exception as e:
            self.logger.error(f"Failed to send chat message: {e}")
            self.save_screenshot()
            return {"success": False, "message": f"发送失败: {str(e)}"}

    def _send_message(self, page, message: str) -> bool:
        """
        发送消息

        Args:
            page: 浏览器页面对象
            message: 消息内容

        Returns:
            是否发送成功
        """
        try:
            # 查找输入框
            input_box = page.ele("css:.chat-input textarea", timeout=5)
            if not input_box:
                self.logger.warning("Chat input box not found")
                return False

            # 输入消息
            input_box.input(message)
            self.wait(0.5)

            # 点击发送按钮
            send_button = page.ele("css:.btn-send", timeout=5)
            if send_button:
                send_button.click()
                self.wait(1)
                self.logger.info(f"Message sent: {message}")
                return True
            else:
                # 尝试回车发送
                input_box.enter()
                self.wait(1)
                self.logger.info(f"Message sent via enter: {message}")
                return True

        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False

    def get_chat_history(self, chat_url: str, **kwargs) -> dict[str, Any]:
        """
        获取聊天记录

        Args:
            chat_url: 聊天链接
            **kwargs: 其他参数

        Returns:
            聊天记录
        """
        try:
            if not self.browser.is_initialized:
                self.init_browser(**kwargs)

            page = self.browser.get_page()

            # 访问聊天页面
            if not chat_url.startswith("http"):
                chat_url = self.base_url + chat_url

            page.get(chat_url, retry=2, timeout=15)
            self.wait(1)

            # 解析聊天记录
            messages = self._parse_chat_history(page)

            return {"success": True, "data": messages}

        except Exception as e:
            self.logger.error(f"Failed to get chat history: {e}")
            return {"success": False, "message": str(e)}

    def _parse_chat_history(self, page) -> list[dict[str, Any]]:
        """
        解析聊天记录

        Args:
            page: 浏览器页面对象

        Returns:
            消息列表
        """
        messages = []
        try:
            # 查找消息列表
            message_elements = page.eles("css:.chat-message", timeout=5)

            for msg_ele in message_elements:
                try:
                    # 判断消息方向（发送/接收）
                    is_sent = "sent" in msg_ele.attr("class")

                    # 消息内容
                    content_ele = msg_ele.ele("css:.message-content", timeout=1)
                    content = content_ele.text if content_ele else ""

                    # 时间
                    time_ele = msg_ele.ele("css:.message-time", timeout=1)
                    time_str = time_ele.text if time_ele else ""

                    messages.append(
                        {
                            "is_sent": is_sent,
                            "content": content,
                            "time": time_str,
                        }
                    )

                except Exception as e:
                    self.logger.warning(f"Error parsing message: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error parsing chat history: {e}")

        return messages

    def auto_greet(
        self, job_url: str, greet_template: Optional[str] = None, **kwargs
    ) -> dict[str, Any]:
        """
        自动打招呼

        Args:
            job_url: 职位链接
            greet_template: 打招呼模板
            **kwargs: 其他参数

        Returns:
            发送结果
        """
        # 默认打招呼语
        if not greet_template:
            greet_template = "您好，我对这个职位很感兴趣，希望能进一步了解"

        return self.execute(job_url, greet_template, **kwargs)

    def batch_send_messages(
        self,
        job_urls: list[str],
        message: str,
        delay: float = 2.0,
        **kwargs,
    ) -> dict[str, Any]:
        """
        批量发送消息

        Args:
            job_urls: 职位链接列表
            message: 消息内容
            delay: 发送间隔（秒）
            **kwargs: 其他参数

        Returns:
            发送结果统计
        """
        results = {"success": 0, "failed": 0, "total": len(job_urls)}

        for i, job_url in enumerate(job_urls):
            try:
                self.logger.info(f"Sending message {i + 1}/{len(job_urls)}")
                result = self.execute(job_url, message, **kwargs)

                if result.get("success"):
                    results["success"] += 1
                else:
                    results["failed"] += 1

                # 延迟
                if i < len(job_urls) - 1:
                    self.wait(delay)

            except Exception as e:
                self.logger.error(f"Failed to send message to {job_url}: {e}")
                results["failed"] += 1

        self.logger.info(f"Batch send completed: {results}")
        return {"success": True, "data": results}
