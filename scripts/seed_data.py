"""
CENTENARYO Database Seeding Script
=================================

Purpose: Populate database with realistic test data for development and testing
Connects to: backend/database.py, backend/models.py
Dependencies: faker, pandas, datetime

This script generates synthetic but realistic data for CENTENARYO development:
- Creates test users with different roles (admin, encoder, auditor, viewer)
- Generates senior citizen records with realistic Filipino demographics
- Creates sample pension disbursement records
- Adds inventory tracking data (IDs, booklets)
- Inserts sample anomaly flags for testing ML detection
- Populates system settings and configuration

Generated data includes:
- Realistic Filipino names and addresses
- Proper age distribution (60-95 years)
- Geographic distribution across barangays
- Historical pension payment patterns
- Sample anomaly scenarios for testing

Usage:
    python scripts/seed_data.py [--clear] [--count=1000]
    
Options:
    --clear    Clear existing data before seeding
    --count    Number of senior citizens to generate (default: 100)

Used by: Development team for testing, ML model training, demos
"""