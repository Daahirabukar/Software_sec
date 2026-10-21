"""CWE-20 demo: missing content bound versus explicit input validation."""

MAX_CONTENT_LENGTH = 4000


def vulnerable_accept(content: str) -> str:
    """Intentionally accepts any string without checking the documented bound."""
    return content


def fixed_accept(content: str) -> str:
    if not isinstance(content, str) or not content or len(content) > MAX_CONTENT_LENGTH:
        raise ValueError("content must contain between 1 and 4000 characters")
    return content
