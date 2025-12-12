#!/usr/bin/env python3
"""
Script pour vérifier et débloquer le compte admin
Utilise uniquement sqlite3 (bibliothèque standard Python)
"""

import sqlite3
from pathlib import Path

DB_PATH = "data/autoecole.db"

def check_admin():
    """Vérifier l'état du compte admin"""
    db_path = Path(DB_PATH)
    
    if not db_path.exists():
        print(f"❌ Base de données non trouvée: {DB_PATH}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Récupérer les informations de l'admin
        cursor.execute("""
            SELECT id, username, email, is_active, is_locked, 
                   failed_login_attempts, password_plain, password_hash
            FROM users 
            WHERE username = 'admin'
        """)
        
        result = cursor.fetchone()
        
        if not result:
            print("❌ Aucun utilisateur 'admin' trouvé!")
            print("\n📋 Utilisateurs existants:")
            cursor.execute("SELECT id, username, email FROM users")
            for row in cursor.fetchall():
                print(f"   - ID: {row[0]}, Username: {row[1]}, Email: {row[2]}")
        else:
            user_id, username, email, is_active, is_locked, failed_attempts, pwd_plain, pwd_hash = result
            
            print("\n" + "="*60)
            print("📊 Informations du compte admin")
            print("="*60)
            print(f"ID: {user_id}")
            print(f"Username: {username}")
            print(f"Email: {email}")
            print(f"Actif: {'✅ OUI' if is_active else '❌ NON'}")
            print(f"Verrouillé: {'🔒 OUI' if is_locked else '✅ NON'}")
            print(f"Tentatives échouées: {failed_attempts}")
            print(f"Mot de passe stocké: {pwd_plain if pwd_plain else '(non disponible)'}")
            print(f"Hash présent: {'✅ OUI' if pwd_hash else '❌ NON'}")
            print("="*60)
            
            # Si le compte est verrouillé, proposer de le débloquer
            if is_locked or failed_attempts > 0:
                print("\n⚠️  Le compte admin est verrouillé ou a des tentatives échouées!")
                print("\n🔧 Pour débloquer, exécutez les commandes SQL suivantes:")
                print("\n--- DÉBUT DES COMMANDES SQL ---")
                print(f"UPDATE users SET is_locked = 0, failed_login_attempts = 0, is_active = 1 WHERE username = 'admin';")
                print("--- FIN DES COMMANDES SQL ---")
                
                # Débloquer automatiquement
                print("\n🔓 Déblocage automatique en cours...")
                cursor.execute("""
                    UPDATE users 
                    SET is_locked = 0, 
                        failed_login_attempts = 0, 
                        is_active = 1
                    WHERE username = 'admin'
                """)
                conn.commit()
                print("✅ Compte admin débloqué avec succès!")
                
                if pwd_plain:
                    print(f"\n🔑 Vous pouvez maintenant vous connecter avec:")
                    print(f"   Username: admin")
                    print(f"   Password: {pwd_plain}")
                else:
                    print(f"\n⚠️  Mot de passe non disponible en clair.")
                    print(f"   Si vous ne connaissez pas le mot de passe, vous devrez le réinitialiser.")
            else:
                print("\n✅ Le compte admin n'est pas verrouillé.")
                if pwd_plain:
                    print(f"\n🔑 Identifiants de connexion:")
                    print(f"   Username: admin")
                    print(f"   Password: {pwd_plain}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Erreur SQLite: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_admin()
