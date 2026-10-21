# Data flow and trust boundaries

## Boundaries

- **TB1 Client → API:** credentials, opaque bearer session, note content and UUIDs are untrusted. API validates identity, account status, role, and request shape.
- **TB2 API → Notes:** API sends a short-lived HMAC-authenticated authority. Notes verifies subject, caller, audience, action, resource, issue time and expiry and independently filters data by owner.
- **TB3 API → Report:** API sends only Notes-authorized records and a grant bound to their exact input digest, subject and username. Report verifies the grant and formats those records only.
- **TB4 Services → SQLite:** API and Notes open only their own SQLite database. Report has no database connection.
- **TB5 Helper/dependencies → build/runtime:** Report imports the separately installable helper; GitHub Actions installs it and scans the installed dependency environment.

## Report sequence

1. User authenticates at API; API checks active status on every later request.
2. User supplies note IDs to `POST /reports`.
3. API obtains each note from Notes under a per-note `note:read` grant bound to that user and ID.
4. Notes rejects missing, malformed, expired, wrong-audience, wrong-action, or wrong-resource grants, then returns only a row matching both ID and owner.
5. API calculates a digest over the exact returned note IDs and content and sends those records to Report under a short-lived `report:create` grant.
6. Report checks subject/username and the report-input digest before formatting with the helper.
7. API returns the result to the same authenticated caller.

In the local demonstration all services bind to loopback and use HTTP. A deployment outside the local host requires authenticated TLS and stronger operational key management.
