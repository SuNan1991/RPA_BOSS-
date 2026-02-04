"""
验证码处理模块 - 使用 ddddocr
"""
from typing import Optional, Tuple
from pathlib import Path
import ddddocr
from PIL import Image
import io
import base64

from ...app.core.logging import get_logger

logger = get_logger("captcha_handler")


class CaptchaHandler:
    """验证码处理器"""

    def __init__(self, captcha_type: str = "slide"):
        """
        初始化验证码处理器

        Args:
            captcha_type: 验证码类型 (slide: 滑块, click: 点选, general: 通用)
        """
        self.captcha_type = captcha_type
        self.detector = ddddocr.DdddOcr(det=False, ocr=False, slide=True)
        self.ocr = ddddocr.DdddOcr()
        self.logger = logger

    def识别滑块验证码(
        self, bg_image: bytes, slider_image: bytes
    ) -> Optional[Tuple[int, int]]:
        """
        识别滑块验证码

        Args:
            bg_image: 背景图片字节数据
            slider_image: 滑块图片字节数据

        Returns:
            (x, y) 滑块目标位置坐标，识别失败返回 None
        """
        try:
            # 使用 ddddocr 识别滑块位置
            result = self.detector.slide_match(slider_image, bg_image, simple_target=True)

            if result and len(result) >= 2:
                x, y = result[0], result[1]
                self.logger.info(f"Slide captcha recognized: x={x}, y={y}")
                return (x, y)
            else:
                self.logger.warning("Failed to recognize slide captcha")
                return None

        except Exception as e:
            self.logger.error(f"Error recognizing slide captcha: {e}")
            return None

    def recognize_text_captcha(self, image: bytes) -> Optional[str]:
        """
        识别文字验证码

        Args:
            image: 验证码图片字节数据

        Returns:
            识别的文字，识别失败返回 None
        """
        try:
            result = self.ocr.classification(image)
            self.logger.info(f"Text captcha recognized: {result}")
            return result

        except Exception as e:
            self.logger.error(f"Error recognizing text captcha: {e}")
            return None

    def save_captcha_image(self, image: bytes, file_path: str = None) -> str:
        """
        保存验证码图片

        Args:
            image: 图片字节数据
            file_path: 保存路径

        Returns:
            保存的文件路径
        """
        try:
            if not file_path:
                import time
                timestamp = int(time.time())
                file_path = Path(__file__).parent.parent.parent.parent / "logs" / f"captcha_{timestamp}.png"

            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存图片
            img = Image.open(io.BytesIO(image))
            img.save(str(file_path))

            self.logger.info(f"Captcha image saved to {file_path}")
            return str(file_path)

        except Exception as e:
            self.logger.error(f"Failed to save captcha image: {e}")
            return ""

    def base64_to_image(self, base64_str: str) -> Optional[bytes]:
        """
        Base64字符串转换为图片字节数据

        Args:
            base64_str: Base64编码的图片字符串

        Returns:
            图片字节数据
        """
        try:
            # 移除可能的前缀
            if "," in base64_str:
                base64_str = base64_str.split(",")[1]

            image_bytes = base64.b64decode(base64_str)
            return image_bytes

        except Exception as e:
            self.logger.error(f"Failed to decode base64 image: {e}")
            return None

    def image_to_base64(self, image: bytes) -> str:
        """
        图片字节数据转换为Base64字符串

        Args:
            image: 图片字节数据

        Returns:
            Base64编码的字符串
        """
        try:
            base64_str = base64.b64encode(image).decode('utf-8')
            return base64_str

        except Exception as e:
            self.logger.error(f"Failed to encode image to base64: {e}")
            return ""


class SlideTrackGenerator:
    """滑块轨迹生成器 - 模拟真人滑动行为"""

    @staticmethod
    def generate_track(distance: int, speed: int = 2) -> list:
        """
        生成滑块移动轨迹

        Args:
            distance: 滑动距离
            speed: 基础速度

        Returns:
            轨迹列表 [(x, y, time), ...]
        """
        import random
        import time

        track = []
        current_x = 0
        current_y = 0
        start_time = time.time() * 1000

        # 加速阶段
        while current_x < distance * 0.7:
            step = random.randint(speed, speed + 3)
            current_x += step
            # 添加微小的y轴抖动
            current_y = random.randint(-1, 1)
            current_time = time.time() * 1000 - start_time
            track.append([current_x, current_y, current_time])

        # 减速阶段
        while current_x < distance:
            step = random.randint(1, speed)
            current_x += step
            current_y = random.randint(-1, 1)
            current_time = time.time() * 1000 - start_time
            track.append([current_x, current_y, current_time])

        return track

    @staticmethod
    def generate_curve_track(distance: int) -> list:
        """
        生成曲线轨迹 (更模拟真人)

        Args:
            distance: 滑动距离

        Returns:
            轨迹列表
        """
        import math
        import random
        import time

        track = []
        current_x = 0
        start_time = time.time() * 1000

        # 使用正弦函数模拟曲线
        for i in range(int(distance)):
            progress = i / distance

            # x轴: 加速后减速
            if progress < 0.5:
                step = 2 + progress * 4  # 加速
            else:
                step = 4 - (progress - 0.5) * 4  # 减速

            current_x += step

            # y轴: 正弦波动
            current_y = int(math.sin(progress * math.pi * 2) * 3 + random.uniform(-1, 1))

            current_time = time.time() * 1000 - start_time
            track.append([int(current_x), current_y, current_time])

        return track
