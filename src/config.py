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

# Configuration de l'application
APP_NAME = "Auto-École Manager"
APP_VERSION = "1.0.0"

# Autres configurations
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
