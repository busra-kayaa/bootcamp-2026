from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.domain.enums.job_status import JobStatus

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_hash = Column(String, unique=True, index=True, nullable=False)
    mime_type = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)
    character_count = Column(Integer, nullable=True)
    extraction_method = Column(String, nullable=True)
    
    processing_status = Column(
        SQLEnum(JobStatus),
        default=JobStatus.PENDING,
        nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    jobs = relationship("AnalysisJob", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="document", cascade="all, delete-orphan")