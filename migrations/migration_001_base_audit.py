"""
Migration 001: Ajout des champs d'audit au BaseModel
Date: 2024-12-08
Priorité: CRITIQUE

Description:
    Ajoute les champs de traçabilité à toutes les tables:
    - created_by_id
    - updated_by_id  
    - deleted_at (soft delete)
    - is_deleted (soft delete)
"""

import sqlite3
from datetime import datetime
from pathlib import Path


def get_db_connection(db_path='data/autoecole.db'):
    """Obtenir une connexion à la base de données"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def backup_database(db_path='data/autoecole.db'):
    """Créer un backup avant migration"""
    import shutil
    
    backup_path = f"backups/backup_before_migration_001_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    Path("backups").mkdir(exist_ok=True)
    
    shutil.copy(db_path, backup_path)
    print(f"✓ Backup créé: {backup_path}")
    return backup_path


def upgrade(db_path='data/autoecole.db'):
    """
    Appliquer la migration
    """
    print("=" * 60)
    print("MIGRATION 001: Ajout des champs d'audit")
    print("=" * 60)
    
    # Backup
    backup_path = backup_database(db_path)
    
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Tables à migrer
    tables = ['students', 'instructors', 'vehicles', 'sessions', 'payments', 'exams']
    
    try:
        for table in tables:
            print(f"\n→ Migration de la table '{table}'...")
            
            # Vérifier si les colonnes existent déjà
            cursor.execute(f"PRAGMA table_info({table})")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            # Ajout created_by_id
            if 'created_by_id' not in existing_columns:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN created_by_id INTEGER")
                print(f"  ✓ Ajout colonne 'created_by_id'")
            else:
                print(f"  ⊘ Colonne 'created_by_id' existe déjà")
            
            # Ajout updated_by_id
            if 'updated_by_id' not in existing_columns:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN updated_by_id INTEGER")
                print(f"  ✓ Ajout colonne 'updated_by_id'")
            else:
                print(f"  ⊘ Colonne 'updated_by_id' existe déjà")
            
            # Ajout deleted_at
            if 'deleted_at' not in existing_columns:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN deleted_at TEXT")
                print(f"  ✓ Ajout colonne 'deleted_at'")
            else:
                print(f"  ⊘ Colonne 'deleted_at' existe déjà")
            
            # Ajout is_deleted
            if 'is_deleted' not in existing_columns:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN is_deleted INTEGER DEFAULT 0")
                print(f"  ✓ Ajout colonne 'is_deleted'")
            else:
                print(f"  ⊘ Colonne 'is_deleted' existe déjà")
        
        # Commit
        conn.commit()
        print("\n" + "=" * 60)
        print("✓ Migration 001 appliquée avec succès!")
        print("=" * 60)
        print(f"\nBackup disponible: {backup_path}")
        print("\nChangements appliqués:")
        print("  • created_by_id ajouté à toutes les tables")
        print("  • updated_by_id ajouté à toutes les tables")
        print("  • deleted_at ajouté (soft delete)")
        print("  • is_deleted ajouté (soft delete)")
        print("\nNOTE: Les controllers doivent être mis à jour pour utiliser ces champs")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ ERREUR lors de la migration: {e}")
        print(f"\nRestauration du backup: {backup_path}")
        
        # Restaurer le backup
        import shutil
        shutil.copy(backup_path, db_path)
        print("✓ Base de données restaurée")
        
        return False
        
    finally:
        conn.close()


def downgrade(db_path='data/autoecole.db'):
    """
    Annuler la migration (rollback)
    
    ATTENTION: SQLite ne supporte pas DROP COLUMN facilement.
    Il faut recréer les tables sans les colonnes.
    """
    print("=" * 60)
    print("ROLLBACK MIGRATION 001")
    print("=" * 60)
    print("\n⚠️  ATTENTION: Le rollback nécessite de recréer les tables.")
    print("⚠️  Il est recommandé de restaurer depuis un backup.\n")
    
    response = input("Voulez-vous continuer? (oui/non): ")
    if response.lower() not in ['oui', 'yes', 'y']:
        print("Rollback annulé.")
        return False
    
    # Backup avant rollback
    backup_path = backup_database(db_path)
    
    print("\n⚠️  Pour faire un rollback complet:")
    print(f"   Restaurez manuellement le backup: {backup_path}")
    print(f"   Commande: cp {backup_path} {db_path}")
    
    return False


def check_migration_status(db_path='data/autoecole.db'):
    """
    Vérifier le statut de la migration
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    tables = ['students', 'instructors', 'vehicles', 'sessions', 'payments', 'exams']
    columns_to_check = ['created_by_id', 'updated_by_id', 'deleted_at', 'is_deleted']
    
    print("\n" + "=" * 60)
    print("STATUS DE LA MIGRATION 001")
    print("=" * 60)
    
    all_migrated = True
    
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        table_status = []
        for col in columns_to_check:
            if col in existing_columns:
                table_status.append("✓")
            else:
                table_status.append("✗")
                all_migrated = False
        
        status_str = " | ".join([f"{col}: {status}" for col, status in zip(columns_to_check, table_status)])
        print(f"{table:15} → {status_str}")
    
    conn.close()
    
    print("=" * 60)
    if all_migrated:
        print("✓ Toutes les tables sont migrées")
    else:
        print("⚠️  Certaines tables ne sont pas migrées")
    print("=" * 60)
    
    return all_migrated


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python migration_001_base_audit.py upgrade    # Appliquer la migration")
        print("  python migration_001_base_audit.py downgrade  # Annuler la migration")
        print("  python migration_001_base_audit.py status     # Vérifier le statut")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    if action == "upgrade":
        upgrade()
    elif action == "downgrade":
        downgrade()
    elif action == "status":
        check_migration_status()
    else:
        print(f"✗ Action inconnue: {action}")
        sys.exit(1)
