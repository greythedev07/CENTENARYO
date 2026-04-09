"""
Test script to verify database mode
Run this to check if cloud/local detection works
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from backend.database import DatabaseManager

def main():
    print("=" * 50)
    print("CENTENARYO Database Mode Test")
    print("=" * 50)
    
    db = DatabaseManager()
    
    if db.is_cloud_mode():
        print("\n✅ RUNNING IN CLOUD MODE")
        print("   - Database hosted on SQLite Cloud")
        print("   - Team members share the same data")
        print("   - Internet connection required")
    else:
        print("\n✅ RUNNING IN LOCAL MODE")
        print("   - Database is local file: data/centenaryo.db")
        print("   - Works completely offline")
        print("   - No internet required")
    
    print("\n" + "=" * 50)
    
    # Test basic operation
    import logging
    import time
    logging.disable(logging.ERROR)  # Suppress sqlitecloud internal error logging
    
    try:
        # Use unique username to avoid conflicts
        test_username = f"test_user_{int(time.time())}"
        
        # Create a test user
        user_id = db.create_user(
            username=test_username,
            password_hash="test_hash",
            full_name="Test User",
            role="viewer"
        )
        print(f"\n✅ Database is working! Created test user with ID: {user_id}")
        
        # Verify user can be retrieved
        user = db.get_user_by_username(test_username)
        if user and user["id"] == user_id:
            print("✅ User retrieval working")
        
        # Clean up (hard delete to actually remove the test user)
        db.hard_delete_user(user_id)
        print("✅ Test user cleaned up")
        
    except Exception as e:
        print(f"\n⚠️ Database test failed: {e}")
    finally:
        logging.disable(logging.NOTSET)  # Re-enable logging
    
    db.close()
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()