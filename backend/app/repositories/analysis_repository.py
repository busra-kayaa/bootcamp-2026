from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.analysis_result import AnalysisResult

class AnalysisRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_result(self, result: AnalysisResult) -> AnalysisResult:
        """Kişi 2'den gelen analiz sonucunu ve fikirleri kaydeder[cite: 1]."""
        self.db.add(result)
        await self.db.flush()
        await self.db.refresh(result)
        return result

    async def get_by_document_id(self, document_id: int) -> Optional[AnalysisResult]:
        query = select(AnalysisResult).where(AnalysisResult.document_id == document_id)
        res = await self.db.execute(query)
        return res.scalar_one_or_none()