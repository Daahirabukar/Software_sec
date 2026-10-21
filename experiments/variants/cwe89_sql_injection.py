"""CWE-89 demo: unsafe SQL concatenation versus bound query parameters."""


def vulnerable_search(connection, subject: str, search: str):
    # Intentionally unsafe: the untrusted search value is inserted into SQL syntax.
    statement = (
        "SELECT owner_id, title FROM notes WHERE owner_id='" + subject
        + "' AND title LIKE '%" + search + "%'")
    return connection.execute(statement).fetchall()


def fixed_search(connection, subject: str, search: str):
    return connection.execute(
        "SELECT owner_id, title FROM notes WHERE owner_id=? AND title LIKE ?",
        (subject, f"%{search}%"),
    ).fetchall()
