#!/usr/bin/env python3
"""
Script d'initialisation simple de la base de données
Appelle directement src/init_db.py
"""

import os
import sys
from pathlib import Path

print("="*80)
print("🗄️  INITIALISATION DE LA BASE DE DONNÉES AUTO-ÉCOLE")
print("="*80)

# Vérifier que nous sommes dans le bon répertoire
if not Path("src/main_gui.py").exists():
    print("\n❌ ERREUR: Ce script doit être exécuté depuis le répertoire racine du projet")
    print(f"   Répertoire actuel: {Path.cwd()}")
    sys.exit(1)

# Créer le dossier data s'il n'existe pas
data_dir = Path("data")
if not data_dir.exists():
    print(f"\n📁 Création du dossier: {data_dir.absolute()}")
    data_dir.mkdir(parents=True, exist_ok=True)
    print("   ✅ Dossier créé")
else:
    print(f"\n📁 Dossier data existe déjà: {data_dir.absolute()}")

# Vérifier si la base existe déjà
db_path = Path("data/autoecole.db")
if db_path.exists():
    print(f"\n⚠️  La base de données existe déjà: {db_path}")
    print("   Pour recommencer, supprimez d'abord: data\\autoecole.db")
    response = input("\n   Voulez-vous la supprimer et recommencer ? (o/n): ")
    if response.lower() in ['o', 'oui', 'y', 'yes']:
        db_path.unlink()
        print("   ✅ Base de données supprimée")
    else:
        print("   ℹ️  Conservation de la base existante")
        print("\n🚀 Vous pouvez lancer l'application:")
        print("   python src\\main_gui.py")
        sys.exit(0)

# Appeler le script d'initialisation
print("\n🔧 Lancement de l'initialisation...")
print("="*80)

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

try:
    # Importer et exécuter le script d'initialisation
    from src import init_db
    
    # Appeler la fonction main du module init_db
    init_db.main()
    
except KeyboardInterrupt:
    print("\n\n⚠️  Initialisation annulée par l'utilisateur")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ ERREUR lors de l'initialisation: {e}")
    import traceback
    traceback.print_exc()
    print("\n⚠️  La base de données n'a pas pu être créée.")
    print("   Vérifiez que tous les modules sont correctement installés.")
    sys.exit(1)
