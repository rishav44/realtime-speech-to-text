
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TranscriptionCreate(BaseModel):
    title: str = "Untitled Transcription"
    text: str
    language: Optional[str] = None
    duration: Optional[int] = None


class TranscriptionUpdate(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None


class TranscriptionResponse(BaseModel):
    id: int
    title: str
    text: str
    language: Optional[str] = None
    duration: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
