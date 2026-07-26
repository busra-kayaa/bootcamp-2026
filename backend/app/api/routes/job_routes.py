"""Job status tracking routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.models.job import Job
from app.schemas.job_schema import JobResponse

router = APIRouter(tags=["Jobs"])


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    summary="İş/Görev durumunu sorgula",
)
async def get_job_status(
    job_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Arka planda çalışan doküman işleme görevinin durumunu sorgular.
    (PENDING, PROCESSING, COMPLETED, FAILED)
    """
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID'si {job_id} olan iş kaydı bulunamadı.",
        )
    return JobResponse.model_validate(job)