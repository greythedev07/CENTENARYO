"""
Login service for authenticating users and managing sessions.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from backend.database import DatabaseManager
from backend.utils.validators import normalize_username, validate_username


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        encoded_salt, encoded_digest = stored_hash.split(":", maxsplit=1)
        salt = base64.b64decode(encoded_salt)
        expected_digest = base64.b64decode(encoded_digest)
    except Exception:
        return False

    actual_digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return hmac.compare_digest(actual_digest, expected_digest)


class LoginService:
    def __init__(self, database: DatabaseManager) -> None:
        self.database = database
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def login(self, username: str, password: str, remember_me: bool = False) -> Dict[str, Any]:
        normalized_username = normalize_username(username)

        if not normalized_username or not password:
            return {"ok": False, "error": "Username and password are required."}
        username_error = validate_username(normalized_username)
        if username_error:
            return {"ok": False, "error": username_error}

        user = self.database.get_user_by_username(normalized_username)
        if not user or not _verify_password(password, user["password_hash"]):
            return {"ok": False, "error": "Invalid username or password."}
        if "is_active" in user and int(user["is_active"]) != 1:
            return {"ok": False, "error": "This account is inactive. Please contact an administrator."}

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=30 if remember_me else 1)
        self._sessions[token] = {
            "user_id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "expires_at": expires_at.isoformat(),
        }
        self.database.mark_last_login(int(user["id"]))

        return {
            "ok": True,
            "token": token,
            "expires_at": expires_at.isoformat(),
            "user": {
                "id": user["id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "role": user.get("role"),
            },
        }

    def logout(self, token: str) -> Dict[str, Any]:
        if token in self._sessions:
            self._sessions.pop(token, None)
        return {"ok": True}

    def get_session(self, token: str) -> Dict[str, Any]:
        if not token:
            return {"ok": False, "error": "No session token provided."}

        session = self._sessions.get(token)
        if not session:
            return {"ok": False, "error": "Session not found."}

        if datetime.now(timezone.utc) > datetime.fromisoformat(session["expires_at"]):
            self._sessions.pop(token, None)
            return {"ok": False, "error": "Session expired."}

        return {"ok": True, "session": session}
