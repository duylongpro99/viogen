from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str


class Message(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    metadata: dict
    created_at: datetime

    class Config:
        from_attributes = True
