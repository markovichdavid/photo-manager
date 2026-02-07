from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ImageRead(BaseModel):
    id: int
    filename: str
    content_type: str
    uploaded_at: datetime
    subject: Optional[str]
    owner_name: Optional[str]
    location: Optional[str]
    guide_name: Optional[str]
    notes: Optional[str]
    llm_review: Optional[str]
    llm_reviewed_at: Optional[datetime]


class ImageReviewRequest(BaseModel):
    criteria: str
    tone: Optional[str] = "מקצועי"
    language: Optional[str] = "עברית"


class ImageReviewResponse(BaseModel):
    image_id: int
    review: str
    model: Optional[str] = None
