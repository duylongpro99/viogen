from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.deps import get_db
from app.models.session import Session, SessionCreate, SessionUpdate

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/", response_model=Session)
async def create_session(session: SessionCreate):
    db = get_db()
    result = db.table("sessions").insert({
        "model_assignments": session.model_assignments,
        "settings": session.settings,
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create session")

    return result.data[0]


@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: UUID):
    db = get_db()
    result = db.table("sessions").select("*").eq("id", str(session_id)).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Session not found")

    return result.data[0]


@router.patch("/{session_id}", response_model=Session)
async def update_session(session_id: UUID, session: SessionUpdate):
    db = get_db()

    update_data = {}
    if session.model_assignments is not None:
        update_data["model_assignments"] = session.model_assignments
    if session.settings is not None:
        update_data["settings"] = session.settings

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = db.table("sessions").update(update_data).eq("id", str(session_id)).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Session not found")

    return result.data[0]


@router.delete("/{session_id}")
async def delete_session(session_id: UUID):
    db = get_db()
    result = db.table("sessions").delete().eq("id", str(session_id)).execute()

    return {"deleted": True}
