#!/usr/bin/env python3
"""
Lanceur sécurisé de l'application Auto-École
Désactive matplotlib complètement avant le démarrage
"""

import sys
import os
from pathlib import Path

# Aller dans le répertoire du script
os.chdir(Path(__file__).parent)

# Bloquer l'import de matplotlib
sys.modules['matplotlib'] = None
sys.modules['matplotlib.pyplot'] = None
sys.modules['matplotlib.backends'] = None
sys.modules['matplotlib.backends.backend_qt'] = None

# Configuration pour éviter les erreurs
os.environ['MPLBACKEND'] = 'Agg'

print("="*60)
print("  AUTO-ÉCOLE MANAGER - Démarrage sécurisé")
print("="*60)
print()
print("  Mode : Sans graphiques matplotlib")
print("  Dashboard : Version simplifiée")
print()

# Ajouter le répertoire au path
sys.path.insert(0, str(Path.cwd()))

# Importer et lancer l'application
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QFont
    from src.views import LoginWindow, MainWindow
    from src.utils import get_logger
    
    logger = get_logger()
    
    # Créer l'application Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Auto-École Manager")
    app.setOrganizationName("AutoEcole")
    
    # Style
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    app.setStyle("Fusion")
    
    # Fenêtre de connexion
    login_window = LoginWindow()
    
    def on_login_success(user):
        logger.info(f"Connexion réussie : {user.username}")
        try:
            main_window = MainWindow(user)
            main_window.show()
            print(f"\n✅ Application démarrée pour : {user.full_name}")
        except Exception as e:
            print(f"\n❌ Erreur : {e}")
            import traceback
            traceback.print_exc()
    
    login_window.login_successful.connect(on_login_success)
    login_window.show()
    
    print("\n✅ Fenêtre de connexion affichée")
    print("   Login : admin / Admin123!")
    print()
    
    sys.exit(app.exec())
    
except Exception as e:
    print(f"\n❌ ERREUR CRITIQUE : {e}")
    import traceback
    traceback.print_exc()
    input("\nAppuyez sur Entrée pour quitter...")
    sys.exit(1)
