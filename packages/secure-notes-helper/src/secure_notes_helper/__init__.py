"""Small formatter for notes already authorized by the Notes Service."""

from collections.abc import Iterable, Mapping


def format_report(username: str, notes: Iterable[Mapping[str, str]]) -> str:
    """Format only the note records supplied by the calling Report Service."""
    records = list(notes)
    lines = [f"Research notes for {username}", f"Notes included: {len(records)}", ""]
    for index, note in enumerate(records, start=1):
        lines.extend((f"{index}. {note['title']}", note["content"], ""))
    return "\n".join(lines).rstrip() + "\n"
