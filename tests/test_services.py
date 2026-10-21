import secrets

from fastapi.testclient import TestClient

from services.api.main import create_app as create_api
from services.common import issue_authority, report_scope
from services.notes.main import create_app as create_notes
from services.reports.main import create_app as create_reports

NOTES_SECRET = secrets.token_bytes(32)
REPORTS_SECRET = secrets.token_bytes(32)
TEST_PASSWORDS = {username: f"{username}-test-{secrets.token_urlsafe(16)}"
                  for username in ("alice", "bob", "admin")}


class ServiceBridge:
    """HTTP-shaped bridge used to test the three independent FastAPI apps together."""

    def __init__(self, notes, reports):
        self.notes = notes
        self.reports = reports

    def get(self, url, **kwargs):
        target = self.notes if ":8002/" in url else self.reports
        return target.get(url.split(":8002" if target is self.notes else ":8003", 1)[1], **kwargs)

    def post(self, url, **kwargs):
        target = self.notes if ":8002/" in url else self.reports
        return target.post(url.split(":8002" if target is self.notes else ":8003", 1)[1], **kwargs)


def service_clients(tmp_path):
    notes = TestClient(create_notes(str(tmp_path / "notes.db"), NOTES_SECRET))
    reports = TestClient(create_reports(REPORTS_SECRET))
    bridge = ServiceBridge(notes, reports)
    api = TestClient(create_api(database=str(tmp_path / "api.db"), notes_secret=NOTES_SECRET,
                                reports_secret=REPORTS_SECRET, client=bridge, seed_passwords=TEST_PASSWORDS))
    return api, notes, reports


def login(api, username):
    response = api.post("/auth/login", json={"username": username, "password": TEST_PASSWORDS[username]})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_login_identity_and_generic_failure(tmp_path):
    api, _, _ = service_clients(tmp_path)
    alice = login(api, "alice")
    assert api.get("/auth/me", headers=alice).json()["username"] == "alice"
    assert api.post("/auth/login", json={"username": "alice", "password": "wrong"}).json() == {
        "detail": "Invalid username or password"
    }
    assert api.post("/auth/login", json={"username": "not-a-user", "password": "wrong"}).json() == {
        "detail": "Invalid username or password"
    }
    assert api.get("/auth/me").status_code == 401


def test_owner_isolation_and_report_workflow_across_three_services(tmp_path):
    api, _, _ = service_clients(tmp_path)
    alice, bob = login(api, "alice"), login(api, "bob")
    alice_user_id = api.get("/auth/me", headers=alice).json()["id"]
    alice_note = api.post("/notes", headers=alice, json={"title": "Alice work", "content": "Alice private",
                                                         "owner_id": "bob"})
    bob_note = api.post("/notes", headers=bob, json={"title": "Bob work", "content": "Bob private"})
    assert alice_note.status_code == bob_note.status_code == 201
    assert alice_note.json()["owner_id"] == alice_user_id

    assert api.get("/notes", headers=alice).json()[0]["owner_id"] == api.get("/auth/me", headers=alice).json()["id"]
    assert api.get(f"/notes/{alice_note.json()['id']}", headers=alice).status_code == 200
    assert api.get(f"/notes/{bob_note.json()['id']}", headers=alice).status_code == 404
    assert api.get(f"/notes/{alice_note.json()['id']}", headers=bob).status_code == 404

    alice_report = api.post("/reports", headers=alice, json={"note_ids": [alice_note.json()["id"]]})
    bob_report = api.post("/reports", headers=bob, json={"note_ids": [bob_note.json()["id"]]})
    assert alice_report.status_code == bob_report.status_code == 200
    assert "Alice private" in alice_report.json()["report"]
    assert "Bob private" not in alice_report.json()["report"]
    assert "Bob private" in bob_report.json()["report"]
    assert api.post("/reports", headers=alice, json={"note_ids": [bob_note.json()["id"]]}).status_code == 404


def test_notes_service_rejects_missing_wrong_audience_action_scope_and_expired_authority(tmp_path):
    _, notes, _ = service_clients(tmp_path)
    assert notes.get("/notes").status_code == 401
    note_id = "8c9a6a5a-0bfb-4d83-8c2d-590749fb1639"
    cases = [
        "malformed.token",
        issue_authority(NOTES_SECRET, subject="alice", caller="api", audience="reports",
                        action="note:read", resource=note_id, username="alice"),
        issue_authority(NOTES_SECRET, subject="alice", caller="api", audience="notes",
                        action="note:list", resource=note_id, username="alice"),
        issue_authority(NOTES_SECRET, subject="alice", caller="api", audience="notes",
                        action="note:read", resource="different-id", username="alice"),
        issue_authority(NOTES_SECRET, subject="alice", caller="api", audience="notes",
                        action="note:read", resource=note_id, username="alice", lifetime=-1),
    ]
    for grant in cases:
        if grant == "malformed.token":
            grant = "not-a-valid-token"
        assert notes.get(f"/notes/{note_id}", headers={"Authorization": f"Bearer {grant}"}).status_code == 403


def test_service_fails_closed_when_secret_is_missing(tmp_path, monkeypatch):
    monkeypatch.delenv("API_NOTES_SECRET", raising=False)
    monkeypatch.delenv("API_REPORTS_SECRET", raising=False)
    import pytest

    with pytest.raises(RuntimeError, match="API_NOTES_SECRET"):
        create_notes(str(tmp_path / "notes.db"))
    with pytest.raises(RuntimeError, match="API_NOTES_SECRET"):
        create_api(database=str(tmp_path / "api.db"), seed_passwords=TEST_PASSWORDS)


def test_admin_is_restricted_to_disabling_ordinary_users_and_disable_takes_effect(tmp_path):
    api, _, _ = service_clients(tmp_path)
    alice, admin = login(api, "alice"), login(api, "admin")
    assert api.post("/admin/users/bob/disable", headers=alice).status_code == 403
    assert api.post("/notes", headers=admin, json={"title": "No", "content": "No"}).status_code == 403
    assert api.get("/notes", headers=admin).status_code == 403
    assert api.post("/reports", headers=admin, json={"note_ids": []}).status_code == 403
    assert api.post("/admin/users/admin/disable", headers=admin).status_code == 400
    assert api.post("/admin/users/alice/disable", headers=admin).status_code == 200
    assert api.get("/auth/me", headers=alice).status_code == 401
    assert api.post("/auth/login", json={"username": "alice", "password": TEST_PASSWORDS["alice"]}).status_code == 401


def test_user_session_expiry_and_input_bounds(tmp_path):
    clock = [100]
    notes = TestClient(create_notes(str(tmp_path / "notes.db"), NOTES_SECRET))
    reports = TestClient(create_reports(REPORTS_SECRET))
    api = TestClient(create_api(database=str(tmp_path / "api.db"), notes_secret=NOTES_SECRET,
                                reports_secret=REPORTS_SECRET, client=ServiceBridge(notes, reports),
                                seed_passwords=TEST_PASSWORDS,
                                now=lambda: clock[0]))
    alice = login(api, "alice")
    clock[0] = 1000
    assert api.get("/auth/me", headers=alice).status_code == 401
    fresh = login(api, "alice")
    assert api.post("/notes", headers=fresh,
                    json={"title": "too much", "content": "x" * 4001}).status_code == 422


def test_report_service_binds_username_and_input_to_signed_authority(tmp_path):
    _, _, reports = service_clients(tmp_path)
    token = issue_authority(REPORTS_SECRET, subject="alice-id", caller="api", audience="reports",
                            action="report:create", resource=report_scope([]), username="alice")
    response = reports.post("/reports", headers={"Authorization": f"Bearer {token}"},
                            json={"username": "bob", "notes": []})
    assert response.status_code == 403
    tampered = reports.post("/reports", headers={"Authorization": f"Bearer {token}"},
                            json={"username": "alice", "notes": [{"id": "note-1", "title": "Changed",
                                                                        "content": "Not in signed input"}]})
    assert tampered.status_code == 403
