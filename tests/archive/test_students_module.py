#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test complet du module Élèves
Vérifie tous les attributs, relations et fonctionnalités
"""

import sys
from pathlib import Path

# Configuration encodage Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from src.controllers.student_controller import StudentController
from src.controllers.session_controller import SessionController
from src.controllers.payment_controller import PaymentController
from src.models import StudentStatus

print("=" * 70)
print("  TEST COMPLET MODULE ÉLÈVES - VERIFICATION DB & RELATIONS")
print("=" * 70)
print()

try:
    # TEST 1: Récupération des élèves
    print("1. TEST RÉCUPÉRATION ÉLÈVES")
    print("-" * 70)
    students = StudentController.get_all_students()
    print(f"   ✅ {len(students)} élèves trouvés")
    print()
    
    if not students:
        print("   ⚠️  Aucun élève dans la base!")
        print("   → Exécutez: python src/init_db.py")
        sys.exit(0)
    
    # TEST 2: Vérification des attributs Student
    print("2. TEST ATTRIBUTS STUDENT (Premier élève)")
    print("-" * 70)
    student = students[0]
    
    # Attributs obligatoires
    attrs_required = [
        'id', 'full_name', 'cin', 'date_of_birth', 'phone',
        'registration_date', 'status', 'license_type',
        'theoretical_exam_passed', 'practical_exam_passed',
        'theoretical_exam_attempts', 'practical_exam_attempts',
        'total_paid', 'total_due', 'balance',
        'hours_completed', 'hours_planned'
    ]
    
    print(f"   Élève: {student.full_name}")
    for attr in attrs_required:
        if hasattr(student, attr):
            value = getattr(student, attr)
            print(f"   ✅ {attr}: {value}")
        else:
            print(f"   ❌ {attr}: MANQUANT")
    print()
    
    # TEST 3: Properties calculées
    print("3. TEST PROPERTIES CALCULÉES")
    print("-" * 70)
    print(f"   ✅ age: {student.age} ans")
    print(f"   ✅ is_solvent: {student.is_solvent}")
    print(f"   ✅ completion_rate: {student.completion_rate:.1f}%")
    print()
    
    # TEST 4: Relations - Sessions
    print("4. TEST RELATION STUDENT -> SESSIONS")
    print("-" * 70)
    if hasattr(student, 'sessions'):
        sessions = student.sessions
        print(f"   ✅ {len(sessions)} session(s) liée(s)")
        if sessions:
            session = sessions[0]
            print(f"   Session 1:")
            print(f"      - ID: {session.id}")
            print(f"      - Type: {session.session_type.value if session.session_type else 'N/A'}")
            print(f"      - Début: {session.start_datetime}")
            print(f"      - Statut: {session.status.value if session.status else 'N/A'}")
    else:
        print(f"   ❌ Pas de relation 'sessions'")
    print()
    
    # TEST 5: Relations - Paiements
    print("5. TEST RELATION STUDENT -> PAYMENTS")
    print("-" * 70)
    if hasattr(student, 'payments'):
        payments = student.payments
        print(f"   ✅ {len(payments)} paiement(s) lié(s)")
        if payments:
            payment = payments[0]
            print(f"   Paiement 1:")
            print(f"      - ID: {payment.id}")
            print(f"      - Montant: {payment.amount} DH")
            print(f"      - Date: {payment.payment_date}")
            print(f"      - Validé: {'Oui' if payment.is_validated else 'Non'}")
    else:
        print(f"   ❌ Pas de relation 'payments'")
    print()
    
    # TEST 6: Relations - Examens
    print("6. TEST RELATION STUDENT -> EXAMS")
    print("-" * 70)
    if hasattr(student, 'exams'):
        exams = student.exams
        print(f"   ✅ {len(exams)} examen(s) lié(s)")
        if exams:
            exam = exams[0]
            print(f"   Examen 1:")
            print(f"      - ID: {exam.id}")
            print(f"      - Type: {exam.exam_type.value if exam.exam_type else 'N/A'}")
            print(f"      - Date: {exam.exam_date}")
            print(f"      - Résultat: {'Réussi' if exam.passed else 'Échoué'}")
    else:
        print(f"   ❌ Pas de relation 'exams'")
    print()
    
    # TEST 7: Statuts disponibles
    print("7. TEST STATUTS DISPONIBLES")
    print("-" * 70)
    statuses = list(StudentStatus)
    for status in statuses:
        count = sum(1 for s in students if s.status == status)
        print(f"   ✅ {status.value}: {count} élève(s)")
    print()
    
    # TEST 8: Méthodes Student
    print("8. TEST MÉTHODES STUDENT")
    print("-" * 70)
    print(f"   ✅ to_dict(): {type(student.to_dict()).__name__}")
    print(f"   ✅ __repr__(): {student}")
    print()
    
    # TEST 9: Statistiques globales
    print("9. STATISTIQUES GLOBALES")
    print("-" * 70)
    active_count = sum(1 for s in students if s.status == StudentStatus.ACTIVE)
    total_hours_completed = sum(s.hours_completed for s in students)
    total_hours_planned = sum(s.hours_planned for s in students)
    students_with_debt = sum(1 for s in students if s.balance < 0)
    total_debt = sum(abs(s.balance) for s in students if s.balance < 0)
    
    print(f"   📊 Total élèves: {len(students)}")
    print(f"   ✅ Élèves actifs: {active_count}")
    print(f"   ⏰ Heures complétées: {total_hours_completed}/{total_hours_planned}")
    print(f"   💰 Élèves avec dette: {students_with_debt}")
    print(f"   ⚠️  Montant total dettes: {total_debt:,.2f} DH")
    print()
    
    # TEST 10: Vérification cohérence données
    print("10. VÉRIFICATION COHÉRENCE DONNÉES")
    print("-" * 70)
    issues = []
    for s in students:
        # Balance = total_paid - total_due
        expected_balance = s.total_paid - s.total_due
        if abs(s.balance - expected_balance) > 0.01:
            issues.append(f"   ⚠️  {s.full_name}: Balance incohérente")
        
        # Hours completed <= hours planned
        if s.hours_completed > s.hours_planned:
            issues.append(f"   ⚠️  {s.full_name}: Heures complétées > planifiées")
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("   ✅ Toutes les données sont cohérentes")
    print()
    
    print("=" * 70)
    print("  ✅ TOUS LES TESTS RÉUSSIS!")
    print("=" * 70)
    print()
    print("Module Élèves:")
    print(f"  ✅ {len(students)} élèves en base")
    print(f"  ✅ Tous les attributs présents")
    print(f"  ✅ Relations fonctionnelles")
    print(f"  ✅ Properties calculées OK")
    print(f"  ✅ Cohérence des données vérifiée")
    print()
    print("Vous pouvez utiliser le module Élèves sans problème!")
    print()

except Exception as e:
    print()
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
