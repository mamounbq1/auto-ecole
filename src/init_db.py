#!/usr/bin/env python3
"""
Script d'initialisation de la base de données
Crée les tables et insère des données de démonstration
"""

import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import (
    init_db, get_session,
    User, UserRole,
    Student, StudentStatus,
    Instructor,
    Vehicle, VehicleStatus,
    Session, SessionType, SessionStatus,
    Payment, PaymentMethod,
    Exam, ExamType, ExamResult
)
from src.utils.license_manager import get_license_manager


def create_sample_users(session):
    """Créer des utilisateurs de démonstration"""
    print("Création des utilisateurs...")
    
    users = [
        User(
            username="admin",
            password="Admin123!",
            full_name="Administrateur Principal",
            email="admin@autoecole.ma",
            phone="+212 600-000001",
            role=UserRole.ADMIN
        ),
        User(
            username="caissier",
            password="Caisse123!",
            full_name="Mohamed Alami",
            email="caissier@autoecole.ma",
            phone="+212 600-000002",
            role=UserRole.CASHIER
        ),
        User(
            username="moniteur1",
            password="Moniteur123!",
            full_name="Ahmed Bennis",
            email="ahmed@autoecole.ma",
            phone="+212 600-000003",
            role=UserRole.INSTRUCTOR
        ),
        User(
            username="receptionniste",
            password="Reception123!",
            full_name="Fatima Zahra",
            email="reception@autoecole.ma",
            phone="+212 600-000004",
            role=UserRole.RECEPTIONIST
        ),
    ]
    
    for user in users:
        session.add(user)
    
    session.commit()
    print(f"✓ {len(users)} utilisateurs créés")
    return users


def create_sample_instructors(session):
    """Créer des moniteurs de démonstration"""
    print("Création des moniteurs...")
    
    instructors = [
        Instructor(
            full_name="Ahmed Bennis",
            cin="AA123456",
            phone="+212 600-111001",
            license_number="MON-2020-001",
            license_types="B,C",
            email="ahmed.bennis@autoecole.ma",
            hourly_rate=100,
            monthly_salary=5000,
            date_of_birth=date(1985, 5, 15),
            hire_date=date(2020, 1, 10)
        ),
        Instructor(
            full_name="Youssef Idrissi",
            cin="BB234567",
            phone="+212 600-111002",
            license_number="MON-2019-015",
            license_types="A,B",
            email="youssef@autoecole.ma",
            hourly_rate=120,
            monthly_salary=5500,
            date_of_birth=date(1982, 8, 22),
            hire_date=date(2019, 3, 1)
        ),
        Instructor(
            full_name="Karim Tazi",
            cin="CC345678",
            phone="+212 600-111003",
            license_number="MON-2021-008",
            license_types="B",
            email="karim@autoecole.ma",
            hourly_rate=90,
            monthly_salary=4500,
            date_of_birth=date(1990, 2, 10),
            hire_date=date(2021, 6, 15)
        ),
    ]
    
    for instructor in instructors:
        session.add(instructor)
    
    session.commit()
    print(f"✓ {len(instructors)} moniteurs créés")
    return instructors


def create_sample_vehicles(session):
    """Créer des véhicules de démonstration"""
    print("Création des véhicules...")
    
    vehicles = [
        Vehicle(
            plate_number="12345-A-67",
            make="Dacia",
            model="Logan",
            year=2022,
            color="Blanc",
            license_type="B",
            fuel_type="Diesel",
            transmission="Manuelle",
            purchase_date=date(2022, 1, 15),
            current_mileage=25000,
            insurance_expiry_date=date.today() + timedelta(days=180),
            technical_inspection_date=date.today() + timedelta(days=120)
        ),
        Vehicle(
            plate_number="23456-B-89",
            make="Renault",
            model="Clio",
            year=2021,
            color="Gris",
            license_type="B",
            fuel_type="Essence",
            transmission="Manuelle",
            purchase_date=date(2021, 6, 10),
            current_mileage=45000,
            insurance_expiry_date=date.today() + timedelta(days=150),
            technical_inspection_date=date.today() + timedelta(days=90)
        ),
        Vehicle(
            plate_number="34567-C-12",
            make="Peugeot",
            model="208",
            year=2023,
            color="Rouge",
            license_type="B",
            fuel_type="Essence",
            transmission="Automatique",
            purchase_date=date(2023, 2, 1),
            current_mileage=8000,
            insurance_expiry_date=date.today() + timedelta(days=300),
            technical_inspection_date=date.today() + timedelta(days=365)
        ),
    ]
    
    for vehicle in vehicles:
        session.add(vehicle)
    
    session.commit()
    print(f"✓ {len(vehicles)} véhicules créés")
    return vehicles


def create_sample_students(session):
    """Créer des élèves de démonstration"""
    print("Création des élèves...")
    
    students = [
        Student(
            full_name="Sara Bennani",
            cin="EE123456",
            date_of_birth=date(2002, 3, 15),
            phone="+212 600-222001",
            email="sara.bennani@email.com",
            address="Casablanca, Maarif",
            registration_date=date(2024, 9, 1),
            license_type="B",
            status=StudentStatus.ACTIVE,
            hours_planned=20,
            hours_completed=12,
            total_due=5000,
            total_paid=3500,
            emergency_contact_name="Mme Bennani",
            emergency_contact_phone="+212 600-222000"
        ),
        Student(
            full_name="Omar El Fassi",
            cin="FF234567",
            date_of_birth=date(2001, 7, 22),
            phone="+212 600-222002",
            email="omar.fassi@email.com",
            address="Rabat, Agdal",
            registration_date=date(2024, 10, 5),
            license_type="B",
            status=StudentStatus.ACTIVE,
            hours_planned=20,
            hours_completed=8,
            total_due=5000,
            total_paid=5000,
            emergency_contact_name="M. El Fassi",
            emergency_contact_phone="+212 600-222010"
        ),
        Student(
            full_name="Leila Amrani",
            cin="GG345678",
            date_of_birth=date(2003, 11, 5),
            phone="+212 600-222003",
            email="leila.amrani@email.com",
            address="Marrakech, Gueliz",
            registration_date=date(2024, 8, 15),
            license_type="B",
            status=StudentStatus.ACTIVE,
            hours_planned=20,
            hours_completed=18,
            total_due=5500,
            total_paid=5500,
            theoretical_exam_passed=1,
            theoretical_exam_attempts=1
        ),
        Student(
            full_name="Mehdi Ziani",
            cin="HH456789",
            date_of_birth=date(2000, 4, 18),
            phone="+212 600-222004",
            email="mehdi.ziani@email.com",
            address="Fès, Centre Ville",
            registration_date=date(2024, 7, 1),
            license_type="B",
            status=StudentStatus.GRADUATED,
            hours_planned=20,
            hours_completed=22,
            total_due=6000,
            total_paid=6000,
            theoretical_exam_passed=1,
            theoretical_exam_attempts=2,
            practical_exam_passed=1,
            practical_exam_attempts=1
        ),
        Student(
            full_name="Yasmine Taoufik",
            cin="II567890",
            date_of_birth=date(2002, 9, 30),
            phone="+212 600-222005",
            email="yasmine.t@email.com",
            address="Tanger, Malabata",
            registration_date=date(2024, 11, 1),
            license_type="B",
            status=StudentStatus.PENDING,
            hours_planned=20,
            hours_completed=0,
            total_due=5000,
            total_paid=1000
        ),
    ]
    
    for student in students:
        # Mettre à jour le solde
        from decimal import Decimal
        paid = Decimal(str(float(student.total_paid) if student.total_paid else 0.0))
        due = Decimal(str(float(student.total_due) if student.total_due else 0.0))
        student.balance = paid - due
        session.add(student)
    
    session.commit()
    print(f"✓ {len(students)} élèves créés")
    return students


def create_sample_payments(session, students):
    """Créer des paiements de démonstration"""
    print("Création des paiements...")
    
    payments = [
        # Paiements pour Sara Bennani
        Payment(
            student_id=students[0].id,
            amount=2000,
            payment_method=PaymentMethod.CASH,
            payment_date=date(2024, 9, 1),
            description="Inscription + 1er versement",
            category="inscription",
            validated_by="Mohamed Alami"
        ),
        Payment(
            student_id=students[0].id,
            amount=1500,
            payment_method=PaymentMethod.CARD,
            payment_date=date(2024, 10, 15),
            description="2ème versement",
            category="conduite",
            validated_by="Mohamed Alami"
        ),
        # Paiements pour Omar El Fassi
        Payment(
            student_id=students[1].id,
            amount=5000,
            payment_method=PaymentMethod.CHECK,
            payment_date=date(2024, 10, 5),
            description="Paiement intégral",
            category="inscription",
            reference_number="CHQ-123456",
            validated_by="Mohamed Alami"
        ),
        # Paiements pour Leila Amrani
        Payment(
            student_id=students[2].id,
            amount=2500,
            payment_method=PaymentMethod.CASH,
            payment_date=date(2024, 8, 15),
            description="1er versement",
            category="inscription",
            validated_by="Mohamed Alami"
        ),
        Payment(
            student_id=students[2].id,
            amount=3000,
            payment_method=PaymentMethod.TRANSFER,
            payment_date=date(2024, 9, 20),
            description="Solde",
            category="conduite",
            reference_number="VIR-789012",
            validated_by="Mohamed Alami"
        ),
    ]
    
    for payment in payments:
        payment.receipt_number = payment.generate_receipt_number()
        session.add(payment)
    
    session.commit()
    print(f"✓ {len(payments)} paiements créés")
    return payments


def create_sample_sessions(session, students, instructors, vehicles):
    """Créer des sessions de démonstration"""
    print("Création des sessions...")
    
    today = datetime.now()
    sessions_data = []
    
    # Sessions pour Sara Bennani (12 heures complétées)
    for i in range(12):
        start_date = today - timedelta(days=30-i*2, hours=10)
        sessions_data.append({
            'student_id': students[0].id,
            'instructor_id': instructors[0].id,
            'vehicle_id': vehicles[0].id,
            'start_datetime': start_date,
            'duration_minutes': 60,
            'session_type': SessionType.PRACTICAL_DRIVING,
            'status': SessionStatus.COMPLETED,
            'performance_score': 7 + (i % 3),
            'price': 200,
            'is_paid': 1
        })
    
    # Sessions futures pour Sara
    for i in range(3):
        start_date = today + timedelta(days=i+1, hours=14)
        sessions_data.append({
            'student_id': students[0].id,
            'instructor_id': instructors[0].id,
            'vehicle_id': vehicles[0].id,
            'start_datetime': start_date,
            'duration_minutes': 60,
            'session_type': SessionType.PRACTICAL_DRIVING,
            'status': SessionStatus.SCHEDULED,
            'price': 200,
            'is_paid': 0
        })
    
    # Sessions pour Omar El Fassi (8 heures)
    for i in range(8):
        start_date = today - timedelta(days=20-i*2, hours=9)
        sessions_data.append({
            'student_id': students[1].id,
            'instructor_id': instructors[1].id,
            'vehicle_id': vehicles[1].id,
            'start_datetime': start_date,
            'duration_minutes': 60,
            'session_type': SessionType.PRACTICAL_DRIVING,
            'status': SessionStatus.COMPLETED,
            'performance_score': 8 + (i % 2),
            'price': 200,
            'is_paid': 1
        })
    
    # Sessions pour Leila Amrani (18 heures + futures)
    for i in range(18):
        start_date = today - timedelta(days=60-i*3, hours=11)
        sessions_data.append({
            'student_id': students[2].id,
            'instructor_id': instructors[2].id,
            'vehicle_id': vehicles[2].id,
            'start_datetime': start_date,
            'duration_minutes': 60,
            'session_type': SessionType.PRACTICAL_DRIVING,
            'status': SessionStatus.COMPLETED,
            'performance_score': 8 + (i % 3),
            'price': 200,
            'is_paid': 1
        })
    
    # Créer les sessions
    sessions = []
    for data in sessions_data:
        session_obj = Session(**data)
        sessions.append(session_obj)
        session.add(session_obj)
    
    session.commit()
    print(f"✓ {len(sessions)} sessions créées")
    return sessions


def create_sample_exams(session, students):
    """Créer des examens de démonstration"""
    print("Création des examens...")
    
    exams = [
        # Examen théorique réussi pour Leila
        Exam(
            student_id=students[2].id,
            exam_type=ExamType.THEORETICAL,
            scheduled_date=date(2024, 9, 15),
            completion_date=date(2024, 9, 15),
            result=ExamResult.PASSED,
            theory_score=37,
            theory_max_score=40,
            location="Centre d'examen Casablanca",
            attempt_number=1,
            is_official=True,
            is_paid=True,
            registration_fee=300
        ),
        # Examen théorique échoué puis réussi pour Mehdi
        Exam(
            student_id=students[3].id,
            exam_type=ExamType.THEORETICAL,
            scheduled_date=date(2024, 8, 1),
            completion_date=date(2024, 8, 1),
            result=ExamResult.FAILED,
            theory_score=32,
            theory_max_score=40,
            location="Centre d'examen Fès",
            attempt_number=1,
            is_official=True,
            is_paid=True,
            registration_fee=300
        ),
        Exam(
            student_id=students[3].id,
            exam_type=ExamType.THEORETICAL,
            scheduled_date=date(2024, 9, 5),
            completion_date=date(2024, 9, 5),
            result=ExamResult.PASSED,
            theory_score=38,
            theory_max_score=40,
            location="Centre d'examen Fès",
            attempt_number=2,
            is_official=True,
            is_paid=True,
            registration_fee=300
        ),
        # Examen pratique réussi pour Mehdi
        Exam(
            student_id=students[3].id,
            exam_type=ExamType.PRACTICAL,
            scheduled_date=date(2024, 10, 10),
            completion_date=date(2024, 10, 10),
            result=ExamResult.PASSED,
            practical_score=85,
            location="Circuit d'examen Fès",
            examiner_name="Inspecteur Alaoui",
            vehicle_plate="12345-A-67",
            attempt_number=1,
            is_official=True,
            is_paid=True,
            registration_fee=500
        ),
        # Examen pratique à venir pour Leila
        Exam(
            student_id=students[2].id,
            exam_type=ExamType.PRACTICAL,
            scheduled_date=date.today() + timedelta(days=15),
            result=ExamResult.PENDING,
            location="Circuit d'examen Marrakech",
            attempt_number=1,
            is_official=True,
            is_paid=True,
            registration_fee=500
        ),
    ]
    
    for exam in exams:
        exam.summons_number = exam.generate_summons_number()
        exam.summons_generated = True
        session.add(exam)
    
    session.commit()
    print(f"✓ {len(exams)} examens créés")
    return exams


def main():
    """Fonction principale d'initialisation"""
    print("=" * 60)
    print("🚗 Initialisation de la base de données Auto-École")
    print("=" * 60)
    
    # === VÉRIFICATION DE LA LICENCE ===
    print("\n🔐 Vérification de la licence...")
    license_manager = get_license_manager()
    
    if not license_manager.is_licensed():
        print("\n❌ ERREUR : Aucune licence valide détectée!")
        print()
        print("⚠️  Pour initialiser la base de données, vous devez d'abord:")
        print("   1. Lancer l'application graphique (python src/main_gui.py)")
        print("   2. Activer une licence valide")
        print("   3. Ensuite relancer ce script d'initialisation")
        print()
        print("📧 Pour obtenir une licence, contactez le support technique")
        print()
        return
    
    license_info = license_manager.get_license_info()
    print(f"✅ Licence valide pour: {license_info.get('company')}")
    print(f"   ({license_info.get('days_remaining')} jours restants)")
    
    # Créer le dossier data s'il n'existe pas
    os.makedirs("data", exist_ok=True)
    
    # Initialiser la base de données
    database_path = "data/autoecole.db"
    
    # Demander confirmation si la base existe déjà
    if os.path.exists(database_path):
        print(f"\n⚠️  La base de données existe déjà : {database_path}")
        response = input("Voulez-vous la supprimer et recommencer ? (oui/non) : ")
        if response.lower() not in ['oui', 'o', 'yes', 'y']:
            print("❌ Opération annulée")
            return
        os.remove(database_path)
        print("✓ Base de données supprimée")
    
    # Créer les tables
    print(f"\nCréation des tables dans : {database_path}")
    init_db(database_path)
    
    # Obtenir une session
    db_session = get_session()
    
    try:
        # Créer les données de démonstration
        print("\n" + "=" * 60)
        print("Création des données de démonstration")
        print("=" * 60)
        
        users = create_sample_users(db_session)
        instructors = create_sample_instructors(db_session)
        vehicles = create_sample_vehicles(db_session)
        students = create_sample_students(db_session)
        payments = create_sample_payments(db_session, students)
        sessions = create_sample_sessions(db_session, students, instructors, vehicles)
        exams = create_sample_exams(db_session, students)
        
        print("\n" + "=" * 60)
        print("✅ Initialisation terminée avec succès !")
        print("=" * 60)
        
        # Afficher les informations de connexion
        print("\n📋 Comptes créés :")
        print("-" * 60)
        print("Admin       : admin / Admin123!")
        print("Caissier    : caissier / Caisse123!")
        print("Moniteur    : moniteur1 / Moniteur123!")
        print("Réception   : receptionniste / Reception123!")
        print("-" * 60)
        
        print("\n📊 Statistiques :")
        print(f"  • {len(users)} utilisateurs")
        print(f"  • {len(instructors)} moniteurs")
        print(f"  • {len(vehicles)} véhicules")
        print(f"  • {len(students)} élèves")
        print(f"  • {len(payments)} paiements")
        print(f"  • {len(sessions)} sessions")
        print(f"  • {len(exams)} examens")
        
        print("\n🎉 Vous pouvez maintenant lancer l'application :")
        print("   python src/main.py")
        print()
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'initialisation : {e}")
        db_session.rollback()
        raise
    finally:
        db_session.close()


if __name__ == "__main__":
    main()
