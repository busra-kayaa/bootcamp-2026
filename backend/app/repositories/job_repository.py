from datetime import datetime
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis_job import AnalysisJob
from app.domain.enums.job_status import JobStatus
from app.domain.enums.job_stage import JobStage

class JobRepository:
    """AnalysisJob tablosu için veritabanı sorgu katmanı[cite: 1]."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_job(self, document_id: int) -> AnalysisJob:
        """Yeni bir analiz işi (job) başlatır[cite: 1]."""
        job = AnalysisJob(
            document_id=document_id,
            status=JobStatus.PENDING,
            stage=JobStage.PENDING,
            progress_percentage=0
        )
        self.db.add(job)
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def get_by_id(self, job_id: int) -> Optional[AnalysisJob]:
        """ID'ye göre analiz işini getirir[cite: 1]."""
        query = select(AnalysisJob).where(AnalysisJob.id == job_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_stage(
        self,
        job_id: int,
        stage: JobStage,
        progress_percentage: Optional[int] = None
    ) -> Optional[AnalysisJob]:
        """İşin mevcut aşamasını ve (varsa) ilerleme yüzdesini günceller[cite: 1]."""
        values = {"stage": stage}
        if progress_percentage is not None:
            values["progress_percentage"] = progress_percentage
        if stage != JobStage.PENDING and values.get("status") is None:
            values["status"] = JobStatus.IN_PROGRESS
            values["started_at"] = datetime.utcnow()

        query = (
            update(AnalysisJob)
            .where(AnalysisJob.id == job_id)
            .values(**values)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(query)
        return await self.get_by_id(job_id)

    async def update_progress(self, job_id: int, progress_percentage: int) -> Optional[AnalysisJob]:
        """İşin % ilerleme değerini günceller[cite: 1]."""
        query = (
            update(AnalysisJob)
            .where(AnalysisJob.id == job_id)
            .values(progress_percentage=progress_percentage)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(query)
        return await self.get_by_id(job_id)

    async def mark_failed(self, job_id: int, error_message: str) -> Optional[AnalysisJob]:
        """İşi hatalı (FAILED) olarak işaretler ve hata mesajını kaydeder[cite: 1]."""
        query = (
            update(AnalysisJob)
            .where(AnalysisJob.id == job_id)
            .values(
                status=JobStatus.FAILED,
                error_message=error_message,
                completed_at=datetime.utcnow()
            )
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(query)
        return await self.get_by_id(job_id)

    async def mark_completed(self, job_id: int) -> Optional[AnalysisJob]:
        """İşi başarıyla tamamlandı (SUCCESS / COMPLETED) yapar[cite: 1]."""
        query = (
            update(AnalysisJob)
            .where(AnalysisJob.id == job_id)
            .values(
                status=JobStatus.SUCCESS,
                stage=JobStage.COMPLETED,
                progress_percentage=100,
                completed_at=datetime.utcnow()
            )
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(query)
        return await self.get_by_id(job_id)