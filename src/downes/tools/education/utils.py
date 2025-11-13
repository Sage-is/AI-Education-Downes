"""Shared utilities for education tools to reduce code duplication."""

from typing import List, Optional, Dict, Any


class MarkdownBuilder:
    """Builder for constructing Markdown documents with common patterns."""

    def __init__(self):
        self.lines: List[str] = []

    def add_heading(self, text: str, level: int = 1) -> "MarkdownBuilder":
        """Add a heading at the specified level."""
        prefix = "#" * level
        self.lines.extend([f"{prefix} {text}", ""])
        return self

    def add_text(self, text: str) -> "MarkdownBuilder":
        """Add a line of text."""
        self.lines.append(text)
        return self

    def add_blank(self) -> "MarkdownBuilder":
        """Add a blank line."""
        self.lines.append("")
        return self

    def add_bullet_list(self, items: List[str]) -> "MarkdownBuilder":
        """Add a bulleted list."""
        for item in items:
            self.lines.append(f"- {item}")
        self.lines.append("")
        return self

    def add_numbered_list(self, items: List[str]) -> "MarkdownBuilder":
        """Add a numbered list."""
        for i, item in enumerate(items, 1):
            self.lines.append(f"{i}. {item}")
        self.lines.append("")
        return self

    def add_metadata(self, **kwargs) -> "MarkdownBuilder":
        """Add key-value metadata pairs."""
        for key, value in kwargs.items():
            if value is not None:
                label = key.replace("_", " ").title()
                self.lines.append(f"**{label}:** {value}")
        self.lines.append("")
        return self

    def add_table(self, headers: List[str], rows: List[List[Any]]) -> "MarkdownBuilder":
        """Add a Markdown table."""
        # Header row
        self.lines.append("| " + " | ".join(str(h) for h in headers) + " |")
        # Separator row
        self.lines.append("|" + "|".join("---" for _ in headers) + "|")
        # Data rows
        for row in rows:
            self.lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
        self.lines.append("")
        return self

    def build(self) -> str:
        """Return the final Markdown string."""
        return "\n".join(self.lines)


def normalize_list_input(value, default: Optional[List] = None) -> List:
    """
    Normalize various list input formats to a Python list.
    Handles: JSON strings, comma-separated strings, actual lists.
    """
    if value is None:
        return default or []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        # Try JSON parsing first
        try:
            import json

            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass

        # Try comma-separated
        if "," in value:
            return [s.strip() for s in value.split(",") if s.strip()]

        # Single value - wrap in list
        if value.strip():
            return [value.strip()]

    return default or []


def distribute_items_across_groups(
    items: List[Any], group_count: int
) -> List[List[Any]]:
    """
    Distribute items evenly across N groups.
    Returns a list of groups, each containing items.
    """
    if not items or group_count <= 0:
        return [[] for _ in range(max(1, group_count))]

    items_per_group = max(1, len(items) // group_count)
    groups = []

    for i in range(group_count):
        start = i * items_per_group
        end = start + items_per_group
        group_items = items[start:end]

        # If last group and items remain, grab them
        if i == group_count - 1 and end < len(items):
            group_items = items[start:]

        # Ensure we always have at least something
        if not group_items and items:
            group_items = items[-items_per_group:]

        groups.append(group_items)

    return groups
