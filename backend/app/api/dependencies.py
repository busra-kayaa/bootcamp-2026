from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI endpoint'leri için asenkron veritabanı oturumu (session) üretir."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()