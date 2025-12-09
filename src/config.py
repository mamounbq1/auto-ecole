"""
Configuration globale de l'application
"""

import os
from pathlib import Path

# Répertoire racine du projet
PROJECT_ROOT = Path(__file__).resolve().parent.parent

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
