#!/usr/bin/env python3
"""
Test rapide du dashboard pour vérifier que les statistiques se chargent correctement
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, date
from src.controllers import StudentController, PaymentController, SessionController

print("="*60)
print("  TEST DU DASHBOARD - Auto-École Manager")
print("="*60)
print()

try:
    # Test 1: Élèves
    print("1️⃣  Test des élèves...")
    students = StudentController.get_all_students()
    active_students = sum(1 for s in students if s.status.value == 'active')
    print(f"   ✅ {len(students)} élèves trouvés, {active_students} actifs")
    
    # Test 2: Paiements
    print("\n2️⃣  Test des paiements...")
    today = datetime.now()
    start_of_month = today.replace(day=1).date()
    
    all_payments = PaymentController.get_all_payments()
    print(f"   ✅ {len(all_payments)} paiements trouvés")
    
    payments = [p for p in all_payments if p.payment_date and 
               p.payment_date >= start_of_month]
    monthly_revenue = sum(p.amount for p in payments if p.is_validated)
    print(f"   ✅ CA mensuel: {monthly_revenue:.2f} DH ({len(payments)} paiements ce mois)")
    
    # Test 3: Sessions
    print("\n3️⃣  Test des sessions...")
    sessions_today = SessionController.get_today_sessions()
    print(f"   ✅ {len(sessions_today)} sessions aujourd'hui")
    
    # Test 4: Élèves avec dette
    print("\n4️⃣  Test des impayés...")
    students_with_debt = sum(1 for s in students if s.balance < 0)
    print(f"   ✅ {students_with_debt} élèves avec impayés")
    
    print("\n" + "="*60)
    print("  ✅ TOUS LES TESTS RÉUSSIS !")
    print("="*60)
    print()
    print("Statistiques du dashboard :")
    print(f"  👥 Élèves actifs       : {active_students}")
    print(f"  💰 CA mensuel          : {monthly_revenue:.2f} DH")
    print(f"  📅 Sessions aujourd'hui: {len(sessions_today)}")
    print(f"  ⚠️  Impayés            : {students_with_debt}")
    print()
    print("🎉 Le dashboard devrait fonctionner correctement !")
    print()
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
    print("\n⚠️  Le dashboard pourrait avoir des problèmes.")
    sys.exit(1)
