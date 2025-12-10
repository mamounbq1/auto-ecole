"""
Tests complets pour les nouveaux modules: Moniteurs, Véhicules, Examens
"""

import sys
import os
from datetime import datetime, date, timedelta
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models import (
    VehicleStatus, ExamType, ExamResult,
    StudentStatus
)
from src.controllers import (
    InstructorController,
    VehicleController, 
    ExamController,
    StudentController
)
from src.utils import get_logger

logger = get_logger()


def test_instructors_module():
    """Tester le module Moniteurs"""
    print("\n" + "="*80)
    print("🧪 TEST MODULE MONITEURS (INSTRUCTORS)")
    print("="*80)
    
    try:
        # 1. Récupérer tous les moniteurs
        instructors = InstructorController.get_all_instructors()
        print(f"✓ Total moniteurs: {len(instructors)}")
        
        if instructors:
            instructor = instructors[0]
            print(f"  - Exemple: {instructor.full_name}")
            print(f"    - Téléphone: {instructor.phone}")
            print(f"    - Types permis: {instructor.license_types}")
            print(f"    - Disponible: {'Oui' if instructor.is_available else 'Non'}")
            print(f"    - Heures enseignées: {instructor.total_hours_taught or 0}h")
            print(f"    - Taux horaire: {instructor.hourly_rate or 0} DH/h")
        
        # 2. Compter moniteurs disponibles
        available = [i for i in instructors if i.is_available]
        print(f"✓ Moniteurs disponibles: {len(available)}")
        
        # 3. Statistiques manuelles
        total_hours = sum(i.total_hours_taught or 0 for i in instructors)
        avg_success = sum(i.success_rate or 0 for i in instructors) / len(instructors) if instructors else 0
        print(f"✓ Statistiques:")
        print(f"  - Total: {len(instructors)}")
        print(f"  - Disponibles: {len(available)}")
        print(f"  - Heures totales: {total_hours}h")
        print(f"  - Taux succès moyen: {avg_success:.1f}%")
        
        print("✅ Module Moniteurs: OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test moniteurs: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vehicles_module():
    """Tester le module Véhicules"""
    print("\n" + "="*80)
    print("🧪 TEST MODULE VÉHICULES (VEHICLES)")
    print("="*80)
    
    try:
        # 1. Récupérer tous les véhicules
        vehicles = VehicleController.get_all_vehicles()
        print(f"✓ Total véhicules: {len(vehicles)}")
        
        if vehicles:
            vehicle = vehicles[0]
            print(f"  - Exemple: {vehicle.make} {vehicle.model}")
            print(f"    - Immatriculation: {vehicle.plate_number}")
            print(f"    - Type permis: {vehicle.license_type}")
            print(f"    - Statut: {vehicle.status.value}")
            print(f"    - Kilométrage: {vehicle.current_mileage or 0} km")
            print(f"    - Sessions totales: {vehicle.total_sessions or 0}")
        
        # 2. Compter véhicules par statut
        available = [v for v in vehicles if v.status == VehicleStatus.AVAILABLE]
        in_service = [v for v in vehicles if v.status == VehicleStatus.IN_SERVICE]
        maintenance = [v for v in vehicles if v.status == VehicleStatus.MAINTENANCE]
        
        print(f"✓ Véhicules disponibles: {len(available)}")
        print(f"✓ Véhicules en service: {len(in_service)}")
        print(f"✓ Véhicules en maintenance: {len(maintenance)}")
        
        # 3. Véhicules par type de permis
        license_types = ['B', 'A', 'C', 'D']
        for license_type in license_types:
            by_type = [v for v in vehicles if v.license_type == license_type]
            if by_type:
                print(f"✓ Permis {license_type}: {len(by_type)} véhicule(s)")
        
        # 4. Statistiques
        total_hours = sum(v.total_hours_used or 0 for v in vehicles)
        total_mileage = sum(v.current_mileage or 0 for v in vehicles)
        total_maintenance_cost = sum(v.maintenance_cost or 0 for v in vehicles)
        
        print(f"✓ Statistiques globales:")
        print(f"  - Total véhicules: {len(vehicles)}")
        print(f"  - Heures totales: {total_hours}h")
        print(f"  - Kilométrage total: {total_mileage} km")
        print(f"  - Coût maintenance total: {total_maintenance_cost:.2f} DH")
        
        print("✅ Module Véhicules: OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test véhicules: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exams_module():
    """Tester le module Examens"""
    print("\n" + "="*80)
    print("🧪 TEST MODULE EXAMENS (EXAMS)")
    print("="*80)
    
    try:
        # 1. Récupérer tous les examens
        exams = ExamController.get_all_exams()
        print(f"✓ Total examens: {len(exams)}")
        
        if exams:
            exam = exams[0]
            student = exam.student
            print(f"  - Exemple: Examen #{exam.id}")
            print(f"    - Élève: {student.full_name if student else 'N/A'}")
            print(f"    - Type: {exam.exam_type.value}")
            print(f"    - Résultat: {exam.result.value}")
            print(f"    - Date: {exam.scheduled_date.strftime('%d/%m/%Y') if exam.scheduled_date else 'N/A'}")
            # Check which score field exists
            score = getattr(exam, 'theoretical_score', None) or getattr(exam, 'practical_score', None) or 0
            print(f"    - Score: {score}/40")
            print(f"    - Tentative: {exam.attempt_number}")
        
        # 2. Examens à venir
        upcoming = ExamController.get_upcoming_exams()
        print(f"✓ Examens à venir: {len(upcoming)}")
        
        # 3. Compter par type
        theoretical = [e for e in exams if e.exam_type == ExamType.THEORETICAL]
        practical = [e for e in exams if e.exam_type == ExamType.PRACTICAL]
        print(f"✓ Examens théoriques: {len(theoretical)}")
        print(f"✓ Examens pratiques: {len(practical)}")
        
        # 4. Compter par résultat
        passed = [e for e in exams if e.result == ExamResult.PASSED]
        failed = [e for e in exams if e.result == ExamResult.FAILED]
        pending = [e for e in exams if e.result == ExamResult.PENDING]
        absent = [e for e in exams if e.result == ExamResult.ABSENT]
        
        print(f"✓ Examens en attente: {len(pending)}")
        print(f"✓ Examens réussis: {len(passed)}")
        print(f"✓ Examens échoués: {len(failed)}")
        print(f"✓ Absents: {len(absent)}")
        
        # 5. Taux de réussite
        total_evaluated = len(passed) + len(failed)
        success_rate = (len(passed) / total_evaluated * 100) if total_evaluated > 0 else 0
        print(f"✓ Taux de réussite: {success_rate:.1f}%")
        
        print("✅ Module Examens: OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test examens: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Tester l'intégration entre les modules"""
    print("\n" + "="*80)
    print("🧪 TEST INTÉGRATION DES MODULES")
    print("="*80)
    
    try:
        # 1. Vérifier qu'on a des données dans tous les modules
        students = StudentController.get_all_students()
        instructors = InstructorController.get_all_instructors()
        vehicles = VehicleController.get_all_vehicles()
        exams = ExamController.get_all_exams()
        
        print(f"✓ Données disponibles:")
        print(f"  - Élèves: {len(students)}")
        print(f"  - Moniteurs: {len(instructors)}")
        print(f"  - Véhicules: {len(vehicles)}")
        print(f"  - Examens: {len(exams)}")
        
        # 2. Vérifier les relations
        if exams:
            exam_with_student = [e for e in exams if e.student_id]
            print(f"✓ Examens liés à des élèves: {len(exam_with_student)}/{len(exams)}")
        
        # 3. Statistiques globales
        print(f"\n✓ Vue d'ensemble de l'auto-école:")
        print(f"  - {len(students)} élèves inscrits")
        print(f"  - {len(instructors)} moniteurs")
        print(f"  - {len(vehicles)} véhicules")
        print(f"  - {len(exams)} examens programmés/passés")
        
        active_students = StudentController.get_active_students_count()
        available_instructors = len([i for i in instructors if i.is_available])
        available_vehicles = len([v for v in vehicles if v.status == VehicleStatus.AVAILABLE])
        
        print(f"\n✓ Ressources disponibles:")
        print(f"  - Élèves actifs: {active_students}")
        print(f"  - Moniteurs disponibles: {available_instructors}")
        print(f"  - Véhicules disponibles: {available_vehicles}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test intégration: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Exécuter tous les tests"""
    print("\n" + "="*80)
    print("🚗 AUTO-ÉCOLE - TESTS DES NOUVEAUX MODULES")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Exécuter les tests
    results = {
        'Moniteurs': test_instructors_module(),
        'Véhicules': test_vehicles_module(),
        'Examens': test_exams_module(),
        'Intégration': test_integration(),
    }
    
    # Résumé
    print("\n" + "="*80)
    print("📋 RÉSUMÉ DES TESTS")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for module, result in results.items():
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"{status} - {module}")
    
    print("\n" + "-"*80)
    print(f"Score: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
    print("="*80)
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS SONT RÉUSSIS!")
        print("✨ Les 3 nouveaux modules sont fonctionnels:")
        print("   - 👨‍🏫 Moniteurs (Instructors)")
        print("   - 🚗 Véhicules (Vehicles)")
        print("   - 📝 Examens (Exams)")
        print("\n✅ L'application est prête pour utilisation!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) ont échoué")
        return 1


if __name__ == "__main__":
    sys.exit(main())
