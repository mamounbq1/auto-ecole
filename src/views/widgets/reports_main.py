"""
Module: Widget principal des rapports
Version: 1.0.0 - Créé le 2025-12-08

Description:
    Widget principal avec dashboard de rapports complet:
    - Analyses multi-modules
    - Graphiques matplotlib
    - KPIs globaux
    - Exports
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from src.views.widgets.reports_dashboard import ReportsDashboard


class ReportsMainWidget(QWidget):
    """Widget principal des rapports"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Configuration de l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Dashboard unique
        self.dashboard = ReportsDashboard()
        layout.addWidget(self.dashboard)
    
    def refresh(self):
        """Rafraîchir les rapports"""
        self.dashboard.load_reports()
