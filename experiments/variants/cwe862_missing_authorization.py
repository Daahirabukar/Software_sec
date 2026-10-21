"""CWE-862 demo: vulnerable read omits the owner predicate.

This isolated variant is never used by the application services.
"""


def vulnerable_read(connection, note_id: str):
    """Intentionally unsafe: the caller's identity is not checked."""
    return connection.execute(
        "SELECT id, owner_id, content FROM notes WHERE id=?", (note_id,)
    ).fetchone()


def fixed_read(connection, note_id: str, subject: str):
    """Mitigation: enforce ownership in the data-owning service query."""
    return connection.execute(
        "SELECT id, owner_id, content FROM notes WHERE id=? AND owner_id=?",
        (note_id, subject),
    ).fetchone()
