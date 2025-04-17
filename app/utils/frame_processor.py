# 帧处理优化
import cv2
import numpy as np
from typing import List, Dict
from app.core.config import settings

# 加载模型（单例模式）
net = cv2.dnn.readNetFromONNX(settings.MODEL_PATH)
if settings.USE_CUDA:
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

def preprocess(frame: np.ndarray) -> np.ndarray:
    """帧预处理"""
    blob = cv2.dnn.blobFromImage(
        frame, 
        scalefactor=1/255.0, 
        size=(640, 640),  # YOLOv8默认输入尺寸
        mean=[0, 0, 0], 
        swapRB=True, 
        crop=False
    )
    return blob

def postprocess(outputs: np.ndarray, frame_shape: tuple) -> List[Dict]:
    """后处理检测结果"""
    # outputs形状: [1, 84, 8400] (YOLOv8输出格式)
    results = []
    for detection in outputs[0].T:
        scores = detection[4:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]
        
        if confidence > settings.CONFIDENCE_THRESHOLD:
            # 解算边界框坐标 (cx, cy, w, h)
            x, y, w, h = detection[0:4] * np.array([
                frame_shape[1], frame_shape[0], 
                frame_shape[1], frame_shape[0]
            ])
            results.append({
                "class_id": int(class_id),
                "confidence": float(confidence),
                "bbox": [int(x-w/2), int(y-h/2), int(w), int(h)]
            })
    return results

async def process_frame(frame: np.ndarray) -> List[Dict]:
    """处理单帧图像"""
    try:
        # 预处理
        blob = preprocess(frame)
        
        # 推理
        net.setInput(blob)
        outputs = net.forward()
        
        # 后处理
        return postprocess(outputs, frame.shape)
    
    except Exception as e:
        print(f"帧处理失败: {str(e)}")
        return []