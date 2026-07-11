from typing import Optional

from langchain.tools import tool
from pydantic import BaseModel, Field

from downes.model import call_llm
from downes.profile import load_profile
from downes.tools.web.url import fetch_url

_PROFILE = load_profile()


class VerifyAndSummarizeInput(BaseModel):
    url: str = Field(description="The URL to verify and summarize.")
    topic: Optional[str] = Field(
        default=None,
        description="What to assess relevance against. Defaults to the agent's focus area.",
    )
    audience: Optional[str] = Field(
        default=None,
        description="Target audience (e.g., 'Grade 9 students', 'adult learners').",
    )


_VERIFY_SYSTEM_PROMPT = """\
You are a resource evaluator. Given fetched web page content and a topic, produce a \
structured assessment of the page and its relevance to that topic.

Return your response in EXACTLY this format (keep the labels):

SUMMARY: A 2-3 sentence summary of the page content.
KEY_CONCEPTS: A comma-separated list of 3-7 key concepts covered.
RELEVANCE: High, Medium, or Low
RELEVANCE_REASON: One sentence explaining the relevance rating.
SUGGESTED_USE: One sentence suggesting how this resource could be used.
CONTENT_TYPE: One of: article, video, interactive, dataset, course, reference, tool, other
QUALITY_NOTES: Brief note on content quality, recency, or caveats.\
"""


def _parse_verification_response(text: str) -> dict:
    """Parse the structured LLM response into a dict of fields."""
    fields = {}
    for line in text.strip().splitlines():
        for key in [
            "SUMMARY",
            "KEY_CONCEPTS",
            "RELEVANCE",
            "RELEVANCE_REASON",
            "SUGGESTED_USE",
            "CONTENT_TYPE",
            "QUALITY_NOTES",
        ]:
            if line.startswith(f"{key}:"):
                fields[key] = line[len(key) + 1 :].strip()
                break
    return fields


@tool(args_schema=VerifyAndSummarizeInput)
def verify_and_summarize(
    url: str, topic: Optional[str] = None, audience: Optional[str] = None
) -> str:
    """Fetch a URL, verify it is accessible, and produce a structured summary with a
    relevance assessment. If no topic is given, relevance is judged against the
    agent's focus area."""
    topic = topic or _PROFILE.focus
    # 1. Fetch the URL using the enhanced fetch_url tool
    fetched = fetch_url.invoke({"url": url})

    # 2. Detect dead links
    is_dead = "(DEAD LINK)" in fetched or fetched.startswith("Error fetching URL")
    if is_dead:
        return (
            f"## Source Verification: {url}\n\n"
            f"**Accessible:** No\n"
            f"**Relevance to '{topic}':** N/A\n\n"
            f"### Details\n"
            f"{fetched}"
        )

    # 3. Build LLM prompt with capped content
    content_for_llm = fetched[:12000]
    audience_line = f"\nTarget audience: {audience}" if audience else ""
    user_prompt = (
        f"Topic: {topic}{audience_line}\n\n"
        f"--- Fetched Content ---\n{content_for_llm}"
    )

    # 4. Call LLM for structured assessment
    try:
        response = call_llm(user_prompt, system_prompt=_VERIFY_SYSTEM_PROMPT)
        if response and hasattr(response, "content"):
            fields = _parse_verification_response(response.content)
        else:
            fields = {}
    except Exception:
        fields = {}

    # 5. Build structured output
    summary = fields.get("SUMMARY", "Summary not available.")
    key_concepts = fields.get("KEY_CONCEPTS", "N/A")
    relevance = fields.get("RELEVANCE", "Unknown")
    relevance_reason = fields.get("RELEVANCE_REASON", "")
    suggested_use = fields.get("SUGGESTED_USE", "")
    content_type = fields.get("CONTENT_TYPE", "unknown")
    quality_notes = fields.get("QUALITY_NOTES", "")

    parts = [
        f"## Source Verification: {url}\n",
        f"**Accessible:** Yes",
        f"**Content Type:** {content_type}",
        f"**Relevance to '{topic}':** {relevance}",
        "",
        f"### Summary",
        summary,
        "",
        f"### Key Concepts",
        key_concepts,
        "",
        f"### Relevance Assessment",
        relevance_reason,
        "",
        f"### Suggested Use",
        suggested_use,
        "",
        f"### Quality Notes",
        quality_notes,
    ]

    return "\n".join(parts)
