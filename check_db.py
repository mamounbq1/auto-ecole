#!/usr/bin/env python3
"""
Script de diagnostic de la base de données
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.models import get_session, Student, User
from src.config import DATABASE_PATH

def main():
    print(f"\n{'='*60}")
    print("DIAGNOSTIC BASE DE DONNÉES")
    print(f"{'='*60}\n")
    
    print(f"📁 Chemin DB : {DATABASE_PATH}")
    print(f"✓ Existe : {Path(DATABASE_PATH).exists()}")
    
    if Path(DATABASE_PATH).exists():
        print(f"📊 Taille : {Path(DATABASE_PATH).stat().st_size} octets")
    
    print("\n" + "-"*60)
    
    try:
        session = get_session()
        
        # Compter les utilisateurs
        user_count = session.query(User).count()
        print(f"\n👥 Utilisateurs : {user_count}")
        
        if user_count > 0:
            print("\nListe des utilisateurs :")
            users = session.query(User).all()
            for user in users:
                print(f"  • {user.username} - {user.full_name} ({user.role.value})")
        
        # Compter les élèves
        student_count = session.query(Student).count()
        print(f"\n🎓 Élèves : {student_count}")
        
        if student_count > 0:
            print("\nListe des élèves :")
            students = session.query(Student).all()
            for student in students:
                print(f"  • {student.full_name} - Balance: {student.balance} DH")
        
        session.close()
        
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
