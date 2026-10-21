import os
import secrets
import socket
import subprocess
import sys
import time

import httpx

TEST_PASSWORDS = {username: f"{username}-test-{secrets.token_urlsafe(16)}"
                  for username in ("alice", "bob", "admin")}


def free_port():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def start_service(module, port, env):
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", f"{module}:create_app", "--factory",
         "--host", "127.0.0.1", "--port", str(port)],
        env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def wait_ready(process, url):
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise AssertionError(f"service exited early with code {process.returncode}")
        try:
            if httpx.get(f"{url}/openapi.json", timeout=0.3).status_code == 200:
                return
        except httpx.HTTPError:
            time.sleep(0.1)
    raise AssertionError(f"service did not start at {url}")


def test_real_three_process_report_workflow(tmp_path):
    notes_port, reports_port, api_port = free_port(), free_port(), free_port()
    notes_secret = secrets.token_urlsafe(32)
    reports_secret = secrets.token_urlsafe(32)
    base_env = os.environ.copy()
    api_env = base_env | {
        "API_NOTES_SECRET": notes_secret,
        "API_REPORTS_SECRET": reports_secret,
        "API_DB": str(tmp_path / "api.sqlite3"),
        "SEED_ALICE_PASSWORD": TEST_PASSWORDS["alice"],
        "SEED_BOB_PASSWORD": TEST_PASSWORDS["bob"],
        "SEED_ADMIN_PASSWORD": TEST_PASSWORDS["admin"],
        "NOTES_SERVICE_URL": f"http://127.0.0.1:{notes_port}",
        "REPORTS_SERVICE_URL": f"http://127.0.0.1:{reports_port}",
    }
    notes_env = base_env | {"API_NOTES_SECRET": notes_secret,
                            "NOTES_DB": str(tmp_path / "notes.sqlite3")}
    reports_env = base_env | {"API_REPORTS_SECRET": reports_secret}

    api_main = "services.api.main"
    notes_process = start_service("services.notes.main", notes_port, notes_env)
    reports_process = start_service("services.reports.main", reports_port, reports_env)
    api_process = None
    try:
        wait_ready(notes_process, f"http://127.0.0.1:{notes_port}")
        wait_ready(reports_process, f"http://127.0.0.1:{reports_port}")
        api_process = start_service(api_main, api_port, api_env)
        wait_ready(api_process, f"http://127.0.0.1:{api_port}")
        base = f"http://127.0.0.1:{api_port}"
        with httpx.Client(base_url=base, timeout=3) as client:
            login = client.post("/auth/login", json={"username": "alice", "password": TEST_PASSWORDS["alice"]})
            assert login.status_code == 200
            auth = {"Authorization": f"Bearer {login.json()['access_token']}"}
            note = client.post("/notes", headers=auth,
                               json={"title": "Process test", "content": "Only Alice can read this"})
            assert note.status_code == 201
            report = client.post("/reports", headers=auth, json={"note_ids": [note.json()["id"]]})
            assert report.status_code == 200
            assert "Only Alice can read this" in report.json()["report"]
    finally:
        for process in (api_process, reports_process, notes_process):
            if process is not None:
                process.terminate()
        for process in (api_process, reports_process, notes_process):
            if process is not None:
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
