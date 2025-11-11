import os
from typing import List, Optional
import requests
from langchain.tools import tool
from pydantic import BaseModel, Field
from datetime import datetime

from downes.tools.search.models import SearchResult


class SearxSearchInput(BaseModel):
    query: str = Field(description="Search query (education/topic keywords).")
    max_results: int = Field(
        default=10, description="Maximum number of results to return."
    )
    categories: Optional[List[str]] = Field(
        default=None,
        description="Optional SearXNG categories (e.g., ['science','files','it']).",
    )
    language: str = Field(
        default="en", description="Language code for results (RFC 5646)."
    )
    instance_url: Optional[str] = Field(
        default=None,
        description="Override SEARXNG_INSTANCE_URL env var with a specific instance base URL.",
    )
    safe: bool = Field(
        default=True, description="Enable SearXNG safe search filtering if supported."
    )
    education_bias: bool = Field(
        default=True,
        description="If True, expands query with curriculum / pedagogy modifiers.",
    )


@tool(args_schema=SearxSearchInput)
def searx_search(
    query: str,
    max_results: int = 10,
    categories: Optional[List[str]] = None,
    language: str = "en",
    instance_url: Optional[str] = None,
    safe: bool = True,
    education_bias: bool = True,
) -> List[SearchResult]:
    """
    Perform a meta-search via a SearXNG instance, returning normalized search results.

    Features:
    - Education bias adds terms like curriculum, syllabus, "learning objectives", rubric, OER
    - Uses JSON API output from SearXNG
    - Respects categories if provided

    Configuration:
    - Set SEARXNG_INSTANCE_URL env var to e.g. https://searx.tiekoetter.com
    - Tool parameter instance_url overrides the environment variable
    """
    base = instance_url or os.getenv("SEARXNG_INSTANCE_URL")
    if not base:
        # No instance configured; fail gracefully with empty list.
        return []
    base = base.rstrip("/")

    expanded_query = query
    if education_bias:
        edu_terms = [
            'curriculum',
            'syllabus',
            '"learning objectives"',
            '"lesson plan"',
            'rubric',
            'OER',
            '"open educational resources"',
        ]
        expanded_query = f"{query} (" + " OR ".join(edu_terms) + ")"

    params = {
        "q": expanded_query,
        "format": "json",
        "language": language,
        "safesearch": 1 if safe else 0,
        "categories": ",".join(categories) if categories else None,
    }
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    try:
        resp = requests.get(f"{base}/search", params=params, timeout=15)
    except Exception:
        return []
    if resp.status_code != 200:
        return []
    try:
        data = resp.json()
    except Exception:
        return []

    results: List[SearchResult] = []
    for r in data.get("results", [])[: max_results * 2]:
        # Basic filtering for missing fields
        title = r.get("title") or "Untitled"
        url = r.get("url") or r.get("link") or ""
        if not url:
            continue
        # Attempt to parse a date-like field if present
        published_date = None
        for key in ["publishedDate", "published", "date"]:
            if key in r and isinstance(r[key], str):
                try:
                    published_date = datetime.fromisoformat(r[key].replace("Z", "+00:00"))
                except Exception:
                    published_date = None
        results.append(SearchResult(title=title, url=url, published_date=published_date))
        if len(results) >= max_results:
            break
    return results
