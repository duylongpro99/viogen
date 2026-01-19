import json
from typing import AsyncGenerator

import httpx

from app.config import settings


class OllamaClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.ollama_base_url
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=120.0)

    async def generate(
        self,
        model: str,
        prompt: str,
        system: str | None = None,
        context: list | None = None,
    ) -> AsyncGenerator[dict, None]:
        """Stream generate response from Ollama."""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
        }
        if system:
            payload["system"] = system
        if context:
            payload["context"] = context

        async with self._client.stream("POST", "/api/generate", json=payload) as response:
            async for line in response.aiter_lines():
                if line:
                    yield json.loads(line)

    async def list_models(self) -> list[dict]:
        """List available models."""
        response = await self._client.get("/api/tags")
        response.raise_for_status()
        return response.json().get("models", [])

    async def check_health(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = await self._client.get("/api/tags")
            return response.status_code == 200
        except httpx.RequestError:
            return False

    async def close(self):
        await self._client.aclose()


# Singleton instance
_ollama_client: OllamaClient | None = None


def get_ollama_client() -> OllamaClient:
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client
