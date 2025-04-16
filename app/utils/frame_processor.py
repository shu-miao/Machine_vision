'''
视频处理优化
'''


# 视频帧处理示例（支持硬件加速）
async def process_frame(frame: bytes):
    # 使用OpenCV DNN模块优化
    net = cv2.dnn.readNetFromONNX("models/yolov8/best.onnx")
    blob = cv2.dnn.blobFromImage(frame, scalefactor=1 / 255.0)

    # 使用CUDA加速推理
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

    # 异步批处理
    detections = await run_in_threadpool(net.forward)
    return parse_detections(detections)
