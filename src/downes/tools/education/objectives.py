from typing import Optional
from pydantic import BaseModel, Field
from langchain.tools import tool

from .utils import MarkdownBuilder


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
) -> str:
    """
    Drafts clear, measurable learning objectives using action verbs and
    observable outcomes tailored to the audience and level.
    Returns objectives in clean Markdown format.
    """
    base_verbs = {
        "beginner": ["identify", "describe", "apply"],
        "intermediate": ["analyze", "compare", "implement"],
        "advanced": ["evaluate", "synthesize", "design"],
    }
    verbs = base_verbs.get(level.lower(), base_verbs["beginner"])

    md = MarkdownBuilder()
    md.add_heading("Learning Objectives", level=2)
    md.add_metadata(
        course=topic,
        audience=audience,
        level=level.capitalize(),
        duration=f"{duration_weeks} weeks" if duration_weeks else None
    )
    md.add_heading("Objectives", level=3)
    
    objectives = [
        f"By the end of this course, {audience} will be able to **{verbs[i % len(verbs)]}** key concepts in {topic} with appropriate accuracy."
        for i in range(outcomes_count)
    ]
    
    md.add_numbered_list(objectives)
    
    return md.build()
