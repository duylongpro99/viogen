import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_comfyui_queue_workflow():
    from app.services.comfyui import ComfyUIClient

    client = ComfyUIClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"prompt_id": "test-123"}

    with patch.object(client._client, 'post', new_callable=AsyncMock, return_value=mock_response):
        prompt_id = await client.queue_workflow({"test": "workflow"})
        assert prompt_id == "test-123"
