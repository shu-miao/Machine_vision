import asyncio
import logging
from app.utils.cluster import NodeRegistry
import datetime

logging.basicConfig(level=logging.INFO)

async def test_node_registry():
    registry = NodeRegistry.get_instance()
    node_id = "test_node_001"

    # 注册节点
    await registry.register_node(node_id)
    print(f"注册节点: {node_id}")

    # 获取活跃节点
    active_nodes = await registry.get_active_nodes()
    print(f"活跃节点列表: {active_nodes}")

    # 更新节点状态
    status = {
        "cpu_usage": 38.5,
        "memory_usage": 1024,
    }
    await registry.update_node_status(status)
    print(f"更新节点状态: {status}")

    # 再次获取活跃节点，确认节点还在
    active_nodes = await registry.get_active_nodes()
    print(f"活跃节点列表（更新后）: {active_nodes}")

    # 注销节点
    await registry.unregister_node(node_id)
    print(f"注销节点: {node_id}")

    # 最后确认节点已注销
    active_nodes = await registry.get_active_nodes()
    print(f"活跃节点列表（注销后）: {active_nodes}")


if __name__ == "__main__":
    asyncio.run(test_node_registry())
