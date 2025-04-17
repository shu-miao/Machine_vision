# 视频流消费
import cv2
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from .result_writer import batch_save
from app.utils.frame_processor import process_frame
from app.core.config import settings

class VideoStreamConsumer:
    def __init__(self, stream_url: str, platform_id: str):
        self.stream_url = stream_url
        self.platform_id = platform_id
        self.max_retries = 3
        self.batch_size = 32  # 批量处理帧数
        self.frame_buffer = []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _connect_stream(self):
        """带重试的视频流连接"""
        cap = cv2.VideoCapture(self.stream_url)
        if not cap.isOpened():
            raise ConnectionError(f"无法连接视频流: {self.stream_url}")
        return cap

    async def consume(self):
        """主消费循环"""
        cap = self._connect_stream()
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = max(1, int(fps / settings.TARGET_FPS))  # 控制处理频率

        frame_count = 0
        while True:
            try:
                ret, frame = cap.read()
                if not ret:
                    if not self._reconnect():
                        break
                    continue

                frame_count += 1
                if frame_count % frame_interval != 0:
                    continue

                # 异步处理帧并批量保存
                results = await process_frame(frame)
                self.frame_buffer.extend(results)
                
                if len(self.frame_buffer) >= self.batch_size:
                    await batch_save(self.platform_id, self.frame_buffer)
                    self.frame_buffer.clear()

            except Exception as e:
                print(f"视频流处理异常: {str(e)}")
                if not self._reconnect():
                    break

        # 保存剩余结果
        if self.frame_buffer:
            await batch_save(self.platform_id, self.frame_buffer)
        cap.release()

    def _reconnect(self) -> bool:
        """断流重连机制"""
        for _ in range(self.max_retries):
            time.sleep(5)
            try:
                new_cap = self._connect_stream()
                return True
            except Exception:
                continue
        return False