"""Generic utilities shared across the project."""

from typing import Any


def no(value: Any) -> bool:
	"""Return the logical negation of ``value`` for readability helpers."""
	return not value


def strip_or_empty(value: Any) -> str:
	"""Return ``value`` stripped as text, or ``""`` when missing."""
	if value is None:
		return ""
	return str(value).strip()


__all__ = ["no", "strip_or_empty"]
