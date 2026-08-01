"""Document management routes."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.api.dependencies import get_db
from app.schemas.document_schema import DocumentResponse, DocumentUploadResponse
from app.services.document_service import DocumentService

from app.pipelines.sprint_planning_pipeline import SprintPlanningPipeline
from app.pipelines.idea_generation_pipeline import IdeaGenerationPipeline # YENİ EKLENDİ
from app.infrastructure.vector_store.pgvector_store import PGVectorStore
from app.infrastructure.llm.llm_provider import GroqLLMProvider
from app.infrastructure.embeddings.sentence_transformer_provider import SentenceTransformerProvider

router = APIRouter(tags=["Documents"])

class IdeaSelectRequest(BaseModel):
    title: str
    description: str
    aiContribution: str
    teamSize: Optional[int] = 5
    sprintCount: Optional[int] = 3
    customRoles: Optional[str] = "Product Owner, Scrum Master, Developer"


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


@router.post(
    "/documents/{document_id}/sprint-plan",
    status_code=status.HTTP_200_OK,
    summary="Seçilen fikir için sprint planı oluşturur"
)
async def generate_sprint_plan(
    document_id: int, 
    idea: IdeaSelectRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Kullanıcının arayüzden seçtiği proje fikrini ve ayarlarını alıp yapay zekâya göndererek
    Sprint'lere, User Story'lere ve Task'lara bölünmüş detaylı planı döner.
    """
    try:
        vector_store = PGVectorStore(db_session=db)
        llm_provider = GroqLLMProvider()
        embedding_provider = SentenceTransformerProvider()
        
        pipeline = SprintPlanningPipeline(
            vector_store=vector_store,
            llm_provider=llm_provider,
            embedding_provider=embedding_provider
        )
        
        sprint_plan = await pipeline.execute(
            document_id=document_id,
            selected_idea=idea.model_dump()
        )
        
        return sprint_plan

    except Exception as e:
        print(f"Sprint Planlama Hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Sprint planı oluşturulurken bir hata oluştu."
        )

# YENİ EKLENEN ENDPOINT
@router.post(
    "/documents/{document_id}/regenerate-ideas",
    status_code=status.HTTP_200_OK,
    summary="Yalnızca şartnameye uygun 3 yeni fikir üretir"
)
async def regenerate_ideas(
    document_id: int, 
    db: AsyncSession = Depends(get_db)
):
    try:
        vector_store = PGVectorStore(db_session=db)
        llm_provider = GroqLLMProvider()
        embedding_provider = SentenceTransformerProvider()
        
        pipeline = IdeaGenerationPipeline(
            vector_store=vector_store,
            llm_provider=llm_provider,
            embedding_provider=embedding_provider
        )
        
        new_ideas = await pipeline.execute(document_id=document_id)
        return {"ideas": new_ideas}

    except Exception as e:
        print(f"Fikir Yenileme Hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Yeni fikirler üretilirken bir hata oluştu."
        )