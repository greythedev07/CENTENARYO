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
