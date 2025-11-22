import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
from pydantic import BaseModel, Field


class FetchUrlInput(BaseModel):
    url: str = Field(description="The URL to fetch content from.")


@tool(args_schema=FetchUrlInput)
def fetch_url(url: str) -> str:
    """Fetch and parse content from a URL using BeautifulSoup."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        return f"Error fetching URL {url}: {e}"

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Get text
    text = soup.get_text()

    # Break into lines and remove leading/trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = "\n".join(chunk for chunk in chunks if chunk)

    # Limit output size to avoid context overflow
    return f"## Content from {url}\n\n{text[:20000]}"
