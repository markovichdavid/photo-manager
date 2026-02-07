from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Image(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    content_type: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    subject: Optional[str] = Field(default=None, index=True)
    owner_name: Optional[str] = Field(default=None, index=True)
    location: Optional[str] = Field(default=None, index=True)
    guide_name: Optional[str] = Field(default=None, index=True)
    notes: Optional[str] = None
    stored_path: str
    llm_review: Optional[str] = None
    llm_reviewed_at: Optional[datetime] = None
