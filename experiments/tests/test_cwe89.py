import sqlite3

from experiments.variants.cwe89_sql_injection import fixed_search, vulnerable_search


def test_cwe89_injection_returns_other_owner_row_until_parameterized():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.execute("CREATE TABLE notes (owner_id TEXT, title TEXT)")
    db.executemany("INSERT INTO notes VALUES (?, ?)", [("alice", "Plan"), ("bob", "Secret")])
    payload = "%' OR 1=1 -- "

    vulnerable = vulnerable_search(db, "alice", payload)
    fixed = fixed_search(db, "alice", payload)
    assert {row["owner_id"] for row in vulnerable} == {"alice", "bob"}
    assert fixed == []
