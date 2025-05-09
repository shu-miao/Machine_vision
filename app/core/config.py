# 配置管理
from pydantic_settings import BaseSettings
import logging
from typing import ClassVar, Dict, Any

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=r'D:\PyCharm\pycharm_project\Machine_vision\test\run.log',
        filemode='a',
        encoding='utf-8'
    )

class Settings(BaseSettings):
    # 鉴权配置
    SECRET_KEY: str = "Huatai@20230208"
    ALGORITHM: str = "HS256"
    PLATFORM_ID: str = "platform-identifier" # 平台标识（按部署环境变化）
    RESOURCE_ID : str = "ht-user"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    LOGGING_CONFIG: ClassVar[Dict[str, Any]] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": r'D:\PyCharm\pycharm_project\Machine_vision\test\run.log',
                "formatter": "default",
                "mode": "a",
                "encoding": "utf-8"
            }
        },
        "root": {
            "handlers": ["file"],
            "level": "INFO",
        },
    }

    # 集群配置
    REDIS_URL: str = "redis://127.0.0.1:6379"

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

    # 视觉检测配置
    MODEL_PATH: str = "yolov12n.pt"
    DETECTION_THRESHOLD: int = 5  # 连续检测阈值
    CONF_THRESHOLD: float = 0.5  # 置信度阈值
    CLASS_DICT: dict = {
        "0": "fire",
        "1": "smoke",
    } # 类别列表

    # 192.168.1.31  账号:postgres 密码:htzy@2017  库:ht_fmdata
    # 数据库配置
    DB_HOST: str = "192.168.1.31"
    DB_PORT: int = 5432
    DB_NAME: str = "ht_fmdata"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "htzy@2017"
    DEBUG: bool = True


    _reload_flag: bool = False

    class Config:
        env_file = ".env"
    
    def get_updated_config(self):
        if self._reload_flag:
            self.__init__()
            self._reload_flag = False

settings = Settings()

def watch_config_changes():
    # 实现环境变量监听逻辑
    pass