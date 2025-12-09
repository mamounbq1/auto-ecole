"""
Module principal de gestion documentaire avec Dashboard et Gestion
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabWidget, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from .documents_dashboard import DocumentsDashboardWidget
from .documents_management import DocumentsManagementWidget


class DocumentsMainWidget(QWidget):
    """Widget principal du module Documents avec onglets Dashboard et Gestion"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Créer les widgets AVANT le header (qui les référence)
        # Onglet Dashboard
        self.dashboard_widget = DocumentsDashboardWidget()
        
        # Onglet Gestion
        self.management_widget = DocumentsManagementWidget()
        
        # Header (maintenant que management_widget existe)
        header = self.create_header()
        layout.addWidget(header)
        
        # Onglets
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        
        tabs.addTab(self.dashboard_widget, "📊 Dashboard")
        tabs.addTab(self.management_widget, "📁 Gestion Documents")
        
        layout.addWidget(tabs)
        
        # Connecter signaux pour rafraîchir dashboard après modifications
        self.management_widget.document_changed.connect(self.dashboard_widget.refresh_statistics)
    
    def create_header(self):
        """Créer le header du module"""
        header = QWidget()
        header.setObjectName("moduleHeader")
        header.setStyleSheet("""
            #moduleHeader {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                padding: 20px;
                border-bottom: 3px solid #2c3e50;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        # Titre
        title = QLabel("📄 Gestion Documentaire")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Bouton Upload rapide
        upload_btn = QPushButton("⬆️ Upload Document")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #2980b9;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ecf0f1;
            }
        """)
        upload_btn.setCursor(Qt.PointingHandCursor)
        upload_btn.clicked.connect(self.management_widget.upload_document)
        layout.addWidget(upload_btn)
        
        return header
