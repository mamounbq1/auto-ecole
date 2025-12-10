"""
Instructors Main Widget - Widget principal du module Moniteurs
Combine Dashboard et Gestion avec navigation par onglets
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from .instructors_dashboard import InstructorsDashboard
from .instructors_management import InstructorsManagement


class InstructorsMainWidget(QWidget):
    """Widget principal du module Moniteurs avec onglets"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Créer le widget à onglets
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #f5f6fa;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 12px 30px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #3498db;
            }
            QTabBar::tab:hover {
                background-color: #d5e8f7;
            }
        """)
        
        # Onglet Gestion (en premier)
        self.management = InstructorsManagement()
        self.tabs.addTab(self.management, "👨‍🏫 Gestion des Moniteurs")
        
        # Onglet Dashboard (en deuxième)
        self.dashboard = InstructorsDashboard()
        self.tabs.addTab(self.dashboard, "📊 Dashboard Moniteurs")
        
        layout.addWidget(self.tabs)
    
    def on_tab_changed(self, index):
        """Rafraîchir les données lors du changement d'onglet"""
        if index == 0:
            # Management (en premier)
            self.management.load_instructors()
        elif index == 1:
            # Dashboard (en deuxième)
            self.dashboard.load_all_stats()
    
    def refresh_all(self):
        """Rafraîchir tous les onglets"""
        self.dashboard.load_all_stats()
        self.management.load_instructors()
