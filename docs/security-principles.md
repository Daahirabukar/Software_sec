# Secure design principles

| Principle | Implemented decision | Enforcement point | Evidence |
|---|---|---|---|
| Least privilege | Admin can disable ordinary accounts only; Report receives exact already-authorized notes; each service has its own database | API role checks, report digest scope, service boundaries | `test_admin_is_restricted...`; `test_owner_isolation...` |
| Complete mediation | Notes checks ownership for every note read, including report reads initiated by API | Notes query filters by note ID and verified subject | `test_owner_isolation_and_report_workflow_across_three_services` |
| Fail-safe defaults | Missing credentials, invalid sessions, malformed/expired/out-of-scope authorities, or invalid data are rejected | API auth dependency, Notes authority verifier, Pydantic request models | `test_login_identity_and_generic_failure`; `test_notes_service_rejects...`; `test_service_fails_closed...`; input bounds test |

These controls are implemented and exercised by pytest. Vulnerability-specific evidence, scanning gates, Jenkins runs, and production deployment hardening remain planned work.
