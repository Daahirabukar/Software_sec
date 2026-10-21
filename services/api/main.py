"""API Service: user authentication, orchestration, and narrow admin operation."""

import os
import sqlite3
import time
import uuid
from uuid import UUID
from pathlib import Path

import httpx
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerificationError
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from services.common import issue_authority, report_scope, required_secret

_password_hasher = PasswordHasher()
_dummy_password_hash = _password_hasher.hash("not-a-real-password")


class LoginInput(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class NoteInput(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=4000)


class ReportInput(BaseModel):
    note_ids: list[UUID] = Field(max_length=50)


def create_app(*, database: str | None = None, notes_url: str | None = None,
               reports_url: str | None = None, notes_secret: bytes | None = None,
               reports_secret: bytes | None = None, client: httpx.Client | None = None,
               seed_passwords: dict[str, str] | None = None, now=time.time) -> FastAPI:
    db_path = database or os.environ.get("API_DB", "api.sqlite3")
    notes_url = notes_url or os.environ.get("NOTES_SERVICE_URL", "http://127.0.0.1:8002")
    reports_url = reports_url or os.environ.get("REPORTS_SERVICE_URL", "http://127.0.0.1:8003")
    notes_key = notes_secret or required_secret("API_NOTES_SECRET")
    reports_key = reports_secret or required_secret("API_REPORTS_SECRET")
    seed_passwords = seed_passwords or {
        username: os.environ.get(f"SEED_{username.upper()}_PASSWORD", "")
        for username in ("alice", "bob", "admin")
    }
    if set(seed_passwords) != {"alice", "bob", "admin"} or any(len(value) < 12 for value in seed_passwords.values()):
        raise RuntimeError("Set SEED_ALICE_PASSWORD, SEED_BOB_PASSWORD and SEED_ADMIN_PASSWORD to at least 12 characters")
    http = client or httpx.Client(timeout=3.0)
    app = FastAPI(title="Secure Notes Mini API Service")

    def connect() -> sqlite3.Connection:
        connection = sqlite3.connect(db_path, timeout=5)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize() -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        with connect() as connection:
            connection.execute("""CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
                role TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1)""")
            for username, password in seed_passwords.items():
                role = "admin" if username == "admin" else "user"
                connection.execute(
                    "INSERT OR IGNORE INTO users (id, username, password_hash, role, active) VALUES (?, ?, ?, ?, 1)",
                    (str(uuid.uuid5(uuid.NAMESPACE_DNS, f"secure-notes-mini:{username}")), username,
                     _password_hasher.hash(password), role),
                )

    initialize()
    sessions: dict[str, tuple[str, float]] = {}

    def user_by_name(username: str):
        with connect() as connection:
            return connection.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

    def current_user(authorization: str | None = Header(default=None)):
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authentication required")
        token = authorization[7:]
        record = sessions.get(token)
        if not record or record[1] <= now():
            sessions.pop(token, None)
            raise HTTPException(status_code=401, detail="Authentication required")
        with connect() as connection:
            user = connection.execute("SELECT * FROM users WHERE id=? AND active=1", (record[0],)).fetchone()
        if not user:
            sessions.pop(token, None)
            raise HTTPException(status_code=401, detail="Authentication required")
        return user

    def require_ordinary_user(user):
        if user["role"] != "user":
            raise HTTPException(status_code=403, detail="Ordinary user permission required")
        return user

    @app.post("/auth/login")
    def login(data: LoginInput):
        user = user_by_name(data.username)
        # Perform a real Argon2 verification for unknown users too, with generic failure.
        stored_hash = user["password_hash"] if user else _dummy_password_hash
        try:
            valid = _password_hasher.verify(stored_hash, data.password)
        except (InvalidHash, VerificationError):
            valid = False
        if not user or not user["active"] or not valid:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        token = uuid.uuid4().hex + uuid.uuid4().hex
        sessions[token] = (user["id"], now() + 900)
        return {"access_token": token, "token_type": "bearer", "expires_in": 900}

    @app.get("/auth/me")
    def me(user=Depends(current_user)):
        return {"id": user["id"], "username": user["username"], "role": user["role"]}

    def service_header(subject: str, username: str, key: bytes, audience: str, action: str, resource: str):
        grant = issue_authority(key, subject=subject, caller="api", audience=audience,
                                action=action, resource=resource, username=username, lifetime=30)
        return {"Authorization": f"Bearer {grant}"}

    @app.post("/notes", status_code=201)
    def create_note(data: NoteInput, user=Depends(current_user)):
        require_ordinary_user(user)
        response = http.post(f"{notes_url}/notes", json=data.model_dump(),
                             headers=service_header(user["id"], user["username"], notes_key, "notes", "note:create", "new-note"))
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail="Notes service request denied")
        return response.json()

    @app.get("/notes")
    def list_notes(user=Depends(current_user)):
        require_ordinary_user(user)
        response = http.get(f"{notes_url}/notes", headers=service_header(
            user["id"], user["username"], notes_key, "notes", "note:list", "collection"))
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail="Notes service request denied")
        return response.json()

    @app.get("/notes/{note_id}")
    def get_note(note_id: UUID, user=Depends(current_user)):
        require_ordinary_user(user)
        note_id = str(note_id)
        response = http.get(f"{notes_url}/notes/{note_id}", headers=service_header(
            user["id"], user["username"], notes_key, "notes", "note:read", note_id))
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code,
                                detail="Note not found" if response.status_code == 404 else "Notes service request denied")
        return response.json()

    @app.post("/reports")
    def report(data: ReportInput, user=Depends(current_user)):
        require_ordinary_user(user)
        if len(set(data.note_ids)) != len(data.note_ids):
            raise HTTPException(status_code=422, detail="Duplicate note IDs are not allowed")
        notes = []
        for note_id in data.note_ids:
            note_id = str(note_id)
            response = http.get(f"{notes_url}/notes/{note_id}", headers=service_header(
                user["id"], user["username"], notes_key, "notes", "note:read", note_id))
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Note not found")
            if response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail="Notes service request denied")
            notes.append(response.json())
        report_notes = [{"id": note["id"], "title": note["title"], "content": note["content"]}
                        for note in notes]
        grant = service_header(user["id"], user["username"], reports_key, "reports", "report:create",
                               report_scope(report_notes))
        response = http.post(f"{reports_url}/reports", json={
            "username": user["username"],
            "notes": report_notes,
        }, headers=grant)
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail="Report service request denied")
        result = response.json()
        if result.get("subject") != user["id"]:
            raise HTTPException(status_code=502, detail="Report service identity mismatch")
        return {"report": result["report"]}

    @app.post("/admin/users/{username}/disable")
    def disable_user(username: str, user=Depends(current_user)):
        if user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Administrator permission required")
        if username == "admin":
            raise HTTPException(status_code=400, detail="Admin account cannot be disabled here")
        with connect() as connection:
            cursor = connection.execute("UPDATE users SET active=0 WHERE username=? AND role='user'", (username,))
        if cursor.rowcount != 1:
            raise HTTPException(status_code=404, detail="Ordinary user not found")
        return {"disabled": username}

    return app
