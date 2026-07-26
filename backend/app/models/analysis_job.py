from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.domain.enums.job_status import JobStatus
from app.domain.enums.job_stage import JobStage

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    stage = Column(SQLEnum(JobStage), default=JobStage.PENDING, nullable=False)
    
    progress_percentage = Column(Integer, default=0, nullable=False)
    error_message = Column(String, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="jobs")