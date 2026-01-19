import httpx

from app.config import settings


class ComfyUIClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.comfyui_base_url
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=300.0)

    async def queue_workflow(self, workflow: dict) -> str:
        """Queue a workflow and return the prompt ID."""
        response = await self._client.post("/prompt", json={"prompt": workflow})
        response.raise_for_status()
        return response.json()["prompt_id"]

    async def get_history(self, prompt_id: str) -> dict:
        """Get the history/status of a prompt."""
        response = await self._client.get(f"/history/{prompt_id}")
        response.raise_for_status()
        return response.json()

    async def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
        """Get generated image data."""
        params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        response = await self._client.get("/view", params=params)
        response.raise_for_status()
        return response.content

    async def check_health(self) -> bool:
        """Check if ComfyUI is running."""
        try:
            response = await self._client.get("/system_stats")
            return response.status_code == 200
        except httpx.RequestError:
            return False

    async def get_progress(self, prompt_id: str) -> dict:
        """Poll for generation progress."""
        history = await self.get_history(prompt_id)
        if prompt_id in history:
            return {"status": "complete", "outputs": history[prompt_id].get("outputs", {})}
        return {"status": "running", "progress": 0}

    async def close(self):
        await self._client.aclose()


_comfyui_client: ComfyUIClient | None = None


def get_comfyui_client() -> ComfyUIClient:
    global _comfyui_client
    if _comfyui_client is None:
        _comfyui_client = ComfyUIClient()
    return _comfyui_client
