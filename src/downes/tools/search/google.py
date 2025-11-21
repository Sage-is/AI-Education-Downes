import requests
from concurrent.futures import ThreadPoolExecutor
from downes.tools.search.models import SearchResult
from downes.tools.search.utils import parse_rss_content
from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import List, Optional


class SearchGoogleNewsInput(BaseModel):
    query: str = Field(
        description="The search query to send to Google News. E.g., 'project-based learning'"
    )
    max_results: int = Field(
        default=5, description="The maximum number of results to retrieve."
    )
    education_bias: bool = Field(
        default=True,
        description="If True, enriches the query with education-focused terms to surface curricula, syllabi, and pedagogy.",
    )
    site_filters: Optional[List[str]] = Field(
        default=None,
        description="Optional list of site: filters (e.g., ['site:.edu','site:oercommons.org']).",
    )
    extra_terms: Optional[List[str]] = Field(
        default=None,
        description='Additional quoted terms to add to the query (e.g., [""lesson plan"", ""rubric""]).',
    )


@tool(args_schema=SearchGoogleNewsInput)
def search_google_news(
    query: str,
    max_results: int = 5,
    education_bias: bool = True,
    site_filters: Optional[List[str]] = None,
    extra_terms: Optional[List[str]] = None,
) -> list[SearchResult]:
    """
    - Searches Google News RSS for articles/resources matching a query.
        - When education_bias=True (default), the tool augments the query with curriculum-related terms
        - You can also constrain results with site filters like 'site:.edu' or 'site:oercommons.org'.
        - Use extra_terms to inject additional phrases.
    """
    # Build enriched query for education use cases
    terms = []
    if education_bias:
        terms.extend(
            [
                '"curriculum"',
                '"syllabus"',
                '"learning objectives"',
                '"lesson plan"',
                '"assessment rubric"',
                '"pacing guide"',
                '"Bloom\'s taxonomy"',
            ]
        )
    if extra_terms:
        terms.extend(extra_terms)

    # Default site filters suitable for education discovery
    default_sites = [
        "site:.edu",
        "site:oercommons.org",
        "site:openstax.org",
        "site:khanacademy.org",
    ]
    sites = site_filters if site_filters is not None else default_sites

    # Build final query string
    terms_clause = f" ({' OR '.join(terms)})" if terms else ""
    sites_clause = f" ({' OR '.join(sites)})" if sites else ""
    full_query = f"{query}{terms_clause}{sites_clause}".strip()

    q = full_query.replace(" ", "%20")
    search_url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"

    response = requests.get(search_url)
    if response.status_code != 200:
        return []
    xml_content = response.text
    results = parse_rss_content(xml_content, max_results)

    urls_to_resolve = [result.url for result in results]
    with ThreadPoolExecutor() as executor:
        resolved_urls = list(executor.map(_resolve_google_news_url, urls_to_resolve))

    final: list[SearchResult] = []
    for r, resolved in zip(results, resolved_urls):
        final.append(
            SearchResult(
                title=r.title,
                url=resolved,
                published_date=r.published_date,
            )
        )
    return final


def _resolve_google_news_url(url: str) -> str:
    if not url or "news.google.com" not in url:
        return url
    try:
        from googlenewsdecoder import gnewsdecoder

        result = gnewsdecoder(url, interval=1)
        if result.get("status"):
            return result["decoded_url"]
        return url
    except Exception:
        return url
