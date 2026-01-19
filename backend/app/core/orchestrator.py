from typing import AsyncGenerator

from app.core.phases import Phase, PHASE_SPECIALISTS, get_next_phase
from app.core.specialists import (
    StyleSpecialist,
    CompositionSpecialist,
    StorySpecialist,
    TechnicalSpecialist,
    CriticSpecialist,
)


class Orchestrator:
    def __init__(self, model_assignments: dict[str, str]):
        self.model_assignments = model_assignments
        self.current_phase = Phase.IDEATION
        self.conversation_history: list[dict] = []
        self.round_count = 0
        self.max_rounds_per_phase = 3

        # Initialize specialists
        self.specialists = {
            "style": StyleSpecialist(model_assignments.get("style", "llama3.2")),
            "composition": CompositionSpecialist(model_assignments.get("composition", "llama3.2")),
            "story": StorySpecialist(model_assignments.get("story", "llama3.2")),
            "technical": TechnicalSpecialist(model_assignments.get("technical", "llama3.2")),
            "critic": CriticSpecialist(model_assignments.get("critic", "llama3.2")),
        }

    async def process_user_message(
        self,
        message: str,
    ) -> AsyncGenerator[dict, None]:
        """Process a user message and stream specialist responses."""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "role_name": "User",
            "content": message,
        })

        yield {
            "type": "user_message",
            "content": message,
        }

        # Get specialists for current phase
        active_specialists = PHASE_SPECIALISTS.get(self.current_phase, [])

        # Each specialist responds
        for role in active_specialists:
            specialist = self.specialists[role]

            yield {
                "type": "specialist_start",
                "role": role,
                "name": specialist.name,
            }

            full_response = ""
            async for chunk in specialist.respond(message, self.conversation_history):
                full_response += chunk
                yield {
                    "type": "specialist_chunk",
                    "role": role,
                    "name": specialist.name,
                    "content": chunk,
                }

            # Add to history
            self.conversation_history.append({
                "role": role,
                "role_name": specialist.name,
                "content": full_response,
            })

            yield {
                "type": "specialist_end",
                "role": role,
                "name": specialist.name,
                "content": full_response,
            }

        self.round_count += 1

        # Check if we should advance phase
        if self.round_count >= self.max_rounds_per_phase:
            self.advance_phase()
            yield {
                "type": "phase_change",
                "phase": self.current_phase.value,
            }

    def advance_phase(self):
        """Move to the next phase."""
        self.current_phase = get_next_phase(self.current_phase)
        self.round_count = 0

    def inject_user_message(self, message: str):
        """Handle user interjection during orchestration."""
        self.conversation_history.append({
            "role": "user",
            "role_name": "User",
            "content": message,
        })
