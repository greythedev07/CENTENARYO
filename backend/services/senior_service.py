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
