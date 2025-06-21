from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BlogPost(BaseModel):
    id: str
    prompt: str
    content: str
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    feedback: Optional[str] = None
    related_versions: Optional[List[str]] = []
