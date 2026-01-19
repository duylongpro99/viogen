from abc import ABC, abstractmethod
from typing import AsyncGenerator

from app.services.ollama import get_ollama_client


class BaseSpecialist(ABC):
    role: str = ""
    name: str = ""
    system_prompt: str = ""

    def __init__(self, model: str):
        self.model = model
        self._client = get_ollama_client()

    def _build_prompt(self, user_message: str, conversation_history: list[dict]) -> str:
        """Build prompt with conversation context."""
        history_text = ""
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            role_name = msg.get("role_name", msg["role"])
            history_text += f"{role_name}: {msg['content']}\n"

        return f"""Previous conversation:
{history_text}

Current request: {user_message}

Respond as {self.name}, focusing on your specialty."""

    async def respond(
        self,
        user_message: str,
        conversation_history: list[dict],
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response."""
        prompt = self._build_prompt(user_message, conversation_history)

        async for chunk in self._client.generate(
            model=self.model,
            prompt=prompt,
            system=self.system_prompt,
        ):
            if chunk.get("response"):
                yield chunk["response"]
