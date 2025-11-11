from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain.tools import tool


class CreatePacingGuideInput(BaseModel):
    duration_weeks: int = Field(description="Total course duration in weeks.")
    modules_count: int = Field(description="Number of modules/units.")
    hours_per_week: int = Field(
        default=6, description="Estimated hours per learner per week."
    )


@tool(args_schema=CreatePacingGuideInput)
def create_pacing_guide(
    duration_weeks: int,
    modules_count: int,
    hours_per_week: int = 6,
) -> List[Dict[str, Any]]:
    """
    Creates a week-by-week pacing guide allocating time to content, practice,
    and assessment across modules.
    Returns a list of week plans with suggested focus areas.
    """
    weeks: List[Dict[str, Any]] = []
    module_span = max(1, duration_weeks // modules_count or 1)
    for w in range(1, duration_weeks + 1):
        module_idx = (w - 1) // module_span + 1
        weeks.append(
            {
                "week": w,
                "module": min(module_idx, modules_count),
                "hours": hours_per_week,
                "distribution": {
                    "content": round(hours_per_week * 0.4, 1),
                    "practice": round(hours_per_week * 0.4, 1),
                    "assessment": round(hours_per_week * 0.2, 1),
                },
                "focus": "Advance core concepts and apply through practice.",
            }
        )
    return weeks
