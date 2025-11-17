from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from langchain.tools import tool

from downes.model import call_llm
from .utils import MarkdownBuilder, normalize_list_input


DEFAULT_WORKSHEET_SECTIONS = [
    "Warm-Up Prompt",
    "Guided Practice",
    "Apply & Create",
    "Reflection & Exit Ticket",
]

DEFAULT_DIFFERENTIATION = ["All Learners", "Needs Support", "Ready for More"]


class WorksheetInput(BaseModel):
    topic: str = Field(description="Primary topic or theme for the worksheet.")
    audience: str = Field(description="Intended learners (grade level or profile).")
    skill_focus: str = Field(description="Core skill, standard, or competency emphasized.")
    estimated_time_minutes: int = Field(
        default=30,
        description="Approximate time for completion.",
    )
    learning_objectives: Optional[List[str]] = Field(
        default=None, description="Objectives the worksheet reinforces."
    )
    materials: Optional[List[str]] = Field(
        default=None, description="Optional materials or tools required."
    )
    sections: Optional[List[str]] = Field(
        default=None,
        description="Specific worksheet sections or activity titles to include.",
    )
    differentiation_tiers: Optional[List[str]] = Field(
        default=None,
        description="Labels for differentiation suggestions (e.g., All Learners, Supports).",
    )
    include_answer_key: bool = Field(
        default=True,
        description="Append a brief answer key when True.",
    )

    @field_validator("learning_objectives", mode="before")
    @classmethod
    def normalize_objectives(cls, value):
        return normalize_list_input(value, default=None)

    @field_validator("materials", mode="before")
    @classmethod
    def normalize_materials(cls, value):
        return normalize_list_input(value, default=None)

    @field_validator("sections", mode="before")
    @classmethod
    def normalize_sections(cls, value):
        result = normalize_list_input(value, default=None)
        return result or None

    @field_validator("differentiation_tiers", mode="before")
    @classmethod
    def normalize_differentiation(cls, value):
        result = normalize_list_input(value, default=None)
        return result or None


@tool(args_schema=WorksheetInput)
def design_worksheet(
    topic: str,
    audience: str,
    skill_focus: str,
    estimated_time_minutes: int = 30,
    learning_objectives: Optional[List[str]] = None,
    materials: Optional[List[str]] = None,
    sections: Optional[List[str]] = None,
    differentiation_tiers: Optional[List[str]] = None,
    include_answer_key: bool = True,
) -> str:
    """Create a clear, classroom-ready worksheet in Markdown."""

    section_labels = sections or DEFAULT_WORKSHEET_SECTIONS
    tiers = differentiation_tiers or DEFAULT_DIFFERENTIATION

    system_prompt = """You create printable worksheets for educators using Markdown.\nStructure requirements:\n1. Title slide style header: # Worksheet: <topic>.\n2. Overview block that lists audience, skill focus, estimated time, and materials as bullets.\n3. One section per provided label with `## <Section>` heading containing: \n   - 1 sentence framing text.\n   - 2-3 numbered tasks or prompts aligned to objectives.\n   - Optional mini-table or checklist when it strengthens clarity.\n4. Include a `### Differentiation` section with one bullet per tier that explains how to adapt a task.\n5. If an answer key is requested, end with `### Answer Key` summarizing expected responses.\n6. Avoid extra commentary, YAML, or fenced code blocks.\n7. Keep tone encouraging and directions student-facing."""

    objectives_block = "\n".join(learning_objectives or []) or "Support learners in demonstrating understanding."
    materials_block = ", ".join(materials or ["Pencil", "Notebook"])
    sections_line = " | ".join(section_labels)

    user_prompt = (
        f"Topic: {topic}\n"
        f"Audience: {audience}\n"
        f"Skill focus: {skill_focus}\n"
        f"Estimated time: {estimated_time_minutes} minutes\n"
        f"Worksheet sections (in order): {sections_line}\n"
        f"Learning objectives to emphasize:\n{objectives_block}\n\n"
        f"Materials: {materials_block}\n"
        f"Differentiation tiers: {', '.join(tiers)}\n"
        f"Include answer key: {'yes' if include_answer_key else 'no'}"
    )

    try:
        response = call_llm(user_prompt, system_prompt=system_prompt)
        if response and hasattr(response, "content"):
            content = response.content.strip()
            if content:
                return content
    except Exception:
        pass

    return _fallback_worksheet(
        topic=topic,
        audience=audience,
        skill_focus=skill_focus,
        estimated_time_minutes=estimated_time_minutes,
        learning_objectives=learning_objectives,
        materials=materials,
        section_labels=section_labels,
        tiers=tiers,
        include_answer_key=include_answer_key,
    )


def _fallback_worksheet(
    topic: str,
    audience: str,
    skill_focus: str,
    estimated_time_minutes: int,
    learning_objectives: Optional[List[str]],
    materials: Optional[List[str]],
    section_labels: List[str],
    tiers: List[str],
    include_answer_key: bool,
) -> str:
    builder = MarkdownBuilder()
    objectives = learning_objectives or [
        "Activate prior knowledge",
        "Practice the target skill",
        "Reflect on learning",
    ]

    builder.add_heading(f"Worksheet: {topic}")
    builder.add_heading("Overview", level=2)
    builder.add_bullet_list(
        [
            f"Audience: {audience}",
            f"Skill Focus: {skill_focus}",
            f"Estimated Time: {estimated_time_minutes} minutes",
            f"Materials: {', '.join(materials or ['Pencil', 'Notebook'])}",
        ]
    )

    builder.add_heading("Objectives", level=2)
    builder.add_bullet_list(objectives)

    for idx, section in enumerate(section_labels, 1):
        builder.add_heading(f"{idx}. {section}", level=2)
        builder.add_text(
            "Invite learners to engage directly with the concept, record thinking, and show evidence."
        )
        builder.add_blank()
        builder.add_numbered_list(
            [
                "Read or observe the scenario provided.",
                "Complete the prompt in your own words or sketches.",
                "Check your response with a partner or quick self-review.",
            ]
        )

    builder.add_heading("Differentiation", level=3)
    for tier in tiers:
        builder.add_text(f"- **{tier}:** Adjust the tasks with sentence starters, exemplars, or stretch goals.")
    builder.add_blank()

    builder.add_heading("Evidence Tracker", level=3)
    builder.add_table(
        headers=["Task", "Completed?", "Notes"],
        rows=[[f"Task {i+1}", "[ ]", ""] for i in range(len(section_labels))],
    )

    if include_answer_key:
        builder.add_heading("Answer Key", level=3)
        builder.add_text(
            "Provide model phrases or sample reasoning. Emphasize process over one correct answer."
        )

    return builder.build()
