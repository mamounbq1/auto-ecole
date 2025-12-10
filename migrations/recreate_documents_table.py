"""
Migration: Recréer la table documents avec la nouvelle structure
Date: 2025-12-10
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.models import get_engine, Base, Document

def upgrade():
    """Recréer la table documents"""
    engine = get_engine()
    
    print("🔄 Suppression de l'ancienne table documents...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS documents"))
        conn.commit()
    
    print("✅ Ancienne table supprimée")
    
    print("🔄 Création de la nouvelle table documents...")
    Base.metadata.create_all(engine, tables=[Document.__table__])
    
    print("✅ Nouvelle table 'documents' créée avec succès")
    print("\nStructure de la table:")
    print("- student_id (FK vers students)")
    print("- title, document_type, status")
    print("- file_path, file_name, file_size, mime_type")
    print("- upload_date, expiry_date, verification_date")
    print("- description, notes")
    print("- is_required, is_verified, verified_by")

if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Recréation de la table documents")
    print("=" * 60)
    
    try:
        upgrade()
        print("\n✅ Migration réussie!")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)
