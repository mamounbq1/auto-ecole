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
from .vehicles_widget import VehiclesWidget
from .exams_widget import ExamsWidget

# Les widgets avec matplotlib sont importés dynamiquement:
# - DashboardAdvancedWidget (dashboard avec graphiques)
# - ReportsWidget (rapports avec graphiques)

__all__ = [
    'DashboardSimpleWidget',
    'StudentsEnhancedWidget',
    'PaymentsEnhancedWidget',
    'PaymentsMainWidget',  # NEW: Module Paiements complet
    'PlanningEnhancedWidget',
    'InstructorsWidget',
    'VehiclesWidget',
    'ExamsWidget',
    # 'DashboardAdvancedWidget',  # Import dynamique
    # 'ReportsWidget',  # Import dynamique
]
