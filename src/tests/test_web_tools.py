"""Tests for enhanced fetch_url and verify_and_summarize web tools."""

from unittest.mock import MagicMock, patch

import pytest

from downes.tools.web.url import fetch_url, _extract_metadata, _extract_main_content
from downes.tools.web.verify import verify_and_summarize, _parse_verification_response


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_html(
    body: str = "<p>Hello world</p>",
    title: str = "Test Page",
    og_title: str = None,
    description: str = None,
    author: str = None,
    date: str = None,
    wrap_article: bool = False,
):
    """Build a minimal HTML page for testing."""
    meta_parts = []
    if og_title:
        meta_parts.append(f'<meta property="og:title" content="{og_title}"/>')
    if description:
        meta_parts.append(f'<meta name="description" content="{description}"/>')
    if author:
        meta_parts.append(f'<meta name="author" content="{author}"/>')
    if date:
        meta_parts.append(f'<meta property="article:published_time" content="{date}"/>')

    if wrap_article:
        body = f"<article>{body}</article>"

    return (
        f"<html><head><title>{title}</title>"
        f"{''.join(meta_parts)}</head>"
        f"<body>{body}</body></html>"
    )


def _mock_response(status_code: int, text: str = "", ok: bool = True):
    """Create a mock requests.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    resp.ok = ok
    return resp


# ---------------------------------------------------------------------------
# fetch_url tests
# ---------------------------------------------------------------------------

class TestFetchUrlValid:
    """Test that a successful fetch returns structured output."""

    @patch("downes.tools.web.url.requests.get")
    def test_structured_output_sections(self, mock_get):
        html = _make_html(
            body="<p>" + "Content paragraph. " * 30 + "</p>",
            title="My Page",
            description="A test page",
        )
        mock_get.return_value = _mock_response(200, html)

        result = fetch_url.invoke({"url": "https://example.com/page"})

        assert "## Content from https://example.com/page" in result
        assert "**Status:** 200 OK" in result
        assert "### Page Content" in result

    @patch("downes.tools.web.url.requests.get")
    def test_title_in_output(self, mock_get):
        html = _make_html(title="My Page Title")
        mock_get.return_value = _mock_response(200, html)

        result = fetch_url.invoke({"url": "https://example.com"})

        assert "**Title:** My Page Title" in result


class TestFetchUrlDeadLink:
    """Test that HTTP errors produce DEAD LINK output."""

    @patch("downes.tools.web.url.requests.get")
    def test_404_dead_link(self, mock_get):
        mock_get.return_value = _mock_response(404, "", ok=False)

        result = fetch_url.invoke({"url": "https://example.com/missing"})

        assert "(DEAD LINK)" in result
        assert "404" in result

    @patch("downes.tools.web.url.requests.get")
    def test_500_dead_link(self, mock_get):
        mock_get.return_value = _mock_response(500, "", ok=False)

        result = fetch_url.invoke({"url": "https://example.com/error"})

        assert "(DEAD LINK)" in result
        assert "500" in result

    @patch("downes.tools.web.url.requests.get")
    def test_connection_error_keeps_format(self, mock_get):
        mock_get.side_effect = ConnectionError("DNS failure")

        result = fetch_url.invoke({"url": "https://nonexistent.invalid"})

        assert result.startswith("Error fetching URL")
        assert "DNS failure" in result


class TestFetchUrlMetadata:
    """Test metadata extraction in fetch_url output."""

    @patch("downes.tools.web.url.requests.get")
    def test_all_metadata_fields(self, mock_get):
        html = _make_html(
            body="<p>" + "Long content here. " * 30 + "</p>",
            title="Fallback Title",
            og_title="OG Title",
            description="Page description",
            author="Jane Doe",
            date="2024-01-15",
        )
        mock_get.return_value = _mock_response(200, html)

        result = fetch_url.invoke({"url": "https://example.com"})

        # og:title takes priority over <title>
        assert "**Title:** OG Title" in result
        assert "**Description:** Page description" in result
        assert "**Author:** Jane Doe" in result
        assert "**Date:** 2024-01-15" in result

    @patch("downes.tools.web.url.requests.get")
    def test_missing_optional_metadata(self, mock_get):
        html = _make_html(title="Just Title", body="<p>Short body</p>")
        mock_get.return_value = _mock_response(200, html)

        result = fetch_url.invoke({"url": "https://example.com"})

        assert "**Title:** Just Title" in result
        # Author and date should be absent, not "None"
        assert "**Author:**" not in result
        assert "**Date:**" not in result


# ---------------------------------------------------------------------------
# _extract_main_content tests
# ---------------------------------------------------------------------------

class TestExtractMainContent:
    def test_prefers_article_tag(self):
        from bs4 import BeautifulSoup

        html = (
            "<html><body>"
            "<nav>Navigation stuff</nav>"
            "<article>" + "Article content. " * 30 + "</article>"
            "<footer>Footer</footer>"
            "</body></html>"
        )
        soup = BeautifulSoup(html, "html.parser")
        for s in soup(["script", "style"]):
            s.decompose()

        content = _extract_main_content(soup)
        assert "Article content" in content
        assert "Navigation stuff" not in content

    def test_falls_back_to_body(self):
        from bs4 import BeautifulSoup

        html = "<html><body><p>Just body text here.</p></body></html>"
        soup = BeautifulSoup(html, "html.parser")

        content = _extract_main_content(soup)
        assert "Just body text" in content


# ---------------------------------------------------------------------------
# verify_and_summarize tests
# ---------------------------------------------------------------------------

class TestVerifyAndSummarizeAccessible:
    """Test full verification output for an accessible URL."""

    @patch("downes.tools.web.verify.call_llm")
    @patch("downes.tools.web.verify.fetch_url")
    def test_accessible_structured_output(self, mock_fetch, mock_llm):
        mock_fetch.invoke.return_value = (
            "## Content from https://example.com\n\n"
            "**Status:** 200 OK\n"
            "**Title:** Test Article\n\n"
            "### Page Content\n"
            "This is educational content about machine learning."
        )

        mock_response = MagicMock()
        mock_response.content = (
            "SUMMARY: An article about machine learning fundamentals.\n"
            "KEY_CONCEPTS: supervised learning, neural networks, training data\n"
            "RELEVANCE: High\n"
            "RELEVANCE_REASON: Directly covers ML concepts relevant to the topic.\n"
            "CURRICULUM_USE: Use as introductory reading for a data science module.\n"
            "CONTENT_TYPE: article\n"
            "QUALITY_NOTES: Well-structured and up-to-date."
        )
        mock_llm.return_value = mock_response

        result = verify_and_summarize.invoke({
            "url": "https://example.com",
            "topic": "machine learning",
        })

        assert "## Source Verification: https://example.com" in result
        assert "**Accessible:** Yes" in result
        assert "**Content Type:** article" in result
        assert "**Relevance to 'machine learning':** High" in result
        assert "### Summary" in result
        assert "### Key Concepts" in result
        assert "### Suggested Curriculum Use" in result


class TestVerifyAndSummarizeDeadLink:
    """Test verification output for dead links."""

    @patch("downes.tools.web.verify.fetch_url")
    def test_dead_link_detected(self, mock_fetch):
        mock_fetch.invoke.return_value = (
            "## Content from https://dead.example.com\n\n"
            "**Status:** 404 (DEAD LINK)\n"
        )

        result = verify_and_summarize.invoke({
            "url": "https://dead.example.com",
            "topic": "biology",
        })

        assert "**Accessible:** No" in result
        assert "DEAD LINK" in result

    @patch("downes.tools.web.verify.fetch_url")
    def test_connection_error_detected(self, mock_fetch):
        mock_fetch.invoke.return_value = "Error fetching URL https://down.example.com: Connection timeout"

        result = verify_and_summarize.invoke({
            "url": "https://down.example.com",
            "topic": "chemistry",
        })

        assert "**Accessible:** No" in result


# ---------------------------------------------------------------------------
# _parse_verification_response tests
# ---------------------------------------------------------------------------

class TestParseVerificationResponse:
    def test_parses_all_fields(self):
        text = (
            "SUMMARY: A great article.\n"
            "KEY_CONCEPTS: math, algebra, geometry\n"
            "RELEVANCE: High\n"
            "RELEVANCE_REASON: Directly on topic.\n"
            "CURRICULUM_USE: Use as homework reading.\n"
            "CONTENT_TYPE: article\n"
            "QUALITY_NOTES: Recent and well-cited."
        )
        fields = _parse_verification_response(text)

        assert fields["SUMMARY"] == "A great article."
        assert fields["RELEVANCE"] == "High"
        assert fields["CONTENT_TYPE"] == "article"
        assert len(fields) == 7

    def test_handles_missing_fields(self):
        text = "SUMMARY: Just a summary.\nRELEVANCE: Low\n"
        fields = _parse_verification_response(text)

        assert fields["SUMMARY"] == "Just a summary."
        assert fields["RELEVANCE"] == "Low"
        assert "KEY_CONCEPTS" not in fields
