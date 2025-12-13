"""
Configuration globale de l'application
"""

import os
import sys
from pathlib import Path

# Détecter si on est dans PyInstaller
def get_project_root():
    """
    Retourne le répertoire racine du projet
    - En développement : répertoire parent de src/
    - En exécutable : répertoire de l'exécutable
    """
    if getattr(sys, 'frozen', False):
        # Mode PyInstaller : utiliser le répertoire de l'exécutable
        return Path(sys.executable).parent
    else:
        # Mode développement : répertoire parent de src/
        return Path(__file__).resolve().parent.parent

# Répertoire racine du projet
PROJECT_ROOT = get_project_root()

# Chemins de la base de données
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "autoecole.db"

# Créer le dossier data s'il n'existe pas
DATA_DIR.mkdir(exist_ok=True)

# Configuration de la base de données
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Configuration du logging
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "autoecole.log"

# Dossiers d'export sur le Bureau
def get_desktop_path():
    """Retourne le chemin du Bureau de l'utilisateur"""
    # Windows
    if os.name == 'nt':
        desktop = Path.home() / "Desktop"
        # Alternative si Desktop n'existe pas (OneDrive, langue non-anglaise)
        if not desktop.exists():
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
            desktop = Path(winreg.QueryValueEx(key, "Desktop")[0])
            winreg.CloseKey(key)
    # Linux/Mac
    else:
        desktop = Path.home() / "Desktop"
    
    return desktop

# Créer le dossier AutoEcole sur le Bureau
try:
    DESKTOP_DIR = get_desktop_path() / "AutoEcole_Documents"
    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sous-dossiers pour les exports
    EXPORTS_DIR = DESKTOP_DIR / "Exports"
    CONTRACTS_DIR = DESKTOP_DIR / "Contrats"
    RECEIPTS_DIR = DESKTOP_DIR / "Reçus"
    CONVOCATIONS_DIR = DESKTOP_DIR / "Convocations"
    REPORTS_DIR = DESKTOP_DIR / "Rapports"
    
    # Créer tous les sous-dossiers
    for folder in [EXPORTS_DIR, CONTRACTS_DIR, RECEIPTS_DIR, CONVOCATIONS_DIR, REPORTS_DIR]:
        folder.mkdir(parents=True, exist_ok=True)
except Exception:
    # Fallback : utiliser le dossier du projet si le Bureau n'est pas accessible
    DESKTOP_DIR = PROJECT_ROOT / "documents"
    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)
    
    EXPORTS_DIR = DESKTOP_DIR / "Exports"
    CONTRACTS_DIR = DESKTOP_DIR / "Contrats"
    RECEIPTS_DIR = DESKTOP_DIR / "Reçus"
    CONVOCATIONS_DIR = DESKTOP_DIR / "Convocations"
    REPORTS_DIR = DESKTOP_DIR / "Rapports"
    
    for folder in [EXPORTS_DIR, CONTRACTS_DIR, RECEIPTS_DIR, CONVOCATIONS_DIR, REPORTS_DIR]:
        folder.mkdir(parents=True, exist_ok=True)

# Configuration de l'application
APP_NAME = "Auto-École Manager"
APP_VERSION = "1.0.0"

# Autres configurations
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
