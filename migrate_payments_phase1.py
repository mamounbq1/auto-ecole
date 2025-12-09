#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migration PHASE 1 - Corrections Paiements
Recalcule tous les soldes des élèves basés sur les paiements réels
"""

import sys
from pathlib import Path
from decimal import Decimal

# Ajouter le répertoire au path
sys.path.insert(0, str(Path(__file__).parent))

from src.models import get_session, Student, Payment
from src.utils import get_logger

logger = get_logger()

print("=" * 80)
print("  MIGRATION PHASE 1 - CORRECTIONS MODULE PAIEMENTS")
print("=" * 80)
print()
print("Cette migration va :")
print("  1. Recalculer tous les soldes élèves basés sur les paiements réels")
print("  2. Exclure les paiements annulés du calcul")
print("  3. Convertir les montants en Decimal pour précision")
print("  4. Synchroniser balance = total_paid - total_due")
print()
input("Appuyez sur Entrée pour continuer ou Ctrl+C pour annuler...")
print()

try:
    session = get_session()
    
    # Récupérer tous les élèves
    students = session.query(Student).all()
    print(f"✓ {len(students)} élèves trouvés")
    print()
    
    # Statistiques
    students_updated = 0
    total_corrections = 0
    errors = 0
    
    for student in students:
        try:
            print(f"Traitement: {student.full_name} (ID: {student.id})")
            
            # Sauvegarder anciennes valeurs
            old_total_paid = float(student.total_paid) if student.total_paid else 0.0
            old_total_due = float(student.total_due) if student.total_due else 0.0
            old_balance = float(student.balance) if student.balance else 0.0
            
            # Recalculer total_paid depuis les paiements réels (NON ANNULÉS)
            payments = session.query(Payment).filter(
                Payment.student_id == student.id,
                Payment.is_cancelled == False  # IMPORTANT
            ).all()
            
            new_total_paid = sum(float(p.amount) for p in payments)
            
            # total_due reste inchangé (défini par les inscriptions/séances)
            new_total_due = old_total_due
            
            # Calculer nouveau balance
            new_balance = new_total_paid - new_total_due
            
            # Vérifier si changement nécessaire
            needs_update = (
                abs(new_total_paid - old_total_paid) > 0.01 or
                abs(new_balance - old_balance) > 0.01
            )
            
            if needs_update:
                print(f"  ⚠️  Correction nécessaire:")
                print(f"      Total Payé:  {old_total_paid:>10,.2f} → {new_total_paid:>10,.2f} DH")
                print(f"      Total Dû:    {old_total_due:>10,.2f} (inchangé)")
                print(f"      Balance:     {old_balance:>10,.2f} → {new_balance:>10,.2f} DH")
                
                # Déterminer si dette ou crédit
                if new_balance < 0:
                    print(f"      Status:      🔴 DETTE de {abs(new_balance):,.2f} DH")
                elif new_balance > 0:
                    print(f"      Status:      🟢 CRÉDIT de {new_balance:,.2f} DH")
                else:
                    print(f"      Status:      ✅ À JOUR")
                
                # Appliquer corrections
                student.total_paid = Decimal(str(round(new_total_paid, 2)))
                student.total_due = Decimal(str(round(new_total_due, 2)))
                student.balance = Decimal(str(round(new_balance, 2)))
                
                students_updated += 1
                total_corrections += 1
            else:
                print(f"  ✓ Solde correct (balance: {old_balance:,.2f} DH)")
            
            print()
            
        except Exception as e:
            print(f"  ❌ ERREUR: {str(e)}")
            errors += 1
            print()
    
    # Commit toutes les modifications
    if students_updated > 0:
        print("=" * 80)
        print("Sauvegarde des modifications...")
        session.commit()
        print("✓ Modifications sauvegardées avec succès")
    else:
        print("=" * 80)
        print("Aucune modification nécessaire")
    
    print()
    print("=" * 80)
    print("  RÉSUMÉ DE LA MIGRATION")
    print("=" * 80)
    print(f"  Élèves traités:      {len(students)}")
    print(f"  Élèves corrigés:     {students_updated}")
    print(f"  Total corrections:   {total_corrections}")
    print(f"  Erreurs:             {errors}")
    print("=" * 80)
    print()
    
    if errors == 0:
        print("✅ MIGRATION RÉUSSIE - Tous les soldes sont maintenant synchronisés")
    else:
        print(f"⚠️  MIGRATION TERMINÉE AVEC {errors} ERREUR(S)")
    
    print()
    print("Vous pouvez maintenant lancer l'application:")
    print("  python src/main_gui.py")
    print()

except KeyboardInterrupt:
    print("\n\n⚠️  Migration annulée par l'utilisateur")
    sys.exit(1)

except Exception as e:
    print(f"\n\n❌ ERREUR CRITIQUE: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
