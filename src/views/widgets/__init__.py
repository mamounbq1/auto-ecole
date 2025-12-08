"""
Widgets réutilisables pour l'interface PySide6

Note: Les imports sont faits dynamiquement dans main_window.py
pour éviter de charger matplotlib au démarrage si pas nécessaire
"""

# Import des widgets sans matplotlib (chargement rapide)
from .dashboard_simple import DashboardSimpleWidget
from .students_enhanced import StudentsEnhancedWidget
from .payments_enhanced import PaymentsEnhancedWidget
from .payments_main import PaymentsMainWidget  # NEW: Module Paiements complet
from .planning_enhanced import PlanningEnhancedWidget
from .instructors_widget import InstructorsWidget
from .instructors_main import InstructorsMainWidget  # NEW: Module Moniteurs complet
from .vehicles_widget import VehiclesWidget
from .vehicles_main import VehiclesMainWidget  # NEW: Module Véhicules complet
from .exams_widget import ExamsWidget
from .exams_main import ExamsMainWidget  # NEW: Module Examens complet
from .settings_widget import SettingsWidget  # NEW: Module Paramètres complet

# Les widgets avec matplotlib sont importés dynamiquement:
# - DashboardAdvancedWidget (dashboard avec graphiques)
# - ReportsWidget (rapports avec graphiques - OLD)
# - ReportsMainWidget (rapports avec graphiques - NEW)

__all__ = [
    'DashboardSimpleWidget',
    'StudentsEnhancedWidget',
    'PaymentsEnhancedWidget',
    'PaymentsMainWidget',  # NEW: Module Paiements complet
    'PlanningEnhancedWidget',
    'InstructorsWidget',
    'InstructorsMainWidget',  # NEW: Module Moniteurs complet
    'VehiclesWidget',
    'VehiclesMainWidget',  # NEW: Module Véhicules complet
    'ExamsWidget',
    'ExamsMainWidget',  # NEW: Module Examens complet
    'SettingsWidget',  # NEW: Module Paramètres complet
    # 'DashboardAdvancedWidget',  # Import dynamique
    # 'ReportsWidget',  # Import dynamique (OLD)
    # 'ReportsMainWidget',  # Import dynamique (NEW)
]
