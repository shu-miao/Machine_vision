# 检测任务调度
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List
import redis.asyncio as redis
from app.core.config import settings
from app.utils.cluster import NodeRegistry
from .video_consumer import VideoStreamConsumer
import logging

class TaskDispatcher:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=settings.MAX_WORKERS)
        self.redis = redis.from_url(settings.REDIS_URL)
        self.task_queue = "detection_tasks"
        self.priority_queue = "priority_tasks"

    async def _dispatch_to_node(self, stream_url: str, platform_id: str):
        """单任务分发到工作节点"""
        consumer = VideoStreamConsumer(stream_url, platform_id)
        try:
            await consumer.consume()
            return {"status": "completed", "url": stream_url}
        except Exception as e:
            logging.error(f"任务处理失败: {e}")
            return {"status": "failed", "error": str(e)}

    async def _get_available_nodes(self) -> List[str]:
        """获取可用节点列表"""
        nodes = await self.redis.smembers("active_nodes")
        return [node.decode() for node in nodes]

    async def dispatch_task(self, stream_urls: List[str], platform_id: str, priority: int = 0):
        """批量分发检测任务"""
        if priority > 0:
            # 高优先级任务插入队列头部
            await self.redis.lpush(
                self.priority_queue,
                *[f"{platform_id}:{url}" for url in stream_urls]
            )
        else:
            # 普通任务插入队列尾部
            await self.redis.rpush(
                self.task_queue,
                *[f"{platform_id}:{url}" for url in stream_urls]
            )

        # 启动后台消费任务
        asyncio.create_task(self._consume_tasks())

    async def _consume_tasks(self):
        """从队列消费任务"""
        while True:
            # 优先处理高优先级任务
            task = await self.redis.lpop(self.priority_queue) or \
                   await self.redis.lpop(self.task_queue)
            
            if not task:
                await asyncio.sleep(1)
                continue

            platform_id, url = task.decode().split(":")
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                lambda: asyncio.run(self._dispatch_to_node(url, platform_id))
            )

# 单例模式
dispatcher = TaskDispatcher()
dispatch_task = dispatcher.dispatch_task