from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any

class DocumentCreate(BaseModel):
    filename: str
    content_length: Optional[int] = 0

class DocumentResponse(BaseModel):
    id: int
    filename: str
    uploaded_at: Optional[Any] = None

    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    # Dışarıdan gelen ekstra alanların (summary, ideas, risks vb.) filtrelenmesini engeller:
    model_config = ConfigDict(extra='allow')

    message: str
    document_id: Optional[int] = None
    job_id: Optional[str] = None
    sourceName: Optional[str] = None
    summary: Optional[str] = None
    criticalDates: Optional[List[Dict[str, Any]]] = None
    rules: Optional[List[Dict[str, Any]]] = None 
    ideas: Optional[List[Dict[str, Any]]] = None
    risks: Optional[List[Dict[str, Any]]] = None