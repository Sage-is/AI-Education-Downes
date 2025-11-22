import os
import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
from pydantic import BaseModel, Field


class SearxSearchInput(BaseModel):
    query: str = Field(description="Search query.")
    max_results: int = Field(default=10, description="Max results.")


@tool(args_schema=SearxSearchInput)
def searx_search(query: str, max_results: int = 10) -> str:
    """Search via SearXNG (HTML fallback) and return Markdown. Note only ever use one `site:` filter per query."""
    url = os.getenv("SEARXNG_INSTANCE_URL")
    if not url:
        return "Error: SEARXNG_INSTANCE_URL not set."

    # Use HTML endpoint because JSON API (used by SearxSearchWrapper) returns 403
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    params = {
        "q": query,
        "categories": "general",
        "language": "auto",
        "safesearch": "0",
        "format": "html",
    }

    try:
        resp = requests.get(
            f"{url.rstrip('/')}/search", params=params, headers=headers, timeout=10
        )
        resp.raise_for_status()
    except Exception as e:
        return f"Search failed: {e}"

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    # Parse standard SearXNG HTML results
    for res in soup.select(".result")[:max_results]:
        link_tag = res.select_one("h3 a, h4 a")
        if not link_tag:
            continue

        title = link_tag.get_text(strip=True)
        href = link_tag.get("href")
        snippet_tag = res.select_one(".content")
        snippet = (
            snippet_tag.get_text(separator=" ", strip=True).replace("\n", " ") if snippet_tag else ""
        )

        results.append(f"- [{title}]({href}) - {snippet}")

    if not results:
        return "_No results found._"

    return f"## Search: {query}\n" + "\n".join(results)

