from enum import Enum


class Phase(Enum):
    IDEATION = "ideation"
    REFINEMENT = "refinement"
    SYNTHESIS = "synthesis"
    REVIEW = "review"
    GENERATING = "generating"
    COMPLETE = "complete"


PHASE_SPECIALISTS = {
    Phase.IDEATION: ["style", "composition", "story"],
    Phase.REFINEMENT: ["style", "composition", "story", "critic"],
    Phase.SYNTHESIS: ["technical"],
    Phase.REVIEW: ["critic"],
}


def get_next_phase(current: Phase) -> Phase:
    """Get the next phase in the workflow."""
    order = [Phase.IDEATION, Phase.REFINEMENT, Phase.SYNTHESIS, Phase.REVIEW, Phase.GENERATING, Phase.COMPLETE]
    current_idx = order.index(current)
    if current_idx < len(order) - 1:
        return order[current_idx + 1]
    return current
