"""
Registration service for creating user accounts.
"""

from __future__ import annotations

import base64
import hashlib
import os
from sqlite3 import IntegrityError
from typing import Any, Dict, Optional

from backend.database import DatabaseManager
from backend.utils.validators import normalize_username, validate_password_strength, validate_username


def _hash_password(password: str, salt: Optional[bytes] = None) -> str:
    local_salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), local_salt, 120_000)
    return f"{base64.b64encode(local_salt).decode()}:{base64.b64encode(digest).decode()}"


class RegistrationService:
    def __init__(self, database: DatabaseManager) -> None:
        self.database = database

    def register(self, full_name: str, username: str, password: str, confirm_password: str) -> Dict[str, Any]:
        normalized_username = normalize_username(username)
        normalized_full_name = (full_name or "").strip() or None

        if not normalized_username or not password or not confirm_password:
            return {"ok": False, "error": "Please complete all required fields."}
        username_error = validate_username(normalized_username)
        if username_error:
            return {"ok": False, "error": username_error}
        password_error = validate_password_strength(password)
        if password_error:
            return {"ok": False, "error": password_error}
        if password != confirm_password:
            return {"ok": False, "error": "Passwords do not match."}
        if self.database.get_user_by_username(normalized_username):
            return {"ok": False, "error": "This username is already taken."}

        try:
            self.database.create_user(
                username=normalized_username,
                full_name=normalized_full_name,
                password_hash=_hash_password(password),
            )
        except IntegrityError:
            return {"ok": False, "error": "This username is already taken."}

        return {"ok": True, "message": "Registration successful. You can now sign in."}
