"""
CENTENARYO Payroll Service
==========================

Purpose: Business logic for pension payroll generation and management
Connects to: backend/database.py, backend/models.py, backend/services/senior_service.py
Dependencies: backend/utils/pdf_exporter.py

This service handles all payroll-related operations:
- Quarterly pension payroll generation
- Automated beneficiary selection and filtering
- Pension disbursement tracking and status management
- Payroll report generation and printing
- Integration with senior citizen registry
- Audit trail for all payroll operations

Used by: Frontend payroll module, audit service, external payment systems
"""