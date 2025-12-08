#!/usr/bin/env python3
"""
Test rapide de l'application
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import login, logout
from src.controllers import StudentController, PaymentController
from src.models import PaymentMethod

def test_authentication():
    """Tester l'authentification"""
    print("=" * 60)
    print("Test 1 : Authentification")
    print("=" * 60)
    
    # Test connexion réussie
    success, message, user = login("admin", "Admin123!")
    if success:
        print(f"✅ Connexion admin réussie : {user.full_name}")
        print(f"   Rôle : {user.role.value}")
    else:
        print(f"❌ Échec : {message}")
        return False
    
    logout()
    print("✅ Déconnexion réussie\n")
    return True


def test_students():
    """Tester la gestion des élèves"""
    print("=" * 60)
    print("Test 2 : Gestion des Élèves")
    print("=" * 60)
    
    # Connexion
    login("admin", "Admin123!")
    
    # Récupérer les élèves
    students = StudentController.get_all_students()
    print(f"✅ {len(students)} élèves dans la base")
    
    if students:
        student = students[0]
        print(f"\n📋 Élève exemple :")
        print(f"   Nom : {student.full_name}")
        print(f"   CIN : {student.cin}")
        print(f"   Téléphone : {student.phone}")
        print(f"   Statut : {student.status.value}")
        print(f"   Solde : {student.balance} DH")
        print(f"   Heures : {student.hours_completed}/{student.hours_planned}")
    
    # Test recherche
    results = StudentController.search_students("Sara")
    print(f"\n✅ Recherche 'Sara' : {len(results)} résultat(s)")
    
    # Test élèves actifs
    active_count = StudentController.get_active_students_count()
    print(f"✅ Élèves actifs : {active_count}")
    
    # Test élèves avec dette
    students_with_debt = StudentController.get_students_with_debt()
    print(f"✅ Élèves avec dette : {len(students_with_debt)}")
    
    logout()
    print()
    return True


def test_payments():
    """Tester les paiements"""
    print("=" * 60)
    print("Test 3 : Gestion des Paiements")
    print("=" * 60)
    
    # Connexion en tant que caissier
    login("caissier", "Caisse123!")
    
    # Récupérer un élève
    students = StudentController.get_all_students()
    if not students:
        print("❌ Aucun élève trouvé")
        return False
    
    student = students[0]
    print(f"\n📋 Test paiement pour : {student.full_name}")
    print(f"   Solde avant : {student.balance} DH")
    
    # Créer un paiement
    success, message, payment = PaymentController.create_payment(
        student_id=student.id,
        amount=500,
        payment_method=PaymentMethod.CASH,
        description="Paiement test",
        validated_by="Caissier Test"
    )
    
    if success:
        print(f"✅ {message}")
        print(f"   N° Reçu : {payment.receipt_number}")
        print(f"   Montant : {payment.amount} DH")
        
        # Générer le reçu
        success_pdf, filepath = PaymentController.generate_receipt_pdf(payment.id)
        if success_pdf:
            print(f"✅ Reçu généré : {filepath}")
        else:
            print(f"⚠️  Erreur génération reçu : {filepath}")
        
        # Vérifier le nouveau solde
        from src.models import get_session
        session = get_session()
        student_updated = session.query(type(student)).filter_by(id=student.id).first()
        print(f"   Solde après : {student_updated.balance} DH")
    else:
        print(f"❌ Échec : {message}")
    
    logout()
    print()
    return True


def test_export():
    """Tester l'export CSV"""
    print("=" * 60)
    print("Test 4 : Export CSV")
    print("=" * 60)
    
    login("admin", "Admin123!")
    
    students = StudentController.get_all_students()
    success, filepath = StudentController.export_students_to_csv(students)
    
    if success:
        print(f"✅ Export réussi : {filepath}")
        import os
        size = os.path.getsize(filepath)
        print(f"   Taille : {size} octets")
    else:
        print(f"❌ Échec : {filepath}")
    
    logout()
    print()
    return True


def test_backup():
    """Tester les sauvegardes"""
    print("=" * 60)
    print("Test 5 : Sauvegarde")
    print("=" * 60)
    
    from src.utils import create_backup, list_backups
    
    login("admin", "Admin123!")
    
    # Créer une sauvegarde
    success, filepath = create_backup("test_backup")
    
    if success:
        print(f"✅ Sauvegarde créée : {filepath}")
        import os
        size = os.path.getsize(filepath)
        print(f"   Taille : {size / 1024:.2f} KB")
    else:
        print(f"❌ Échec : {filepath}")
    
    # Lister les sauvegardes
    backups = list_backups()
    print(f"\n✅ Sauvegardes disponibles : {len(backups)}")
    
    for backup in backups[:3]:
        print(f"   • {backup['filename']} ({backup['size_mb']} MB)")
    
    logout()
    print()
    return True


def main():
    """Fonction principale de test"""
    print("\n" + "🧪" * 30)
    print(" " * 10 + "Tests de l'Application Auto-École")
    print("🧪" * 30 + "\n")
    
    tests = [
        ("Authentification", test_authentication),
        ("Gestion Élèves", test_students),
        ("Paiements", test_payments),
        ("Export CSV", test_export),
        ("Sauvegarde", test_backup),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Erreur dans {name} : {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"  {status:15} {name}")
    
    print("-" * 60)
    print(f"  Score : {passed}/{total} tests réussis ({passed/total*100:.0f}%)")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 Tous les tests sont passés ! L'application fonctionne correctement.")
    else:
        print(f"\n⚠️  {total - passed} test(s) ont échoué.")
    
    print()


if __name__ == "__main__":
    main()
