from typing import List, Optional
from pydantic import BaseModel, Field
from langchain.tools import tool


class GenerateObjectivesInput(BaseModel):
    topic: str = Field(description="High-level subject or course title.")
    audience: str = Field(
        description="Intended learners (e.g., 'adult beginners', 'undergrads in business')."
    )
    level: Optional[str] = Field(
        default="beginner",
        description="Proficiency level (beginner, intermediate, advanced).",
    )
    duration_weeks: Optional[int] = Field(
        default=None, description="Approximate course length in weeks."
    )
    outcomes_count: Optional[int] = Field(
        default=5,
        description="Target number of measurable learning objectives to produce.",
    )


@tool(args_schema=GenerateObjectivesInput)
def generate_learning_objectives(
    topic: str,
    audience: str,
    level: str = "beginner",
    duration_weeks: Optional[int] = None,
    outcomes_count: int = 5,
) -> List[str]:
    """
    Drafts clear, measurable learning objectives using action verbs and
    observable outcomes tailored to the audience and level.
    Returns a list of objective statements.
    """
    # For now, provide a deterministic scaffold; LLM can refine.
    # Keep side-effect free; agent composes with LLM for improvements.
    base_verbs = {
        "beginner": ["identify", "describe", "apply"],
        "intermediate": ["analyze", "compare", "implement"],
        "advanced": ["evaluate", "synthesize", "design"],
    }
    verbs = base_verbs.get(level.lower(), base_verbs["beginner"])

    objectives: List[str] = []
    for i in range(outcomes_count):
        verb = verbs[i % len(verbs)]
        objectives.append(
            f"By the end of this course, {audience} will be able to {verb} key concepts in {topic} with appropriate accuracy."
        )

    if duration_weeks:
        objectives.append(
            f"Learners will demonstrate progress toward these objectives over approximately {duration_weeks} weeks."
        )
    return objectives
