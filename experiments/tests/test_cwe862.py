import sqlite3

from experiments.variants.cwe862_missing_authorization import fixed_read, vulnerable_read


def test_cwe862_exposes_bob_without_owner_check_and_fixed_variant_denies():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.execute("CREATE TABLE notes (id TEXT, owner_id TEXT, content TEXT)")
    db.execute("INSERT INTO notes VALUES ('bob-1', 'bob', 'Synthetic Bob note')")

    leaked = vulnerable_read(db, "bob-1")
    assert leaked["owner_id"] == "bob"
    assert leaked["content"] == "Synthetic Bob note"
    assert fixed_read(db, "bob-1", "alice") is None
    assert fixed_read(db, "bob-1", "bob")["content"] == "Synthetic Bob note"
