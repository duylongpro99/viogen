import json
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.api.deps import get_db
from app.core.orchestrator import Orchestrator
from app.models.message import MessageCreate
from app.models.conversation import Conversation, ConversationCreate

router = APIRouter(prefix="/chat", tags=["chat"])

# Store active orchestrators by conversation ID
active_orchestrators: dict[str, Orchestrator] = {}


@router.post("/conversations", response_model=Conversation)
async def create_conversation(data: ConversationCreate):
    db = get_db()

    # Get session for model assignments
    session = db.table("sessions").select("*").eq("id", str(data.session_id)).execute()
    if not session.data:
        raise HTTPException(status_code=404, detail="Session not found")

    # Create conversation
    result = db.table("conversations").insert({
        "session_id": str(data.session_id),
        "status": "ideation",
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create conversation")

    # Initialize orchestrator
    conv_id = result.data[0]["id"]
    model_assignments = session.data[0].get("model_assignments", {})
    active_orchestrators[conv_id] = Orchestrator(model_assignments)

    return result.data[0]


@router.post("/conversations/{conversation_id}/messages")
async def send_message(conversation_id: UUID, message: MessageCreate):
    db = get_db()
    conv_id_str = str(conversation_id)

    # Verify conversation exists
    conv = db.table("conversations").select("*").eq("id", conv_id_str).execute()
    if not conv.data:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get or create orchestrator
    if conv_id_str not in active_orchestrators:
        session = db.table("sessions").select("*").eq("id", conv.data[0]["session_id"]).execute()
        model_assignments = session.data[0].get("model_assignments", {}) if session.data else {}
        active_orchestrators[conv_id_str] = Orchestrator(model_assignments)

    # Save user message
    db.table("messages").insert({
        "conversation_id": conv_id_str,
        "role": "user",
        "content": message.content,
        "metadata": {},
    }).execute()

    async def event_generator():
        orchestrator = active_orchestrators[conv_id_str]

        async for event in orchestrator.process_user_message(message.content):
            # Save specialist messages to DB
            if event["type"] == "specialist_end":
                db.table("messages").insert({
                    "conversation_id": conv_id_str,
                    "role": event["role"],
                    "content": event["content"],
                    "metadata": {"name": event["name"]},
                }).execute()

            yield {
                "event": event["type"],
                "data": json.dumps(event),
            }

        # Update conversation status
        db.table("conversations").update({
            "status": orchestrator.current_phase.value,
        }).eq("id", conv_id_str).execute()

    return EventSourceResponse(event_generator())


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: UUID):
    db = get_db()

    result = db.table("messages")\
        .select("*")\
        .eq("conversation_id", str(conversation_id))\
        .order("created_at")\
        .execute()

    return result.data
