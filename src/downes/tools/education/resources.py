import json
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from langchain.tools import tool

from downes.model import call_llm
from .utils import normalize_list_input


class SynthesizeResourcesInput(BaseModel):
    model_config = ConfigDict(extra="allow")
    topic: str = Field(description="Primary subject or focus area.")
    resource_types: Optional[List[str]] = Field(
        default=None,
        description="Desired resource types (article, video, dataset, repo).",
    )
    max_items: int = Field(default=8, description="Maximum number of resources.")
    searx_results_markdown: Optional[str] = Field(
        default=None,
        description="Raw Markdown output from searx_search for grounding real URLs.",
    )
    searx_results: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Structured SearXNG results with keys like title/url/snippet.",
    )

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


@tool(args_schema=SynthesizeResourcesInput)
def synthesize_learning_resources(
    topic: str,
    resource_types: Optional[List[str]] = None,
    max_items: int = 8,
    searx_results_markdown: Optional[str] = None,
    searx_results: Optional[List[Dict[str, Any]]] = None,
    **kwargs,
) -> str:
    """
        - Generates a synthesized list of learning resources to be searched for.
        - The list is tailored to the specified topic and resource types.
        - Returns Markdown formatted resource list.

        - If provided, uses searx_search results to ground real URLs. 
          Otherwise, the agent may search for resources using search tools.
    """
    resource_types = resource_types or ["article", "video", "repository", "dataset"]

    seed_resources = _collect_seed_resources(
        searx_results=searx_results,
        searx_results_markdown=searx_results_markdown,
        extra_inputs=kwargs,
    )

    synthesized_entries: List[Dict[str, str]] = []

    if seed_resources:
        synthesized_entries = _curate_seed_resources(
            topic=topic,
            seed_resources=seed_resources,
            resource_types=resource_types,
            max_items=max_items,
        )

    if not synthesized_entries:
        synthesized_entries = _llm_generate_resources(
            topic=topic,
            resource_types=resource_types,
            max_items=max_items,
        )

    if synthesized_entries:
        return _render_resources(topic, synthesized_entries, len(synthesized_entries))

    return _fallback_resources(topic, resource_types, max_items)


def _collect_seed_resources(
    searx_results: Optional[List[Dict[str, Any]]],
    searx_results_markdown: Optional[str],
    extra_inputs: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Gather structured resource candidates from various inputs."""
    def _coerce_list(value) -> List[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                return []
            try:
                parsed = json.loads(cleaned)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return []
        return []

    structured_candidates: List[Any] = []
    for candidate in [
        searx_results,
        extra_inputs.get("searx_results"),
        extra_inputs.get("search_results"),
        extra_inputs.get("resources"),
        extra_inputs.get("hits"),
    ]:
        structured_candidates.extend(_coerce_list(candidate))

    markdown_blobs = [
        searx_results_markdown,
        extra_inputs.get("searx_results_markdown"),
        extra_inputs.get("search_results_markdown"),
        extra_inputs.get("searx_output"),
    ]

    entries: List[Dict[str, Any]] = []
    for blob in structured_candidates:
        if hasattr(blob, "model_dump"):
            entries.append(blob.model_dump())
        elif isinstance(blob, dict):
            entries.append(blob)

    for text in markdown_blobs:
        if isinstance(text, str) and text.strip():
            entries.extend(_parse_markdown_links(text))

    normalized = _normalize_seed_entries(entries)
    for idx, entry in enumerate(normalized, start=1):
        entry["id"] = idx
    return normalized[:50]


def _normalize_seed_entries(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    seen_urls: set[str] = set()
    for cand in candidates:
        data: Dict[str, Any] = {}
        if isinstance(cand, dict):
            data["title"] = cand.get("title") or cand.get("name")
            data["url"] = cand.get("url") or cand.get("link")
            data["snippet"] = (
                cand.get("snippet")
                or cand.get("summary")
                or cand.get("description")
            )
            data["source"] = cand.get("source")
            data["type"] = cand.get("type")
        elif isinstance(cand, tuple) and len(cand) >= 2:
            data["title"], data["url"] = cand[:2]
            data["snippet"] = cand[2] if len(cand) > 2 else None
            data["source"] = None
            data["type"] = None
        else:
            continue

        url = (data.get("url") or "").strip()
        if not url or not url.startswith("http"):
            continue
        if url in seen_urls:
            continue

        seen_urls.add(url)
        normalized.append(
            {
                "title": (data.get("title") or "Untitled resource").strip(),
                "url": url,
                "snippet": data.get("snippet"),
                "source": data.get("source") or _infer_source_from_url(url),
                "type": data.get("type"),
            }
        )

    return normalized


def _parse_markdown_links(markdown_text: str) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    pattern = r"(?:^|\n)\s*(?:-\s*|\d+\.\s*)\[(.+?)\]\((https?://[^)]+)\)"
    for match in re.finditer(pattern, markdown_text):
        title, url = match.groups()
        entries.append({"title": title.strip(), "url": url.strip()})
    return entries


def _curate_seed_resources(
    topic: str,
    seed_resources: List[Dict[str, Any]],
    resource_types: List[str],
    max_items: int,
) -> List[Dict[str, str]]:
    limited = seed_resources[:max_items]
    metadata_map = _summarize_seed_resources(topic, limited)
    synthesized: List[Dict[str, str]] = []

    for entry in limited:
        meta = metadata_map.get(entry["id"], {})
        inferred_type = (
            meta.get("type")
            or entry.get("type")
            or _infer_type_from_url(entry["url"], resource_types)
        )
        type_label = (str(inferred_type) if inferred_type else "article").title()
        synthesized.append(
            {
                "title": meta.get("title") or entry["title"],
                "type": type_label,
                "source": meta.get("source")
                or entry.get("source")
                or _infer_source_from_url(entry["url"]),
                "url": entry["url"],
                "summary": meta.get("summary") or entry.get("snippet") or "Summary forthcoming.",
                "suggested_use": meta.get("suggested_use") or "Use in a flipped lesson or discussion.",
            }
        )

    return synthesized


def _summarize_seed_resources(
    topic: str, seed_resources: List[Dict[str, Any]]
) -> Dict[int, Dict[str, str]]:
    if not seed_resources:
        return {}

    payload = [
        {
            "id": entry["id"],
            "title": entry["title"],
            "url": entry["url"],
            "snippet": entry.get("snippet"),
        }
        for entry in seed_resources
    ]

    system_prompt = """
        You are an educational librarian.
        Given real search hits, enrich their metadata for curriculum planning.
        Return ONLY JSON: {{"resources": [{{"id": int, "title": str, "type": str, "summary": str, "suggested_use": str}}]}}.
        Rules:
        - Keep IDs exactly as provided
        - Do NOT invent or modify URLs (they are handled separately)
        - Titles can be lightly rephrased for clarity
        - Types must be short labels like article, video, dataset, repository, toolkit
        - Summaries limited to one sentence
        - Suggested use should mention how an educator might apply it.
        """

    user_prompt = (
        f"Topic: {topic}\n"
        "Resources to enrich:\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )

    try:
        response = call_llm(user_prompt, system_prompt=system_prompt)
        if response and hasattr(response, "content"):
            data = _parse_seed_metadata(response.content)
            return data
    except Exception:
        return {}

    return {}


def _parse_seed_metadata(raw_content: str) -> Dict[int, Dict[str, str]]:
    text = raw_content.strip()
    fence_match = re.search(r"```json(.*?)```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    elif text.startswith("```") and text.endswith("```"):
        text = text[3:-3]

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {}

    if isinstance(data, list):
        resources = data
    elif isinstance(data, dict) and isinstance(data.get("resources"), list):
        resources = data["resources"]
    else:
        return {}

    output: Dict[int, Dict[str, str]] = {}
    for item in resources:
        if not isinstance(item, dict):
            continue
        rid = item.get("id")
        if isinstance(rid, int):
            output[rid] = item
    return output


def _llm_generate_resources(
    topic: str,
    resource_types: List[str],
    max_items: int,
) -> List[Dict[str, str]]:
    system_prompt = """
    You are an educational librarian. Synthesize accessible, high-quality learning resources for the requested topic.
        Return ONLY valid JSON matching:
        {"resources": [{"title": str, "type": str, "source": str, "url": str, "summary": str, "suggested_use": str}]}
        - Provide exactly the requested number of items when possible
        - Favor openly available or widely known sources
        - Keep summaries to one sentence
        - Invent plausible yet generic sources/URLs if unsure (e.g., example.edu/article).
    """

    user_prompt = (
        f"Topic: {topic}\n"
        f"Requested resource count: {max_items}\n"
        f"Preferred resource types: {', '.join(resource_types)}\n"
        "Audience context: general educators seeking reusable materials."
    )

    try:
        response = call_llm(user_prompt, system_prompt=system_prompt)
        if response and hasattr(response, "content"):
            entries = _parse_resource_payload(response.content, max_items)
            return entries
    except Exception:
        return []

    return []


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
                "title": item.get("title") or "Synthesized Resource",
                "type": item.get("type") or "Article",
                "source": item.get("source") or "TBD",
                "url": item.get("url") or "TBD",
                "summary": item.get("summary") or item.get("description") or "Summary forthcoming.",
                "suggested_use": item.get("suggested_use") or "Use as a discussion catalyst.",
            }
        )

    return entries


def _infer_source_from_url(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        return host or "Unknown source"
    except Exception:
        return "Unknown source"


def _infer_type_from_url(url: str, resource_types: List[str]) -> str:
    lower = url.lower()
    if any(token in lower for token in ["youtube", "vimeo", ".mp4", ".mov", "watch?v="]):
        return "video"
    if any(lower.endswith(ext) for ext in [".csv", ".tsv", ".json", ".xlsx", ".zip"]):
        return "dataset"
    if any(token in lower for token in ["github.com", "gitlab", "bitbucket"]):
        return "repository"
    if any(token in lower for token in ["lesson", "curriculum", "guide", "module"]):
        return "lesson"
    if resource_types:
        return resource_types[0]
    return "article"


def _render_resources(topic: str, entries: List[dict], entry_count: int) -> str:
    lines = [
        "## Synthesized Learning Resources",
        "",
        f"**Topic:** {topic}",
        f"**Resource Count:** {entry_count}",
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
        "## Synthesized Learning Resources",
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
