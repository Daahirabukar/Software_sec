"""Composition demo: secure Notes + Report composed by an unsafe API cache."""


class NotesService:
    """Notes stays secure in both variants and checks ownership on every read."""

    def __init__(self):
        self.notes = {
            "bob-note": {"owner": "bob", "content": "Synthetic Bob private note"},
        }

    def read(self, subject: str, note_id: str) -> dict[str, str]:
        note = self.notes.get(note_id)
        if note is None or note["owner"] != subject:
            raise PermissionError("note not found")
        return note


class ReportService:
    def format(self, subject: str, notes: list[dict[str, str]]) -> str:
        content = "\n".join(note["content"] for note in notes)
        return f"Report for {subject}\n{content}\n"


class VulnerableAPI:
    """Intentionally caches by note IDs only and skips Notes on a cache hit."""

    def __init__(self, notes: NotesService, reports: ReportService):
        self.notes = notes
        self.reports = reports
        self.cache: dict[tuple[str, ...], str] = {}

    def generate_report(self, subject: str, note_ids: list[str]) -> str:
        key = tuple(note_ids)
        if key in self.cache:
            return self.cache[key]
        records = [self.notes.read(subject, note_id) for note_id in note_ids]
        result = self.reports.format(subject, records)
        self.cache[key] = result
        return result


class FixedAPI:
    """Mitigation: reauthorize each request; this mini app needs no cache."""

    def __init__(self, notes: NotesService, reports: ReportService):
        self.notes = notes
        self.reports = reports

    def generate_report(self, subject: str, note_ids: list[str]) -> str:
        records = [self.notes.read(subject, note_id) for note_id in note_ids]
        return self.reports.format(subject, records)
