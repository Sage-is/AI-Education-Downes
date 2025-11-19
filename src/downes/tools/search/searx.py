import os
from typing import List, Optional
import requests
from langchain.tools import tool
from pydantic import BaseModel, Field, field_validator, ConfigDict
from bs4 import BeautifulSoup

from downes.tools.search.models import SearchResult


class SearxSearchInput(BaseModel):
    model_config = ConfigDict(extra="allow")
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
    safe: bool = Field(
        default=True, description="Enable SearXNG safe search filtering if supported."
    )
    education_bias: bool = Field(
        default=True,
        description="If True, expands query with curriculum / pedagogy modifiers.",
    )

    @field_validator("safe", mode="before")
    @classmethod
    def _coerce_safe(cls, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            cleaned = v.split("#", 1)[0].strip()
            if not cleaned:
                return True
            return cleaned
        return v

    @field_validator("categories", mode="before")
    @classmethod
    def _coerce_categories(cls, v):
        if v is None:
            return None
        if isinstance(v, list):
            # Normalize and drop empties
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return None
            lower = s.lower()
            if lower in {"null", "none", "[]"}:
                return None
            # Try JSON first
            try:
                import json

                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if str(x).strip()]
            except Exception:
                pass
            # Fallback: comma-separated values
            parts = [p.strip() for p in s.split(",") if p.strip()]
            return parts or None
        # Unknown type – let pydantic handle or coerce to None
        return None


@tool(args_schema=SearxSearchInput)
def searx_search(
    query: str,
    max_results: int = 10,
    categories: Optional[List[str]] = None,
    language: str = "en",
    safe: bool = True,
    education_bias: bool = True,
) -> str:
    """
    - Perform a meta-search via a SearXNG instance and return Markdown-formatted results.
        - Education bias adds terms like curriculum, syllabus, "learning objectives", rubric, OER
        - Uses HTML parsing
        - Respects categories if provided

    """
    base = os.getenv("SEARXNG_INSTANCE_URL")
    if not base:
        return (
            "## SearXNG Search\n"
            "No SearXNG instance configured. Set `SEARXNG_INSTANCE_URL`."
        )
    base = base.rstrip("/")

    expanded_query = query
    if education_bias:
        edu_terms = [
            "curriculum",
            "syllabus",
            '"learning objectives"',
            '"lesson plan"',
            "rubric",
            "OER",
            '"open educational resources"',
        ]
        expanded_query = f"{query} (" + " OR ".join(edu_terms) + ")"

    params = {
        "q": expanded_query,
        "language": language,
        "safesearch": 1 if safe else 0,
        "categories": ",".join(categories) if categories else None,
    }
    params = {k: v for k, v in params.items() if v is not None}

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; DownesBot/1.0)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def render(results: List[SearchResult], error: Optional[str] = None) -> str:
        lines = [
            "## SearXNG Search",
            f"**Query:** {expanded_query}",
            "",
        ]
        if error:
            lines.extend(
                [
                    "_Search failed._",
                    f"Error: {error}",
                ]
            )
            return "\n".join(lines)

        if not results:
            lines.append("_No results returned._")
            return "\n".join(lines)

        for idx, entry in enumerate(results, start=1):
            lines.append(f"{idx}. [{entry.title}]({entry.url})")
            if entry.published_date:
                lines.append(f"   - Published: {entry.published_date.date()}")
        return "\n".join(lines)

    # HTML parsing to collect search results when JSON is unavailable or blocked
    try:
        r = requests.get(
            f"{base}/search",
            params={k: v for k, v in params.items() if v is not None},
            headers=headers,
            timeout=5,
        )
        if r.status_code != 200:
            return render([], error=f"HTML fetch returned status {r.status_code}")
        soup = BeautifulSoup(r.text, "html.parser")

        candidates = []
        # Try common SearXNG selectors
        for sel in [
            "article.result h3 a",
            "h3.result_header a",
            "h4.result_header a",
            "div.result h3 a",
            "#results h3 a",
        ]:
            for a in soup.select(sel):
                href = (a.get("href") or "").strip()
                title = (a.get_text(strip=True) or "").strip() or "Untitled"
                if href and href.startswith("http"):
                    candidates.append((title, href))
        # If still empty, fallback to any reasonable anchors within results container
        if not candidates:
            container = soup.select_one("#results, .results, main") or soup
            for a in container.select("a[href]"):
                href = (a.get("href") or "").strip()
                title = (a.get_text(strip=True) or "").strip()
                if href.startswith("http") and title:
                    candidates.append((title, href))

        # Deduplicate by URL and cap to max_results
        seen = set()
        results: List[SearchResult] = []
        for title, url in candidates:
            if url in seen:
                continue
            seen.add(url)
            results.append(
                SearchResult(title=title or "Untitled", url=url, published_date=None)
            )
            if len(results) >= max_results:
                break
        return render(results)
    except Exception as exc:
        return render([], error=str(exc))
