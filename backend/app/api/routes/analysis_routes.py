"""Analysis and Sprint planning routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.schemas.analysis_schema import FullAnalysisResponse, SprintPlanResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(tags=["Analyses"])


@router.get(
    "/analyses/documents/{document_id}/analysis",
    response_model=FullAnalysisResponse,
    summary="Dokümana ait son analiz sonucunu getir",
)
async def get_analysis_by_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Yüklenen dokümana ait AI analiz özetini ve üretilen fikir listesini döner."""
    service = AnalysisService(db)
    analysis = await service.get_analysis_by_document_id(document_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID'si {document_id} olan dokümana ait analiz sonucu bulunamadı.",
        )
    return FullAnalysisResponse.model_validate(analysis)


@router.post(
    "/analyses/{analysis_id}/ideas/{idea_id}/sprint-plan",
    response_model=SprintPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Seçilen fikir için Sprint Planı oluştur",
)
async def generate_sprint_plan(
    analysis_id: int,
    idea_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Seçilen fikir (idea_id) üzerinden LLM kullanarak
    User Story'ler, öncelikler ve Story Point'ler içeren Sprint Planı oluşturur.
    """
    service = AnalysisService(db)
    plan = await service.create_sprint_plan(analysis_id=analysis_id, idea_id=idea_id)
    return plan