from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from langchain.tools import tool

from .utils import normalize_list_input


class DraftSyllabusInput(BaseModel):
    course_title: str = Field(description="Title of the course.")
    learning_objectives: List[str] = Field(
        description="List of previously generated learning objectives to align modules."
    )
    duration_weeks: int = Field(description="Total duration in weeks.")
    modality: str = Field(
        default="online",
        description="Delivery modality: online, in-person, hybrid.",
    )
    prerequisites: Optional[List[str]] = Field(
        default=None, description="Optional prerequisite knowledge or courses."
    )
    modules_count: int = Field(
        default=6, description="Number of modules or units to create."
    )

    @field_validator("learning_objectives", mode="before")
    @classmethod
    def normalize_learning_objectives(cls, v):
        """Normalize learning_objectives from various formats."""
        result = normalize_list_input(v, default=[])
        if not result:
            raise ValueError("learning_objectives cannot be empty")
        return result
    
    @field_validator("prerequisites", mode="before")
    @classmethod
    def normalize_prerequisites(cls, v):
        """Normalize prerequisites from various formats."""
        return normalize_list_input(v, default=None)


@tool(args_schema=DraftSyllabusInput)
def draft_syllabus(
    course_title: str,
    learning_objectives: List[str],
    duration_weeks: int,
    modality: str = "online",
    prerequisites: Optional[List[str]] = None,
    modules_count: int = 6,
) -> str:
    """
    
        Produces a structured syllabus outline with modules mapped to learning objectives,
            each including a description and suggested instructional strategies.
    
            Returns a Markdown formatted syllabus.
    """
    # Simple even distribution of objectives
    obj_per_module = max(1, len(learning_objectives) // modules_count or 1)

    lines = [
        f"# {course_title} - Syllabus",
        "",
        "## Course Information",
        "",
        f"- **Duration:** {duration_weeks} weeks",
        f"- **Modality:** {modality.capitalize()}",
    ]

    if prerequisites:
        lines.extend(
            [
                "",
                "### Prerequisites",
                "",
            ]
        )
        for prereq in prerequisites:
            lines.append(f"- {prereq}")

    lines.extend(
        [
            "",
            "## Course Modules",
            "",
        ]
    )

    for i in range(modules_count):
        start = i * obj_per_module
        end = start + obj_per_module
        aligned = learning_objectives[start:end]
        if not aligned:
            aligned = learning_objectives[-obj_per_module:]

        lines.extend(
            [
                f"### Module {i + 1}: Core Concepts",
                "",
                f"**Summary:** Introduces foundational elements of {course_title} with focus on applied understanding.",
                "",
                "**Aligned Learning Objectives:**",
                "",
            ]
        )

        for obj in aligned:
            lines.append(f"- {obj}")

        lines.extend(
            [
                "",
                "**Suggested Activities:**",
                "",
                "- Micro-lecture",
                "- Guided discussion",
                "- Hands-on exercise",
                "",
                "**Formative Assessment:** Short quiz or reflective prompt",
                "",
            ]
        )

    return "\n".join(lines)
