#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test complet du module Paiements"""

import sys
from pathlib import Path

# Configuration encodage Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from src.controllers.payment_controller import PaymentController
from src.models import PaymentMethod

print("="*60)
print("  TEST MODULE PAIEMENTS - Verification complete")
print("="*60)
print()

try:
    # Test 1: Récupération des paiements
    print("1. Recuperation des paiements...")
    payments = PaymentController.get_all_payments()
    print(f"   [OK] {len(payments)} paiements recuperes")
    print()
    
    # Test 2: Vérification des champs
    print("2. Verification des champs de paiement...")
    if payments:
        for i, p in enumerate(payments[:3], 1):
            print(f"   Paiement {i}:")
            print(f"      - ID: {p.id}")
            print(f"      - Montant: {p.amount} DH")
            print(f"      - Date: {p.payment_date} (type: {type(p.payment_date).__name__})")
            print(f"      - Categorie: {p.category} (type: {type(p.category).__name__})")
            print(f"      - Methode: {p.payment_method} (type: {type(p.payment_method).__name__})")
            
            # Test de conversion
            category_str = p.category if p.category else "N/A"
            method_str = p.payment_method.value if p.payment_method else "N/A"
            
            print(f"      - Categorie (affichage): {category_str}")
            print(f"      - Methode (affichage): {method_str}")
            print(f"      - Valide: {'Oui' if p.is_validated else 'Non'}")
            print()
    
    # Test 3: Vérification des enums PaymentMethod
    print("3. Verification des valeurs PaymentMethod...")
    print(f"   PaymentMethod.CASH = {PaymentMethod.CASH.value}")
    print(f"   PaymentMethod.CHECK = {PaymentMethod.CHECK.value}")
    print(f"   PaymentMethod.CARD = {PaymentMethod.CARD.value}")
    print(f"   PaymentMethod.TRANSFER = {PaymentMethod.TRANSFER.value}")
    print()
    
    # Test 4: Calcul statistiques (comme dans le widget)
    print("4. Test calcul statistiques (widget simulation)...")
    from datetime import datetime, date
    
    today = datetime.now().date()
    today_payments = [p for p in payments 
                     if (p.payment_date if isinstance(p.payment_date, date) 
                         else p.payment_date.date()) == today]
    today_amount = sum(p.amount for p in today_payments)
    
    month = datetime.now().month
    year = datetime.now().year
    month_payments = [p for p in payments 
                     if (p.payment_date if isinstance(p.payment_date, date) 
                         else p.payment_date.date()).month == month 
                     and (p.payment_date if isinstance(p.payment_date, date) 
                         else p.payment_date.date()).year == year]
    month_amount = sum(p.amount for p in month_payments)
    
    print(f"   Paiements aujourd'hui: {len(today_payments)} ({today_amount:,.2f} DH)")
    print(f"   Paiements ce mois: {len(month_payments)} ({month_amount:,.2f} DH)")
    print(f"   Total paiements: {len(payments)} ({sum(p.amount for p in payments):,.2f} DH)")
    print()
    
    print("="*60)
    print("  TOUS LES TESTS REUSSIS!")
    print("="*60)
    print()
    print("Le module Paiements peut maintenant s'ouvrir sans erreur!")
    print()

except Exception as e:
    print()
    print(f"[ERREUR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
