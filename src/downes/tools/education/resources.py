from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from langchain.tools import tool

from .utils import normalize_list_input


class CurateResourcesInput(BaseModel):
    model_config = ConfigDict(extra="allow")
    topic: str = Field(description="Primary subject or focus area.")
    resource_types: Optional[List[str]] = Field(
        default=None,
        description="Desired resource types (article, video, dataset, repo).",
    )
    max_items: int = Field(default=8, description="Maximum number of resources.")

    @model_validator(mode="before")
    @classmethod
    def _ensure_topic(cls, data):
        if isinstance(data, dict):
            if not data.get("topic"):
                for k in ["query", "course_title", "subject", "title"]:
                    if data.get(k):
                        data["topic"] = data[k]
                        break
                if not data.get("topic"):
                    data["topic"] = "General"
        return data

    @field_validator("resource_types", mode="before")
    @classmethod
    def normalize_resource_types(cls, v):
        """Normalize resource_types from various formats."""
        return normalize_list_input(v, default=None)


@tool(args_schema=CurateResourcesInput)
def curate_learning_resources(
    topic: str, resource_types: Optional[List[str]] = None, max_items: int = 8, **kwargs
) -> str:
    """
    Generates a curated placeholder set of learning resources (metadata only) for a topic.
    The agent can later refine or replace entries via external search tools.
    Returns Markdown formatted resource list.
    """
    types = resource_types or ["article", "video", "repository", "dataset"]

    descriptors = {
        "article": {
            "label": "Feature Article",
            "uses": [
                "Introduce core concepts",
                "Support flipped learning",
                "Extend independent study",
                "Anchor a seminar discussion",
            ],
        },
        "video": {
            "label": "Video Lesson",
            "uses": [
                "Model software workflow",
                "Demonstrate techniques",
                "Provide guided practice",
                "Flip the classroom warm-up",
            ],
        },
        "repository": {
            "label": "Project Repository",
            "uses": [
                "Offer starter files",
                "Share remix-ready assets",
                "Provide reference implementations",
                "Support capstone build",
            ],
        },
        "dataset": {
            "label": "Practice Dataset",
            "uses": [
                "Enable exploratory analysis",
                "Support performance tasks",
                "Feed applied labs",
                "Back project-based learning",
            ],
        },
    }

    focus_phrases = [
        "fundamentals",
        "creative workflow",
        "classroom implementation",
        "assessment alignment",
        "differentiation",
        "student showcase",
        "extension challenge",
        "reflection prompts",
    ]

    lines = [
        "## Curated Learning Resources",
        "",
        f"**Topic:** {topic}",
        f"**Resource Count:** {max_items}",
        "",
        "### Resources",
        "",
    ]

    for i in range(max_items):
        kind = types[i % len(types)]
        meta = descriptors.get(kind, descriptors["article"])
        use = meta["uses"][i % len(meta["uses"])]
        focus = focus_phrases[i % len(focus_phrases)]

        lines.extend(
            [
                f"#### {i + 1}. {topic}: {meta['label']} on {focus.capitalize()}",
                "",
                f"- **Type:** {kind.capitalize()}",
                f"- **Source:** Placeholder (replace with vetted source)",
                f"- **URL:** TBD",
                f"- **Suggested Use:** {use}",
                "- **Quality Notes:** Verify accuracy and accessibility before sharing",
                "",
            ]
        )

    lines.append(
        "_Tip: Replace placeholders with vetted resources from `searx_search` results to personalize this list._"
    )

    return "\n".join(lines)
