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
from PySide6.QtGui import QFont, QIcon
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
    
    # Set application icon (prioritize .ico for Windows)
    icon_ico = Path(__file__).parent.parent / "assets" / "app_icon.ico"
    icon_png = Path(__file__).parent.parent / "assets" / "app_icon_new.png"
    
    if icon_ico.exists():
        app.setWindowIcon(QIcon(str(icon_ico)))
    elif icon_png.exists():
        app.setWindowIcon(QIcon(str(icon_png)))
    
    # Configurer le style
    setup_app_style(app)
    
    # === VÉRIFICATION DE LA LICENCE ===
    license_manager = get_license_manager()
    
    if not license_manager.is_licensed():
        logger.warning("⚠️ Aucune licence valide détectée")
        
        # Afficher la fenêtre d'activation
        license_window = LicenseActivationWindow()
        result = license_window.exec()
        
        if result != LicenseActivationWindow.Accepted:
            logger.info("Application fermée sans activation de licence")
            return 0
        
        logger.info("✅ Licence activée avec succès")
    else:
        license_info = license_manager.get_license_info()
        logger.info(f"✅ Licence valide pour {license_info.get('company')} ({license_info.get('days_remaining')} jours restants)")
    
    # === MIGRATIONS AUTOMATIQUES ===
    try:
        from sqlalchemy import inspect, text
        from src.models import get_engine
        
        engine = get_engine()
        inspector = inspect(engine)
        
        # Migration 1: Ajouter la colonne password_plain
        columns = [col['name'] for col in inspector.get_columns('users')]
        if 'password_plain' not in columns:
            with engine.connect() as connection:
                connection.execute(text("ALTER TABLE users ADD COLUMN password_plain TEXT"))
                connection.commit()
        
        # Migration 2: Créer les tables RBAC si nécessaire
        existing_tables = inspector.get_table_names()
        if 'roles' not in existing_tables or 'permissions' not in existing_tables:
            from src.utils.init_rbac import initialize_rbac_system
            success_rbac, message_rbac = initialize_rbac_system()
            if not success_rbac:
                logger.warning(f"⚠️ RBAC init: {message_rbac}")
    except Exception as e:
        logger.warning(f"⚠️ Erreur migrations (ignorée) : {e}")
    
    # === FENÊTRE DE CONNEXION ===
    # Store reference to main window to prevent garbage collection
    app.main_window = None
    
    def on_login_success(user):
        """Callback appelé lors d'une connexion réussie"""
        logger.info(f"✅ Connexion réussie : {user.username}")
        
        # === BACKUP AUTOMATIQUE AU DÉMARRAGE ===
        try:
            from src.utils.config_manager import get_config_manager
            from src.config import DATABASE_PATH
            import shutil
            from pathlib import Path
            from datetime import datetime as dt
            
            config_mgr = get_config_manager()
            if config_mgr.get('database', {}).get('backup_on_start', False):
                db_path = Path(DATABASE_PATH)
                if db_path.exists():
                    backup_dir = Path(config_mgr.get_backup_path())
                    backup_dir.mkdir(exist_ok=True)
                    timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = backup_dir / f"startup_backup_{timestamp}.db"
                    shutil.copy(db_path, backup_path)
        except Exception as e:
            logger.warning(f"⚠️ Erreur backup automatique: {e}")
        
        # Créer et afficher la fenêtre principale
        try:
            # Store as app attribute to prevent garbage collection
            app.main_window = MainWindow(user)
            app.main_window.show()
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
            app.quit()
    
    # Créer et connecter la fenêtre de login
    login_window = LoginWindow()
    login_window.login_successful.connect(on_login_success)
    login_window.show()
    
    # Lancer la boucle d'événements
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
