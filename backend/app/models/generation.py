from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class GenerationCreate(BaseModel):
    conversation_id: UUID
    prompt: str
    negative_prompt: str = "ugly, blurry, low quality"
    parameters: dict = {}


class Generation(BaseModel):
    id: UUID
    conversation_id: UUID
    workflow_json: dict | None
    parameters: dict
    status: str
    progress: int
    error: str | None
    created_at: datetime

    class Config:
        from_attributes = True
