"""
Widgets réutilisables pour l'interface PySide6

Note: Les imports sont faits dynamiquement dans main_window.py
pour éviter de charger matplotlib au démarrage si pas nécessaire
"""

# Import des widgets sans matplotlib (chargement rapide)
from .dashboard_professional import DashboardProfessionalWidget
from .students_enhanced import StudentsEnhancedWidget
from .planning_enhanced import PlanningEnhancedWidget
from .payments_main import PaymentsMainWidget  # Module Paiements complet
from .instructors_main import InstructorsMainWidget  # Module Moniteurs complet
from .vehicles_main import VehiclesMainWidget  # Module Véhicules complet
from .exams_main import ExamsMainWidget  # Module Examens complet
from .settings_widget import SettingsWidget  # Module Paramètres complet

# Les widgets avec matplotlib sont importés dynamiquement dans main_window.py:
# - DashboardAdvancedWidget (REMOVED - unused)
# - ReportsWidget (REMOVED - unused)
# - ReportsMainWidget (reports avec graphiques)

__all__ = [
    # Main widgets (used in main_window.py)
    'DashboardProfessionalWidget',
    'StudentsEnhancedWidget',
    'PlanningEnhancedWidget',
    'PaymentsMainWidget',
    'InstructorsMainWidget',
    'VehiclesMainWidget',
    'ExamsMainWidget',
    'SettingsWidget',
    # 'ReportsMainWidget',  # Import dynamique (matplotlib)
]
