from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain.tools import tool

from downes.model import call_llm
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
        - Creates a pacing guide for allocating time 
          to content, practice, and assessment across modules.
        - Returns a Markdown formatted pacing guide.
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

    md.add_heading("Weekly Highlights", level=3)

    highlights_prompt = _build_highlights_prompt(
        duration_weeks=duration_weeks,
        modules_count=modules_count,
        hours_per_week=hours_per_week,
    )

    system_prompt = """You are a pacing guide expert. Provide concise Markdown bullet points describing the instructional focus for each week. Use the format `- **Week N (Module M):** <focus sentence>`. Mention signature activities or checkpoints when helpful and ensure every week appears exactly once."""

    try:
        response = call_llm(highlights_prompt, system_prompt=system_prompt)
        if response and hasattr(response, "content"):
            content = response.content.strip()
            if content:
                md.add_text(content)
                md.add_blank()
                return md.build()
    except Exception:
        pass

    md.add_text(_fallback_highlights(duration_weeks, modules_count))
    md.add_blank()
    return md.build()


def _build_highlights_prompt(
    duration_weeks: int,
    modules_count: int,
    hours_per_week: int,
) -> str:
    return (
        f"Total weeks: {duration_weeks}\n"
        f"Modules: {modules_count}\n"
        f"Estimated hours/week per learner: {hours_per_week}\n"
        "Goal: Summarize what learners tackle each week, including key checkpoints."
    )


def _fallback_highlights(duration_weeks: int, modules_count: int) -> str:
    """Deterministic weekly highlights when the LLM output is unavailable."""
    focus_bank = [
        "Foundational concepts and shared vocabulary",
        "Guided practice with instructor feedback",
        "Hands-on exploration and mini-project",
        "Peer collaboration and critique",
        "Applied challenge focused on transfer",
        "Assessment readiness and reflection",
    ]
    module_span = max(1, duration_weeks // modules_count or 1)
    lines = []
    for week in range(1, duration_weeks + 1):
        module_idx = min(((week - 1) // module_span) + 1, modules_count)
        focus = focus_bank[(week - 1) % len(focus_bank)]
        lines.append(f"- **Week {week} (Module {module_idx}):** {focus}.")
    return "\n".join(lines)
