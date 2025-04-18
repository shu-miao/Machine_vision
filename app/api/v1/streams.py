# 视频流处理
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi import Depends
from app.core.security import get_current_user
from app.services.video_consumer import VideoStreamConsumer
from app.utils.cluster import NodeRegistry
import asyncio

router = APIRouter()

@router.websocket("/ws/{stream_url}")
async def video_stream_ws(
    websocket: WebSocket,
    stream_url: str,
    current_user: dict = Depends(get_current_user)
):
    """WebSocket视频流处理端点"""
    await websocket.accept()
    node_registry = NodeRegistry.get_instance()
    consumer = VideoStreamConsumer(stream_url, current_user['platform_id'])
    
    try:
        # 注册节点到集群
        node_registry.register_node(f"stream_{stream_url}")
        
        # 启动消费循环
        while True:
            results = await consumer.consume()
            await websocket.send_json({
                "status": "processing",
                "results": results[:10]  # 示例：只返回前10个结果
            })
            await asyncio.sleep(0.1)  # 控制推送频率
            
    except WebSocketDisconnect:
        print(f"客户端断开连接: {stream_url}")
    except Exception as e:
        await websocket.send_json({
            "status": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()