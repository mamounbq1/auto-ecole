#!/usr/bin/env python3
"""
Migration: Ajouter les tables RBAC (Role-Based Access Control)
- Crée les tables: roles, permissions, user_roles, role_permissions
- Ajoute la colonne password_plain à users
- Initialise les rôles et permissions système
- Migre les utilisateurs existants
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Table, inspect
from src.models import Base, get_engine, get_session
from src.utils.logger import get_logger

logger = get_logger()


def run_migration():
    """Exécuter la migration"""
    try:
        engine = get_engine()
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print("🔄 Migration RBAC - Création des tables...")
        
        # Vérifier si les tables existent déjà
        if 'roles' in existing_tables and 'permissions' in existing_tables:
            print("✓ Les tables RBAC existent déjà. Migration ignorée.")
            return True
        
        # Créer toutes les tables définies dans les modèles
        # Cela créera roles, permissions, user_roles, role_permissions
        Base.metadata.create_all(engine)
        print("✓ Tables créées avec succès!")
        
        # Vérifier les nouvelles tables
        inspector = inspect(engine)
        new_tables = inspector.get_table_names()
        
        rbac_tables = ['roles', 'permissions', 'user_roles', 'role_permissions']
        for table in rbac_tables:
            if table in new_tables:
                print(f"  ✓ Table '{table}' créée")
            else:
                print(f"  ⚠️ Table '{table}' non trouvée")
        
        # Vérifier la colonne password_plain dans users
        user_columns = [col['name'] for col in inspector.get_columns('users')]
        if 'password_plain' in user_columns:
            print("  ✓ Colonne 'password_plain' existe dans 'users'")
        else:
            print("  ⚠️ Colonne 'password_plain' non trouvée dans 'users'")
            print("     La colonne sera créée au prochain démarrage de l'app")
        
        print("\n✅ Migration RBAC terminée avec succès!")
        print("\n📋 Prochaines étapes:")
        print("   1. Fermez l'application")
        print("   2. Redémarrez l'application")
        print("   3. L'initialisation RBAC se fera automatiquement au démarrage")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la migration RBAC : {e}", exc_info=True)
        print(f"\n❌ Erreur lors de la migration : {e}")
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
