#!/usr/bin/env python3
"""
Script pour créer l'exécutable de l'application Auto-École Manager
Utilise PyInstaller pour compiler l'application en .exe
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_folders():
    """Nettoyer les anciens dossiers de build"""
    print("🧹 Nettoyage des anciens builds...")
    folders_to_clean = ['build', 'dist', '__pycache__']
    
    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   ✓ {folder}/ supprimé")
    
    # Nettoyer les fichiers .spec
    for spec_file in Path('.').glob('*.spec'):
        os.remove(spec_file)
        print(f"   ✓ {spec_file} supprimé")

def create_version_file():
    """Créer le fichier de version pour Windows"""
    version_info = """
# UTF-8
#
# Version Info for Auto-École Manager

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Auto-École Manager'),
        StringStruct(u'FileDescription', u'Système de Gestion pour Auto-École'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'AutoEcoleManager'),
        StringStruct(u'LegalCopyright', u'© 2024-2025 Auto-École Manager. Tous droits réservés.'),
        StringStruct(u'OriginalFilename', u'AutoEcoleManager.exe'),
        StringStruct(u'ProductName', u'Auto-École Manager'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    print("✓ Fichier de version créé")

def build_executable():
    """Compiler l'application avec PyInstaller"""
    print("\n🔨 Compilation de l'application...")
    print("   Cela peut prendre quelques minutes...\n")
    
    # Commande PyInstaller
    cmd = [
        'pyinstaller',
        '--name=AutoEcoleManager',
        '--onefile',
        '--windowed',
        '--icon=assets/app_icon.ico',  # Utiliser l'icône .ico pour Windows
        '--version-file=version_info.txt',
        
        # Ajouter les données nécessaires
        '--add-data=assets;assets',
        '--add-data=templates;templates',
        '--add-data=src;src',
        
        # Exclure les modules inutiles pour réduire la taille
        '--exclude-module=pytest',
        '--exclude-module=unittest',
        '--exclude-module=setuptools',
        
        # Paramètres de console
        '--noconsole',
        
        # Point d'entrée
        'src/main_gui.py'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Compilation réussie!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la compilation:")
        print(e.stderr)
        return False

def create_installer_structure():
    """Créer la structure pour l'installeur"""
    print("\n📦 Préparation de la structure d'installation...")
    
    installer_dir = Path('installer')
    installer_dir.mkdir(exist_ok=True)
    
    # Copier l'exécutable
    if Path('dist/AutoEcoleManager.exe').exists():
        shutil.copy('dist/AutoEcoleManager.exe', installer_dir)
        print("   ✓ Exécutable copié")
    
    # Copier les icônes
    for icon_file in ['app_icon.png', 'app_icon.ico', 'app_icon_new.png']:
        if Path(f'assets/{icon_file}').exists():
            shutil.copy(f'assets/{icon_file}', installer_dir)
            print(f"   ✓ {icon_file} copié")
    
    # Copier les scripts essentiels
    for script in ['generate_license.py', 'scripts/setup_database.py']:
        if Path(script).exists():
            dest = installer_dir / Path(script).name
            shutil.copy(script, dest)
            print(f"   ✓ {Path(script).name} copié")
    
    # Créer un README
    readme_content = """# Auto-École Manager - Installation

## Installation

Double-cliquez sur le fichier setup.exe pour installer l'application.

## Première utilisation

1. Lancez l'application via le raccourci sur le bureau
2. Générez une licence avec: generate_license.py
3. Connectez-vous avec:
   - Username: admin
   - Password: Admin123!

## Support

Email: e.belqasim@gmail.com
Téléphone: +212 637-636146

---
© 2024-2025 Auto-École Manager
"""
    
    with open(installer_dir / 'README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("   ✓ README créé")
    print(f"\n✅ Structure créée dans: {installer_dir.absolute()}")

def main():
    """Fonction principale"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     🚗 BUILD AUTO-ÉCOLE MANAGER - EXÉCUTABLE              ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # Vérifier que PyInstaller est installé
    try:
        subprocess.run(['pyinstaller', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller n'est pas installé!")
        print("   Installez-le avec: pip install pyinstaller")
        return 1
    
    # Étapes de build
    clean_build_folders()
    create_version_file()
    
    if not build_executable():
        print("\n❌ Échec de la compilation!")
        return 1
    
    create_installer_structure()
    
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║                  ✅ BUILD TERMINÉ AVEC SUCCÈS!             ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print("📁 Fichiers générés:")
    print("   • dist/AutoEcoleManager.exe  (Exécutable)")
    print("   • installer/                 (Dossier d'installation)")
    print()
    print("🎯 Prochaine étape:")
    print("   Créez l'installeur avec Inno Setup (voir setup.iss)")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
