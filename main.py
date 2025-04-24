"""
分布式机器视觉系统主入口
包含FastAPI初始化、路由注册、节点管理、健康检查等功能
"""
import uvicorn
import signal
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.utils.cluster import NodeRegistry
from app.api.v1 import tasks as v1_tasks
from app.api.v1 import streams as v1_streams
import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 初始化节点注册
    node_registry = NodeRegistry.get_instance()
    await node_registry.register_node(node_registry.current_node)

    # 启动后台状态更新任务
    asyncio.create_task(status_updater(node_registry))

    yield

    # 关闭时清理节点
    await node_registry.unregister_node(node_registry.current_node)

app = FastAPI(
    title="Machine_Vision",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 添加全局中间件
@app.middleware("http")
async def add_process_time_header(request, call_next):
    response = await call_next(request)
    response.headers["X-Server-Node"] = settings.PLATFORM_ID
    return response

# 包含API路由
app.include_router(v1_tasks.router, prefix="/api/v1", tags=["Task"])
app.include_router(v1_streams.router, prefix="/api/v1", tags=["Stream"])

# 健康检查端点
@app.get("/health")
async def health_check():
    return {
        "status": "active",
        "node": NodeRegistry.get_instance().current_node
    }

async def status_updater(registry: NodeRegistry):
    """定期更新节点状态"""
    while True:
        try:
            await registry.update_node_status({
                "cpu_usage": 15.2,  # 系统指标
                "memory_usage": 32.1,
                "active_tasks": 0
            })
            await asyncio.sleep(30)
        except Exception as e:
            logging.error(f"状态更新失败: {e}")

def graceful_shutdown():
    """关闭处理"""
    async def shutdown_handler():
        registry = NodeRegistry.get_instance()
        await registry.unregister_node(registry.current_node)

    loop = asyncio.new_event_loop()
    loop.run_until_complete(shutdown_handler())

if __name__ == "__main__":
    # 注册信号处理
    signal.signal(signal.SIGINT, lambda s, f: graceful_shutdown())
    signal.signal(signal.SIGTERM, lambda s, f: graceful_shutdown())

    # 启动服务
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=settings.LOGGING_CONFIG
    )
