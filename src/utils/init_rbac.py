"""
Script d'initialisation du système RBAC (Role-Based Access Control)
Crée les rôles, permissions, et migre les utilisateurs existants
"""

from typing import Dict, List
from sqlalchemy.orm import Session

from src.models import (
    get_session, init_db,
    User, UserRole,
    Role, Permission, PermissionType
)
from .logger import get_logger

logger = get_logger()


# Définition des rôles système et leurs permissions
ROLE_PERMISSIONS_MAP: Dict[str, Dict[str, any]] = {
    'admin': {
        'display_name': 'Administrateur',
        'description': 'Accès complet au système',
        'is_system': True,
        'permissions': [p.value for p in PermissionType]  # Toutes les permissions
    },
    'manager': {
        'display_name': 'Gestionnaire',
        'description': 'Gestion complète sauf administration système',
        'is_system': True,
        'permissions': [
            # Élèves
            PermissionType.VIEW_STUDENTS.value,
            PermissionType.CREATE_STUDENTS.value,
            PermissionType.EDIT_STUDENTS.value,
            PermissionType.DELETE_STUDENTS.value,
            # Moniteurs
            PermissionType.VIEW_INSTRUCTORS.value,
            PermissionType.CREATE_INSTRUCTORS.value,
            PermissionType.EDIT_INSTRUCTORS.value,
            # Véhicules
            PermissionType.VIEW_VEHICLES.value,
            PermissionType.CREATE_VEHICLES.value,
            PermissionType.EDIT_VEHICLES.value,
            # Séances
            PermissionType.VIEW_SESSIONS.value,
            PermissionType.CREATE_SESSIONS.value,
            PermissionType.EDIT_SESSIONS.value,
            PermissionType.DELETE_SESSIONS.value,
            # Paiements
            PermissionType.VIEW_PAYMENTS.value,
            PermissionType.CREATE_PAYMENTS.value,
            PermissionType.EDIT_PAYMENTS.value,
            # Examens
            PermissionType.VIEW_EXAMS.value,
            PermissionType.CREATE_EXAMS.value,
            PermissionType.EDIT_EXAMS.value,
            # Documents
            PermissionType.VIEW_DOCUMENTS.value,
            PermissionType.CREATE_DOCUMENTS.value,
            PermissionType.EDIT_DOCUMENTS.value,
            # Rapports
            PermissionType.VIEW_REPORTS.value,
            PermissionType.VIEW_STATISTICS.value,
            PermissionType.VIEW_FINANCIAL_REPORTS.value,
        ]
    },
    'instructor': {
        'display_name': 'Moniteur',
        'description': 'Gestion des séances et suivi des élèves',
        'is_system': True,
        'permissions': [
            PermissionType.VIEW_STUDENTS.value,
            PermissionType.VIEW_INSTRUCTORS.value,
            PermissionType.VIEW_VEHICLES.value,
            PermissionType.VIEW_SESSIONS.value,
            PermissionType.CREATE_SESSIONS.value,
            PermissionType.EDIT_SESSIONS.value,
            PermissionType.VIEW_EXAMS.value,
            PermissionType.VIEW_DOCUMENTS.value,
        ]
    },
    'cashier': {
        'display_name': 'Caissier',
        'description': 'Gestion des paiements et finances',
        'is_system': True,
        'permissions': [
            PermissionType.VIEW_STUDENTS.value,
            PermissionType.VIEW_PAYMENTS.value,
            PermissionType.CREATE_PAYMENTS.value,
            PermissionType.EDIT_PAYMENTS.value,
            PermissionType.VIEW_FINANCIAL_REPORTS.value,
            PermissionType.VIEW_DOCUMENTS.value,
            PermissionType.CREATE_DOCUMENTS.value,
        ]
    },
    'secretary': {
        'display_name': 'Secrétaire',
        'description': 'Inscriptions, documents et accueil',
        'is_system': True,
        'permissions': [
            PermissionType.VIEW_STUDENTS.value,
            PermissionType.CREATE_STUDENTS.value,
            PermissionType.EDIT_STUDENTS.value,
            PermissionType.VIEW_INSTRUCTORS.value,
            PermissionType.VIEW_VEHICLES.value,
            PermissionType.VIEW_SESSIONS.value,
            PermissionType.CREATE_SESSIONS.value,
            PermissionType.VIEW_PAYMENTS.value,
            PermissionType.VIEW_EXAMS.value,
            PermissionType.VIEW_DOCUMENTS.value,
            PermissionType.CREATE_DOCUMENTS.value,
            PermissionType.EDIT_DOCUMENTS.value,
        ]
    },
    'accountant': {
        'display_name': 'Comptable',
        'description': 'Gestion complète des finances',
        'is_system': True,
        'permissions': [
            PermissionType.VIEW_STUDENTS.value,
            PermissionType.VIEW_PAYMENTS.value,
            PermissionType.CREATE_PAYMENTS.value,
            PermissionType.EDIT_PAYMENTS.value,
            PermissionType.DELETE_PAYMENTS.value,
            PermissionType.VIEW_REPORTS.value,
            PermissionType.VIEW_FINANCIAL_REPORTS.value,
            PermissionType.VIEW_DOCUMENTS.value,
        ]
    }
}


def create_permissions(session: Session) -> Dict[str, Permission]:
    """
    Créer toutes les permissions du système
    
    Args:
        session: Session SQLAlchemy
    
    Returns:
        Dictionnaire {permission_key: Permission}
    """
    permissions = {}
    
    # Catégories de permissions
    categories = {
        'students': 'Élèves',
        'instructors': 'Moniteurs',
        'vehicles': 'Véhicules',
        'sessions': 'Séances',
        'payments': 'Paiements',
        'exams': 'Examens',
        'documents': 'Documents',
        'reports': 'Rapports',
        'settings': 'Administration'
    }
    
    for perm_type in PermissionType:
        # Extraire la catégorie du nom de la permission
        category_key = perm_type.value.split('_')[1].lower() + 's' if '_' in perm_type.value else 'settings'
        
        # Vérifier si la permission existe déjà
        existing_perm = session.query(Permission).filter(Permission.key == perm_type.value).first()
        
        if existing_perm:
            permissions[perm_type.value] = existing_perm
            logger.info(f"Permission existante : {perm_type.value}")
        else:
            # Créer une nouvelle permission
            permission = Permission(
                key=perm_type.value,
                name=perm_type.value.replace('_', ' ').title(),
                description=f"Permission : {perm_type.value}",
                category=categories.get(category_key, 'Autre'),
                is_active=True
            )
            session.add(permission)
            permissions[perm_type.value] = permission
            logger.info(f"✓ Permission créée : {perm_type.value}")
    
    session.commit()
    return permissions


def create_roles(session: Session, permissions: Dict[str, Permission]) -> Dict[str, Role]:
    """
    Créer les rôles système avec leurs permissions
    
    Args:
        session: Session SQLAlchemy
        permissions: Dictionnaire des permissions
    
    Returns:
        Dictionnaire {role_name: Role}
    """
    roles = {}
    
    for role_name, role_data in ROLE_PERMISSIONS_MAP.items():
        # Vérifier si le rôle existe déjà
        existing_role = session.query(Role).filter(Role.name == role_name).first()
        
        if existing_role:
            role = existing_role
            logger.info(f"Rôle existant : {role_name}")
            # Mettre à jour les permissions
            role.permissions = [permissions[pkey] for pkey in role_data['permissions'] if pkey in permissions]
        else:
            # Créer un nouveau rôle
            role = Role(
                name=role_name,
                display_name=role_data['display_name'],
                description=role_data['description'],
                is_active=True,
                is_system=role_data['is_system']
            )
            # Assigner les permissions
            role.permissions = [permissions[pkey] for pkey in role_data['permissions'] if pkey in permissions]
            session.add(role)
            logger.info(f"✓ Rôle créé : {role_name} avec {len(role.permissions)} permissions")
        
        roles[role_name] = role
    
    session.commit()
    return roles


def migrate_existing_users(session: Session, roles: Dict[str, Role]) -> int:
    """
    Migrer les utilisateurs existants du système mono-rôle vers multi-rôles
    
    Args:
        session: Session SQLAlchemy
        roles: Dictionnaire des rôles
    
    Returns:
        Nombre d'utilisateurs migrés
    """
    # Mapping ancien rôle -> nouveau rôle
    legacy_role_mapping = {
        UserRole.ADMIN: 'admin',
        UserRole.CASHIER: 'cashier',
        UserRole.INSTRUCTOR: 'instructor',
        UserRole.RECEPTIONIST: 'secretary'  # receptionist -> secretary
    }
    
    users = session.query(User).all()
    migrated_count = 0
    
    for user in users:
        # Si l'utilisateur n'a pas encore de rôles dans le nouveau système
        if not user.roles or len(user.roles) == 0:
            # Mapper l'ancien rôle au nouveau
            if user.role and user.role in legacy_role_mapping:
                new_role_name = legacy_role_mapping[user.role]
                if new_role_name in roles:
                    user.roles.append(roles[new_role_name])
                    migrated_count += 1
                    logger.info(f"✓ Utilisateur migré : {user.username} ({user.role.value} -> {new_role_name})")
    
    session.commit()
    return migrated_count


def initialize_rbac_system(force: bool = False) -> tuple[bool, str]:
    """
    Initialiser le système RBAC complet
    
    Args:
        force: Forcer la réinitialisation
    
    Returns:
        Tuple (success, message)
    """
    try:
        # Initialiser la base de données
        init_db()
        
        session = get_session()
        
        # Étape 1: Créer les permissions
        logger.info("📝 Création des permissions...")
        permissions = create_permissions(session)
        logger.info(f"✓ {len(permissions)} permissions créées/vérifiées")
        
        # Étape 2: Créer les rôles
        logger.info("👥 Création des rôles...")
        roles = create_roles(session, permissions)
        logger.info(f"✓ {len(roles)} rôles créés/vérifiés")
        
        # Étape 3: Migrer les utilisateurs existants
        logger.info("🔄 Migration des utilisateurs existants...")
        migrated = migrate_existing_users(session, roles)
        logger.info(f"✓ {migrated} utilisateurs migrés")
        
        session.close()
        
        return True, f"✓ Système RBAC initialisé : {len(permissions)} permissions, {len(roles)} rôles, {migrated} utilisateurs migrés"
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation RBAC : {e}", exc_info=True)
        return False, f"Erreur : {str(e)}"


if __name__ == "__main__":
    # Script exécutable directement
    success, message = initialize_rbac_system()
    print(message)
    if success:
        exit(0)
    else:
        exit(1)
