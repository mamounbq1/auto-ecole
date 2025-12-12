#!/usr/bin/env python3
"""
Script de test et initialisation du système RBAC
"""

import sys
from pathlib import Path

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.init_rbac import initialize_rbac_system
from src.controllers.user_controller import UserController
from src.models import get_session, User, Role, Permission


def print_separator():
    print("\n" + "="*80 + "\n")


def test_initialization():
    """Tester l'initialisation du système RBAC"""
    print("🚀 INITIALISATION DU SYSTÈME RBAC")
    print_separator()
    
    success, message = initialize_rbac_system()
    print(message)
    
    if not success:
        print("\n❌ Échec de l'initialisation!")
        return False
    
    print("\n✅ Initialisation réussie!")
    return True


def test_roles_and_permissions():
    """Tester les rôles et permissions créés"""
    print_separator()
    print("📋 VÉRIFICATION DES RÔLES ET PERMISSIONS")
    print_separator()
    
    session = get_session()
    
    # Lister les rôles
    roles = session.query(Role).all()
    print(f"\n✓ {len(roles)} rôles créés:")
    for role in roles:
        print(f"   - {role.display_name} ({role.name}): {len(role.permissions)} permissions")
    
    # Lister les permissions
    permissions = session.query(Permission).all()
    print(f"\n✓ {len(permissions)} permissions créées:")
    categories = {}
    for perm in permissions:
        cat = perm.category or 'Autre'
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(perm.name)
    
    for cat, perms in sorted(categories.items()):
        print(f"\n   📂 {cat} ({len(perms)} permissions):")
        for perm in sorted(perms)[:5]:  # Afficher les 5 premières
            print(f"      • {perm}")
        if len(perms) > 5:
            print(f"      ... et {len(perms) - 5} autres")
    
    session.close()


def test_users():
    """Tester les utilisateurs"""
    print_separator()
    print("👥 VÉRIFICATION DES UTILISATEURS")
    print_separator()
    
    users = UserController.get_all_users(include_inactive=True)
    
    if not users:
        print("\n⚠️ Aucun utilisateur trouvé. Création d'un admin par défaut...")
        
        # Créer un admin par défaut
        session = get_session()
        admin_role = session.query(Role).filter(Role.name == 'admin').first()
        
        if admin_role:
            success, message, user = UserController.create_user(
                username='admin',
                password='admin123',
                full_name='Administrateur',
                email='admin@autoecole.ma',
                role_ids=[admin_role.id]
            )
            
            if success:
                print(f"✅ {message}")
                print(f"   Username: admin")
                print(f"   Password: admin123")
            else:
                print(f"❌ Erreur: {message}")
        
        session.close()
        users = UserController.get_all_users(include_inactive=True)
    
    print(f"\n✓ {len(users)} utilisateur(s) dans le système:\n")
    
    for user in users:
        status_icon = "✅" if user.is_active else "❌"
        locked_icon = "🔒" if user.is_locked else ""
        role_names = user.get_role_names()
        roles_str = ", ".join(role_names) if role_names else "Aucun rôle"
        
        print(f"   {status_icon} {locked_icon} {user.username} ({user.full_name})")
        print(f"      Rôles: {roles_str}")
        print(f"      Email: {user.email or '-'}")
        
        if user.password_plain:
            print(f"      🔑 Mot de passe: {user.password_plain}")
        
        print()


def test_statistics():
    """Afficher les statistiques"""
    print_separator()
    print("📊 STATISTIQUES DU SYSTÈME")
    print_separator()
    
    stats = UserController.get_user_statistics()
    
    print(f"\n   Total utilisateurs: {stats['total']}")
    print(f"   ✅ Actifs: {stats['active']}")
    print(f"   ❌ Inactifs: {stats['inactive']}")
    print(f"   🔒 Verrouillés: {stats['locked']}")


def main():
    """Fonction principale"""
    print("\n" + "="*80)
    print("   SYSTÈME RBAC - AUTO-ÉCOLE MANAGER")
    print("="*80)
    
    # Étape 1: Initialisation
    if not test_initialization():
        return 1
    
    # Étape 2: Vérifier les rôles et permissions
    test_roles_and_permissions()
    
    # Étape 3: Vérifier les utilisateurs
    test_users()
    
    # Étape 4: Statistiques
    test_statistics()
    
    print_separator()
    print("✅ TOUS LES TESTS SONT TERMINÉS AVEC SUCCÈS!")
    print_separator()
    
    print("\n💡 PROCHAINES ÉTAPES:")
    print("   1. Lancez l'application: python main.py")
    print("   2. Connectez-vous avec: admin / admin123")
    print("   3. Allez dans Paramètres → Gestion des Utilisateurs")
    print("   4. Créez de nouveaux utilisateurs et assignez-leur des rôles")
    print("\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
