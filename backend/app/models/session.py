from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SessionCreate(BaseModel):
    model_assignments: dict[str, str] = {}
    settings: dict = {}


class SessionUpdate(BaseModel):
    model_assignments: dict[str, str] | None = None
    settings: dict | None = None


class Session(BaseModel):
    id: UUID
    created_at: datetime
    model_assignments: dict[str, str]
    settings: dict

    class Config:
        from_attributes = True
