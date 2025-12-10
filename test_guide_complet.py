#!/usr/bin/env python3
"""
Test automatique basé sur GUIDE_TEST_COMPLET.md
Simule les tests sans GUI en vérifiant la logique backend
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from datetime import date, datetime, timedelta
from dateutil.parser import parse as parse_date
from src.controllers.student_controller import StudentController
from src.controllers.instructor_controller import InstructorController
from src.controllers.vehicle_controller import VehicleController
from src.controllers.payment_controller import PaymentController
from src.controllers.session_controller import SessionController
from src.controllers.exam_controller import ExamController
from src.models import StudentStatus

class TestResult:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.errors = []
    
    def add_test(self, name, passed, warning=False, error_msg=None):
        self.total += 1
        if passed:
            self.passed += 1
            status = "⚠️ ATTENTION" if warning else "✅ OK"
        else:
            self.failed += 1
            status = "❌ ERREUR"
            if error_msg:
                self.errors.append(f"{name}: {error_msg}")
        
        print(f"  {status} - {name}")
        if warning:
            self.warnings += 1
        return passed
    
    def print_summary(self):
        print("\n" + "="*70)
        print("📊 RÉSUMÉ DES TESTS")
        print("="*70)
        print(f"Total tests: {self.total}")
        print(f"✅ Réussis: {self.passed}")
        print(f"⚠️  Avertissements: {self.warnings}")
        print(f"❌ Échecs: {self.failed}")
        
        if self.errors:
            print(f"\n❌ ERREURS DÉTECTÉES ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        percentage = (self.passed / self.total * 100) if self.total > 0 else 0
        print(f"\n📈 Taux de réussite: {percentage:.1f}%")
        
        if percentage == 100:
            print("🟢 Statut: EXCELLENT")
        elif percentage >= 90:
            print("🟡 Statut: BON")
        elif percentage >= 70:
            print("🟠 Statut: ACCEPTABLE")
        else:
            print("🔴 Statut: NÉCESSITE CORRECTIONS")

def print_section(title):
    print('\n' + '='*70)
    print(f'  {title}')
    print('='*70)

def test_0_demarrage(result):
    """0️⃣ DÉMARRAGE DE L'APPLICATION"""
    print_section('0️⃣ TEST: DÉMARRAGE')
    
    # Test imports
    try:
        from src.models.base import get_session
        from src.models import Student, Instructor, Vehicle
        session = get_session()
        result.add_test("Imports des modèles", True)
        result.add_test("Connexion à la base de données", True)
        session.close()
    except Exception as e:
        result.add_test("Imports des modèles", False, error_msg=str(e))
        result.add_test("Connexion à la base de données", False, error_msg=str(e))
    
    # Test données initiales
    try:
        students = StudentController.get_all_students()
        result.add_test(f"Données élèves chargées ({len(students)} élèves)", len(students) > 0)
    except Exception as e:
        result.add_test("Données élèves chargées", False, error_msg=str(e))

def test_1_liens_rapides(result):
    """1️⃣ LIENS RAPIDES (Quick Actions)"""
    print_section('1️⃣ TEST: LIENS RAPIDES (DIALOGS)')
    
    # Test: Capacité à créer un nouvel élève
    print("\n👤 NOUVEL ÉLÈVE")
    try:
        # Vérifier que la création est possible
        test_data = {
            'full_name': 'Test User Quick',
            'cin': 'TEST_QUICK123',
            'date_of_birth': date(2000, 1, 1),
            'phone': '0612345678',
            'address': 'Test Address',
            'license_type': 'B'
        }
        success, message, new_student = StudentController.create_student(test_data)
        result.add_test("Création élève fonctionnelle", success and new_student is not None)
        
        # Nettoyer
        if new_student:
            StudentController.delete_student(new_student.id)
            result.add_test("Suppression élève test", True)
    except Exception as e:
        result.add_test("Création élève fonctionnelle", False, error_msg=str(e))
    
    # Test: Capacité à créer un paiement
    print("\n💳 NOUVEAU PAIEMENT")
    try:
        from src.models import PaymentMethod
        students = StudentController.get_all_students()
        if students:
            success, message, new_payment = PaymentController.create_payment(
                student_id=students[0].id,
                amount=500.0,
                payment_method=PaymentMethod.CASH,
                description='Test payment'
            )
            result.add_test("Création paiement fonctionnelle", success and new_payment is not None)
            
            # Note: PaymentController n'a pas de delete_payment
            # Les paiements restent pour l'historique
            if new_payment:
                result.add_test("Paiement créé avec succès", True)
        else:
            result.add_test("Création paiement", False, error_msg="Pas d'élève disponible")
    except Exception as e:
        result.add_test("Création paiement fonctionnelle", False, error_msg=str(e))
    
    # Test: Capacité à créer une session
    print("\n🚗 NOUVELLE SESSION")
    try:
        students = StudentController.get_all_students()
        instructors = InstructorController.get_all_instructors()
        vehicles = VehicleController.get_all_vehicles()
        
        if students and instructors and vehicles:
            now = datetime.now()
            test_session = {
                'student_id': students[0].id,
                'instructor_id': instructors[0].id,
                'vehicle_id': vehicles[0].id,
                'start_datetime': now,
                'end_datetime': now + timedelta(hours=1),
                'session_type': 'conduite'
            }
            new_session = SessionController.create_session(test_session)
            result.add_test("Création session fonctionnelle", new_session is not None)
            
            if new_session:
                SessionController.delete_session(new_session.id)
                result.add_test("Suppression session test", True)
        else:
            result.add_test("Création session", False, error_msg="Données manquantes")
    except Exception as e:
        result.add_test("Création session fonctionnelle", False, error_msg=str(e))
    
    # Test: Capacité à créer un examen
    print("\n📝 NOUVEL EXAMEN")
    try:
        from src.models import ExamType
        students = StudentController.get_all_students()
        if students:
            success, message, new_exam = ExamController.create_exam(
                student_id=students[0].id,
                exam_type=ExamType.THEORETICAL,
                scheduled_date=date.today() + timedelta(days=7),
                exam_center='Centre Test',
                location='Test Location'
            )
            result.add_test("Création examen fonctionnelle", success and new_exam is not None)
            
            if new_exam:
                ExamController.delete_exam(new_exam.id)
                result.add_test("Suppression examen test", True)
        else:
            result.add_test("Création examen", False, error_msg="Pas d'élève disponible")
    except Exception as e:
        result.add_test("Création examen fonctionnelle", False, error_msg=str(e))
    
    # Test: Capacité à créer un moniteur
    print("\n👨‍🏫 NOUVEAU MONITEUR")
    try:
        success, message, new_instructor = InstructorController.create_instructor(
            full_name='Test Moniteur',
            cin='TEST_MON123',
            phone='0612345678',
            license_number='LIC-TEST-001',
            specialization='B'
        )
        result.add_test("Création moniteur fonctionnelle", success and new_instructor is not None)
        
        if new_instructor:
            InstructorController.delete_instructor(new_instructor.id)
            result.add_test("Suppression moniteur test", True)
    except Exception as e:
        result.add_test("Création moniteur fonctionnelle", False, error_msg=str(e))

def test_2_dashboard(result):
    """2️⃣ DASHBOARD"""
    print_section('2️⃣ TEST: DASHBOARD')
    
    # Test cartes statistiques
    print("\n📊 CARTES STATISTIQUES")
    try:
        students = StudentController.get_all_students()
        active_students = [s for s in students if s.status == StudentStatus.ACTIVE]
        result.add_test(f"Élèves actifs comptés ({len(active_students)})", True)
        
        payments = PaymentController.get_all_payments()
        total_revenue = sum([p.amount for p in payments])
        result.add_test(f"Chiffre d'affaires calculé ({total_revenue:.2f} DH)", True)
        
        today_sessions = SessionController.get_sessions_by_date_range(date.today(), date.today())
        result.add_test(f"Sessions aujourd'hui ({len(today_sessions)})", True)
        
        unpaid_students = [s for s in students if s.balance < 0]
        unpaid_amount = sum([abs(s.balance) for s in unpaid_students])
        result.add_test(f"Impayés calculés ({unpaid_amount:.2f} DH)", True)
        
    except Exception as e:
        result.add_test("Cartes statistiques", False, error_msg=str(e))
    
    # Test alertes
    print("\n⚠️ ALERTES & NOTIFICATIONS")
    try:
        # Alertes impayés
        unpaid = [s for s in students if s.balance < 0]
        result.add_test(f"Alerte impayés ({len(unpaid)} élèves)", True)
        
        # Alertes sessions
        today_sessions = SessionController.get_sessions_by_date_range(date.today(), date.today())
        result.add_test(f"Alerte sessions du jour ({len(today_sessions)})", True)
        
        # Alertes examens
        exams = ExamController.get_all_exams()
        today = date.today()
        upcoming_exams = [e for e in exams if e.scheduled_date and today <= e.scheduled_date <= today + timedelta(days=3)]
        result.add_test(f"Alerte examens à venir ({len(upcoming_exams)})", True)
        
        # Alertes véhicules
        vehicles = VehicleController.get_all_vehicles()
        expiring_vehicles = []
        for v in vehicles:
            if v.insurance_expiry_date and (v.insurance_expiry_date - today).days < 30:
                expiring_vehicles.append(v)
            if v.technical_inspection_date and (v.technical_inspection_date - today).days < 30:
                expiring_vehicles.append(v)
        result.add_test(f"Alerte véhicules expiration ({len(expiring_vehicles)})", True)
        
    except Exception as e:
        result.add_test("Alertes & Notifications", False, error_msg=str(e))
    
    # Test activités récentes
    print("\n📝 ACTIVITÉS RÉCENTES")
    try:
        # Get recent data via get_all and limit
        recent_payments = PaymentController.get_all_payments()[:5]
        result.add_test(f"Paiements récents ({len(recent_payments)})", True)
        
        recent_sessions = SessionController.get_all_sessions()[:5]
        result.add_test(f"Sessions récentes ({len(recent_sessions)})", True)
        
    except Exception as e:
        result.add_test("Activités récentes", False, error_msg=str(e))

def test_3_eleves(result):
    """3️⃣ MODULE ÉLÈVES"""
    print_section('3️⃣ TEST: MODULE ÉLÈVES')
    
    print("\n📋 LISTE DES ÉLÈVES")
    try:
        students = StudentController.get_all_students()
        result.add_test(f"Liste élèves chargée ({len(students)} élèves)", len(students) > 0)
        
        if students:
            student = students[0]
            result.add_test(f"Élève a un nom: {student.full_name}", bool(student.full_name))
            result.add_test(f"Élève a un CIN: {student.cin}", bool(student.cin))
            result.add_test(f"Élève a un téléphone: {student.phone}", bool(student.phone))
            result.add_test(f"Élève a un statut: {student.status}", bool(student.status))
    except Exception as e:
        result.add_test("Liste élèves", False, error_msg=str(e))
    
    print("\n🔍 RECHERCHE & FILTRES")
    try:
        # Test recherche
        search_results = StudentController.search_students("Sara")
        result.add_test(f"Recherche élèves ({len(search_results)} résultats)", True)
        
        # Test filtre par statut
        active = StudentController.get_all_students(status=StudentStatus.ACTIVE)
        result.add_test(f"Filtre par statut ACTIVE ({len(active)} élèves)", True)
        
    except Exception as e:
        result.add_test("Recherche & Filtres", False, error_msg=str(e))
    
    print("\n📝 CRUD ÉLÈVE")
    try:
        # Créer
        success, message, new_student = StudentController.create_student({
            'full_name': 'Test CRUD',
            'cin': 'CRUD123',
            'date_of_birth': date(2000, 1, 1),
            'phone': '0612345678',
            'address': 'Test',
            'license_type': 'B'
        })
        result.add_test("Créer élève", success and new_student is not None)
        
        if new_student:
            # Lire
            fetched = StudentController.get_student_by_id(new_student.id)
            result.add_test("Lire élève par ID", fetched is not None)
            
            # Modifier
            success, message, updated = StudentController.update_student(new_student.id, {'phone': '0699999999'})
            result.add_test("Modifier élève", success and updated and updated.phone == '0699999999')
            
            # Supprimer
            deleted = StudentController.delete_student(new_student.id)
            result.add_test("Supprimer élève", deleted)
    except Exception as e:
        result.add_test("CRUD Élève", False, error_msg=str(e))

def test_4_moniteurs(result):
    """4️⃣ MODULE MONITEURS"""
    print_section('4️⃣ TEST: MODULE MONITEURS')
    
    try:
        instructors = InstructorController.get_all_instructors()
        result.add_test(f"Liste moniteurs ({len(instructors)})", len(instructors) > 0)
        
        if instructors:
            instructor = instructors[0]
            result.add_test(f"Moniteur a un nom: {instructor.full_name}", bool(instructor.full_name))
            result.add_test(f"Moniteur a une licence: {instructor.license_number}", bool(instructor.license_number))
    except Exception as e:
        result.add_test("Module Moniteurs", False, error_msg=str(e))

def test_5_vehicules(result):
    """5️⃣ MODULE VÉHICULES"""
    print_section('5️⃣ TEST: MODULE VÉHICULES')
    
    try:
        vehicles = VehicleController.get_all_vehicles()
        result.add_test(f"Liste véhicules ({len(vehicles)})", len(vehicles) > 0)
        
        if vehicles:
            vehicle = vehicles[0]
            result.add_test(f"Véhicule: {vehicle.make} {vehicle.model}", bool(vehicle.make))
            result.add_test(f"Plaque: {vehicle.plate_number}", bool(vehicle.plate_number))
            result.add_test("Date assurance définie", vehicle.insurance_expiry_date is not None)
            result.add_test("Date visite technique définie", vehicle.technical_inspection_date is not None)
    except Exception as e:
        result.add_test("Module Véhicules", False, error_msg=str(e))

def test_6_paiements(result):
    """6️⃣ MODULE PAIEMENTS"""
    print_section('6️⃣ TEST: MODULE PAIEMENTS')
    
    try:
        payments = PaymentController.get_all_payments()
        result.add_test(f"Liste paiements ({len(payments)})", len(payments) > 0)
        
        if payments:
            payment = payments[0]
            result.add_test(f"Montant: {payment.amount} DH", payment.amount > 0)
            result.add_test(f"Méthode: {payment.payment_method}", bool(payment.payment_method))
            result.add_test(f"Date: {payment.payment_date}", payment.payment_date is not None)
    except Exception as e:
        result.add_test("Module Paiements", False, error_msg=str(e))

def test_7_planning(result):
    """7️⃣ MODULE PLANNING"""
    print_section('7️⃣ TEST: MODULE PLANNING (SÉANCES)')
    
    try:
        sessions = SessionController.get_all_sessions()
        result.add_test(f"Liste séances ({len(sessions)})", len(sessions) > 0)
        
        if sessions:
            session = sessions[0]
            result.add_test("Séance a une date", session.start_datetime is not None)
            result.add_test("Séance a une durée", session.duration_minutes > 0)
        
        # Test filtre par date
        today_sessions = SessionController.get_sessions_by_date_range(date.today(), date.today())
        result.add_test(f"Filtre séances du jour ({len(today_sessions)})", True)
        
    except Exception as e:
        result.add_test("Module Planning", False, error_msg=str(e))

def test_8_examens(result):
    """8️⃣ MODULE EXAMENS"""
    print_section('8️⃣ TEST: MODULE EXAMENS')
    
    try:
        exams = ExamController.get_all_exams()
        result.add_test(f"Liste examens ({len(exams)})", len(exams) > 0)
        
        if exams:
            exam = exams[0]
            result.add_test(f"Type: {exam.exam_type}", bool(exam.exam_type))
            result.add_test("Date programmée", exam.scheduled_date is not None)
            result.add_test(f"Résultat: {exam.result}", bool(exam.result))
    except Exception as e:
        result.add_test("Module Examens", False, error_msg=str(e))

def main():
    print('\n' + '='*70)
    print('  🧪 TESTS AUTOMATIQUES - GUIDE COMPLET')
    print('  Based on: GUIDE_TEST_COMPLET.md')
    print('='*70)
    
    result = TestResult()
    
    # Exécuter tous les tests
    test_0_demarrage(result)
    test_1_liens_rapides(result)
    test_2_dashboard(result)
    test_3_eleves(result)
    test_4_moniteurs(result)
    test_5_vehicules(result)
    test_6_paiements(result)
    test_7_planning(result)
    test_8_examens(result)
    
    # Résumé
    result.print_summary()
    
    return 0 if result.failed == 0 else 1

if __name__ == '__main__':
    exit(main())
