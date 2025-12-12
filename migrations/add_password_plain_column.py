#!/usr/bin/env python3
"""
Migration: Ajouter la colonne password_plain à la table users
Permet à l'admin de voir les mots de passe des utilisateurs
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import inspect, text
from src.models import get_engine
from src.utils.logger import get_logger

logger = get_logger()


def run_migration():
    """Exécuter la migration"""
    try:
        engine = get_engine()
        inspector = inspect(engine)
        
        # Vérifier si la colonne existe déjà
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'password_plain' in columns:
            print("✓ La colonne 'password_plain' existe déjà dans la table 'users'")
            return True
        
        print("🔄 Ajout de la colonne 'password_plain' à la table 'users'...")
        
        # Ajouter la colonne
        with engine.connect() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN password_plain TEXT"))
            connection.commit()
        
        print("✅ Colonne 'password_plain' ajoutée avec succès!")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la migration : {e}", exc_info=True)
        print(f"\n❌ Erreur lors de la migration : {e}")
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
