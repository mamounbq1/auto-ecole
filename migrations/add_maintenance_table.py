#!/usr/bin/env python3
"""
Migration: Ajouter la table vehicle_maintenances
Phase 1 - Critical Improvements
Date: 2024-12-09
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.base import Base, get_engine, get_session
from src.models.maintenance import VehicleMaintenance
from src.utils import get_logger

logger = get_logger()


def run_migration():
    """Exécuter la migration pour ajouter la table vehicle_maintenances"""
    try:
        logger.info("🔄 Début de la migration : Ajout de la table vehicle_maintenances...")
        
        # Obtenir l'engine
        engine = get_engine()
        
        # Créer la table si elle n'existe pas
        Base.metadata.create_all(engine, tables=[VehicleMaintenance.__table__])
        
        logger.info("✅ Migration terminée avec succès !")
        logger.info(f"   - Table créée : {VehicleMaintenance.__tablename__}")
        
        # Vérifier que la table existe
        session = get_session()
        result = session.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vehicle_maintenances'")
        table_exists = result.fetchone() is not None
        
        if table_exists:
            logger.info("✅ Vérification : La table vehicle_maintenances existe bien dans la base de données")
        else:
            logger.error("❌ Erreur : La table vehicle_maintenances n'a pas été créée")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la migration : {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("Migration : Ajout de la table vehicle_maintenances")
    print("=" * 70)
    
    success = run_migration()
    
    if success:
        print("\n✅ Migration réussie ! La table vehicle_maintenances est maintenant disponible.")
        print("\nFonctionnalités ajoutées :")
        print("  - Historique complet de maintenance pour chaque véhicule")
        print("  - Suivi des coûts (main d'œuvre, pièces, autres)")
        print("  - Alertes de maintenance préventive")
        print("  - Statistiques de maintenance par véhicule et par type")
        print("  - Export CSV des données de maintenance")
        sys.exit(0)
    else:
        print("\n❌ La migration a échoué. Vérifiez les logs pour plus de détails.")
        sys.exit(1)
