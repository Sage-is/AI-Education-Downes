import os
from typing import List, Optional
import requests
from langchain.tools import tool
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
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
    - Set SEARXNG_INSTANCE_URL env var to.
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
        "format": "json",
        "language": language,
        "safesearch": 1 if safe else 0,
        "categories": ",".join(categories) if categories else None,
    }
    params = {k: v for k, v in params.items() if v is not None}

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; DownesBot/1.0)",
        "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # First attempt: JSON API
    try:
        resp = requests.get(f"{base}/search", params=params, headers=headers, timeout=20)
        if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("application/json"):
            try:
                data = resp.json()
            except Exception:
                data = {"results": []}
            results: List[SearchResult] = []
            for r in data.get("results", [])[: max_results * 2]:
                title = r.get("title") or "Untitled"
                url = r.get("url") or r.get("link") or ""
                if not url:
                    continue
                published_date = None
                for key in ["publishedDate", "published", "date"]:
                    if key in r and isinstance(r[key], str):
                        try:
                            published_date = datetime.fromisoformat(
                                r[key].replace("Z", "+00:00")
                            )
                        except Exception:
                            published_date = None
                results.append(SearchResult(title=title, url=url, published_date=published_date))
                if len(results) >= max_results:
                    break
            if results:
                return results
    except Exception:
        pass

    # Fallback: HTML parsing when JSON is blocked (e.g., 403)
    try:
        html_params = {k: v for k, v in params.items() if k != "format"}
        html_headers = headers.copy()
        html_headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        r = requests.get(f"{base}/search", params=html_params, headers=html_headers, timeout=20)
        if r.status_code != 200:
            return []
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
            results.append(SearchResult(title=title or "Untitled", url=url, published_date=None))
            if len(results) >= max_results:
                break
        return results
    except Exception:
        return []
