import asyncio
from uuid import UUID

from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.api.deps import get_db, get_comfyui
from app.models.generation import Generation, GenerationCreate
from app.workflows.builder import build_txt2img_workflow
from app.services.supabase import get_supabase_client

router = APIRouter(prefix="/generations", tags=["generations"])


async def run_generation(generation_id: str, workflow: dict):
    """Background task to run generation and poll for completion."""
    db = get_supabase_client()
    comfyui = get_comfyui()

    try:
        # Update status to running
        db.table("generations").update({
            "status": "running",
            "progress": 0,
        }).eq("id", generation_id).execute()

        # Queue workflow
        prompt_id = await comfyui.queue_workflow(workflow)

        # Poll for completion
        max_attempts = 300  # 5 minutes max
        for attempt in range(max_attempts):
            progress = await comfyui.get_progress(prompt_id)

            if progress["status"] == "complete":
                # Get output images
                outputs = progress.get("outputs", {})

                db.table("generations").update({
                    "status": "complete",
                    "progress": 100,
                    "parameters": {**outputs, "prompt_id": prompt_id},
                }).eq("id", generation_id).execute()
                return

            # Update progress (estimated)
            estimated_progress = min(95, (attempt / max_attempts) * 100)
            db.table("generations").update({
                "progress": int(estimated_progress),
            }).eq("id", generation_id).execute()

            await asyncio.sleep(1)

        # Timeout
        db.table("generations").update({
            "status": "failed",
            "error": "Generation timed out",
        }).eq("id", generation_id).execute()

    except Exception as e:
        db.table("generations").update({
            "status": "failed",
            "error": str(e),
        }).eq("id", generation_id).execute()


@router.post("/", response_model=Generation)
async def create_generation(data: GenerationCreate, background_tasks: BackgroundTasks):
    db = get_db()

    # Build workflow
    workflow = build_txt2img_workflow(
        prompt=data.prompt,
        negative_prompt=data.negative_prompt,
        **data.parameters,
    )

    # Create generation record
    result = db.table("generations").insert({
        "conversation_id": str(data.conversation_id),
        "workflow_json": workflow,
        "parameters": data.parameters,
        "status": "queued",
        "progress": 0,
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create generation")

    generation = result.data[0]

    # Start background generation
    background_tasks.add_task(run_generation, generation["id"], workflow)

    return generation


@router.get("/{generation_id}", response_model=Generation)
async def get_generation(generation_id: UUID):
    db = get_db()
    result = db.table("generations").select("*").eq("id", str(generation_id)).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Generation not found")

    return result.data[0]


@router.get("/conversation/{conversation_id}")
async def get_conversation_generations(conversation_id: UUID):
    db = get_db()
    result = db.table("generations")\
        .select("*")\
        .eq("conversation_id", str(conversation_id))\
        .order("created_at", desc=True)\
        .execute()

    return result.data
