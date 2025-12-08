#!/usr/bin/env python3
"""
Application de Gestion Auto-École - Version Console
Point d'entrée principal de l'application
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import login, logout, get_current_user, create_backup, list_backups
from src.controllers import (
    StudentController,
    InstructorController,
    VehicleController,
    SessionController,
    PaymentController,
    ExamController
)
from src.models import UserRole, PaymentMethod


def print_header(title: str):
    """Afficher un en-tête formaté"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_menu(title: str, options: list):
    """Afficher un menu"""
    print(f"\n📋 {title}")
    print("-" * 60)
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    print("  0. Retour / Quitter")
    print("-" * 60)


def login_menu():
    """Menu de connexion"""
    print_header("🚗 Auto-École Manager - Connexion")
    
    while True:
        print("\n")
        username = input("👤 Nom d'utilisateur : ").strip()
        if not username:
            print("❌ Veuillez entrer un nom d'utilisateur")
            continue
        
        password = input("🔒 Mot de passe : ").strip()
        if not password:
            print("❌ Veuillez entrer un mot de passe")
            continue
        
        # Tenter la connexion
        success, message, user = login(username, password)
        
        if success:
            print(f"\n✅ {message}")
            print(f"   Bienvenue {user.full_name} ({user.role.value})")
            return True
        else:
            print(f"\n❌ {message}")
            
            retry = input("\n   Réessayer ? (o/n) : ").lower()
            if retry != 'o':
                return False


def dashboard_menu():
    """Menu principal / Dashboard"""
    user = get_current_user()
    
    while True:
        print_header(f"Dashboard - {user.full_name} ({user.role.value})")
        
        # Statistiques rapides
        active_students = StudentController.get_active_students_count()
        today_sessions = SessionController.get_today_sessions()
        upcoming_exams = ExamController.get_upcoming_exams()
        
        print("\n📊 Statistiques du jour")
        print("-" * 60)
        print(f"  • Élèves actifs : {active_students}")
        print(f"  • Sessions aujourd'hui : {len(today_sessions)}")
        print(f"  • Examens à venir : {len(upcoming_exams)}")
        
        # Menu selon le rôle
        menu_options = []
        
        if user.role in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
            menu_options.extend([
                "📚 Gestion des Élèves",
            ])
        
        if user.role in [UserRole.ADMIN, UserRole.INSTRUCTOR]:
            menu_options.extend([
                "📅 Planning des Sessions",
            ])
        
        if user.role in [UserRole.ADMIN, UserRole.CASHIER]:
            menu_options.extend([
                "💰 Gestion des Paiements",
            ])
        
        if user.role == UserRole.ADMIN:
            menu_options.extend([
                "👨‍🏫 Gestion des Moniteurs",
                "🚗 Gestion des Véhicules",
                "📝 Gestion des Examens",
                "💾 Sauvegardes",
                "📈 Rapports",
            ])
        
        menu_options.append("🚪 Déconnexion")
        
        print_menu("Menu Principal", menu_options)
        
        try:
            choice = input("\nVotre choix : ").strip()
            
            if choice == "0" or choice.lower() == "q":
                break
            
            choice_int = int(choice)
            
            if choice_int == 1 and "Élèves" in menu_options[0]:
                students_menu()
            elif choice_int == 2 and len(menu_options) > 1 and "Planning" in menu_options[1]:
                sessions_menu()
            elif "Paiements" in str(menu_options) and choice_int <= len(menu_options):
                for i, opt in enumerate(menu_options, 1):
                    if choice_int == i and "Paiements" in opt:
                        payments_menu()
            elif "Sauvegardes" in str(menu_options) and choice_int <= len(menu_options):
                for i, opt in enumerate(menu_options, 1):
                    if choice_int == i and "Sauvegardes" in opt:
                        backup_menu()
            elif choice_int == len(menu_options):
                # Déconnexion
                logout()
                print("\n✅ Déconnexion réussie")
                return
            else:
                print("❌ Option non disponible pour le moment")
                
        except ValueError:
            print("❌ Veuillez entrer un nombre valide")
        except Exception as e:
            print(f"❌ Erreur : {e}")
        
        input("\nAppuyez sur Entrée pour continuer...")


def students_menu():
    """Menu de gestion des élèves"""
    while True:
        print_header("Gestion des Élèves")
        
        students = StudentController.get_all_students()
        
        print(f"\n📋 Liste des élèves ({len(students)} total)")
        print("-" * 100)
        print(f"{'ID':<5} {'Nom':<25} {'CIN':<15} {'Téléphone':<15} {'Statut':<12} {'Solde':<10}")
        print("-" * 100)
        
        for student in students[:10]:  # Afficher les 10 premiers
            balance_str = f"{student.balance:,.0f} DH"
            balance_colored = f"{'✅' if student.balance >= 0 else '❌'} {balance_str}"
            print(f"{student.id:<5} {student.full_name[:24]:<25} {student.cin:<15} "
                  f"{student.phone:<15} {student.status.value:<12} {balance_colored}")
        
        if len(students) > 10:
            print(f"... et {len(students) - 10} autres élèves")
        
        print_menu("Actions", [
            "Afficher tous les élèves",
            "Rechercher un élève",
            "Ajouter un élève",
            "Exporter en CSV",
        ])
        
        choice = input("\nVotre choix : ").strip()
        
        if choice == "0":
            break
        elif choice == "2":
            search_term = input("Rechercher (nom/CIN/téléphone) : ").strip()
            if search_term:
                results = StudentController.search_students(search_term)
                print(f"\n✅ {len(results)} résultat(s) trouvé(s)")
                for student in results:
                    print(f"  • {student.full_name} - {student.cin} - {student.phone}")
            input("\nAppuyez sur Entrée...")
        elif choice == "4":
            success, filepath = StudentController.export_students_to_csv(students)
            if success:
                print(f"\n✅ Export réussi : {filepath}")
            else:
                print(f"\n❌ Erreur : {filepath}")
            input("\nAppuyez sur Entrée...")
        else:
            print("❌ Option non disponible dans cette version console")
            input("\nAppuyez sur Entrée...")


def sessions_menu():
    """Menu de gestion des sessions"""
    print_header("Planning des Sessions")
    
    today_sessions = SessionController.get_today_sessions()
    upcoming = SessionController.get_upcoming_sessions(days=7)
    
    print(f"\n📅 Sessions aujourd'hui : {len(today_sessions)}")
    print("-" * 100)
    
    for session in today_sessions[:5]:
        student_name = session.student.full_name if session.student else "N/A"
        instructor_name = session.instructor.full_name if session.instructor else "N/A"
        time_str = session.start_datetime.strftime("%H:%M")
        status_icon = "✅" if session.status.value == "realise" else "⏰"
        
        print(f"{status_icon} {time_str} - {student_name} avec {instructor_name} ({session.duration_minutes}min)")
    
    print(f"\n📆 Sessions à venir (7 prochains jours) : {len(upcoming)}")
    
    input("\nAppuyez sur Entrée...")


def payments_menu():
    """Menu de gestion des paiements"""
    print_header("Gestion des Paiements")
    
    # Afficher les élèves avec dette
    students_with_debt = StudentController.get_students_with_debt()
    
    if students_with_debt:
        print(f"\n⚠️  Élèves avec dette : {len(students_with_debt)}")
        print("-" * 100)
        print(f"{'Nom':<30} {'CIN':<15} {'Téléphone':<15} {'Dette':<15}")
        print("-" * 100)
        
        for student in students_with_debt[:10]:
            debt = abs(student.balance)
            print(f"{student.full_name[:29]:<30} {student.cin:<15} {student.phone:<15} {debt:,.0f} DH")
    else:
        print("\n✅ Aucun élève en dette")
    
    print_menu("Actions", [
        "Enregistrer un paiement",
        "Voir historique paiements",
    ])
    
    choice = input("\nVotre choix : ").strip()
    
    if choice == "0":
        return
    elif choice == "1":
        try:
            student_id = int(input("ID de l'élève : "))
            amount = float(input("Montant (DH) : "))
            
            print("\nMéthodes de paiement :")
            print("1. Espèces")
            print("2. Carte bancaire")
            print("3. Chèque")
            method_choice = input("Votre choix : ")
            
            methods = {
                "1": PaymentMethod.CASH,
                "2": PaymentMethod.CARD,
                "3": PaymentMethod.CHECK,
            }
            
            method = methods.get(method_choice, PaymentMethod.CASH)
            description = input("Description (optionnel) : ").strip()
            
            success, message, payment = PaymentController.create_payment(
                student_id, amount, method, description, get_current_user().full_name
            )
            
            if success:
                print(f"\n✅ {message}")
                print(f"   N° Reçu : {payment.receipt_number}")
                
                # Générer le reçu
                gen_receipt = input("\nGénérer le reçu PDF ? (o/n) : ").lower()
                if gen_receipt == 'o':
                    success, filepath = PaymentController.generate_receipt_pdf(payment.id)
                    if success:
                        print(f"   ✅ Reçu généré : {filepath}")
                    else:
                        print(f"   ❌ Erreur : {filepath}")
            else:
                print(f"\n❌ {message}")
                
        except ValueError:
            print("❌ Valeurs invalides")
        except Exception as e:
            print(f"❌ Erreur : {e}")
        
        input("\nAppuyez sur Entrée...")
    else:
        print("❌ Option non disponible")
        input("\nAppuyez sur Entrée...")


def backup_menu():
    """Menu de gestion des sauvegardes"""
    print_header("Gestion des Sauvegardes")
    
    backups = list_backups()
    
    if backups:
        print(f"\n💾 Sauvegardes disponibles : {len(backups)}")
        print("-" * 100)
        print(f"{'#':<4} {'Fichier':<40} {'Taille':<12} {'Date':<25}")
        print("-" * 100)
        
        for i, backup in enumerate(backups[:10], 1):
            print(f"{i:<4} {backup['filename'][:39]:<40} "
                  f"{backup['size_mb']:,.2f} MB   {backup['modified'].strftime('%d/%m/%Y %H:%M:%S')}")
    else:
        print("\n⚠️  Aucune sauvegarde disponible")
    
    print_menu("Actions", [
        "Créer une nouvelle sauvegarde",
        "Restaurer une sauvegarde",
    ])
    
    choice = input("\nVotre choix : ").strip()
    
    if choice == "0":
        return
    elif choice == "1":
        backup_name = input("Nom de la sauvegarde (optionnel) : ").strip() or None
        success, result = create_backup(backup_name)
        
        if success:
            print(f"\n✅ Sauvegarde créée : {result}")
        else:
            print(f"\n❌ Erreur : {result}")
        
        input("\nAppuyez sur Entrée...")
    else:
        print("❌ Option non disponible")
        input("\nAppuyez sur Entrée...")


def main():
    """Fonction principale"""
    print_header("🚗 Application de Gestion Auto-École")
    print("\n   Version 1.0.0 - Console Edition")
    print("   Développé pour digitaliser la gestion des auto-écoles")
    
    # Connexion
    if not login_menu():
        print("\n👋 Au revoir !")
        return
    
    # Dashboard
    try:
        dashboard_menu()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption détectée")
    finally:
        logout()
        print("\n👋 Au revoir !\n")


if __name__ == "__main__":
    main()
