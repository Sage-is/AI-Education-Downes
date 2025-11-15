from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from langchain.tools import tool

from downes.model import call_llm
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
    rubric_scale: Optional[List[str]] = None,
) -> str:
    """
        - Designs aligned assessments and draft rubrics for each objective.
        - Returns assessments in clean Markdown format.
    """
    rubric_scale = rubric_scale or ["Exceeds", "Meets", "Approaches", "Below"]
    default_types = ["quiz", "project", "reflection", "presentation"]
    types = assessment_types or default_types

    header = "\n".join(
        [
            "## Assessments & Rubrics",
            "",
            "Aligned assessments for each learning objective:",
            "",
        ]
    )

    objectives_text = "\n".join(
        [f"{idx + 1}. {obj}" for idx, obj in enumerate(learning_objectives)]
    )
    types_text = ", ".join(types)
    rubric_text = ", ".join(rubric_scale)

    system_prompt = """You are an assessment designer. For each provided learning objective, craft a matching assessment concept.\nFormat strictly in Markdown with the pattern:\n### Assessment N: <Assessment Type>\n**Aligned Objective:** ...\n**Assessment Summary:** ...\n| Level | Descriptor |\n|-------|------------|\n... one row per rubric level ...\nInclude 3 criteria bullets (Skills Demonstrated, Evidence of Mastery, Feedback Focus). Use only the provided rubric scale ordering and vary assessment types within the suggested set."""

    user_prompt = f"""Learning objectives:\n{objectives_text}\n\nPreferred assessment types: {types_text}\nRubric levels (top to bottom): {rubric_text}"""

    try:
        response = call_llm(user_prompt, system_prompt=system_prompt)
        if response and hasattr(response, "content"):
            content = response.content.strip()
            if content:
                if "Criterion" not in content or "Weight" not in content:
                    content = _append_default_criteria(content)
                return f"{header}{content}"
    except Exception:
        pass

    return _fallback_assessments(learning_objectives, types, rubric_scale)


def _fallback_assessments(
    learning_objectives: List[str],
    assessment_types: List[str],
    rubric_scale: List[str],
) -> str:
    """Procedural backup in case the LLM response fails."""
    lines = [
        "## Assessments & Rubrics",
        "",
        "Aligned assessments for each learning objective:",
        "",
    ]

    for idx, obj in enumerate(learning_objectives):
        kind = assessment_types[idx % len(assessment_types)]

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


def _append_default_criteria(content: str) -> str:
    template = """

**Assessment Criteria Template:**

| Criterion | Weight |
|-----------|--------|
| Accuracy/Correctness | 40% |
| Clarity/Communication | 30% |
| Application/Transfer | 30% |
"""
    return f"{content}{template}"
