from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.core.database import Base

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    # İşlemin hangi aşamada olduğu (Örn: UPLOADING, CHUNKING, ANALYZING, COMPLETED)
    job_stage = Column(String, default="PENDING") 
    
    # İşlemin genel durumu (Örn: IN_PROGRESS, SUCCESS, FAILED)
    job_status = Column(String, default="IN_PROGRESS") 
    
    error_message = Column(String, nullable=True) # Eğer işlem hata verirse sebebini tutacağız
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())