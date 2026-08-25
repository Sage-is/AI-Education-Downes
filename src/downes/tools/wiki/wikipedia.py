import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
from pydantic import BaseModel, Field
from urllib.parse import urljoin

class WikipediaExtractInput(BaseModel):
    url: str = Field(description="The URL of the Wikipedia page to analyze.")

@tool(args_schema=WikipediaExtractInput)
def wikipedia_extract_links(url: str) -> str:
    """Extracts links from the 'References' and 'External links' sections of a Wikipedia page."""

    # Wikipedia requires a descriptive User-Agent
    headers = {
        "User-Agent": "AI-Education-Downes/0.1.0 (https://github.com/somma/AI-Education-Downes; bot)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return f"Error fetching page: {e}"

    soup = BeautifulSoup(response.text, 'html.parser')

    output = [f"# Links from {soup.title.string if soup.title else url}"]

    def get_links_from_siblings(start_element, header_level='h2'):
        links = []
        if not start_element:
            return links

        # Iterate through siblings until the next header of same or higher level
        curr = start_element.find_next_sibling()
        current_level_num = int(header_level[1]) if len(header_level) > 1 and header_level[1].isdigit() else 2

        while curr:
            # Check for bare headers
            if curr.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                 level = int(curr.name[1])
                 if level <= current_level_num:
                     break

            # Check for mw-heading wrapper
            if curr.name == 'div' and 'mw-heading' in curr.get('class', []):
                classes = curr.get('class', [])
                level = 100
                for c in classes:
                    if c.startswith('mw-heading') and c[10:].isdigit():
                        level = int(c[10:])
                        break

                if level <= current_level_num:
                    break

            if curr.name in ['ul', 'ol', 'div', 'p']:
                # Extract external links primarily
                for a in curr.find_all('a', href=True):
                    href = a['href']
                    text = a.get_text(strip=True)

                    # Skip internal anchors, edit links, etc.
                    if href.startswith('#'): continue
                    if 'action=edit' in href: continue
                    # if href.startswith('/wiki/'): continue # Optional: skip internal wiki links

                    # Resolve relative URLs
                    full_url = urljoin(url, href)

                    # Clean up text
                    if not text:
                        text = full_url

                    links.append(f"- [{text}]({full_url})")
            curr = curr.find_next_sibling()
        return links

    def find_section_start(soup, section_id):
        elem = soup.find(id=section_id)
        if not elem:
            return None, None

        header = None
        if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            header = elem
        else:
            header = elem.find_parent(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

        if not header:
            return None, None

        # Check for mw-heading wrapper
        parent = header.parent
        if parent and parent.name == 'div' and 'mw-heading' in parent.get('class', []):
            return parent, header.name

        return header, header.name

    # 1. References
    ref_start, ref_level = find_section_start(soup, "References")
    if ref_start:
        links = get_links_from_siblings(ref_start, ref_level)
        output.append(f"\n## References ({len(links)} found)")
        if len(links) > 50:
            output.extend(links[:50])
            output.append(f"... and {len(links)-50} more.")
        else:
            output.extend(links)
    else:
        output.append("\n## References\n_Section not found._")

    # 2. External links
    ext_start, ext_level = find_section_start(soup, "External_links")
    if ext_start:
        links = get_links_from_siblings(ext_start, ext_level)
        output.append(f"\n## External Links ({len(links)} found)")
        if len(links) > 50:
            output.extend(links[:50])
            output.append(f"... and {len(links)-50} more.")
        else:
            output.extend(links)
    else:
        output.append("\n## External Links\n_Section not found._")

    return "\n".join(output)

class WikipediaSearchInput(BaseModel):
    query: str = Field(description="The search query to find Wikipedia pages.")

@tool(args_schema=WikipediaSearchInput)
def wikipedia_search(query: str) -> str:
    """Searches Wikipedia for a given query and returns a list of relevant page titles and URLs."""
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "opensearch",
        "search": query,
        "limit": 5,
        "namespace": 0,
        "format": "json"
    }
    headers = {
        "User-Agent": "AI-Education-Downes/0.1.0 (https://github.com/somma/AI-Education-Downes; bot)"
    }

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        # data format: [query, [titles], [descriptions], [urls]]
        titles = data[1]
        urls = data[3]

        results = []
        for title, url in zip(titles, urls):
            results.append(f"- [{title}]({url})")

        if not results:
            return "No results found."

        return "\n".join(results)

    except Exception as e:
        return f"Error searching Wikipedia: {e}"
