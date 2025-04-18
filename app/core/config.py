# 配置管理
from pydantic_settings import BaseSettings
import logging

class Settings(BaseSettings):
    # 鉴权配置
    SECRET_KEY: str = "Huatai@20230208"
    ALGORITHM: str = "HS256"
    PLATFORM_ID: str = "platform-identifier" # 平台标识（按部署环境变化）
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    
    # 视频处理配置
    MAX_STREAMS_PER_NODE: int = 100
    MODEL_PATH: str = "models/yolov8/best.onnx"
    
    # 集群配置
    REDIS_URL: str = "redis://localhost"
    
    TARGET_FPS: int = 10  # 目标处理帧率
    STREAM_TIMEOUT: int = 30  # 流超时时间(秒)

    CONFIDENCE_THRESHOLD: float = 0.5  # 置信度阈值
    USE_CUDA: bool = True  # 是否启用CUDA加速

    # 新增API配置
    MAX_STREAMS_PER_TASK: int = 50
    WS_MAX_CONNECTIONS: int = 1000

    # 任务调度配置
    MAX_WORKERS: int = 50
    TASK_QUEUE_TIMEOUT: int = 60

    # ... 其他配置 ...
    MODEL_PATH = "yolov8n.pt"
    DETECTION_THRESHOLD = 5  # 连续检测阈值
    CONF_THRESHOLD = 0.5  # 置信度阈值
    CLASS_DICT = {
        "0": "fire",
        "1": "smoke",
    } # 类别列表

    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "machine_vision"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='./run.log',
        filemode='a',
        encoding='utf-8'
    )

    class Config:
        env_file = ".env"
    
settings = Settings()