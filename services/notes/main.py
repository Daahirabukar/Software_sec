"""Notes Service: note storage and owner authorization."""

import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from services.common import InvalidAuthority, required_secret, verify_authority


class NoteInput(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=4000)


def create_app(database: str | None = None, service_secret: bytes | None = None) -> FastAPI:
    db_path = database or os.environ.get("NOTES_DB", "notes.sqlite3")
    secret = service_secret or required_secret("API_NOTES_SECRET")
    app = FastAPI(title="Secure Notes Mini Notes Service")

    def connect() -> sqlite3.Connection:
        connection = sqlite3.connect(db_path, timeout=5)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize() -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        with connect() as connection:
            connection.execute("""CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, title TEXT NOT NULL,
                content TEXT NOT NULL, created_at TEXT NOT NULL)""")

    initialize()

    def authorize(authorization: str | None, action: str, resource: str = "*") -> dict:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Service authorization required")
        try:
            return verify_authority(authorization[7:], secret, audience="notes",
                                    action=action, resource=resource)
        except InvalidAuthority:
            raise HTTPException(status_code=403, detail="Service authorization denied") from None

    @app.post("/notes", status_code=201)
    def create_note(note: NoteInput, authorization: str | None = Header(default=None)):
        grant = authorize(authorization, "note:create", "new-note")
        note_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        with connect() as connection:
            connection.execute("INSERT INTO notes VALUES (?, ?, ?, ?, ?)",
                               (note_id, grant["sub"], note.title, note.content, created_at))
        return {"id": note_id, "owner_id": grant["sub"], "title": note.title,
                "content": note.content, "created_at": created_at}

    @app.get("/notes")
    def list_notes(authorization: str | None = Header(default=None)):
        grant = authorize(authorization, "note:list", "collection")
        with connect() as connection:
            rows = connection.execute(
                "SELECT id, owner_id, title, content, created_at FROM notes WHERE owner_id=? ORDER BY created_at, id",
                (grant["sub"],),
            ).fetchall()
        return [dict(row) for row in rows]

    @app.get("/notes/{note_id}")
    def get_note(note_id: UUID, authorization: str | None = Header(default=None)):
        note_id = str(note_id)
        grant = authorize(authorization, "note:read", note_id)
        with connect() as connection:
            row = connection.execute(
                "SELECT id, owner_id, title, content, created_at FROM notes WHERE id=? AND owner_id=?",
                (note_id, grant["sub"]),
            ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Note not found")
        return dict(row)

    return app
