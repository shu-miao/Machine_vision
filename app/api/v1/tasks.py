# 提供任务管理的API端点
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from app.core.security import get_current_user
from app.services.detection import dispatch_task
from app.utils.cluster import NodeRegistry
from fastapi import HTTPException

router = APIRouter()

class TaskRequest(BaseModel):
    stream_urls: list[str]
    priority: int = 1

@router.post("/tasks")
async def create_task(
    request: TaskRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """创建视频分析任务"""
    # 检查集群节点状态
    node_registry = NodeRegistry.get_instance()
    if not node_registry.nodes:
        raise HTTPException(status_code=503, detail="无可用工作节点")
    
    # 分发任务到后台
    background_tasks.add_task(
        dispatch_task,
        request.stream_urls
    )
    
    return {
        "task_id": f"task_{hash(tuple(request.stream_urls))}",
        "stream_count": len(request.stream_urls),
        "assigned_nodes": list(node_registry.nodes)
    }

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    # 实现查询任务队列状态
    return {
        "task_id": task_id,
        "status": "running",
        "processed": 0,
        "total": 100
    }