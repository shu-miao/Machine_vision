# 配置管理
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 鉴权配置
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    PLATFORM_ID: str = "platform-identifier"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    
    # ... 其他现有配置 ...
    # 视频处理配置
    MAX_STREAMS_PER_NODE: int = 100
    MODEL_PATH: str = "models/yolov8/best.onnx"
    
    # 集群配置
    REDIS_URL: str = "redis://localhost"
    
    TARGET_FPS: int = 10  # 目标处理帧率
    STREAM_TIMEOUT: int = 30  # 流超时时间(秒)

    CONFIDENCE_THRESHOLD: float = 0.5  # 置信度阈值
    USE_CUDA: bool = True  # 是否启用CUDA加速

    class Config:
        env_file = ".env"
    
settings = Settings()