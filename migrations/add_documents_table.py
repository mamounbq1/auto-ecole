#!/usr/bin/env python3
"""
Migration: Ajouter la table documents
Phase 3 - Gestion Documentaire
Date: 2024-12-09
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.base import Base, get_engine
from src.models.document import Document
from src.utils import get_logger

logger = get_logger()


def run_migration():
    """Exécuter la migration pour ajouter la table documents"""
    try:
        logger.info("🔄 Début de la migration : Ajout de la table documents...")
        
        # Obtenir l'engine
        engine = get_engine()
        
        # Créer la table si elle n'existe pas
        Base.metadata.create_all(engine, tables=[Document.__table__])
        
        # Créer le répertoire de stockage
        storage_dir = Path("storage/documents")
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ Migration terminée avec succès !")
        logger.info(f"   - Table créée : {Document.__tablename__}")
        logger.info(f"   - Répertoire créé : {storage_dir}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la migration : {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("Migration : Ajout de la table documents")
    print("=" * 70)
    
    success = run_migration()
    
    if success:
        print("\n✅ Migration réussie ! La table documents est maintenant disponible.")
        print("\nFonctionnalités ajoutées :")
        print("  - Stockage de tous types de documents (CIN, contrats, reçus, etc.)")
        print("  - Upload et gestion de fichiers")
        print("  - Génération automatique de contrats et attestations")
        print("  - Validation et expiration de documents")
        print("  - Statistiques des documents")
        sys.exit(0)
    else:
        print("\n❌ La migration a échoué. Vérifiez les logs pour plus de détails.")
        sys.exit(1)
