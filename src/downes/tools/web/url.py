import re

import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
from pydantic import BaseModel, Field


class FetchUrlInput(BaseModel):
    url: str = Field(description="The URL to fetch content from.")


def _extract_metadata(soup, url: str) -> dict:
    """Extract title, description, author, and date from meta tags."""
    metadata = {}

    # Title: og:title > <title>
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        metadata["title"] = og_title["content"].strip()
    elif soup.title and soup.title.string:
        metadata["title"] = soup.title.string.strip()

    # Description
    og_desc = soup.find("meta", property="og:description")
    if og_desc and og_desc.get("content"):
        metadata["description"] = og_desc["content"].strip()
    else:
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            metadata["description"] = meta_desc["content"].strip()

    # Author
    meta_author = soup.find("meta", attrs={"name": "author"})
    if meta_author and meta_author.get("content"):
        metadata["author"] = meta_author["content"].strip()

    # Date
    for attr in ["article:published_time", "datePublished", "date"]:
        meta_date = soup.find("meta", property=attr) or soup.find(
            "meta", attrs={"name": attr}
        )
        if meta_date and meta_date.get("content"):
            metadata["date"] = meta_date["content"].strip()
            break

    return metadata


def _extract_main_content(soup) -> str:
    """Extract main content from the page, preferring article/main elements."""
    MIN_CONTENT_LENGTH = 200

    # Try content containers in priority order
    for selector in [
        soup.find("article"),
        soup.find("main"),
        soup.find(attrs={"role": "main"}),
        soup.find("div", class_=re.compile(r"content|article|post|entry", re.I)),
    ]:
        if selector:
            text = selector.get_text(separator="\n", strip=True)
            if len(text) >= MIN_CONTENT_LENGTH:
                return text

    # Fallback to full body text
    body = soup.find("body")
    if body:
        return body.get_text(separator="\n", strip=True)

    return soup.get_text(separator="\n", strip=True)


def _clean_text(raw_text: str) -> str:
    """Clean extracted text: collapse blank lines, strip each line."""
    lines = (line.strip() for line in raw_text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return "\n".join(chunk for chunk in chunks if chunk)


@tool(args_schema=FetchUrlInput)
def fetch_url(url: str) -> str:
    """Fetch and parse content from a URL using BeautifulSoup."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
    except Exception as e:
        # Connection errors (timeout, DNS, etc.) keep the existing format
        return f"Error fetching URL {url}: {e}"

    # Handle HTTP errors with structured dead-link output
    if not response.ok:
        return (
            f"## Content from {url}\n\n"
            f"**Status:** {response.status_code} (DEAD LINK)\n"
        )

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    metadata = _extract_metadata(soup, url)
    text = _clean_text(_extract_main_content(soup))

    # Build structured output
    parts = [f"## Content from {url}\n"]
    parts.append(f"**Status:** {response.status_code} OK")

    if metadata.get("title"):
        parts.append(f"**Title:** {metadata['title']}")
    if metadata.get("description"):
        parts.append(f"**Description:** {metadata['description']}")
    if metadata.get("author"):
        parts.append(f"**Author:** {metadata['author']}")
    if metadata.get("date"):
        parts.append(f"**Date:** {metadata['date']}")

    parts.append("\n### Page Content")
    parts.append(text[:20000])

    return "\n".join(parts)
