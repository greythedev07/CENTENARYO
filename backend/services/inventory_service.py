"""
CENTENARYO Inventory Service
============================

Purpose: Inventory stock and issuance management for OSCA staff.
"""

from __future__ import annotations

from sqlite3 import IntegrityError
from typing import Any, Dict, List, Optional

from backend.database import DatabaseManager


class InventoryService:
    def __init__(self, database: DatabaseManager) -> None:
        self.database = database
        self._initialize_tables()

    def _initialize_tables(self) -> None:
        with self.database._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS inventory_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL,
                    category TEXT NOT NULL CHECK(category IN ('Medicine', 'Grocery')),
                    stock_quantity INTEGER NOT NULL DEFAULT 0,
                    unit TEXT NOT NULL DEFAULT 'booklet',
                    serialized_code TEXT UNIQUE NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS booklet_issuances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    senior_id INTEGER NOT NULL,
                    inventory_item_id INTEGER NOT NULL,
                    quantity_issued INTEGER NOT NULL,
                    date_issued TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    issued_by_staff TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'issued',
                    remarks TEXT,
                    FOREIGN KEY (inventory_item_id) REFERENCES inventory_items(id),
                    FOREIGN KEY (senior_id) REFERENCES senior_citizens(id)
                )
                """
            )
            conn.commit()

    def list_items(self, search: str = "") -> Dict[str, Any]:
        query = (search or "").strip().lower()
        with self.database._get_connection() as conn:
            if query:
                rows = conn.execute(
                    """
                    SELECT id, item_name, category, stock_quantity, unit, serialized_code, status, created_at
                    FROM inventory_items
                    WHERE LOWER(item_name) LIKE ? OR LOWER(serialized_code) LIKE ?
                    ORDER BY created_at DESC
                    """,
                    (f"%{query}%", f"%{query}%"),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT id, item_name, category, stock_quantity, unit, serialized_code, status, created_at
                    FROM inventory_items
                    ORDER BY created_at DESC
                    """
                ).fetchall()
        return {"ok": True, "items": [dict(row) for row in rows]}

    def create_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        item_name = str(payload.get("item_name", "")).strip()
        category = str(payload.get("category", "")).strip()
        unit = str(payload.get("unit", "booklet")).strip() or "booklet"
        serialized_code = str(payload.get("serialized_code", "")).strip()
        status = str(payload.get("status", "active")).strip() or "active"
        try:
            stock_quantity = int(payload.get("stock_quantity", 0))
        except (TypeError, ValueError):
            return {"ok": False, "error": "Stock quantity must be a valid number."}

        if not item_name or not serialized_code:
            return {"ok": False, "error": "Item name and serialized code are required."}
        if category not in {"Medicine", "Grocery"}:
            return {"ok": False, "error": "Category must be Medicine or Grocery."}
        if stock_quantity < 0:
            return {"ok": False, "error": "Stock quantity cannot be negative."}

        try:
            with self.database._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO inventory_items (item_name, category, stock_quantity, unit, serialized_code, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (item_name, category, stock_quantity, unit, serialized_code, status),
                )
                conn.commit()
        except IntegrityError:
            return {"ok": False, "error": "Serialized code already exists."}

        return {"ok": True, "message": "Inventory item created successfully."}

    def update_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            item_id = int(payload.get("id"))
            stock_quantity = int(payload.get("stock_quantity", 0))
        except (TypeError, ValueError):
            return {"ok": False, "error": "Invalid item id or stock quantity."}

        item_name = str(payload.get("item_name", "")).strip()
        category = str(payload.get("category", "")).strip()
        unit = str(payload.get("unit", "booklet")).strip() or "booklet"
        serialized_code = str(payload.get("serialized_code", "")).strip()
        status = str(payload.get("status", "active")).strip() or "active"

        if not item_name or not serialized_code:
            return {"ok": False, "error": "Item name and serialized code are required."}
        if category not in {"Medicine", "Grocery"}:
            return {"ok": False, "error": "Category must be Medicine or Grocery."}
        if stock_quantity < 0:
            return {"ok": False, "error": "Stock quantity cannot be negative."}

        try:
            with self.database._get_connection() as conn:
                conn.execute(
                    """
                    UPDATE inventory_items
                    SET item_name = ?, category = ?, stock_quantity = ?, unit = ?, serialized_code = ?, status = ?
                    WHERE id = ?
                    """,
                    (item_name, category, stock_quantity, unit, serialized_code, status, item_id),
                )
                conn.commit()
        except IntegrityError:
            return {"ok": False, "error": "Serialized code already exists."}

        return {"ok": True, "message": "Inventory item updated successfully."}

    def delete_item(self, item_id: int) -> Dict[str, Any]:
        try:
            resolved_id = int(item_id)
        except (TypeError, ValueError):
            return {"ok": False, "error": "Invalid item id."}

        with self.database._get_connection() as conn:
            usage = conn.execute(
                "SELECT COUNT(*) as total FROM booklet_issuances WHERE inventory_item_id = ?",
                (resolved_id,),
            ).fetchone()
            if usage and int(usage["total"]) > 0:
                return {"ok": False, "error": "Cannot delete item with issuance history."}

            conn.execute("DELETE FROM inventory_items WHERE id = ?", (resolved_id,))
            conn.commit()
        return {"ok": True, "message": "Inventory item deleted successfully."}

    def _get_senior_columns(self) -> List[str]:
        with self.database._get_connection() as conn:
            table = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='senior_citizens'"
            ).fetchone()
            if not table:
                return []
            rows = conn.execute("PRAGMA table_info(senior_citizens)").fetchall()
            return [row[1] for row in rows]

    def search_seniors(self, query: str = "") -> Dict[str, Any]:
        columns = self._get_senior_columns()
        if not columns:
            return {"ok": True, "seniors": []}

        searchable_columns = [name for name in ("full_name", "name", "username", "id_number", "id") if name in columns]
        display_name_col = "full_name" if "full_name" in columns else ("name" if "name" in columns else "username")
        barangay_col = "barangay" if "barangay" in columns else None
        age_col = "age" if "age" in columns else None
        status_col = "status" if "status" in columns else None

        select_columns = ["id", f"{display_name_col} AS display_name"]
        if age_col:
            select_columns.append(age_col)
        if barangay_col:
            select_columns.append(barangay_col)
        if status_col:
            select_columns.append(status_col)
        if "username" in columns and "username" not in select_columns:
            select_columns.append("username")
        if "id_number" in columns:
            select_columns.append("id_number")

        resolved_query = (query or "").strip().lower()
        with self.database._get_connection() as conn:
            if resolved_query and searchable_columns:
                filters = " OR ".join([f"LOWER(CAST({col} AS TEXT)) LIKE ?" for col in searchable_columns])
                params = tuple([f"%{resolved_query}%"] * len(searchable_columns))
                rows = conn.execute(
                    f"""
                    SELECT {", ".join(select_columns)}
                    FROM senior_citizens
                    WHERE {filters}
                    ORDER BY id DESC
                    LIMIT 100
                    """,
                    params,
                ).fetchall()
            else:
                rows = conn.execute(
                    f"""
                    SELECT {", ".join(select_columns)}
                    FROM senior_citizens
                    ORDER BY id DESC
                    LIMIT 100
                    """
                ).fetchall()
        return {"ok": True, "seniors": [dict(row) for row in rows]}

    def get_senior_profile(self, senior_id: int) -> Dict[str, Any]:
        columns = self._get_senior_columns()
        if not columns:
            return {"ok": False, "error": "Senior citizens table is not available."}
        try:
            resolved_id = int(senior_id)
        except (TypeError, ValueError):
            return {"ok": False, "error": "Invalid senior id."}

        with self.database._get_connection() as conn:
            row = conn.execute(
                f"SELECT * FROM senior_citizens WHERE id = ?",
                (resolved_id,),
            ).fetchone()
            if not row:
                return {"ok": False, "error": "Senior record not found."}
            return {"ok": True, "senior": dict(row)}

    def issue_booklet(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            senior_id = int(payload.get("senior_id"))
            inventory_item_id = int(payload.get("inventory_item_id"))
            quantity_issued = int(payload.get("quantity_issued"))
        except (TypeError, ValueError):
            return {"ok": False, "error": "Invalid issuance input values."}

        issued_by_staff = str(payload.get("issued_by_staff", "")).strip()
        remarks = str(payload.get("remarks", "")).strip() or None
        status = str(payload.get("status", "issued")).strip() or "issued"

        if quantity_issued <= 0:
            return {"ok": False, "error": "Issued quantity must be greater than zero."}
        if not issued_by_staff:
            return {"ok": False, "error": "Staff username is required for issuance."}

        with self.database._get_connection() as conn:
            senior_exists = conn.execute(
                "SELECT id FROM senior_citizens WHERE id = ?",
                (senior_id,),
            ).fetchone()
            if not senior_exists:
                return {"ok": False, "error": "Senior record not found."}

            item = conn.execute(
                "SELECT id, stock_quantity FROM inventory_items WHERE id = ?",
                (inventory_item_id,),
            ).fetchone()
            if not item:
                return {"ok": False, "error": "Inventory item not found."}
            if int(item["stock_quantity"]) < quantity_issued:
                return {"ok": False, "error": "Insufficient stock for this issuance."}

            conn.execute(
                """
                INSERT INTO booklet_issuances
                (senior_id, inventory_item_id, quantity_issued, issued_by_staff, status, remarks)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (senior_id, inventory_item_id, quantity_issued, issued_by_staff, status, remarks),
            )
            conn.execute(
                """
                UPDATE inventory_items
                SET stock_quantity = stock_quantity - ?
                WHERE id = ?
                """,
                (quantity_issued, inventory_item_id),
            )
            conn.commit()
        return {"ok": True, "message": "Booklet issued successfully."}

    def get_history(self, limit: int = 20) -> Dict[str, Any]:
        resolved_limit = 20
        try:
            if limit:
                resolved_limit = max(1, min(int(limit), 100))
        except (TypeError, ValueError):
            resolved_limit = 20

        with self.database._get_connection() as conn:
            senior_columns = self._get_senior_columns()
            display_name_expr = "sc.full_name" if "full_name" in senior_columns else ("sc.name" if "name" in senior_columns else "sc.username")
            rows = conn.execute(
                f"""
                SELECT bi.id,
                       bi.date_issued,
                       bi.quantity_issued,
                       bi.issued_by_staff,
                       bi.status,
                       bi.remarks,
                       ii.item_name,
                       ii.serialized_code,
                       {display_name_expr} as senior_name
                FROM booklet_issuances bi
                LEFT JOIN inventory_items ii ON ii.id = bi.inventory_item_id
                LEFT JOIN senior_citizens sc ON sc.id = bi.senior_id
                ORDER BY bi.date_issued DESC
                LIMIT ?
                """,
                (resolved_limit,),
            ).fetchall()
        return {"ok": True, "history": [dict(row) for row in rows]}
