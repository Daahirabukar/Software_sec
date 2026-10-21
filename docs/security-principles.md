# Secure design principles

| Principle | Design decision | Enforcement point | Planned evidence |
|---|---|---|---|
| Least privilege | Admin only disables ordinary accounts; Report receives a fixed note selection; Notes grants no database access to other services | API role checks, scoped authority, Notes ownership query | Admin restriction tests; attempts to add another note ID fail |
| Complete mediation | Ownership is checked by Notes on every read, including requests routed through Report | Notes HTTP endpoint and owner-filtered database query | Alice/Bob direct and report-workflow negative tests |
| Fail-safe defaults | Missing, malformed, expired, wrong-action, wrong-audience, or out-of-scope authority is denied | Service authentication dependencies and request validation | Missing/invalid authority and malformed-input tests |

These are planned controls. The report will distinguish decisions, implementation, tests, and actual results.
