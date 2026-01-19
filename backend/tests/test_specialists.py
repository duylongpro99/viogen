import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_specialist_generates_response():
    from app.core.specialists.base import BaseSpecialist

    class TestSpecialist(BaseSpecialist):
        role = "test"
        name = "Testy"
        system_prompt = "You are a test specialist."

    mock_chunks = [
        {"response": "Hello", "done": False},
        {"response": " there", "done": True},
    ]

    async def mock_generate(*args, **kwargs):
        for chunk in mock_chunks:
            yield chunk

    with patch('app.core.specialists.base.get_ollama_client') as mock_client:
        mock_client.return_value.generate = mock_generate

        specialist = TestSpecialist(model="test-model")

        response = ""
        async for chunk in specialist.respond("Test message", []):
            response += chunk

        assert response == "Hello there"
