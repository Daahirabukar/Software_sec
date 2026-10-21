# Architecture

## Proposed components

| Process | Responsibility | Data and permissions |
|---|---|---|
| API Service | Login, user-role checks, note/report request coordination, restricted Admin operation | Own SQLite user database; may issue short-lived, narrowly scoped service authorities |
| Notes Service | Own note storage and enforce ownership for every note read/write | Own SQLite notes database; accepts only authenticated, scoped service requests |
| Report Service | Fetch specifically authorized notes from Notes over HTTP and format a text report | No note database; uses the installed helper package; no authority to select unapproved notes |

The database files do not count as application components. All three services are separate processes, not modules inside one server. The Report Service calls Notes; the API coordinates the report request and returns the result to the user.

## Identity and service authority

The API authenticates users and issues client access tokens. User-token signing material is API-only. Service authority uses distinct per-destination keys that are not the client-token key. A short-lived signed authority includes subject (sub), issuer/caller (iss/act), audience (aud), action, exact resource or selected note IDs, issue time, and expiry. API grants Report only report creation for an explicit selection; it gives Report only API-signed per-note read authorities for those exact note IDs. Report can forward those authorities but cannot mint or broaden them. Notes verifies the signature, audience, action, caller, expiry, and exact note scope, then independently checks that the note owner equals the subject. Missing or invalid authority denies.

These are design decisions, not implemented controls. Token lifetime, key loading, and local transport settings will be fixed and tested during implementation. Local HTTP is acceptable only on loopback for synthetic development; production would require authenticated TLS or an equivalent protected channel.

## Storage and assumptions

API SQLite stores seeded user IDs, Argon2id password hashes, role, and active status. Notes SQLite stores note UUID, owner UUID, title, content, and timestamps. Report output is generated for the current request and returned through the API; no queue or persistent report database is planned.

Assumptions: service ports are not exposed to untrusted networks; secrets are outside Git; the API is the user identity authority; Notes is the ownership authority; the helper formats only the notes given to it. Trust boundaries and flows are in data-flow.md.
