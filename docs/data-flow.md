# Data flow and trust boundaries

## Boundaries

- **TB1 Client → API:** untrusted credentials, access token, note input, IDs, and report request. API authenticates, checks active status/role, and validates input.
- **TB2 API → Notes:** trusted service process carrying short-lived user/action/resource authority. Notes verifies the grant and independently enforces owner equality.
- **TB3 API → Report:** report request, selected IDs, and bounded service authority. Report verifies caller/audience/action and may act only on the authorized selection.
- **TB4 Report → Notes:** forwarded API-signed read authority for each selected note. Notes still performs the ownership check; Report cannot mint authority.
- **TB5 Each service → its SQLite file:** separate process/storage ownership; no service directly opens another service's database.
- **TB6 Helper/dependencies → build/runtime:** helper is a separate installed dependency; review and dependency analysis occur before tests/release.

## Report sequence

1. Alice or Bob logs into API and receives a short-lived access token.
2. User sends POST /reports with note UUIDs to API.
3. API authenticates the active ordinary user, validates the selection, and issues Report-scoped report:create authority plus exact Notes note:read authorities for that user and those IDs.
4. API calls Report over HTTP. Report verifies its authority and rejects IDs outside the selection.
5. Report calls Notes over HTTP for each selected UUID, forwarding the corresponding narrowly scoped authority.
6. Notes verifies caller, action, audience, expiry, and scope, then filters the row by both UUID and authenticated owner. A foreign or missing note is denied.
7. Report sends only returned notes to the installed helper, then returns the formatted text to API.
8. API returns the response to the authenticated user.

A report cache that ignores the user and returns a prior user's result would cross TB1–TB4 and is the planned composition experiment. The secure design does not reuse a cached report across subjects.
