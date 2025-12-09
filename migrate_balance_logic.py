"""
Script de migration pour inverser la logique du solde

ANCIENNE LOGIQUE: balance = total_paid - total_due
- Balance négative = Dette
- Balance positive = Crédit

NOUVELLE LOGIQUE: balance = total_due - total_paid
- Balance positive = Dette
- Balance négative = Crédit

Ce script inverse tous les soldes existants dans la base de données.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models import get_session, Student
from sqlalchemy import func

def migrate_balance():
    """Migrer tous les soldes vers la nouvelle logique"""
    session = get_session()
    
    try:
        # Récupérer tous les étudiants
        students = session.query(Student).all()
        
        print(f"Migration de {len(students)} étudiants...")
        
        for student in students:
            # Ancienne logique: balance = total_paid - total_due
            # Nouvelle logique: balance = total_due - total_paid
            # Donc on inverse simplement le signe
            old_balance = student.balance
            new_balance = -old_balance
            
            # Ou recalculer depuis les valeurs:
            new_balance = student.total_due - student.total_paid
            
            print(f"  {student.full_name}: "
                  f"Ancien solde={old_balance:,.2f}, "
                  f"Nouveau solde={new_balance:,.2f} "
                  f"(Total dû={student.total_due:,.2f}, Total payé={student.total_paid:,.2f})")
            
            student.balance = new_balance
        
        session.commit()
        print(f"\n✅ Migration réussie! {len(students)} étudiants mis à jour.")
        
        # Vérification
        print("\n📊 Vérification:")
        students_with_debt = session.query(Student).filter(Student.balance > 0).count()
        students_with_credit = session.query(Student).filter(Student.balance < 0).count()
        students_balanced = session.query(Student).filter(Student.balance == 0).count()
        
        print(f"  - Étudiants avec dette (balance > 0): {students_with_debt}")
        print(f"  - Étudiants avec crédit (balance < 0): {students_with_credit}")
        print(f"  - Étudiants à jour (balance = 0): {students_balanced}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erreur lors de la migration: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("="*60)
    print("MIGRATION DE LA LOGIQUE DU SOLDE")
    print("="*60)
    print("\nCe script va inverser la logique du solde:")
    print("  AVANT: balance = total_paid - total_due (négatif = dette)")
    print("  APRÈS: balance = total_due - total_paid (positif = dette)")
    print()
    
    response = input("Voulez-vous continuer? (oui/non): ")
    if response.lower() in ['oui', 'o', 'yes', 'y']:
        migrate_balance()
    else:
        print("Migration annulée.")
