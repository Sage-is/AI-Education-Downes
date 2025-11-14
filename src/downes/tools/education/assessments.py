from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from langchain.tools import tool

from .utils import normalize_list_input


class DesignAssessmentsInput(BaseModel):
    learning_objectives: List[str] = Field(
        description="List of learning objectives to align assessments against."
    )
    assessment_types: Optional[List[str]] = Field(
        default=None,
        description="Preferred assessment types (e.g., quiz, project, presentation).",
    )
    rubric_scale: List[str] = Field(
        default_factory=lambda: ["Exceeds", "Meets", "Approaches", "Below"],
        description="Rubric performance levels.",
    )

    @field_validator("learning_objectives", mode="before")
    @classmethod
    def normalize_learning_objectives(cls, v):
        """Normalize learning_objectives from various formats."""
        result = normalize_list_input(v, default=[])
        if not result:
            raise ValueError("learning_objectives cannot be empty")
        return result
    
    @field_validator("assessment_types", mode="before")
    @classmethod
    def normalize_assessment_types(cls, v):
        """Normalize assessment_types from various formats."""
        return normalize_list_input(v, default=None)

    @field_validator("rubric_scale", mode="before")
    @classmethod
    def normalize_rubric_scale(cls, v):
        """Normalize rubric_scale from various formats."""
        result = normalize_list_input(v, default=None)
        return result or ["Exceeds", "Meets", "Approaches", "Below"]


@tool(args_schema=DesignAssessmentsInput)
def design_assessments(
    learning_objectives: List[str],
    assessment_types: Optional[List[str]] = None,
    rubric_scale: List[str] = ["Exceeds", "Meets", "Approaches", "Below"],
) -> str:
    """
        - Designs aligned assessments and draft rubrics for each objective.
        - Returns assessments in clean Markdown format.
    """
    default_types = ["quiz", "project", "reflection", "presentation"]
    types = assessment_types or default_types

    lines = [
        "## Assessments & Rubrics",
        "",
        "Aligned assessments for each learning objective:",
        "",
    ]

    for idx, obj in enumerate(learning_objectives):
        kind = types[idx % len(types)]

        lines.extend(
            [
                f"### Assessment {idx + 1}: {kind.capitalize()}",
                "",
                f"**Aligned Objective:** {obj}",
                "",
                "**Assessment Criteria:**",
                "",
                "| Criterion | Weight |",
                "|-----------|--------|",
                "| Accuracy/Correctness | 40% |",
                "| Clarity/Communication | 30% |",
                "| Application/Transfer | 30% |",
                "",
                "**Rubric Levels:**",
                "",
            ]
        )

        for level in rubric_scale:
            lines.append(f"- **{level}:** Descriptor TBD")

        lines.append("")

    return "\n".join(lines)
