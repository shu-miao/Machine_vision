# 集群协调
import socket
import asyncio
import redis.asyncio as redis
from typing import Set, Optional
from app.core.config import *

class NodeRegistry:
    _instance = None

    def __init__(self):
        self.redis = redis.from_url(
            settings.REDIS_URL,
            max_connections=20,
            socket_keepalive=True
        )
        self.current_node = socket.gethostname()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def register_node(self, node_id: str):
        """注册节点到Redis"""
        try:
            await self.redis.sadd("active_nodes", node_id)
            await self.redis.set(f"node:{node_id}:status", "active")
            logging.info(f"节点 {node_id} 注册成功")
        except Exception as e:
            logging.error(f"节点注册失败: {e}")

    async def unregister_node(self, node_id: str):
        """从Redis移除节点"""
        try:
            await self.redis.srem("active_nodes", node_id)
            await self.redis.delete(f"node:{node_id}:status")
            logging.info(f"节点 {node_id} 注销成功")
        except Exception as e:
            logging.error(f"节点注销失败: {e}")

    async def get_active_nodes(self) -> Set[str]:
        """获取所有活跃节点"""
        try:
            async with self.redis.client() as conn:
                nodes = await conn.smembers("active_nodes")
                return {node.decode() for node in nodes}
        except Exception as e:
            logging.error(f"获取活跃节点失败: {e}")
            return set()

    async def update_node_status(self, status: dict):
        """更新节点状态"""
        try:
            if not status:
                logging.warning("状态字典为空，跳过更新")
                return

            # 强制转换所有键值到字符串
            str_status = {str(k): str(v) for k, v in status.items()}
            await self.redis.hset(
                f"node:{self.current_node}:metrics",  # Redis 键名
                mapping=str_status  # 字段值字典
            )
            logging.info(f"节点状态更新成功")
        except Exception as e:
            logging.error(f"更新节点状态失败: {e}")