# Local vulnerability experiments

These intentionally vulnerable functions are isolated under `experiments/variants/`. The normal `services/` code does not import them, and the default application has no switch that enables them. All probes use in-memory SQLite or synthetic in-memory service objects; no network endpoint, real account, or persistent database is attacked.

Run the focused regression tests and demonstrations from the repository root:

```sh
.venv/bin/python -m pytest -q experiments/tests -p no:cacheprovider
.venv/bin/python -m experiments.run
```

The tests assert both the deliberately vulnerable observation and the fixed result. `evidence/phase3-results.txt` and `evidence/phase3-tests.txt` contain outputs captured from actual local executions. `evidence/phase3-full-tests.txt` records the full suite after the experiments were added. `evidence/phase3-source-sha256.txt` identifies the exact variants, tests and runner used.

| ID | Vulnerable behavior | Mitigation | Focused test |
|---|---|---|---|
| CWE-862 | Lookup uses note UUID without checking owner | Add owner predicate to the query | `test_cwe862.py` |
| CWE-89 | Search value is concatenated into SQL | Bind subject and search as SQL parameters | `test_cwe89.py` |
| CWE-20 | Accept arbitrary note length | Reject content longer than the documented 4,000-character limit | `test_cwe20.py` |
| Composition | API reuses a report cache entry keyed only by note IDs and skips fresh Notes authorization; Notes itself remains secure | Remove cross-subject cache reuse and call Notes for every requested report | `test_composition.py` |

The composition probe models API orchestration with separate Notes and Report service interfaces. Bob first requests a report; Alice then supplies the same known note ID. The vulnerable API returns its cached report without calling the still-secure Notes component. The fixed API calls Notes again and receives denial. The exercise intentionally focuses on the cross-service authorization interaction rather than adding production cache behavior to the secure mini application.
