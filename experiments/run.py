"""Run the four local vulnerable/fixed probes and print their observed outcomes."""

import sqlite3

from experiments.variants.composition_report_cache import FixedAPI, NotesService, ReportService, VulnerableAPI
from experiments.variants.cwe20_input_validation import fixed_accept, vulnerable_accept
from experiments.variants.cwe862_missing_authorization import fixed_read, vulnerable_read
from experiments.variants.cwe89_sql_injection import fixed_search, vulnerable_search


def main() -> None:
    print("Secure Notes Mini Phase 3 probes; in-memory synthetic data only")
    print("Command: .venv/bin/python -m experiments.run")
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.execute("CREATE TABLE notes (id TEXT, owner_id TEXT, title TEXT, content TEXT)")
    db.execute("INSERT INTO notes VALUES ('bob-1', 'bob', 'Bob note', 'Synthetic Bob note')")
    row = vulnerable_read(db, "bob-1")
    print(f"CWE-862 vulnerable: Alice read owner={row['owner_id']} content={row['content']}")
    print(f"CWE-862 fixed: Alice denied={fixed_read(db, 'bob-1', 'alice') is None}")

    search_db = sqlite3.connect(":memory:")
    search_db.row_factory = sqlite3.Row
    search_db.execute("CREATE TABLE notes (owner_id TEXT, title TEXT)")
    search_db.executemany("INSERT INTO notes VALUES (?, ?)", [("alice", "Plan"), ("bob", "Secret")])
    payload = "%' OR 1=1 -- "
    leaked = sorted(row["owner_id"] for row in vulnerable_search(search_db, "alice", payload))
    safe = sorted(row["owner_id"] for row in fixed_search(search_db, "alice", payload))
    print(f"CWE-89 vulnerable: injected search returned owners={leaked}")
    print(f"CWE-89 fixed: parameterized search returned owners={safe}")

    oversized = "x" * 4001
    print(f"CWE-20 vulnerable: accepted_chars={len(vulnerable_accept(oversized))}")
    try:
        fixed_accept(oversized)
    except ValueError:
        print("CWE-20 fixed: oversized note rejected=True")

    notes, reports = NotesService(), ReportService()
    vulnerable_api = VulnerableAPI(notes, reports)
    vulnerable_api.generate_report("bob", ["bob-note"])
    leaked_report = vulnerable_api.generate_report("alice", ["bob-note"])
    print(f"Composition vulnerable: Alice received Bob report={ 'Synthetic Bob private note' in leaked_report }")
    fixed_api = FixedAPI(notes, reports)
    try:
        fixed_api.generate_report("alice", ["bob-note"])
    except PermissionError:
        print("Composition fixed: Notes reauthorization denied Alice=True")


if __name__ == "__main__":
    main()
