from typing import Optional
from pydantic import BaseModel, Field
from langchain.tools import tool

from downes.model import call_llm
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
    - Drafts clear, measurable learning objectives using action verbs and
      observable outcomes tailored to the audience and level.
    - Returns objectives in clean Markdown format.
    """
    header = _build_objectives_header(
        topic=topic,
        audience=audience,
        level=level,
        duration_weeks=duration_weeks,
    )

    system_prompt = """You are an instructional designer who specializes in writing measurable learning objectives using Bloom-inspired verbs.\nReturn ONLY a Markdown numbered list of objectives. Each objective must:\n- Start with a strong action verb\n- Specify the performance or artifact learners will produce\n- Reference the context or content focus\n- Include an accuracy or quality criteria when reasonable\nMatch the requested number of objectives exactly and avoid extra commentary."""

    user_prompt = f"""Course topic: {topic}\nAudience: {audience}\nLevel: {level}\nDuration (weeks): {duration_weeks or 'unspecified'}\nRequested objective count: {outcomes_count}"""

    try:
        response = call_llm(user_prompt, system_prompt=system_prompt)
        if response and hasattr(response, "content"):
            content = response.content.strip()
            if content:
                if not content.startswith("1.") and not content.startswith("-"):
                    content = f"1. {content}"
                return f"{header}{content}"
    except Exception:
        pass

    return _fallback_objectives(topic, audience, level, duration_weeks, outcomes_count)


def _build_objectives_header(
    topic: str,
    audience: str,
    level: str,
    duration_weeks: Optional[int],
) -> str:
    lines = [
        "## Learning Objectives",
        "",
        f"**Course:** {topic}",
        f"**Audience:** {audience}",
        f"**Level:** {level.capitalize()}",
    ]
    if duration_weeks:
        lines.append(f"**Duration:** {duration_weeks} weeks")
    lines.extend(["", "### Objectives", ""])
    return "\n".join(lines)


def _fallback_objectives(
    topic: str,
    audience: str,
    level: str,
    duration_weeks: Optional[int],
    outcomes_count: int,
) -> str:
    """Heuristic fallback used when the LLM call is unavailable."""
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
        duration=f"{duration_weeks} weeks" if duration_weeks else None,
    )
    md.add_heading("Objectives", level=3)

    objectives = [
        f"By the end of this course, {audience} will be able to **{verbs[i % len(verbs)]}** key concepts in {topic} with appropriate accuracy."
        for i in range(outcomes_count)
    ]

    md.add_numbered_list(objectives)

    return md.build()
