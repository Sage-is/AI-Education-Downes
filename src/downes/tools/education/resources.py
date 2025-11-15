import json
import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from langchain.tools import tool

from downes.model import call_llm
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
        - Generates a curated placeholder set of learning resources (metadata only) for a topic.
        - The agent can later refine or replace entries via external search tools.
        - Returns Markdown formatted resource list.
    """
    resource_types = resource_types or ["article", "video", "repository", "dataset"]

    system_prompt = """You are an educational librarian. Curate accessible, high-quality learning resources for the requested topic.\nReturn ONLY valid JSON matching:\n{"resources": [{"title": str, "type": str, "source": str, "url": str, "summary": str, "suggested_use": str}]}\n- Provide exactly the requested number of items when possible\n- Favor openly available or widely known sources\n- Keep summaries to one sentence\n- Invent plausible yet generic sources/URLs if unsure (e.g., example.edu/article)."""

    user_prompt = f"""Topic: {topic}\nRequested resource count: {max_items}\nPreferred resource types: {', '.join(resource_types)}\nAudience context: general educators seeking reusable materials."""

    try:
        response = call_llm(user_prompt, system_prompt=system_prompt)
        if response and hasattr(response, "content"):
            entries = _parse_resource_payload(response.content, max_items)
            if entries:
                return _render_resources(topic, entries, max_items)
    except Exception:
        pass

    return _fallback_resources(topic, resource_types, max_items)


def _parse_resource_payload(raw_content: str, max_items: int) -> List[dict]:
    """Extract a list of resource dictionaries from the LLM response."""
    text = raw_content.strip()
    fence_match = re.search(r"```json(.*?)```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    elif text.startswith("```") and text.endswith("```"):
        text = text[3:-3]

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []

    if isinstance(data, dict) and "resources" in data:
        data = data["resources"]

    if not isinstance(data, list):
        return []

    entries = []
    for item in data[:max_items]:
        if not isinstance(item, dict):
            continue
        entries.append(
            {
                "title": item.get("title") or "Curated Resource",
                "type": item.get("type") or "Article",
                "source": item.get("source") or "TBD",
                "url": item.get("url") or "TBD",
                "summary": item.get("summary") or item.get("description") or "Summary forthcoming.",
                "suggested_use": item.get("suggested_use") or "Use as a discussion catalyst.",
            }
        )

    return entries


def _render_resources(topic: str, entries: List[dict], max_items: int) -> str:
    lines = [
        "## Curated Learning Resources",
        "",
        f"**Topic:** {topic}",
        f"**Resource Count:** {max_items}",
        "",
        "### Resources",
        "",
    ]

    for idx, entry in enumerate(entries, 1):
        lines.extend(
            [
                f"#### {idx}. {entry['title']}",
                "",
                f"- **Type:** {entry['type']}",
                f"- **Source:** {entry['source']}",
                f"- **URL:** {entry['url']}",
                f"- **Summary:** {entry['summary']}",
                f"- **Suggested Use:** {entry['suggested_use']}",
                "",
            ]
        )

    lines.append(
        "_Tip: Replace or enrich entries with live search results for your learners' context._"
    )
    return "\n".join(lines)


def _fallback_resources(topic: str, resource_types: List[str], max_items: int) -> str:
    """Deterministic placeholder list used when the LLM output is unavailable."""
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
                "Model workflow",
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
                "Support performance steps",
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
        kind = resource_types[i % len(resource_types)] if resource_types else "article"
        meta = descriptors.get(kind, descriptors["article"])
        use = meta["uses"][i % len(meta["uses"])]
        focus = focus_phrases[i % len(focus_phrases)]

        lines.extend(
            [
                f"#### {i + 1}. {topic}: {meta['label']} on {focus.capitalize()}",
                "",
                f"- **Type:** {kind.capitalize()}",
                "- **Source:** Placeholder (replace with vetted source)",
                "- **URL:** TBD",
                f"- **Suggested Use:** {use}",
                "- **Quality Notes:** Verify accuracy and accessibility before sharing",
                "",
            ]
        )

    lines.append(
        "_Tip: Replace placeholders with vetted resources from `searx_search` results to personalize this list._"
    )

    return "\n".join(lines)
