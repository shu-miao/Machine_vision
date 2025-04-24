# 视频流消费
from collections import deque
import time
import cv2
import logging
from ultralytics import YOLO
import threading
from app.core.config import settings
import asyncio

class VideoStream:
    def __init__(self, src,max_retries=3):
        self.src = src
        self.stopped = False
        self.stream = cv2.VideoCapture(src)
        # if not self.stream.isOpened():
        #     logging.error(f"无法打开视频源: {self.src}")
        #     raise ValueError(f"无法打开视频源: {self.src}")
        for attempt in range(max_retries):
            self.stream = cv2.VideoCapture(src)
            if self.stream.isOpened():
                logging.info(f"成功打开视频源: {self.src}")
                break
            else:
                logging.error(f"无法打开视频源: {self.src}，尝试 {attempt + 1}/{max_retries} 次")
                time.sleep(1)  # 等待后重试
        else:
            raise ValueError(f"无法打开视频源: {self.src}，已达到最大重试次数")
        self.frame = None
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()

    def update(self):
        while not self.stopped:
            grabbed, frame = self.stream.read()
            if grabbed:
                self.frame = frame
            else:
                continue

    def read(self):
        return self.frame

    def stop(self):
        logging.info(f"停止取流: {self.src}")
        if not self.stopped:
            self.stopped = True
            if self.thread.is_alive():
                self.thread.join()  # 等待线程结束
            self.stream.release()  # 确保释放资源

class FrameBuffer:
    # 帧缓存池
    def __init__(self,max_duration=5,fps=30):
        self.frames = deque()
        self.max_duration = max_duration
        self.fps = fps
        self.max_frames = max_duration * fps
    def add_frame(self,frame):
        # 添加帧
        if len(self.frames) >= self.max_frames:
            try:
                self.frames.popleft()  # 移除最旧的帧
            except Exception as e:
                logging.info(f'移除旧帧失败，error: {e}')
            self.frames.append((time.time(), frame))  # 添加新帧
        else:
            self.frames.append((time.time(), frame))  # 添加新帧
    def get_frames(self):
        # 获取当前所有帧
        # current_time = time.time()
        return [frame for timestamp, frame in self.frames]
        # return [frame for timestamp,frame in self.frames if current_time - timestamp <= self.max_duration]
    def copy(self):
        # 复制缓存区
        new_buffer = FrameBuffer(self.max_duration,self.fps)
        # 共享帧队列
        new_buffer.frames = self.frames
        return new_buffer

class VideoStreamConsumer:
    def __init__(self, stream_url, platform_id):
        self.stream_url = stream_url
        self.platform_id = platform_id # 平台ID
        self.model = YOLO(settings.MODEL_PATH)
        self.stop_event = threading.Event()
        self.boxid_set = set()
        self.framebuffer = FrameBuffer(max_duration=30, fps=30)

    async def get_frames(self):
        cap = cv2.VideoCapture(self.stream_url)
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                yield cv2.imencode('.jpg', frame)[1]
                await asyncio.sleep(1 / 30)  # 控制帧率
        finally:
            cap.release()

    async def consume(self):
        try:
            video_stream = VideoStream(self.stream_url)
            consecutive_detections = 0

            while not self.stop_event.is_set():
                frame = video_stream.read()
                if frame is None:
                    continue

                results = self.model.track(frame, verbose=False, persist=True)
                detected = False

                for result in results:
                    boxes = result.boxes
                    if boxes:
                        detected = True
                        if consecutive_detections >= settings.DETECTION_THRESHOLD:
                            for box in boxes:
                                if box.conf.item() > settings.CONF_THRESHOLD:
                                    # 处理检测结果
                                    self._process_detection(box, frame)
                                    consecutive_detections = 0

                if detected:
                    consecutive_detections += 1
                else:
                    consecutive_detections = 0

                self.framebuffer.add_frame(frame)

        except Exception as e:
            logging.error(f"视频流处理错误: {e}")
        finally:
            video_stream.stop()
            self.boxid_set.clear()

    def _process_detection(self, box, frame):
        """处理检测结果并保存到数据库"""
        height, width, _ = frame.shape
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        class_str = settings.CLASS_DICT[str(box.cls.item())]

        if box.id is not None and box.id.item() not in self.boxid_set:
            self.boxid_set.add(box.id.item())
            # 这里添加保存到数据库的逻辑
            self._save_detection_result(
                class_str,
                box.conf.item(),
                (x1 + x2) * 0.5 / width,
                (y1 + y2) * 0.5 / height,
                frame
            )

    def _save_detection_result(self, class_name, confidence, x, y, frame):
        """保存检测结果到数据库"""
        # 实现数据库保存逻辑
        pass