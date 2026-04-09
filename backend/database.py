"""
CENTENARYO Database Module
==========================

Purpose: SQLite database connection, schema management, and query operations
Supports: Local SQLite (production) OR SQLite Cloud (team development)
Connects to: All backend services (senior, payroll, inventory, audit)
Dependencies: SQLite3, sqlitecloud (for cloud mode)

This module handles all database operations for the CENTENARYO system including:
- Database connection and transaction management (local or cloud)
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

import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

# Import SQLite Cloud support
try:
    import sqlitecloud
    CLOUD_SUPPORT = True
except ImportError:
    CLOUD_SUPPORT = False
    print("⚠️ sqlitecloud not installed. Run: pip install sqlitecloud")
    sqlitecloud = None


class DatabaseManager:
    """
    SQLite manager supporting both local SQLite and SQLite Cloud.
    
    Mode selection:
    - If SQLITE_CLOUD_CONNECTION_STRING env var exists → cloud mode
    - Otherwise → local SQLite mode
    
    For team development: Set SQLITE_CLOUD_CONNECTION_STRING environment variable
    For production: Just use local SQLite (no env var needed)
    """

    def __init__(self, db_path: str = "data/centenaryo.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.cloud_mode = False
        self.cloud_conn_string = os.getenv('SQLITE_CLOUD_CONNECTION_STRING', '')
        
        self._initialize_connection()
        self._initialize_schema()

    def _initialize_connection(self) -> None:
        """Set up connection based on environment configuration."""
        
        # Check if cloud connection string is provided
        if self.cloud_conn_string and CLOUD_SUPPORT:
            try:
                # Test cloud connection
                test_conn = sqlitecloud.connect(self.cloud_conn_string)
                test_conn.close()
                self.cloud_mode = True
                print("✅ CENTENARYO running in CLOUD mode (team sync enabled)")
                # Mask API key in display
                masked = self.cloud_conn_string.split('?')[0] if '?' in self.cloud_conn_string else self.cloud_conn_string[:50]
                print(f"   Cloud endpoint: {masked}")
                return
            except Exception as e:
                print(f"⚠️ Cloud connection failed: {e}")
                print("   Falling back to local SQLite mode...")
                self.cloud_mode = False
        elif self.cloud_conn_string and not CLOUD_SUPPORT:
            print("⚠️ Cloud connection string provided but sqlitecloud not installed")
            print("   Install with: pip install sqlitecloud")
            print("   Falling back to local SQLite mode...")
        
        self.cloud_mode = False
        print("✅ CENTENARYO running in LOCAL SQLite mode (offline-capable)")
        print(f"   Database path: {self.db_path.absolute()}")

    def _get_connection(self) -> Union[sqlite3.Connection, Any]:
        """
        Get appropriate database connection.
        Returns cloud connection if in cloud mode, otherwise local SQLite.
        """
        if self.cloud_mode:
            # SQLite Cloud connection
            return sqlitecloud.connect(self.cloud_conn_string)
        
        # Local SQLite mode
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _get_users_columns(self, conn: Union[sqlite3.Connection, Any]) -> Set[str]:
        """Get column names from users table."""
        cursor = conn.execute("PRAGMA table_info(users)")
        return {row[1] for row in cursor.fetchall()}

    def _row_to_dict(self, row: Any, columns: list[str]) -> Dict[str, Any]:
        """Convert row to dict, handling both sqlite3.Row and sqlitecloud rows."""
        if row is None:
            return None
        if hasattr(row, 'keys') and callable(getattr(row, 'keys')):
            # sqlite3.Row style
            return dict(row)
        # sqlitecloud returns tuples, create dict from columns
        return {col: row[i] for i, col in enumerate(columns)}

    def _initialize_schema(self) -> None:
        """Create tables if they don't exist (works for both local and cloud)."""
        with self._get_connection() as conn:
            # Check if users table exists
            cursor = conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name='users'"
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
                        role TEXT DEFAULT 'viewer',
                        is_active INTEGER DEFAULT 1,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        last_login TEXT
                    )
                    """
                )
            
            conn.commit()

    def create_user(
        self,
        username: str,
        password_hash: str,
        full_name: Optional[str] = None,
        role: str = "viewer",
    ) -> int:
        """Create a new user account."""
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
            
            # Get last insert ID (works for both SQLite and SQLite Cloud)
            return int(cursor.lastrowid)

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by username."""
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
            return self._row_to_dict(row, select_columns)

    def mark_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp."""
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

    def is_cloud_mode(self) -> bool:
        """Return True if using cloud database, False for local."""
        return self.cloud_mode

    def get_all_users(self) -> list[Dict[str, Any]]:
        """Retrieve all users (for admin purposes)."""
        with self._get_connection() as conn:
            columns = self._get_users_columns(conn)
            select_columns = ["id", "username", "full_name", "last_login"]
            if "role" in columns:
                select_columns.append("role")
            if "is_active" in columns:
                select_columns.append("is_active")
            
            select_sql = ", ".join(select_columns)
            rows = conn.execute(f"SELECT {select_sql} FROM users").fetchall()
            return [self._row_to_dict(row, select_columns) for row in rows]

    def update_user_role(self, user_id: int, new_role: str) -> bool:
        """Update a user's role."""
        with self._get_connection() as conn:
            columns = self._get_users_columns(conn)
            if "updated_at" in columns:
                cursor = conn.execute(
                    "UPDATE users SET role = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (new_role, user_id),
                )
            else:
                cursor = conn.execute(
                    "UPDATE users SET role = ? WHERE id = ?",
                    (new_role, user_id),
                )
            conn.commit()
            return cursor.rowcount > 0

    def delete_user(self, user_id: int) -> bool:
        """Delete a user (soft delete by setting is_active = 0)."""
        with self._get_connection() as conn:
            columns = self._get_users_columns(conn)
            if "updated_at" in columns:
                cursor = conn.execute(
                    "UPDATE users SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (user_id,),
                )
            else:
                cursor = conn.execute(
                    "UPDATE users SET is_active = 0 WHERE id = ?",
                    (user_id,),
                )
            conn.commit()
            return cursor.rowcount > 0

    def hard_delete_user(self, user_id: int) -> bool:
        """Permanently delete a user from the database."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM users WHERE id = ?",
                (user_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def close(self) -> None:
        """Close any open connections (placeholder for future connection pooling)."""
        pass