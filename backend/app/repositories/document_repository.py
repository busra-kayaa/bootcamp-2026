from typing import Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.domain.enums.job_status import JobStatus

class DocumentRepository:
    """Document tablosu için veritabanı sorgu katmanı."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, document: Document) -> Document:
        """Yeni bir doküman kaydı oluşturur."""
        self.db.add(document)
        await self.db.flush()
        await self.db.refresh(document)
        return document

    async def get_by_id(self, document_id: int) -> Optional[Document]:
        """ID'ye göre doküman getirir."""
        query = select(Document).where(Document.id == document_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_hash(self, file_hash: str) -> Optional[Document]:
        """Dosya hash'ine göre daha önce yüklenmiş dokümanı bulur."""
        query = select(Document).where(Document.file_hash == file_hash)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_status(self, document_id: int, status: JobStatus) -> Optional[Document]:
        """Doküman işleme durumunu günceller."""
        query = (
            update(Document)
            .where(Document.id == document_id)
            .values(processing_status=status)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(query)
        return await self.get_by_id(document_id)

    async def update_processing_metadata(
        self,
        document_id: int,
        page_count: Optional[int] = None,
        character_count: Optional[int] = None,
        extraction_method: Optional[str] = None
    ) -> Optional[Document]:
        """PDF işlendikten sonra metin/sayfa metadatalarını günceller."""
        values = {}
        if page_count is not None:
            values["page_count"] = page_count
        if character_count is not None:
            values["character_count"] = character_count
        if extraction_method is not None:
            values["extraction_method"] = extraction_method

        if values:
            query = (
                update(Document)
                .where(Document.id == document_id)
                .values(**values)
                .execution_options(synchronize_session="fetch")
            )
            await self.db.execute(query)

        return await self.get_by_id(document_id)

    async def delete(self, document_id: int) -> bool:
        """Dokümanı veritabanından siler[cite: 1]."""
        query = delete(Document).where(Document.id == document_id)
        result = await self.db.execute(query)
        return result.rowcount > 0