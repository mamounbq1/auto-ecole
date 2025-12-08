#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test des paiements et de la gestion des dates"""

import sys
from pathlib import Path
from datetime import datetime, date

# Ajouter le répertoire au path
sys.path.insert(0, str(Path(__file__).parent))

from src.controllers.payment_controller import PaymentController
from src.controllers.student_controller import StudentController

print("="*60)
print("  TEST DES PAIEMENTS - Verification des dates")
print("="*60)
print()

try:
    # Récupérer tous les paiements
    print("1. Recuperation des paiements...")
    payments = PaymentController.get_all_payments()
    print(f"   → {len(payments)} paiements trouves")
    print()
    
    if payments:
        print("2. Verification des types de payment_date...")
        for i, p in enumerate(payments[:3], 1):
            date_type = type(p.payment_date).__name__
            print(f"   Paiement {i}:")
            print(f"      - ID: {p.payment_id}")
            print(f"      - Montant: {p.amount} DH")
            print(f"      - Date: {p.payment_date}")
            print(f"      - Type: {date_type}")
            
            # Test de conversion
            if isinstance(p.payment_date, date):
                test_date = p.payment_date
            else:
                test_date = p.payment_date.date()
            print(f"      - Conversion OK: {test_date}")
            print()
    
    # Test de calcul des statistiques
    print("3. Test calcul statistiques...")
    today = datetime.now().date()
    today_payments = [p for p in payments 
                     if (p.payment_date if isinstance(p.payment_date, date) 
                         else p.payment_date.date()) == today]
    today_amount = sum(p.amount for p in today_payments)
    print(f"   → Paiements aujourd'hui: {len(today_payments)}")
    print(f"   → Montant aujourd'hui: {today_amount:.2f} DH")
    print()
    
    month = datetime.now().month
    year = datetime.now().year
    month_payments = [p for p in payments 
                     if (p.payment_date if isinstance(p.payment_date, date) 
                         else p.payment_date.date()).month == month 
                     and (p.payment_date if isinstance(p.payment_date, date) 
                         else p.payment_date.date()).year == year]
    month_amount = sum(p.amount for p in month_payments)
    print(f"   → Paiements ce mois: {len(month_payments)}")
    print(f"   → Montant ce mois: {month_amount:.2f} DH")
    print()
    
    # Récupérer les étudiants
    print("4. Verification des etudiants...")
    students = StudentController.get_all_students()
    print(f"   → {len(students)} etudiants trouves")
    print()
    
    print("="*60)
    print("  TOUS LES TESTS REUSSIS!")
    print("="*60)
    print()
    print("L'application peut maintenant demarrer correctement!")
    print()

except Exception as e:
    print(f"\n[ERREUR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
