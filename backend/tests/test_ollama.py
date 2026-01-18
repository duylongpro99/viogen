import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_ollama_generate_streams_response():
    from app.services.ollama import OllamaClient

    client = OllamaClient()

    # Mock the httpx response
    mock_response = AsyncMock()
    mock_response.aiter_lines = AsyncMock(return_value=iter([
        '{"response": "Hello", "done": false}',
        '{"response": " world", "done": true}'
    ]))
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    with patch.object(client._client, 'stream', return_value=mock_response):
        chunks = []
        async for chunk in client.generate("test-model", "Hello"):
            chunks.append(chunk)

        assert len(chunks) == 2
        assert chunks[0]["response"] == "Hello"
