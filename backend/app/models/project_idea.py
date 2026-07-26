from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProjectIdea(Base):
    __tablename__ = "project_ideas"

    id = Column(Integer, primary_key=True, index=True)
    analysis_result_id = Column(Integer, ForeignKey("analysis_results.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    suitability_reason = Column(Text, nullable=False)
    
    ai_contribution_score = Column(Integer, nullable=False)
    feasibility_score = Column(Integer, nullable=False)
    overall_score = Column(Integer, nullable=False)
    
    advantages = Column(JSON, nullable=True)
    disadvantages = Column(JSON, nullable=True)
    source_chunk_ids = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    analysis_result = relationship("AnalysisResult", back_populates="ideas")