# 帧处理优化
import cv2
import numpy as np
from typing import List, Dict
from ultralytics import YOLO
from app.core.config import settings
import logging


class FrameProcessor:
    _instance = None

    def __init__(self):
        self.model = YOLO(settings.MODEL_PATH)
        if settings.USE_CUDA:
            self.model.to('cuda')

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def process_frame(self, frame: np.ndarray) -> List[Dict]:
        """处理单帧图像并返回检测结果"""
        try:
            results = self.model.track(
                frame,
                verbose=False,
                conf=settings.CONFIDENCE_THRESHOLD,
                device='cuda' if settings.USE_CUDA else 'cpu'
            )

            detections = []
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    detections.append({
                        "class_id": int(box.cls),
                        "class_name": settings.CLASS_DICT.get(str(box.cls.item()), "unknown"),
                        "confidence": float(box.conf),
                        "bbox": [x1, y1, x2 - x1, y2 - y1],  # x,y,w,h格式
                        "track_id": int(box.id) if box.id is not None else None
                    })
            return detections

        except Exception as e:
            logging.error(f"帧处理失败: {e}")
            return []