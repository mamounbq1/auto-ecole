#!/usr/bin/env python3
"""
Application Auto-École avec interface graphique PySide6
Point d'entrée principal
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configurer matplotlib pour éviter les erreurs au chargement
os.environ['MPLBACKEND'] = 'Agg'  # Backend non-interactif par défaut
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', message='.*FigureCanvas.*')

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from src.views import LoginWindow, MainWindow
from src.utils import get_logger

logger = get_logger()


def setup_app_style(app):
    """Configurer le style global de l'application"""
    # Police par défaut
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Style global
    app.setStyle("Fusion")


def main():
    """Fonction principale"""
    # Créer l'application Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Auto-École Manager")
    app.setOrganizationName("AutoEcole")
    
    # Configurer le style
    setup_app_style(app)
    
    # Créer et afficher la fenêtre de connexion
    login_window = LoginWindow()
    
    # Variable pour stocker la fenêtre principale (important pour éviter qu'elle soit détruite)
    main_window_ref = [None]  # Liste pour pouvoir modifier dans la closure
    
    # Fonction appelée lors d'une connexion réussie
    def on_login_success(user):
        logger.info(f"Interface graphique lancée pour : {user.username}")
        
        try:
            # Créer et afficher la fenêtre principale
            main_window = MainWindow(user)
            main_window_ref[0] = main_window  # Stocker la référence !
            main_window.show()
            logger.info("✅ Fenêtre principale affichée avec succès")
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement de la fenêtre principale: {e}")
            import traceback
            traceback.print_exc()
            
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                None,
                "Erreur de chargement",
                f"Impossible de charger l'interface principale:\n{str(e)}\n\nVoir la console pour plus de détails."
            )
    
    # Connecter le signal de connexion réussie
    login_window.login_successful.connect(on_login_success)
    
    # Afficher la fenêtre de connexion
    login_window.show()
    
    # Lancer la boucle d'événements
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
