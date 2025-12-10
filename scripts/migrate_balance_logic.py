"""
Script de migration pour corriger la logique du solde

LOGIQUE CORRECTE: balance = total_paid - total_due
- Balance négative = Dette (l'étudiant doit de l'argent)
- Balance positive = Crédit (l'école doit de l'argent à l'étudiant)
- Balance zéro = À jour

Ce script recalcule tous les soldes existants avec la formule correcte.
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
            # Recalculer avec la formule CORRECTE:
            # balance = total_paid - total_due
            # Négatif = Dette, Positif = Crédit, Zéro = À jour
            old_balance = student.balance
            new_balance = student.total_paid - student.total_due
            
            status = "DETTE" if new_balance < 0 else ("CRÉDIT" if new_balance > 0 else "À JOUR")
            
            print(f"  {student.full_name}: "
                  f"Ancien={old_balance:,.2f}, "
                  f"Nouveau={new_balance:,.2f} [{status}] "
                  f"(Payé={student.total_paid:,.2f}, Dû={student.total_due:,.2f})")
            
            student.balance = new_balance
        
        session.commit()
        print(f"\n✅ Migration réussie! {len(students)} étudiants mis à jour.")
        
        # Vérification
        print("\n📊 Vérification:")
        students_with_debt = session.query(Student).filter(Student.balance < 0).count()
        students_with_credit = session.query(Student).filter(Student.balance > 0).count()
        students_balanced = session.query(Student).filter(Student.balance == 0).count()
        
        print(f"  - Étudiants avec DETTE (balance < 0): {students_with_debt}")
        print(f"  - Étudiants avec CRÉDIT (balance > 0): {students_with_credit}")
        print(f"  - Étudiants À JOUR (balance = 0): {students_balanced}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erreur lors de la migration: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("="*60)
    print("CORRECTION DE LA LOGIQUE DU SOLDE")
    print("="*60)
    print("\nCe script va recalculer TOUS les soldes avec la formule CORRECTE:")
    print("  FORMULE: balance = total_paid - total_due")
    print("  • balance < 0 → DETTE (l'étudiant doit de l'argent)")
    print("  • balance > 0 → CRÉDIT (l'école doit de l'argent)")
    print("  • balance = 0 → À JOUR")
    print()
    
    response = input("Voulez-vous continuer? (oui/non): ")
    if response.lower() in ['oui', 'o', 'yes', 'y']:
        migrate_balance()
    else:
        print("Migration annulée.")
