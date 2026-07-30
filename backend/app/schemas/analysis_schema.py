from pydantic import BaseModel
from typing import List, Optional

class IdeaItem(BaseModel):
    id: str
    title: str
    description: str
    feasibility_score: Optional[int] = 0

class FullAnalysisResponse(BaseModel):
    document_id: Optional[int] = None
    sourceName: Optional[str] = "Şartname Analizi"
    summary: Optional[str] = ""
    requirements: Optional[List[str]] = []
    risks: Optional[List[str]] = []
    ideas: Optional[List[IdeaItem]] = []

class SprintPlanResponse(BaseModel):
    idea_id: str
    sprint_goal: str
    backlog_items: List[dict] = []