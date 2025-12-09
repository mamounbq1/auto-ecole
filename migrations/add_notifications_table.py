#!/usr/bin/env python3
"""
Migration: Ajouter la table notifications
Phase 2 - Système de Notifications Automatiques
Date: 2024-12-09
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.base import Base, get_engine
from src.models.notification import Notification
from src.utils import get_logger

logger = get_logger()


def run_migration():
    """Exécuter la migration pour ajouter la table notifications"""
    try:
        logger.info("🔄 Début de la migration : Ajout de la table notifications...")
        
        # Obtenir l'engine
        engine = get_engine()
        
        # Créer la table si elle n'existe pas
        Base.metadata.create_all(engine, tables=[Notification.__table__])
        
        logger.info("✅ Migration terminée avec succès !")
        logger.info(f"   - Table créée : {Notification.__tablename__}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la migration : {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("Migration : Ajout de la table notifications")
    print("=" * 70)
    
    success = run_migration()
    
    if success:
        print("\n✅ Migration réussie ! La table notifications est maintenant disponible.")
        print("\nFonctionnalités ajoutées :")
        print("  - Historique complet des notifications (Email, SMS, In-App)")
        print("  - Planification de notifications futures")
        print("  - Suivi du statut de livraison")
        print("  - Retry automatique des échecs")
        print("  - Notifications in-app pour l'interface")
        sys.exit(0)
    else:
        print("\n❌ La migration a échoué. Vérifiez les logs pour plus de détails.")
        sys.exit(1)
