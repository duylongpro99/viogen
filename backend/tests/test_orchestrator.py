import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_orchestrator_runs_ideation_phase():
    from app.core.orchestrator import Orchestrator
    from app.core.phases import Phase

    model_assignments = {
        "style": "llama3.2",
        "composition": "llama3.2",
        "story": "llama3.2",
        "technical": "llama3.2",
        "critic": "llama3.2",
    }

    orchestrator = Orchestrator(model_assignments)

    # Mock all specialists to return simple responses
    async def mock_respond(*args, **kwargs):
        yield "Test response from specialist"

    for specialist in orchestrator.specialists.values():
        specialist.respond = mock_respond

    messages = []
    async for msg in orchestrator.process_user_message("Create a sunset scene"):
        messages.append(msg)

    assert len(messages) > 0
    assert orchestrator.current_phase == Phase.IDEATION
