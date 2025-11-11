from typing import List, Dict, Any, Optional
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
) -> List[Dict[str, Any]]:
    """
    Designs aligned assessments and draft rubrics for each objective.
    Returns a list of assessment specs including criteria and rubric levels.
    """
    default_types = ["quiz", "project", "reflection", "presentation"]
    types = assessment_types or default_types

    results: List[Dict[str, Any]] = []
    for idx, obj in enumerate(learning_objectives):
        kind = types[idx % len(types)]
        criteria = [
            {"criterion": "Accuracy/Correctness", "weight": 0.4},
            {"criterion": "Clarity/Communication", "weight": 0.3},
            {"criterion": "Application/Transfer", "weight": 0.3},
        ]
        rubric = {level: "Descriptor TBD" for level in rubric_scale}
        results.append(
            {
                "objective": obj,
                "type": kind,
                "criteria": criteria,
                "rubric": rubric,
            }
        )

    return results
