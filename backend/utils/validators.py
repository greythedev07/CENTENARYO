"""
CENTENARYO Data Validators Utility
================================

Purpose: Validate input data across all system modules
Connects to: backend/services/*.py
Dependencies: re, datetime

This utility handles data validation for:
- Senior citizen registration data
- Payroll information validation
- Inventory data verification
- User authentication credentials
- System configuration parameters

Used by: All backend services for input validation
"""

from __future__ import annotations

import re
from typing import Optional

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(normalize_email(email)))


def validate_password_strength(password: str) -> Optional[str]:
    if len(password) < 6:
        return "Password must be at least 6 characters long."
    return None


def normalize_username(username: str) -> str:
    return (username or "").strip()


def validate_username(username: str) -> Optional[str]:
    normalized_username = normalize_username(username)
    if not normalized_username:
        return "Username is required."
    if " " in normalized_username:
        return "Username must not contain spaces."
    if len(normalized_username) < 4:
        return "Username must be at least 4 characters long."
    return None
