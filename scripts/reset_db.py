"""
CENTENARYO Database Reset Script
===============================

Purpose: Reset database to clean state for development/testing
Connects to: backend/database.py
Dependencies: sqlite3, os

This script provides a clean slate for CENTENARYO development:
- Drops all existing tables and recreates them
- Preserves schema structure from database.py
- Resets auto-increment sequences
- Clears all data while maintaining table structure
- Useful for testing, development, and demos

Usage:
    python scripts/reset_db.py [--backup]
    
Options:
    --backup    Create backup of existing data before reset
    
Safety features:
- Creates automatic backup before deletion
- Confirmation prompt for destructive operations
- Verifies database integrity after reset

Used by: Development team for clean testing environments
"""
