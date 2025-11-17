from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from langchain.tools import tool

from downes.model import call_llm
from .utils import normalize_list_input


DEFAULT_SLIDE_SECTIONS = [
    "Hook & Purpose",
    "Essential Concepts",
    "Application & Practice",
    "Reflection & Next Steps",
]


class SlideDeckInput(BaseModel):
    topic: str = Field(description="Title or focus for the slide deck.")
    audience: str = Field(description="Intended learner audience.")
    duration_minutes: int = Field(
        default=45,
        description="Approximate delivery time in minutes.",
    )
    slide_count: int = Field(
        default=8,
        ge=4,
        le=30,
        description="Approximate number of slides to produce.",
    )
    learning_objectives: Optional[List[str]] = Field(
        default=None,
        description="Optional learning objectives to thread across slides.",
    )
    slide_sections: Optional[List[str]] = Field(
        default=None,
        description="Custom slide section labels to guide structure.",
    )
    call_to_action: Optional[str] = Field(
        default=None,
        description="Optional closing call-to-action or assignment.",
    )
    include_notes: bool = Field(
        default=True,
        description="Include presenter notes beneath each slide when True.",
    )
    tone: str = Field(
        default="approachable",
        description="Tone or narrative style for the deck (e.g., inspiring, practical).",
    )

    @field_validator("learning_objectives", mode="before")
    @classmethod
    def normalize_objectives(cls, value):
        return normalize_list_input(value, default=None)

    @field_validator("slide_sections", mode="before")
    @classmethod
    def normalize_sections(cls, value):
        result = normalize_list_input(value, default=None)
        return result or None


@tool(args_schema=SlideDeckInput)
def build_slide_deck(
    topic: str,
    audience: str,
    duration_minutes: int = 45,
    slide_count: int = 8,
    learning_objectives: Optional[List[str]] = None,
    slide_sections: Optional[List[str]] = None,
    call_to_action: Optional[str] = None,
    include_notes: bool = True,
    tone: str = "approachable",
) -> str:
    """Generate reveal.js-ready Markdown slides for a lesson or talk."""

    sections = slide_sections or DEFAULT_SLIDE_SECTIONS
    total_slides = max(slide_count, len(sections))

    system_prompt = """You are an instructional designer who writes Reveal.js Markdown slide decks.\nRules:\n- Start with a title slide containing # Title and key metadata as bullet list or subheading.\n- Separate slides using a line that contains only --- and a blank line after.\n- Each content slide must start with ## Slide Title.\n- Include short bullet lists or concise paragraphs only; keep each slide under 60 words.\n- When notes are requested, add a blank line followed by Notes: and a short presenter note.\n- Mirror the provided slide sections and learning objectives succinctly.\n- Do not wrap the response in triple backticks or commentary."""

    objectives_text = "\n".join(learning_objectives or []) or "Emphasize key takeaways and applied practice."
    sections_text = " | ".join(sections)

    user_prompt = (
        f"Topic: {topic}\n"
        f"Audience: {audience}\n"
        f"Duration: {duration_minutes} minutes\n"
        f"Desired tone: {tone}\n"
        f"Include presenter notes: {'yes' if include_notes else 'no'}\n"
        f"Requested slide count: {total_slides}\n"
        f"Slide sections to emphasize (ordered): {sections_text}\n"
        f"Learning objectives to weave in:\n{objectives_text}\n\n"
    )

    if call_to_action:
        user_prompt += f"Closing call-to-action: {call_to_action}\n"

    try:
        response = call_llm(user_prompt, system_prompt=system_prompt)
        if response and hasattr(response, "content"):
            content = response.content.strip()
            if content:
                return content
    except Exception:
        pass

    return _fallback_slide_deck(
        topic=topic,
        audience=audience,
        duration_minutes=duration_minutes,
        slide_count=total_slides,
        sections=sections,
        learning_objectives=learning_objectives,
        include_notes=include_notes,
        call_to_action=call_to_action,
    )


def _fallback_slide_deck(
    topic: str,
    audience: str,
    duration_minutes: int,
    slide_count: int,
    sections: List[str],
    learning_objectives: Optional[List[str]],
    include_notes: bool,
    call_to_action: Optional[str],
) -> str:
    """Deterministic reveal.js flavored fallback when LLM output is unavailable."""

    objectives = learning_objectives or [
        "Highlight why the topic matters",
        "Model a key concept",
        "Prompt discussion or application",
        "Offer a concrete next step",
    ]

    lines: List[str] = [
        f"# {topic}",
        "",
        f"### Audience: {audience}",
        f"- Duration: {duration_minutes} minutes",
        f"- Focus: {objectives[0]}",
        "",
        "---",
        "",
    ]

    for idx in range(slide_count):
        section_title = sections[idx] if idx < len(sections) else f"Deep Dive {idx + 1}"
        objective = objectives[idx % len(objectives)]
        lines.extend(
            [
                f"## Slide {idx + 1}: {section_title}",
                "",
                f"- Reinforce: {objective}",
                "- Pose a quick question or micro-task",
                "- Invite a brief share-out",
                "",
            ]
        )
        if include_notes:
            lines.extend(
                [
                    "Notes:",
                    f"Guide learners through {section_title.lower()} and tie it back to the session arc.",
                    "",
                ]
            )
        lines.extend(["---", "",])

    lines.extend([
        "## Slide Finale: Commit to Action",
        "",
        f"- {call_to_action or 'Encourage participants to apply the lesson within 48 hours.'}",
        "- Offer a way to follow up or share evidence",
        "",
    ])
    if include_notes:
        lines.extend(["Notes:", "Close with gratitude and point to follow-up support."])

    return "\n".join(lines)
