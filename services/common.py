"""Shared, small helpers used by the independently started services."""

import base64
import hashlib
import hmac
import json
import os
import time
from collections.abc import Mapping
from typing import Any


class InvalidAuthority(Exception):
    pass


def required_secret(name: str) -> bytes:
    value = os.environ.get(name, "")
    if len(value) < 32:
        raise RuntimeError(f"{name} must contain at least 32 characters")
    return value.encode()


def report_scope(notes: list[Mapping[str, str]]) -> str:
    canonical = json.dumps(notes, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def issue_authority(secret: bytes, *, subject: str, caller: str, audience: str,
                    action: str, resource: str, username: str = "", lifetime: int = 30) -> str:
    now = int(time.time())
    payload = {"sub": subject, "username": username, "caller": caller, "aud": audience, "action": action,
               "resource": resource, "iat": now, "exp": now + lifetime}
    body = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    signature = hmac.new(secret, body.encode(), hashlib.sha256).digest()
    sig = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{body}.{sig}"


def verify_authority(token: str, secret: bytes, *, audience: str, action: str,
                     resource: str | None = None) -> dict[str, Any]:
    try:
        body, supplied_sig = token.split(".")
        expected_sig = base64.urlsafe_b64encode(
            hmac.new(secret, body.encode(), hashlib.sha256).digest()
        ).decode().rstrip("=")
        if not hmac.compare_digest(supplied_sig, expected_sig):
            raise InvalidAuthority
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        now = int(time.time())
        if (payload["aud"] != audience or payload["action"] != action
                or not isinstance(payload["sub"], str) or not payload["sub"]
                or payload["caller"] != "api" or payload["iat"] > now + 5
                or payload["exp"] <= now or payload["exp"] - payload["iat"] > 30):
            raise InvalidAuthority
        if resource is not None and payload["resource"] != resource:
            raise InvalidAuthority
        return payload
    except (ValueError, KeyError, TypeError, json.JSONDecodeError, base64.binascii.Error) as exc:
        raise InvalidAuthority from exc
