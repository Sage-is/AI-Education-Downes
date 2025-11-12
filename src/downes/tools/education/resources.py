from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from langchain.tools import tool


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
    def _coerce_resource_types(cls, v):
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
            return [s.strip() for s in v.split(",") if s.strip()]
        return v


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
        suggested_use = (
            "Introduce concept" if kind == "article" else "Hands-on practice"
        )

        lines.extend(
            [
                f"#### {i+1}. {topic} {kind.title()} Resource {i+1}",
                "",
                f"- **Type:** {kind.capitalize()}",
                f"- **Source:** Placeholder",
                f"- **URL:** TBD",
                f"- **Suggested Use:** {suggested_use}",
                f"- **Quality Notes:** Needs verification",
                "",
            ]
        )

    return "\n".join(lines)
