"""
Migration: Ajouter la table documents pour les élèves
Date: 2025-12-10
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.models import get_engine, Base, Document

def upgrade():
    """Créer la table documents"""
    engine = get_engine()
    
    # Créer la table documents
    Base.metadata.create_all(engine, tables=[Document.__table__])
    
    print("✅ Table 'documents' créée avec succès")

def downgrade():
    """Supprimer la table documents"""
    engine = get_engine()
    
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS documents"))
        conn.commit()
    
    print("✅ Table 'documents' supprimée avec succès")

if __name__ == "__main__":
    print("Migration: Ajout de la table documents")
    print("----------------------------------------")
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
