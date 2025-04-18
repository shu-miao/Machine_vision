# 数据模型
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class TaskCreate(BaseModel):
    """任务创建请求模型"""
    stream_urls: List[str]
    priority: int = 1
    platform_id: Optional[str] = None  # 关联平台ID

class TaskStatus(BaseModel):
    """任务状态响应模型"""
    task_id: str
    status: str  # running/completed/failed
    processed: int = 0
    total: int = 0
    assigned_nodes: List[str] = []

class DetectionResult(BaseModel):
    """检测结果模型"""
    task_id: str
    camera_id: str
    class_name: str
    confidence: float
    normalized_x: float  # 归一化坐标X
    normalized_y: float  # 归一化坐标Y
    timestamp: datetime = datetime.now()
    frame_data: Optional[bytes] = None  # 可选帧数据

class NodeStatus(BaseModel):
    """节点状态模型"""
    node_id: str
    active: bool
    current_load: int  # 当前负载
    max_capacity: int = 100  # 最大容量
    last_heartbeat: Optional[datetime] = None

class BatchResult(BaseModel):
    """批量结果响应模型"""
    success: bool
    results: List[DetectionResult]
    error: Optional[str] = None