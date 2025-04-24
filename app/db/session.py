# 数据库会话管理
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import asyncio
from urllib.parse import quote
from sqlalchemy import text

# 创建异步引擎，PostgreSQL 使用 asyncpg 驱动
password_encoded = quote(settings.DB_PASSWORD)

engine = create_async_engine(
    f"postgresql+asyncpg://{settings.DB_USER}:{password_encoded}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}",
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    connect_args={
        "timeout": 10
    }
)


# 异步会话工厂
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
    future=True,
    twophase=False
)

async def async_session() -> AsyncSession:
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def test_connection():
    try:
        query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
        async with engine.connect() as conn:
            result = await conn.execute(query)
            db_tables = result.scalars().all()
            for db_table in db_tables:
                print(db_table)
        # print('数据库连接成功')
    except Exception as e:
        print(f'数据库连接失败{e}')
    finally:
        await engine.dispose() # 关闭连接池


if __name__ == "__main__":
    asyncio.run(test_connection())