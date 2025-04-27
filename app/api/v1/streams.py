# 视频流地址
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from app.core.security import get_current_user
from app.utils.cluster import NodeRegistry
from app.services.video_consumer import VideoStreamConsumer
from fastapi import HTTPException
import logging

router = APIRouter()


class StreamRequest(BaseModel):
    stream_url: str
    protocol: str = "rtsp"


@router.post("/streams")
async def create_stream(
        request: StreamRequest,
        # current_user: dict = Depends(get_current_user)
):
    """注册新的视频流"""
    node_registry = NodeRegistry.get_instance()

    if not await node_registry.nodes:
        raise HTTPException(status_code=503, detail="没有可用的工作节点")

    return {
        "stream_id": f"stream_{hash(request.stream_url)}",
        "assigned_node": node_registry.current_node,
        "protocol": request.protocol
    }


@router.websocket("/streams/{stream_id}/live")
async def stream_monitor(
        websocket: WebSocket,
        stream_id: str,
        current_user: dict = Depends(get_current_user)
):
    """视频流实时监控端点"""
    await websocket.accept()

    try:
        # 获取实际流地址（需实现缓存或数据库查询）
        stream_url = await get_stream_url(stream_id)

        consumer = VideoStreamConsumer(stream_url)
        async for frame in consumer.get_frames():
            await websocket.send_bytes(frame.tobytes())

    except WebSocketDisconnect:
        logging.info("Client disconnected")
    except Exception as e:
        logging.error(f"Stream error: {e}")
        await websocket.close(code=1008)


async def get_stream_url(stream_id: str) -> str:
    """获取实际流地址"""
    # 查询数据库或缓存获取真实地址
    return f"rtsp://example.com/{stream_id}"