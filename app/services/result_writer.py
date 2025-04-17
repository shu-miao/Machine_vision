# 结果写入
import asyncio
from typing import List, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from app.db.session import async_session
from app.models.detection import DetectionResult  # 假设有这个模型

class ResultWriter:
    def __init__(self):
        self.batch_lock = asyncio.Lock()
        self.write_interval = 5  # 最大等待时间(秒)

    async def batch_save(self, platform_id: str, results: List[Dict]):
        """批量保存检测结果"""
        if not results:
            return

        async with self.batch_lock:
            # 转换数据格式
            records = [{
                'platform_id': platform_id,
                'class_id': r['class_id'],
                'confidence': r['confidence'],
                'bbox': str(r['bbox']),
                'timestamp': datetime.utcnow()
            } for r in results]

            # 批量插入
            async with async_session() as session:
                try:
                    await session.execute(
                        insert(DetectionResult),
                        records
                    )
                    await session.commit()
                except Exception as e:
                    await session.rollback()
                    raise Exception(f"批量保存失败: {str(e)}")

# 单例模式使用
writer = ResultWriter()
batch_save = writer.batch_save