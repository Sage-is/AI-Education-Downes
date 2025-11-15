from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from langchain.tools import tool

from downes.model import call_llm
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
        - Produces a structured syllabus outline with modules mapped to learning objectives,
          each including a description and suggested instructional strategies.
        - Returns a Markdown formatted syllabus.
    """
    header = _build_syllabus_header(
        course_title=course_title,
        duration_weeks=duration_weeks,
        modality=modality,
        prerequisites=prerequisites,
    )

    objectives_block = "\n".join(
        [f"{idx + 1}. {obj}" for idx, obj in enumerate(learning_objectives)]
    )

    prereq_block = "\n".join(prerequisites or ["None specified"])

    system_prompt = """You are a curriculum designer. Draft a concise module-by-module syllabus outline.\nReturn Markdown that uses `### Module X: Title` headings in order and, for each module, include:\n- A 1-2 sentence summary\n- Bullet list of 2-3 aligned objectives pulled or remixed from the provided list\n- Bullet list of signature learning activities\n- A single formative or summative assessment idea\nKeep tone practical and avoid extra commentary outside of the requested structure."""

    user_prompt = f"""Course title: {course_title}\nDuration: {duration_weeks} weeks\nModality: {modality}\nModules to create: {modules_count}\nPrerequisites:\n{prereq_block}\n\nLearning objectives to align:\n{objectives_block}"""

    try:
        response = call_llm(user_prompt, system_prompt=system_prompt)
        if response and hasattr(response, "content"):
            content = response.content.strip()
            if content:
                return f"{header}{content}"
    except Exception:
        pass

    return _fallback_syllabus(
        course_title,
        learning_objectives,
        duration_weeks,
        modality,
        prerequisites,
        modules_count,
    )


def _build_syllabus_header(
    course_title: str,
    duration_weeks: int,
    modality: str,
    prerequisites: Optional[List[str]],
) -> str:
    lines = [
        f"# {course_title} - Syllabus",
        "",
        "## Course Information",
        "",
        f"- **Duration:** {duration_weeks} weeks",
        f"- **Modality:** {modality.capitalize()}",
    ]

    if prerequisites:
        lines.extend(["", "### Prerequisites", ""])
        lines.extend([f"- {prereq}" for prereq in prerequisites])

    lines.extend(["", "## Course Modules", "", ""])
    return "\n".join(lines)


def _fallback_syllabus(
    course_title: str,
    learning_objectives: List[str],
    duration_weeks: int,
    modality: str,
    prerequisites: Optional[List[str]],
    modules_count: int,
) -> str:
    """Legacy procedural syllabus generator used when LLM output is unavailable."""
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
        lines.extend(["", "### Prerequisites", ""])
        for prereq in prerequisites:
            lines.append(f"- {prereq}")

    lines.extend(["", "## Course Modules", "", ""])

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
                "**Summary:**",
                "",
                f"   Introduces foundational elements of {course_title} with focus on applied understanding.",
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
