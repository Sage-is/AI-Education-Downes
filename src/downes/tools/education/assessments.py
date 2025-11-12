from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from langchain.tools import tool


class DesignAssessmentsInput(BaseModel):
    learning_objectives: List[str] = Field(
        description="List of learning objectives to align assessments against."
    )
    assessment_types: Optional[List[str]] = Field(
        default=None, description="Preferred assessment types (e.g., quiz, project, presentation)."
    )
    rubric_scale: List[str] = Field(
        default_factory=lambda: ["Exceeds", "Meets", "Approaches", "Below"],
        description="Rubric performance levels."
    )

    @field_validator("rubric_scale", mode="before")
    @classmethod
    def _coerce_rubric_scale(cls, v):
        if v is None or isinstance(v, list):
            return v
        if isinstance(v, str):
            # Try JSON list first, then comma-separated fallback
            try:
                import json
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
            # If it's a single string that doesn't look like a list, return default
            if "," in v:
                return [s.strip() for s in v.split(",") if s.strip()]
            # Single non-list string, return default
            return ["Exceeds", "Meets", "Approaches", "Below"]
        return v


@tool(args_schema=DesignAssessmentsInput)
def design_assessments(
    learning_objectives: List[str],
    assessment_types: Optional[List[str]] = None,
    rubric_scale: List[str] = ["Exceeds", "Meets", "Approaches", "Below"],
) -> str:
    """
    Designs aligned assessments and draft rubrics for each objective.
    Returns assessments in clean Markdown format.
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
        
        lines.extend([
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
        ])
        
        for level in rubric_scale:
            lines.append(f"- **{level}:** Descriptor TBD")
        
        lines.append("")

    return "\n".join(lines)
