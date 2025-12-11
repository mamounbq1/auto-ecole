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
from src.views.license_activation_window import LicenseActivationWindow
from src.utils import get_logger
from src.utils.license_manager import get_license_manager

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
    
    # === LICENCE DÉSACTIVÉE TEMPORAIREMENT ===
    # license_manager = get_license_manager()
    # 
    # if not license_manager.is_licensed():
    #     logger.warning("⚠️ Aucune licence valide détectée")
    #     
    #     # Afficher la fenêtre d'activation
    #     license_window = LicenseActivationWindow()
    #     result = license_window.exec()
    #     
    #     if result != LicenseActivationWindow.Accepted:
    #         logger.info("Application fermée sans activation de licence")
    #         return 0
    #     
    #     logger.info("✅ Licence activée avec succès")
    # else:
    #     license_info = license_manager.get_license_info()
    #     logger.info(f"✅ Licence valide pour {license_info.get('company')} ({license_info.get('days_remaining')} jours restants)")
    
    logger.info("⚠️ Mode développement : licence et login désactivés")
    
    # === LOGIN DÉSACTIVÉ - BYPASS DIRECT ===
    # Créer directement la fenêtre principale avec un utilisateur admin
    from src.utils import bypass_login
    success, message, user = bypass_login()
    
    if not success:
        logger.error("Impossible de créer un utilisateur bypass")
        return 1
    
    logger.info(f"Connexion automatique : {user.username} ({user.role.value})")
    
    # Créer et afficher directement la fenêtre principale
    try:
        main_window = MainWindow(user)
        main_window.show()
        logger.info("✅ Fenêtre principale affichée avec succès (mode développement)")
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
        return 1
    
    # Lancer la boucle d'événements
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
