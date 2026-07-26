"""Document management routes."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.schemas.document_schema import DocumentResponse, DocumentUploadResponse
from app.services.document_service import DocumentService

router = APIRouter(tags=["Documents"])


@router.post(
    "/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni doküman yükle",
)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Sisteme PDF, DOCX veya TXT formatında doküman yükler.
    Arka plan analizi için otomatik bir Job oluşturur.
    """
    service = DocumentService(db)
    result = await service.process_upload(file)
    return result


@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
    summary="Doküman detaylarını getir",
)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Doküman ID'sine göre yüklenen belgenin detaylarını döner."""
    service = DocumentService(db)
    document = await service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID'si {document_id} olan doküman bulunamadı.",
        )
    return DocumentResponse.model_validate(document)