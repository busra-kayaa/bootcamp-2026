from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("analysis_jobs.id", ondelete="CASCADE"), nullable=True)
    
    summary = Column(Text, nullable=False)
    critical_dates = Column(JSON, nullable=False)  # JSONB
    rules = Column(JSON, nullable=False)           # JSONB
    risks = Column(JSON, nullable=False)           # JSONB
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="analysis_results")
    ideas = relationship("ProjectIdea", back_populates="analysis_result", cascade="all, delete-orphan")