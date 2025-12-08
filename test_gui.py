"""
Test de l'interface graphique complète avec tous les widgets
"""

import sys
import os
from datetime import datetime

# Ajouter le répertoire src au PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMessageBox
from src.views.login_window import LoginWindow
from src.utils import get_logger, get_pdf_generator, get_notification_manager
from src.controllers import (
    StudentController, PaymentController, SessionController,
    InstructorController, VehicleController, ExamController
)

logger = get_logger()


def test_dashboard():
    """Tester le dashboard avancé"""
    print("\n=== Test Dashboard Avancé ===")
    
    try:
        # Statistiques élèves
        active = StudentController.get_active_students_count()
        print(f"✓ Élèves actifs: {active}")
        
        # CA mensuel
        now = datetime.now()
        revenue = PaymentController.get_monthly_revenue(now.year, now.month)
        print(f"✓ CA du mois: {revenue:,.2f} DH")
        
        # Sessions aujourd'hui
        sessions = SessionController.get_today_sessions()
        print(f"✓ Sessions aujourd'hui: {len(sessions)}")
        
        print("✅ Dashboard: OK")
        return True
    except Exception as e:
        print(f"❌ Dashboard: ERREUR - {e}")
        return False


def test_pdf_generation():
    """Tester la génération de PDFs professionnels"""
    print("\n=== Test Génération PDF ===")
    
    try:
        pdf_gen = get_pdf_generator()
        
        # Test reçu
        receipt_data = {
            'receipt_number': 'REC-TEST-001',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'student_name': 'Test Student',
            'student_cin': 'AB123456',
            'student_phone': '+212 600-123456',
            'amount': 1000.0,
            'payment_method': 'Espèces',
            'description': 'Test paiement',
            'validated_by': 'Admin'
        }
        
        success, result = pdf_gen.generate_receipt(receipt_data)
        if success:
            print(f"✓ Reçu PDF généré: {result}")
        else:
            print(f"✗ Erreur reçu: {result}")
            return False
        
        # Test contrat
        student_data = {
            'full_name': 'Test Student',
            'cin': 'AB123456',
            'date_of_birth': '01/01/1990',
            'phone': '+212 600-123456',
            'address': 'Test Address',
            'license_type': 'B',
            'hours_planned': 20,
            'total_due': 5000
        }
        
        success, result = pdf_gen.generate_contract(student_data)
        if success:
            print(f"✓ Contrat PDF généré: {result}")
        else:
            print(f"✗ Erreur contrat: {result}")
            return False
        
        print("✅ Génération PDF: OK")
        return True
    except Exception as e:
        print(f"❌ Génération PDF: ERREUR - {e}")
        return False


def test_notifications():
    """Tester le système de notifications"""
    print("\n=== Test Notifications ===")
    
    try:
        notif = get_notification_manager()
        
        # Vérifier la configuration
        if notif.config["email"]["enabled"]:
            print("✓ Email configuré")
        else:
            print("ℹ Email non configuré (optionnel)")
        
        if notif.config["sms"]["enabled"]:
            print("✓ SMS configuré")
        else:
            print("ℹ SMS non configuré (optionnel)")
        
        print("✅ Notifications: OK")
        return True
    except Exception as e:
        print(f"❌ Notifications: ERREUR - {e}")
        return False


def test_data_availability():
    """Tester la disponibilité des données"""
    print("\n=== Test Disponibilité des Données ===")
    
    try:
        students = StudentController.get_all_students()
        print(f"✓ Élèves: {len(students)}")
        
        instructors = InstructorController.get_all_instructors()
        print(f"✓ Moniteurs: {len(instructors)}")
        
        vehicles = VehicleController.get_all_vehicles()
        print(f"✓ Véhicules: {len(vehicles)}")
        
        sessions = SessionController.get_all_sessions()
        print(f"✓ Sessions: {len(sessions)}")
        
        payments = PaymentController.get_all_payments()
        print(f"✓ Paiements: {len(payments)}")
        
        exams = ExamController.get_all_exams()
        print(f"✓ Examens: {len(exams)}")
        
        print("✅ Données: OK")
        return True
    except Exception as e:
        print(f"❌ Données: ERREUR - {e}")
        return False


def main():
    """Test complet de l'application GUI"""
    print("=" * 60)
    print("TEST COMPLET - Application Auto-École GUI")
    print("=" * 60)
    
    # Tests sans GUI
    results = []
    
    results.append(("Disponibilité des données", test_data_availability()))
    results.append(("Dashboard avancé", test_dashboard()))
    results.append(("Génération PDF", test_pdf_generation()))
    results.append(("Notifications", test_notifications()))
    
    # Résultats
    print("\n" + "=" * 60)
    print("RÉSULTATS DES TESTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    
    print(f"\nScore: {passed}/{total} ({passed/total*100:.1f}%)")
    
    # Lancer l'application GUI
    print("\n" + "=" * 60)
    print("LANCEMENT DE L'APPLICATION GUI")
    print("=" * 60)
    print("\nOuverture de la fenêtre de connexion...")
    print("Identifiants de test:")
    print("  - Administrateur: admin / Admin123!")
    print("  - Caissier: caissier / Caisse123!")
    print("  - Moniteur: moniteur1 / Moniteur123!")
    print("  - Réceptionniste: receptionniste / Reception123!")
    print("\n")
    
    try:
        app = QApplication(sys.argv)
        
        # Style global
        app.setStyle('Fusion')
        
        # Fenêtre de login
        login_window = LoginWindow()
        login_window.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ Erreur lors du lancement de l'application: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
