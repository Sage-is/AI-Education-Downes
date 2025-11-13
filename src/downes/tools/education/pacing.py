from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain.tools import tool

from .utils import MarkdownBuilder


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
) -> str:
    """
    Creates a week-by-week pacing guide allocating time to content, practice,
    and assessment across modules.
    Returns a Markdown formatted pacing guide.
    """
    module_span = max(1, duration_weeks // modules_count or 1)

    md = MarkdownBuilder()
    md.add_heading("Pacing Guide", level=2)
    md.add_metadata(
        total_duration=f"{duration_weeks} weeks",
        modules=modules_count,
        hours_per_week=hours_per_week,
    )
    md.add_heading("Weekly Schedule", level=3)

    # Build table rows
    rows = []
    for w in range(1, duration_weeks + 1):
        module_idx = (w - 1) // module_span + 1
        module = min(module_idx, modules_count)
        content_hours = round(hours_per_week * 0.4, 1)
        practice_hours = round(hours_per_week * 0.4, 1)
        assessment_hours = round(hours_per_week * 0.2, 1)

        rows.append(
            [
                w,
                module,
                f"{hours_per_week}h",
                f"{content_hours}h",
                f"{practice_hours}h",
                f"{assessment_hours}h",
                "Core concepts + practice",
            ]
        )

    md.add_table(
        ["Week", "Module", "Total Hours", "Content", "Practice", "Assessment", "Focus"],
        rows,
    )

    return md.build()
