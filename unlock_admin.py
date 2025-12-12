#!/usr/bin/env python3
"""
Script pour débloquer et réinitialiser le compte admin
Usage: python unlock_admin.py
"""

import sqlite3
import bcrypt
from pathlib import Path

# Configuration
DB_PATH = "data/autoecole.db"
ADMIN_USERNAME = "admin"
NEW_PASSWORD = "admin123"

def reset_admin():
    """Réinitialiser le compte admin"""
    db_path = Path(DB_PATH)
    
    if not db_path.exists():
        print(f"❌ Base de données non trouvée: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Vérifier si l'utilisateur admin existe
        cursor.execute("SELECT id, username, is_locked, failed_login_attempts FROM users WHERE username = ?", (ADMIN_USERNAME,))
        result = cursor.fetchone()
        
        if not result:
            print(f"❌ Utilisateur '{ADMIN_USERNAME}' non trouvé!")
            print("\n📋 Utilisateurs existants:")
            cursor.execute("SELECT id, username, email, is_active, is_locked FROM users")
            for row in cursor.fetchall():
                print(f"  - ID: {row[0]}, Username: {row[1]}, Email: {row[2]}, Active: {row[3]}, Locked: {row[4]}")
            conn.close()
            return False
        
        user_id, username, is_locked, failed_attempts = result
        print(f"\n✅ Utilisateur trouvé: {username}")
        print(f"   - ID: {user_id}")
        print(f"   - Verrouillé: {bool(is_locked)}")
        print(f"   - Tentatives échouées: {failed_attempts}")
        
        # Générer le hash du nouveau mot de passe
        password_hash = bcrypt.hashpw(NEW_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Mettre à jour l'utilisateur
        cursor.execute("""
            UPDATE users 
            SET password_hash = ?,
                password_plain = ?,
                is_locked = 0,
                failed_login_attempts = 0,
                is_active = 1
            WHERE username = ?
        """, (password_hash, NEW_PASSWORD, ADMIN_USERNAME))
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Compte admin réinitialisé avec succès!")
        print(f"   - Nouveau mot de passe: {NEW_PASSWORD}")
        print(f"   - Compte déverrouillé: ✓")
        print(f"   - Tentatives réinitialisées: ✓")
        print(f"   - Compte activé: ✓")
        print(f"\n🔑 Vous pouvez maintenant vous connecter avec:")
        print(f"   Username: {ADMIN_USERNAME}")
        print(f"   Password: {NEW_PASSWORD}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erreur SQLite: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔓 Déblocage et réinitialisation du compte admin")
    print("=" * 60)
    reset_admin()
    print("=" * 60)
