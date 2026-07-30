from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
# Not: Aşağıdaki DocumentChunk modeli Kişi 3 tarafından oluşturulmuş olmalıdır.
# Eğer import hatası alırsan kendi proje yoluna göre düzeltmelisin.
from app.models.document_chunk import DocumentChunk 

class PGVectorStore:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def add_chunks(self, chunks_data: list[dict]):
        """
        Gelen chunk ve embedding verilerini veritabanına toplu olarak ekler.
        chunks_data içinde document_id, chunk_id, text, embedding vb. olmalıdır.
        """
        new_chunks = [DocumentChunk(**data) for data in chunks_data]
        self.db.add_all(new_chunks)
        await self.db.commit()

    async def similarity_search(self, document_id: int, query_embedding: list[float], top_k: int = 5):
        """
        Verilen soru vektörüne (query_embedding) en çok benzeyen (cosine distance)
        top_k adet chunk'ı bulur ve döndürür.
        """
        # pgvector'de cosine distance `<=>` operatörü ile ifade edilir (SQLAlchemy'de cosine_distance metodu).
        stmt = (
            select(
                DocumentChunk, 
                DocumentChunk.embedding.cosine_distance(query_embedding).label("distance")
            )
            .filter(DocumentChunk.document_id == document_id)
            .order_by("distance")
            .limit(top_k)
        )
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        # Yol haritasında istenen formata dönüştürülmüş çıktı
        search_results = []
        for chunk, distance in rows:
            search_results.append({
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "score": 1 - distance, # distance 0'a ne kadar yakınsa benzerlik (score) o kadar yüksektir
                "page_start": chunk.page_start,
                "page_end": chunk.page_end
            })
            
        return search_results

    async def get_document_chunks(self, document_id: int):
        """Bir dokümana ait tüm chunk'ları getirir."""
        stmt = select(DocumentChunk).filter(DocumentChunk.document_id == document_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def delete_document_chunks(self, document_id: int):
        """Bir dokümana ait tüm chunk'ları siler."""
        stmt = delete(DocumentChunk).filter(DocumentChunk.document_id == document_id)
        await self.db.execute(stmt)
        await self.db.commit()