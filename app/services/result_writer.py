# 结果写入
import asyncio
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from app.db.session import async_session
from app.models.schemas import DetectionResult
import logging

class ResultWriter:
    def __init__(self):
        self.batch_lock = asyncio.Lock()
        self.batch_buffer = []
        self.write_interval = 2  # 批量写入间隔(秒)
        self._running = True
        asyncio.create_task(self._batch_writer())

    async def add_result(self, result: DetectionResult):
        """添加单个检测结果到批量缓冲区"""
        async with self.batch_lock:
            self.batch_buffer.append(result)
            if len(self.batch_buffer) >= 50:  # 达到批量大小立即写入
                await self._flush_buffer()

    async def _batch_writer(self):
        """定时批量写入任务"""
        while self._running:
            await asyncio.sleep(self.write_interval)
            await self._flush_buffer()

    async def _flush_buffer(self):
        """将缓冲区数据写入数据库"""
        if not self.batch_buffer:
            return

        async with self.batch_lock:
            current_batch = self.batch_buffer
            self.batch_buffer = []

        records = [{
            'task_id': r.task_id,
            'camera_id': r.camera_id,
            'class_name': r.class_name,
            'confidence': r.confidence,
            'normalized_x': r.normalized_x,
            'normalized_y': r.normalized_y,
            'timestamp': r.timestamp,
            'frame_data': r.frame_data
        } for r in current_batch]

        try:
            async with async_session() as session:
                await session.execute(
                    insert(DetectionResult),
                    records
                )
                await session.commit()
            logging.info(f"成功写入 {len(records)} 条检测结果")
        except Exception as e:
            logging.error(f"批量写入失败: {e}")
            # 失败后重新加入缓冲区
            async with self.batch_lock:
                self.batch_buffer.extend(current_batch)

    async def shutdown(self):
        """关闭写入器"""
        self._running = False
        await self._flush_buffer()

# 单例模式
writer = ResultWriter()
add_result = writer.add_result
shutdown_writer = writer.shutdown