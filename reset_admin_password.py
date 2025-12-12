#!/usr/bin/env python3
"""
Reset admin password to 'admin123'
This script works in the local environment without SQLAlchemy
"""

import sqlite3
import hashlib
import os

DB_PATH = "data/autoecole.db"
NEW_PASSWORD = "admin123"

def hash_password_bcrypt_compatible(password: str) -> str:
    """
    Create a bcrypt-compatible hash
    Note: This is a simplified version for emergency use
    In production, the app will rehash with real bcrypt
    """
    # Use SHA256 as a fallback (app should rehash with bcrypt on first login)
    return hashlib.sha256(password.encode()).hexdigest()

def reset_password():
    """Reset admin password"""
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if admin exists
        cursor.execute("SELECT id, username FROM users WHERE username = 'admin'")
        result = cursor.fetchone()
        
        if not result:
            print("❌ Admin user not found!")
            conn.close()
            return False
        
        user_id, username = result
        print(f"✅ Found user: {username} (ID: {user_id})")
        
        # For this to work, we need to create a bcrypt hash
        # Let's create a temporary password that the user can change
        # We'll set it to a simple SHA256 for now, but recommend immediate password change
        
        print("\n⚠️  IMPORTANT: This script requires bcrypt to set a secure password.")
        print("    Please use the application to reset the password properly.")
        print("\n📋 Alternative solution:")
        print("    1. Run the app with a temporary database")
        print("    2. Or use the test_rbac.py script to recreate the admin user")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("🔑 Admin Password Reset Tool")
    print("="*60)
    print()
    
    # Check if bcrypt is available
    try:
        import bcrypt
        print("✅ bcrypt is available")
        
        # Now we can properly reset the password
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Generate proper bcrypt hash
        password_hash = bcrypt.hashpw(NEW_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update admin password
        cursor.execute("""
            UPDATE users 
            SET password_hash = ?,
                is_locked = 0,
                failed_login_attempts = 0,
                is_active = 1
            WHERE username = 'admin'
        """, (password_hash,))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Password reset successfully!")
        print(f"\n🔑 New login credentials:")
        print(f"   Username: admin")
        print(f"   Password: {NEW_PASSWORD}")
        print()
        print("="*60)
        
    except ImportError:
        print("❌ bcrypt is not available in this environment")
        print()
        reset_password()
