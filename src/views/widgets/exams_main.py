"""
Module: Widget principal des examens
Version: 1.0.0 - Créé le 2025-12-08

Description:
    Widget principal avec navigation par onglets:
    - Onglet 1: Dashboard (statistiques et analyses)
    - Onglet 2: Gestion (tableau CRUD complet)
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtGui import QFont

from src.views.widgets.exams_dashboard import ExamsDashboard
from src.views.widgets.exams_management import ExamsManagement


class ExamsMainWidget(QWidget):
    """Widget principal des examens avec onglets"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Configuration de l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Segoe UI", 11))
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
            }
            QTabBar::tab {
                background: #f5f7fa;
                color: #666;
                padding: 12px 30px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: white;
                color: #2196F3;
            }
            QTabBar::tab:hover {
                background: #e8eaf6;
            }
        """)
        
        # Ajouter les onglets (Gestion en premier)
        self.dashboard = ExamsDashboard()
        self.management = ExamsManagement()
        
        self.tabs.addTab(self.management, "📝 Gestion des Examens")
        self.tabs.addTab(self.dashboard, "📊 Tableau de Bord")
        
        layout.addWidget(self.tabs)
    
    def on_tab_changed(self, index):
        """Rafraîchir les données lors du changement d'onglet"""
        if index == 0:
            # Management (en premier)
            self.management.load_exams()
        elif index == 1:
            # Dashboard (en deuxième)
            self.dashboard.load_stats()
