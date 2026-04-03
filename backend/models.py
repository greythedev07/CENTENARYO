"""
CENTENARYO Data Models
======================

Purpose: Data model classes and validation for all entities
Connects to: backend/database.py (persistence), backend/services/*.py (business logic)
Dependencies: None (pure Python data classes)

This module defines the core data structures for the CENTENARYO system matching schema.sql:
- User: Authentication and role management
- SeniorCitizen: Master registry of senior citizens
- PensionDisbursement: Quarterly pension payment records
- DiscountBooklet: Inventory tracking for benefit booklets
- SeniorID: QR-coded identification card management
- AnomalyFlag: AI-detected suspicious records with risk scoring
- AuditLog: Complete system activity tracking
- SystemSetting: Configuration key-value store

All models include validation methods to ensure data integrity
and prevent invalid records from entering the system.

Used by: All backend service modules for data validation and transfer
"""
