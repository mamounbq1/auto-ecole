"""
Script d'initialisation de la base de données
Crée la base de données et les données de test
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent))

print("="*80)
print("🗄️  INITIALISATION DE LA BASE DE DONNÉES")
print("="*80)

# Créer le dossier data s'il n'existe pas
data_dir = Path("data")
if not data_dir.exists():
    print(f"\n📁 Création du dossier: {data_dir.absolute()}")
    data_dir.mkdir(parents=True, exist_ok=True)
    print("   ✅ Dossier créé")
else:
    print(f"\n📁 Dossier data existe: {data_dir.absolute()}")

# Importer et initialiser la base de données
try:
    print("\n🔧 Importation des modules...")
    from src.models.base import init_db
    from src.init_db import init_database, create_test_data
    
    print("   ✅ Modules importés")
    
    # Initialiser la base de données
    print("\n🔨 Création des tables...")
    init_db(database_path="data/autoecole.db", drop_all=False)
    print("   ✅ Tables créées")
    
    # Créer les données de test
    print("\n📊 Création des données de test...")
    success = init_database()
    
    if success:
        print("   ✅ Données de test créées")
        
        # Créer des données supplémentaires
        print("\n📝 Ajout de données supplémentaires...")
        create_test_data()
        print("   ✅ Données supplémentaires ajoutées")
    else:
        print("   ⚠️  Erreur lors de la création des données de test")
    
    print("\n" + "="*80)
    print("✅ BASE DE DONNÉES INITIALISÉE AVEC SUCCÈS!")
    print("="*80)
    
    print("\n📋 Informations de connexion:")
    print("   👤 Administrateur:")
    print("      Username: admin")
    print("      Password: Admin123!")
    print("\n   👤 Caissier:")
    print("      Username: caissier")
    print("      Password: Caisse123!")
    print("\n   👤 Réceptionniste:")
    print("      Username: receptionniste")
    print("      Password: Reception123!")
    print("\n   👤 Moniteur:")
    print("      Username: moniteur")
    print("      Password: Moniteur123!")
    
    print("\n🚀 Vous pouvez maintenant lancer l'application:")
    print("   python src/main_gui.py")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
    print("\n⚠️  La base de données n'a pas pu être créée.")
    print("   Vérifiez que tous les modules sont correctement installés.")
    sys.exit(1)
