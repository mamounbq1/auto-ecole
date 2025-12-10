#!/usr/bin/env python3
"""
Script de test automatisé pour l'application Auto-École
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from datetime import date, datetime, timedelta
from src.controllers.student_controller import StudentController
from src.controllers.instructor_controller import InstructorController
from src.controllers.vehicle_controller import VehicleController
from src.controllers.payment_controller import PaymentController
from src.controllers.session_controller import SessionController
from src.controllers.exam_controller import ExamController
from src.models import StudentStatus

def print_section(title):
    print('\n' + '='*70)
    print(f'  {title}')
    print('='*70)

def test_students():
    print_section('🧪 TEST MODULE ÉLÈVES')
    
    errors = []
    
    # Test 1: Liste
    print('\n📋 Test 1: Liste des élèves')
    try:
        students = StudentController.get_all_students()
        print(f'   ✅ {len(students)} élèves trouvés')
        for s in students[:2]:
            print(f'      - {s.full_name} | CIN: {s.cin} | Status: {s.status}')
    except Exception as e:
        errors.append(f'Liste élèves: {e}')
        print(f'   ❌ ERREUR: {e}')
    
    # Test 2: Get by ID
    print('\n🔍 Test 2: Récupérer élève par ID')
    try:
        student = StudentController.get_student_by_id(1)
        if student:
            print(f'   ✅ Élève ID=1: {student.full_name}')
            print(f'      Tel: {student.phone}')
            print(f'      Balance: {student.balance} DH')
            print(f'      Heures: {student.hours_completed}/{student.hours_planned}')
        else:
            errors.append('Get student by ID: Aucun élève trouvé')
            print('   ❌ Aucun élève trouvé')
    except Exception as e:
        errors.append(f'Get student by ID: {e}')
        print(f'   ❌ ERREUR: {e}')
    
    # Test 3: Recherche
    print('\n🔎 Test 3: Recherche')
    try:
        results = StudentController.search_students('Sara')
        print(f'   ✅ Recherche "Sara": {len(results)} résultat(s)')
    except Exception as e:
        errors.append(f'Recherche: {e}')
        print(f'   ❌ ERREUR: {e}')
    
    # Test 4: Filtre par statut
    print('\n✅ Test 4: Filtre par statut ACTIVE')
    try:
        active = StudentController.get_all_students(status=StudentStatus.ACTIVE)
        print(f'   ✅ {len(active)} élèves actifs')
    except Exception as e:
        errors.append(f'Filtre statut: {e}')
        print(f'   ❌ ERREUR: {e}')
    
    return errors

def test_instructors():
    print_section('🧪 TEST MODULE MONITEURS')
    
    errors = []
    
    # Test 1: Liste
    print('\n📋 Test 1: Liste des moniteurs')
    try:
        instructors = InstructorController.get_all_instructors()
        print(f'   ✅ {len(instructors)} moniteurs trouvés')
        for i in instructors[:2]:
            print(f'      - {i.full_name} | Tel: {i.phone}')
    except Exception as e:
        errors.append(f'Liste moniteurs: {e}')
        print(f'   ❌ ERREUR: {e}')
    
    # Test 2: Get by ID
    print('\n🔍 Test 2: Récupérer moniteur par ID')
    try:
        instructor = InstructorController.get_instructor_by_id(1)
        if instructor:
            print(f'   ✅ Moniteur ID=1: {instructor.full_name}')
            print(f'      Licence: {instructor.license_number}')
        else:
            errors.append('Get instructor by ID: Aucun moniteur trouvé')
            print('   ❌ Aucun moniteur trouvé')
    except Exception as e:
        errors.append(f'Get instructor by ID: {e}')
        print(f'   ❌ ERREUR: {e}')
    
    return errors

def test_vehicles():
    print_section('🧪 TEST MODULE VÉHICULES')
    
    errors = []
    
    # Test 1: Liste
    print('\n📋 Test 1: Liste des véhicules')
    try:
        vehicles = VehicleController.get_all_vehicles()
        print(f'   ✅ {len(vehicles)} véhicules trouvés')
        for v in vehicles:
            print(f'      - {v.make} {v.model} | {v.plate_number}')
            print(f'        Assurance: {v.insurance_expiry_date}')
            print(f'        Visite technique: {v.technical_inspection_date}')
    except Exception as e:
        errors.append(f'Liste véhicules: {e}')
        print(f'   ❌ ERREUR: {e}')
    
    # Test 2: Vérifier alertes expiration
    print('\n⚠️  Test 2: Vérifier alertes expiration')
    try:
        vehicles = VehicleController.get_all_vehicles()
        today = date.today()
        for v in vehicles:
            if v.insurance_expiry_date:
                days_insurance = (v.insurance_expiry_date - today).days
                if days_insurance < 30:
                    print(f'   🚨 {v.plate_number}: Assurance expire dans {days_insurance}j')
            
            if v.technical_inspection_date:
                days_inspection = (v.technical_inspection_date - today).days
                if days_inspection < 30:
                    print(f'   🚨 {v.plate_number}: Visite expire dans {days_inspection}j')
        print('   ✅ Vérification alertes terminée')
    except Exception as e:
        errors.append(f'Alertes expiration: {e}')
        print(f'   ❌ ERREUR: {e}')
    
    return errors

def test_payments():
    print_section('🧪 TEST MODULE PAIEMENTS')
    
    errors = []
    
    # Test 1: Liste
    print('\n📋 Test 1: Liste des paiements')
    try:
        payments = PaymentController.get_all_payments()
        print(f'   ✅ {len(payments)} paiements trouvés')
        for p in payments[:3]:
            print(f'      - {p.amount} DH | {p.payment_method} | {p.payment_date}')
    except Exception as e:
        errors.append(f'Liste paiements: {e}')
        print(f'   ❌ ERREUR: {e}')
    
    # Test 2: Paiements impayés
    print('\n💰 Test 2: Vérifier impayés')
    try:
        students = StudentController.get_all_students()
        unpaid_count = 0
        unpaid_total = 0
        for s in students:
            if s.balance < 0:
                unpaid_count += 1
                unpaid_total += abs(s.balance)
        print(f'   ✅ {unpaid_count} élèves avec impayés')
        print(f'   ✅ Total impayés: {unpaid_total:.2f} DH')
    except Exception as e:
        errors.append(f'Impayés: {e}')
        print(f'   ❌ ERREUR: {e}')
    
    return errors

def test_sessions():
    print_section('🧪 TEST MODULE SÉANCES')
    
    errors = []
    
    # Test 1: Liste
    print('\n📋 Test 1: Liste des séances')
    try:
        sessions = SessionController.get_all_sessions()
        print(f'   ✅ {len(sessions)} séances trouvées')
    except Exception as e:
        errors.append(f'Liste séances: {e}')
        print(f'   ❌ ERREUR: {e}')
    
    # Test 2: Séances du jour
    print('\n📅 Test 2: Séances aujourd\'hui')
    try:
        today = date.today()
        today_sessions = SessionController.get_sessions_by_date_range(today, today)
        print(f'   ✅ {len(today_sessions)} séances aujourd\'hui')
        for s in today_sessions[:3]:
            print(f'      - {s.session_time} | Durée: {s.duration}min')
    except Exception as e:
        errors.append(f'Séances du jour: {e}')
        print(f'   ❌ ERREUR: {e}')
    
    return errors

def test_exams():
    print_section('🧪 TEST MODULE EXAMENS')
    
    errors = []
    
    # Test 1: Liste
    print('\n📋 Test 1: Liste des examens')
    try:
        exams = ExamController.get_all_exams()
        print(f'   ✅ {len(exams)} examens trouvés')
        for e in exams[:3]:
            print(f'      - {e.exam_type} | {e.scheduled_date} | Résultat: {e.result}')
    except Exception as e:
        errors.append(f'Liste examens: {e}')
        print(f'   ❌ ERREUR: {e}')
    
    # Test 2: Examens à venir (3 jours)
    print('\n📆 Test 2: Examens dans les 3 prochains jours')
    try:
        today = date.today()
        in_3_days = today + timedelta(days=3)
        upcoming = [e for e in ExamController.get_all_exams() 
                   if e.scheduled_date and today <= e.scheduled_date <= in_3_days]
        print(f'   ✅ {len(upcoming)} examens à venir')
        for e in upcoming:
            days_left = (e.scheduled_date - today).days
            print(f'      - Dans {days_left}j: {e.exam_type}')
    except Exception as e:
        errors.append(f'Examens à venir: {e}')
        print(f'   ❌ ERREUR: {e}')
    
    return errors

def main():
    print('\n' + '='*70)
    print('  🚗 AUTO-ÉCOLE - TESTS AUTOMATISÉS')
    print('='*70)
    
    all_errors = []
    
    # Tests des modules
    all_errors.extend(test_students())
    all_errors.extend(test_instructors())
    all_errors.extend(test_vehicles())
    all_errors.extend(test_payments())
    all_errors.extend(test_sessions())
    all_errors.extend(test_exams())
    
    # Résumé
    print_section('📊 RÉSUMÉ DES TESTS')
    
    if all_errors:
        print(f'\n❌ {len(all_errors)} ERREUR(S) DÉTECTÉE(S):\n')
        for i, error in enumerate(all_errors, 1):
            print(f'   {i}. {error}')
        print('\n🔴 Statut: ÉCHEC')
        return 1
    else:
        print('\n✅ TOUS LES TESTS SONT PASSÉS')
        print('🟢 Statut: SUCCÈS')
        return 0

if __name__ == '__main__':
    exit(main())
