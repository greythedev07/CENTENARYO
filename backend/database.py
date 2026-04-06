"""
CENTENARYO Database Module
==========================

Purpose: SQLite database connection, schema management, and query operations
Connects to: All backend services (senior, payroll, inventory, audit)
Dependencies: SQLite3, backend/models.py (data models)

This module handles all database operations for the CENTENARYO system including:
- Database connection and transaction management
- Schema creation and migrations based on existing schema.sql
- CRUD operations for all data tables
- Query optimization for performance on government computers

Tables managed (matching existing schema.sql):
- users: Authentication and role management
- senior_citizens: Master registry of senior citizens
- pension_disbursements: Quarterly pension payment records
- discount_booklets: Inventory tracking for benefit booklets
- senior_ids: QR-coded identification card management
- anomaly_flags: AI-detected suspicious records with risk scoring
- audit_logs: Complete system activity tracking
- system_settings: Configuration key-value store

Used by: backend/services/*.py modules
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional, Set


class DatabaseManager:
    """SQLite manager for core CENTENARYO data operations."""

    def __init__(self, db_path: str = "data/centenaryo.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_schema(self) -> None:
        with self._get_connection() as conn:
            # Check if users table exists and has the username column
            cursor = conn.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='users'
                """
            )
            table_exists = cursor.fetchone() is not None
            
            if table_exists:
                # Check if username column exists
                cursor = conn.execute("PRAGMA table_info(users)")
                columns = {row[1] for row in cursor.fetchall()}
                
                if 'username' not in columns:
                    # Table exists but doesn't have username column, recreate it
                    conn.execute("DROP TABLE IF EXISTS users")
                    table_exists = False
            
            if not table_exists:
                # Create the users table with correct schema
                conn.execute(
                    """
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        full_name TEXT,
                        password_hash TEXT NOT NULL,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        last_login TEXT
                    )
                    """
                )
            conn.commit()

    def _get_users_columns(self, conn: sqlite3.Connection) -> Set[str]:
        cursor = conn.execute("PRAGMA table_info(users)")
        return {row[1] for row in cursor.fetchall()}

    def create_user(
        self,
        username: str,
        password_hash: str,
        full_name: Optional[str],
        role: str = "viewer",
    ) -> int:
        with self._get_connection() as conn:
            columns = self._get_users_columns(conn)
            resolved_full_name = (full_name or "").strip() or username

            insert_columns = ["username", "full_name", "password_hash"]
            values = [username, resolved_full_name, password_hash]

            if "role" in columns:
                insert_columns.append("role")
                values.append(role)
            if "is_active" in columns:
                insert_columns.append("is_active")
                values.append(1)

            placeholders = ", ".join(["?"] * len(insert_columns))
            columns_sql = ", ".join(insert_columns)
            cursor = conn.execute(
                f"INSERT INTO users ({columns_sql}) VALUES ({placeholders})",
                tuple(values),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            columns = self._get_users_columns(conn)
            select_columns = ["id", "username", "full_name", "password_hash", "last_login"]
            if "role" in columns:
                select_columns.append("role")
            if "is_active" in columns:
                select_columns.append("is_active")
            if "created_at" in columns:
                select_columns.append("created_at")
            if "updated_at" in columns:
                select_columns.append("updated_at")

            select_sql = ", ".join(select_columns)
            row = conn.execute(
                f"SELECT {select_sql} FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            return dict(row) if row else None

    def mark_last_login(self, user_id: int) -> None:
        with self._get_connection() as conn:
            columns = self._get_users_columns(conn)
            if "updated_at" in columns:
                conn.execute(
                    """
                    UPDATE users
                    SET last_login = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (user_id,),
                )
            else:
                conn.execute(
                    """
                    UPDATE users
                    SET last_login = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (user_id,),
                )
            conn.commit()
