from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document_chunk import DocumentChunk

class ChunkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_many(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Kişi 1'den gelen chunk listesini topluca kaydeder[cite: 1]."""
        self.db.add_all(chunks)
        await self.db.flush()
        return chunks