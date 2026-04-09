"""
CENTENARYO Senior Citizen Service
================================

Purpose: Business logic for senior citizen registry management
Connects to: backend/database.py, backend/models.py
Dependencies: backend/utils/validators.py

This service handles all senior citizen-related operations:
- CRUD operations for senior citizen records
- Registration and profile management
- Duplicate detection and prevention
- Vital status updates (deceased reporting)
- Search and filtering functionality
- Data validation and integrity checks

Used by: Frontend registry module, payroll service, audit service
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

from backend.database import DatabaseManager


class SeniorService:
    def __init__(self, database: DatabaseManager) -> None:
        self.database = database

    @staticmethod
    def _compute_status(vital_status: str, is_active: int) -> str:
        if (vital_status or "").lower() == "deceased":
            return "Deceased"
        if int(is_active or 0) == 0:
            return "Inactive"
        return "Active"

    @staticmethod
    def _build_full_name(row: Dict[str, Any]) -> str:
        parts = [
            (row.get("first_name") or "").strip(),
            (row.get("middle_name") or "").strip(),
            (row.get("last_name") or "").strip(),
            (row.get("suffix") or "").strip(),
        ]
        return " ".join([part for part in parts if part])

    def list_seniors(
        self,
        query: str = "",
        status: str = "",
        page: int = 1,
        page_size: int = 20,
        sort_key: str = "id",
        sort_dir: str = "asc",
    ) -> Dict[str, Any]:
        resolved_page = max(1, int(page or 1))
        resolved_page_size = max(1, min(int(page_size or 20), 100))
        offset = (resolved_page - 1) * resolved_page_size

        sortable_map = {
            "id": "id",
            "full_name": "last_name, first_name, middle_name",
            "username": "unique_identifier",
            "age": "age",
            "barangay": "barangay",
            "contact_number": "contact_number",
            "status": "vital_status, is_active",
            "registration_date": "registration_date",
        }
        resolved_sort_key = sort_key if sort_key in sortable_map else "id"
        resolved_sort_dir = "DESC" if str(sort_dir).lower() == "desc" else "ASC"
        order_clause = f"{sortable_map[resolved_sort_key]} {resolved_sort_dir}"

        filters: List[str] = []
        params: List[Any] = []

        q = (query or "").strip().lower()
        if q:
            filters.append(
                "("
                "LOWER(first_name) LIKE ? OR LOWER(middle_name) LIKE ? OR LOWER(last_name) LIKE ? OR "
                "LOWER(unique_identifier) LIKE ? OR LOWER(barangay) LIKE ?"
                ")"
            )
            pattern = f"%{q}%"
            params.extend([pattern, pattern, pattern, pattern, pattern])

        normalized_status = (status or "").strip().lower()
        if normalized_status == "active":
            filters.append("LOWER(vital_status) != 'deceased' AND is_active = 1")
        elif normalized_status == "inactive":
            filters.append("LOWER(vital_status) != 'deceased' AND is_active = 0")
        elif normalized_status == "deceased":
            filters.append("LOWER(vital_status) = 'deceased'")

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""

        with self.database._get_connection() as conn:
            total_row = conn.execute(
                f"SELECT COUNT(*) AS total FROM senior_citizens {where_sql}",
                tuple(params),
            ).fetchone()
            total = int(total_row["total"]) if total_row else 0

            rows = conn.execute(
                f"""
                SELECT id, unique_identifier, first_name, middle_name, last_name, suffix, age, barangay,
                       contact_number, is_active, vital_status, registration_date, birth_date, sex, address,
                       city_municipality, is_indigent, date_of_death, last_updated, notes
                FROM senior_citizens
                {where_sql}
                ORDER BY {order_clause}
                LIMIT ? OFFSET ?
                """,
                tuple(params + [resolved_page_size, offset]),
            ).fetchall()

        seniors = []
        for row in rows:
            data = dict(row)
            seniors.append(
                {
                    **data,
                    "full_name": self._build_full_name(data),
                    "username": data.get("unique_identifier"),
                    "status": self._compute_status(data.get("vital_status", ""), data.get("is_active", 0)),
                }
            )

        return {
            "ok": True,
            "seniors": seniors,
            "pagination": {
                "page": resolved_page,
                "page_size": resolved_page_size,
                "total": total,
                "total_pages": max(1, (total + resolved_page_size - 1) // resolved_page_size),
            },
            "sort": {
                "sort_key": resolved_sort_key,
                "sort_dir": resolved_sort_dir.lower(),
            },
        }

    def get_senior(self, senior_id: int) -> Dict[str, Any]:
        with self.database._get_connection() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM senior_citizens
                WHERE id = ?
                """,
                (int(senior_id),),
            ).fetchone()
        if not row:
            return {"ok": False, "error": "Senior record not found."}
        data = dict(row)
        data["full_name"] = self._build_full_name(data)
        data["username"] = data.get("unique_identifier")
        data["status"] = self._compute_status(data.get("vital_status", ""), data.get("is_active", 0))
        return {"ok": True, "senior": data}

    def create_senior(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        first_name = str(payload.get("first_name", "")).strip()
        middle_name = str(payload.get("middle_name", "")).strip() or None
        last_name = str(payload.get("last_name", "")).strip()
        suffix = str(payload.get("suffix", "")).strip() or None
        unique_identifier = str(payload.get("unique_identifier", "")).strip()
        birth_date = str(payload.get("birth_date", "")).strip()
        age = payload.get("age")
        sex = str(payload.get("sex", "")).strip() or None
        address = str(payload.get("address", "")).strip()
        barangay = str(payload.get("barangay", "")).strip() or None
        city_municipality = str(payload.get("city_municipality", "")).strip() or None
        contact_number = str(payload.get("contact_number", "")).strip() or None
        notes = str(payload.get("notes", "")).strip() or None
        registration_date = str(payload.get("registration_date", "")).strip() or str(date.today())

        try:
            age_value = int(age) if age not in (None, "") else None
            is_indigent = int(payload.get("is_indigent", 0) or 0)
            is_active = int(payload.get("is_active", 1) or 1)
        except (TypeError, ValueError):
            return {"ok": False, "error": "Invalid numeric field values."}

        vital_status = str(payload.get("vital_status", "alive")).strip().lower() or "alive"
        date_of_death = str(payload.get("date_of_death", "")).strip() or None

        if not first_name or not last_name or not unique_identifier or not birth_date or not address:
            return {"ok": False, "error": "Please complete all required fields."}

        with self.database._get_connection() as conn:
            exists = conn.execute(
                "SELECT id FROM senior_citizens WHERE unique_identifier = ?",
                (unique_identifier,),
            ).fetchone()
            if exists:
                return {"ok": False, "error": "Username already exists."}
            conn.execute(
                """
                INSERT INTO senior_citizens (
                    unique_identifier, first_name, middle_name, last_name, suffix, birth_date, age, sex,
                    address, barangay, city_municipality, contact_number, is_indigent, vital_status,
                    date_of_death, is_active, registration_date, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    unique_identifier, first_name, middle_name, last_name, suffix, birth_date, age_value, sex,
                    address, barangay, city_municipality, contact_number, is_indigent, vital_status,
                    date_of_death, is_active, registration_date, notes,
                ),
            )
            conn.commit()
        return {"ok": True, "message": "Senior record created successfully."}

    def update_senior(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            senior_id = int(payload.get("id"))
            age_value = int(payload.get("age")) if payload.get("age") not in (None, "") else None
            is_indigent = int(payload.get("is_indigent", 0) or 0)
            is_active = int(payload.get("is_active", 1) or 1)
        except (TypeError, ValueError):
            return {"ok": False, "error": "Invalid numeric field values."}

        first_name = str(payload.get("first_name", "")).strip()
        middle_name = str(payload.get("middle_name", "")).strip() or None
        last_name = str(payload.get("last_name", "")).strip()
        suffix = str(payload.get("suffix", "")).strip() or None
        unique_identifier = str(payload.get("unique_identifier", "")).strip()
        birth_date = str(payload.get("birth_date", "")).strip()
        sex = str(payload.get("sex", "")).strip() or None
        address = str(payload.get("address", "")).strip()
        barangay = str(payload.get("barangay", "")).strip() or None
        city_municipality = str(payload.get("city_municipality", "")).strip() or None
        contact_number = str(payload.get("contact_number", "")).strip() or None
        notes = str(payload.get("notes", "")).strip() or None
        registration_date = str(payload.get("registration_date", "")).strip() or str(date.today())
        vital_status = str(payload.get("vital_status", "alive")).strip().lower() or "alive"
        date_of_death = str(payload.get("date_of_death", "")).strip() or None

        if not first_name or not last_name or not unique_identifier or not birth_date or not address:
            return {"ok": False, "error": "Please complete all required fields."}

        with self.database._get_connection() as conn:
            duplicate = conn.execute(
                "SELECT id FROM senior_citizens WHERE unique_identifier = ? AND id != ?",
                (unique_identifier, senior_id),
            ).fetchone()
            if duplicate:
                return {"ok": False, "error": "Username already exists."}

            conn.execute(
                """
                UPDATE senior_citizens
                SET unique_identifier = ?, first_name = ?, middle_name = ?, last_name = ?, suffix = ?,
                    birth_date = ?, age = ?, sex = ?, address = ?, barangay = ?, city_municipality = ?,
                    contact_number = ?, is_indigent = ?, vital_status = ?, date_of_death = ?, is_active = ?,
                    registration_date = ?, notes = ?, last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    unique_identifier, first_name, middle_name, last_name, suffix,
                    birth_date, age_value, sex, address, barangay, city_municipality,
                    contact_number, is_indigent, vital_status, date_of_death, is_active,
                    registration_date, notes, senior_id,
                ),
            )
            conn.commit()
        return {"ok": True, "message": "Senior record updated successfully."}

    def delete_senior(self, senior_id: int) -> Dict[str, Any]:
        try:
            resolved_id = int(senior_id)
        except (TypeError, ValueError):
            return {"ok": False, "error": "Invalid senior id."}

        with self.database._get_connection() as conn:
            conn.execute("DELETE FROM senior_citizens WHERE id = ?", (resolved_id,))
            conn.commit()
        return {"ok": True, "message": "Senior record deleted successfully."}
