# Secure Notes Mini

A small local demonstration project with three independent FastAPI processes: API Service (authentication and orchestration), Notes Service (SQLite note ownership), and Report Service (report formatting through the separately installable `secure-notes-helper` package).

## Setup

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
cp .env.example .env
```

Edit `.env`: replace both service-secret placeholders with different random values of at least 32 characters and set three different local-only passwords of at least 12 characters for Alice, Bob and Admin. The API hashes seeded passwords with Argon2id. Never reuse real credentials. `.env` and SQLite files are ignored by Git.

## Run the services

From the project root, load `.env` in each terminal and remove credentials that process does not need. Notes receives only its own HMAC key and database path; Report receives only its own HMAC key; API receives both downstream keys and seed credentials.

```sh
set -a; source .env; set +a
unset API_REPORTS_SECRET API_DB NOTES_SERVICE_URL REPORTS_SERVICE_URL \
  SEED_ALICE_PASSWORD SEED_BOB_PASSWORD SEED_ADMIN_PASSWORD
.venv/bin/uvicorn services.notes.main:create_app --factory --host 127.0.0.1 --port 8002
```

```sh
set -a; source .env; set +a
unset API_NOTES_SECRET API_DB NOTES_DB NOTES_SERVICE_URL REPORTS_SERVICE_URL \
  SEED_ALICE_PASSWORD SEED_BOB_PASSWORD SEED_ADMIN_PASSWORD
.venv/bin/uvicorn services.reports.main:create_app --factory --host 127.0.0.1 --port 8003
```

In a third terminal load `.env` without unsetting values, then start API:

```sh
set -a; source .env; set +a
.venv/bin/uvicorn services.api.main:create_app --factory --host 127.0.0.1 --port 8001
```

Stop each process with Ctrl+C. The API seeds `alice`, `bob` and `admin` at first startup; each account receives the password set in `.env`. The API's opaque bearer sessions are held in process memory, so run one API worker and restart to clear sessions. Internal services bind to loopback in this local setup.

## Example workflow

```sh
TOKEN=$(curl -s http://127.0.0.1:8001/auth/login -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"YOUR_LOCAL_ALICE_PASSWORD"}' | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')
curl -s http://127.0.0.1:8001/notes -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"title":"Study","content":"Synthetic note"}'
curl -s http://127.0.0.1:8001/notes -H "Authorization: Bearer $TOKEN"
```

Send `POST /reports` with `{"note_ids":["<owned-note-uuid>"]}` to generate a report. `POST /admin/users/{username}/disable` is Admin-only; Admin has no note or report permissions. FastAPI interactive API docs are available at `http://127.0.0.1:8001/docs` while running locally.

## Tests

```sh
.venv/bin/python -m pytest -q -p no:cacheprovider
```

Tests use temporary SQLite files and synthetic credentials. The suite covers login, note ownership, scoped service authorization, report identity/input binding, Admin restrictions, disabled sessions, input limits, helper formatting, and an HTTP workflow across three real Uvicorn processes.

## Current security boundaries and limitations

- Passwords use Argon2id; user sessions are random opaque bearer values with a 15-minute in-memory lifetime. Active account state is checked on each request.
- API and each downstream service share a different HMAC-SHA256 service key. Each short-lived (30-second) authority binds subject, username, caller, audience, action, exact resource or report-input digest, and expiry. Notes also checks owner identity on every read. Authority keys and user sessions are local-demo controls, not a production identity system.
- API and Notes use separate SQLite files. Report has no database access. Services communicate over loopback HTTP in this local-only setup; deploy beyond one trusted machine only with authenticated TLS and protected key handling.
- Seed passwords are supplied through ignored `.env`; the account names and roles are synthetic. Do not expose the demo services to a public network.

See `experiments/README.md` for the four controlled vulnerable/fixed probes and their captured local evidence. Jenkins CI, deployment hardening and the academic Overleaf report remain unfinished. Do not treat planned or unexecuted checks as completed evidence.
