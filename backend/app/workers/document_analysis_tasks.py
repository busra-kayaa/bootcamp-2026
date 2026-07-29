"""Celery task coordinating document extraction, embedding, analysis, and idea generation."""

import asyncio
import logging
from celery import shared_task

from app.core.database import AsyncSessionLocal
from app.workers.tasks import celery_app

logger = logging.getLogger(__name__)


def _get_or_create_event_loop() -> asyncio.AbstractEventLoop:
    """Aktif bir event loop varsa onu döner, yoksa yeni bir tane oluşturup ayarlar."""
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


@celery_app.task(bind=True, name="analyze_document_task", max_retries=3)
def analyze_document_task(self, document_id: int, job_id: int):
    """
    Arka planda doküman analiz boru hattını (pipeline) çalıştırır.
    Senkron Celery worker içinden güvenli Asyncio Event Loop yönetimi yapılır.
    """

    async def _run_pipeline():
        async with AsyncSessionLocal() as db:
            from app.repositories.chunk_repository import ChunkRepository
            from app.repositories.document_repository import DocumentRepository
            from app.repositories.job_repository import JobRepository
            from app.services.analysis_service import AnalysisService
            from app.services.document_service import DocumentService

            job_repo = JobRepository(db)
            doc_repo = DocumentRepository(db)
            chunk_repo = ChunkRepository(db)
            doc_service = DocumentService(db)
            analysis_service = AnalysisService(db)

            # Dokümanı veritabanından sorgula
            document = await doc_repo.get_by_id(document_id)
            if not document:
                raise ValueError(f"Document ID {document_id} bulunamadı.")

            # -------------------------------------------------------------
            # ADIM 1: Job durumunu TEXT_EXTRACTION yap
            # -------------------------------------------------------------
            logger.info(f"Job {job_id}: TEXT_EXTRACTION başlatılıyor...")
            await job_repo.update_progress(job_id, progress=15, status="TEXT_EXTRACTION")

            # ADIM 2: Kişi 1'in pipeline'ını çağır (Metin/Sayfa Çıkarma + Chunking)
            pages = await doc_service._extract_pages(document.file_path, document.file_type)
            chunks_data = doc_service.chunker.chunk(pages, max_chars=4000)

            # -------------------------------------------------------------
            # ADIM 3: Job durumunu EMBEDDING yap
            # -------------------------------------------------------------
            logger.info(f"Job {job_id}: EMBEDDING başlatılıyor...")
            await job_repo.update_progress(job_id, progress=40, status="EMBEDDING")

            # ADIM 4: Kişi 2'nin embedding işlemini çağır ve veritabanına kaydet
            if chunks_data:
                chunk_texts = [c["text"] for c in chunks_data]
                embeddings = doc_service.embedding_provider.get_embeddings(chunk_texts)
                await chunk_repo.save_chunks(
                    document_id=document_id,
                    chunks=chunks_data,
                    embeddings=embeddings,
                )

            # -------------------------------------------------------------
            # ADIM 5: Job durumunu ANALYZING_REQUIREMENTS yap
            # -------------------------------------------------------------
            logger.info(f"Job {job_id}: ANALYZING_REQUIREMENTS başlatılıyor...")
            await job_repo.update_progress(job_id, progress=70, status="ANALYZING_REQUIREMENTS")

            # ADIM 6 & 7: Requirement analizi ve Fikir üretimi (LLM/Service Çağrısı)
            await analysis_service.get_analysis_by_document_id(document_id)

            # -------------------------------------------------------------
            # ADIM 8: Sonuçları kaydet & ADIM 9: Job'ı COMPLETED yap
            # -------------------------------------------------------------
            logger.info(f"Job {job_id}: İşlem başarıyla tamamlanıyor...")
            await job_repo.update_progress(job_id, progress=100, status="COMPLETED")

    async def _mark_failed(error_msg: str):
        """Hata durumunda DB'deki Job kaydını FAILED olarak günceller."""
        async with AsyncSessionLocal() as db:
            from app.repositories.job_repository import JobRepository
            job_repo = JobRepository(db)
            await job_repo.update_progress(
                job_id, progress=0, status="FAILED", error_message=error_msg
            )

    loop = _get_or_create_event_loop()

    try:
        # Pipeline'ı mevcut güvenli event loop üzerinde koşturuyoruz
        loop.run_until_complete(_run_pipeline())
        return {"status": "SUCCESS", "document_id": document_id, "job_id": job_id}

    except Exception as exc:
        logger.error(f"Job {job_id} başarısız oldu: {str(exc)}")
        
        # Hata durumunda aynı event loop üzerinde durumu FAILED olarak işaretliyoruz
        try:
            loop.run_until_complete(_mark_failed(str(exc)))
        except Exception as db_exc:
            logger.error(f"Job {job_id} FAILED durumuna güncellenirken ikincil hata: {str(db_exc)}")

        # Celery retry mekanizmasını tetikle
        raise self.retry(exc=exc, countdown=10)