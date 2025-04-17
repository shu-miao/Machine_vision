# 检测任务调度
from concurrent.futures import ThreadPoolExecutor
from .video_consumer import process_stream

executor = ThreadPoolExecutor(max_workers=10)

async def dispatch_task(stream_urls: list[str]):
    """批量分发检测任务 (实际应替换为Celery)"""
    loop = asyncio.get_event_loop()
    futures = [
        loop.run_in_executor(executor, process_stream, url)
        for url in stream_urls
    ]
    return await asyncio.gather(*futures)