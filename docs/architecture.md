# Architecture

## Implemented components

| Process | Responsibility | Data and permissions |
|---|---|---|
| API Service | Argon2id login, in-memory user sessions, role checks, orchestration, restricted account disable | Own SQLite user database; issues narrow service authorities |
| Notes Service | Create, list and read notes; enforce ownership at each read | Own SQLite notes database; accepts only API-authorized requests |
| Report Service | Format the exact notes provided by API | No database; imports the independently installable `secure-notes-helper` package |

Each service has its own FastAPI application factory and runs as a separate Uvicorn process. SQLite files are owned by their respective services. Report has no note-database access.

## Authentication and delegated service authority

The API stores Argon2id hashes for the synthetic accounts and issues random opaque bearer sessions valid for 15 minutes. Seed passwords must be at least 12 characters and are supplied through environment variables. Session state is in memory; account active status is checked on every authenticated request. This intentionally small implementation supports one API process and is not a distributed session design.

The API and each downstream service share a distinct HMAC-SHA256 key for that service boundary. A 30-second authority contains the authenticated subject and username, caller (`api`), destination audience (`notes` or `reports`), action, exact resource scope, issue time and expiry. Notes verifies all claims, then independently queries by both note ID and owner ID. Create and list grants are limited to their named collection operation. Report verifies its grant against a digest of the exact note IDs and content supplied by API. Missing or invalid authority is denied. No client-supplied owner ID is accepted.

Keys and seed passwords come from ignored local `.env` configuration; there are no source-code credentials. This is suitable only for a local synthetic-data demonstration. HMAC keys are not asymmetric identities, local HTTP is not suitable outside loopback, and production use would require authenticated TLS, managed secrets and key rotation.

## Report workflow

1. Alice or Bob logs in to API and receives a short-lived opaque session.
2. The user sends `POST /reports` with note UUIDs.
3. API authenticates the user and requests each note from Notes using a short-lived, note-specific read authority.
4. Notes verifies API authority and independently checks note ownership; foreign and missing note IDs return the same not-found result.
5. API sends the returned records to Report with a report-create authority bound to their SHA-256 input digest and the authenticated subject/username.
6. Report verifies the service grant and identity binding, then calls the separately installed helper to format only the submitted records.
7. API returns the report to the user.

The user cannot set note ownership, and the Report Service cannot select or fetch additional records. No cross-user report cache or persistent report store exists.
