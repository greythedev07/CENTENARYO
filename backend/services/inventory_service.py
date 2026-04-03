"""
CENTENARYO Inventory Service
============================

Purpose: Business logic for physical benefit asset management
Connects to: backend/database.py, backend/models.py
Dependencies: backend/utils/serial_generator.py

This service handles all inventory-related operations:
- Senior ID card issuance and tracking
- Discount booklet management (medicine, grocery)
- Serial number generation and validation
- Asset lifecycle tracking (issued, lost, damaged, retired)
- Replacement and renewal processing
- Inventory reporting and analytics

Used by: Frontend inventory module, senior service, audit service
"""
