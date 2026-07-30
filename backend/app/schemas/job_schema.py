from pydantic import BaseModel
from typing import Optional

class JobResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[dict] = None

    class Config:
        from_attributes = True