"""
Dashboard des documents avec statistiques et alertes
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QListWidget, QListWidgetItem, QPushButton,
    QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

from src.controllers import DocumentController
from src.models import DocumentStatus, DocumentType
from datetime import datetime, timedelta


class DocumentsDashboardWidget(QWidget):
    """Dashboard avec statistiques des documents"""
    
    document_selected = Signal(int)  # Signal pour sélectionner un document
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.refresh_statistics()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Titre
        title = QLabel("📊 Statistiques Documents")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Grid de statistiques
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)
        
        # Cards de statistiques
        self.total_card = self.create_stat_card("📄 Total Documents", "0", "#3498db")
        self.verified_card = self.create_stat_card("✅ Vérifiés", "0", "#27ae60")
        self.expired_card = self.create_stat_card("❌ Expirés", "0", "#e74c3c")
        self.expiring_card = self.create_stat_card("⚠️ Expirant Bientôt", "0", "#f39c12")
        
        stats_grid.addWidget(self.total_card, 0, 0)
        stats_grid.addWidget(self.verified_card, 0, 1)
        stats_grid.addWidget(self.expired_card, 0, 2)
        stats_grid.addWidget(self.expiring_card, 0, 3)
        
        layout.addLayout(stats_grid)
        
        # Zone d'alertes et listes
        content_layout = QHBoxLayout()
        
        # Documents expirés
        expired_group = self.create_document_list_group(
            "❌ Documents Expirés",
            "expired_list"
        )
        content_layout.addWidget(expired_group)
        
        # Documents expirant bientôt
        expiring_group = self.create_document_list_group(
            "⚠️ Documents Expirant dans 30 jours",
            "expiring_list"
        )
        content_layout.addWidget(expiring_group)
        
        layout.addLayout(content_layout)
        
        # Statistiques par type
        type_stats_group = QGroupBox("📋 Répartition par Type")
        type_stats_layout = QVBoxLayout(type_stats_group)
        self.type_stats_list = QListWidget()
        self.type_stats_list.setMaximumHeight(200)
        type_stats_layout.addWidget(self.type_stats_list)
        layout.addWidget(type_stats_group)
    
    def create_stat_card(self, title: str, value: str, color: str):
        """Créer une card de statistique"""
        card = QFrame()
        card.setObjectName("statCard")
        card.setStyleSheet(f"""
            #statCard {{
                background-color: white;
                border-left: 5px solid {color};
                border-radius: 10px;
                padding: 15px;
            }}
            #statCard:hover {{
                background-color: #f8f9fa;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12))
        title_label.setStyleSheet("color: #7f8c8d;")
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 28, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setObjectName("statValue")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        # Stocker la référence au label de valeur
        card.value_label = value_label
        
        return card
    
    def create_document_list_group(self, title: str, list_name: str):
        """Créer un groupe avec liste de documents"""
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        
        list_widget = QListWidget()
        list_widget.setObjectName(list_name)
        list_widget.itemDoubleClicked.connect(self.on_document_selected)
        layout.addWidget(list_widget)
        
        # Stocker la référence
        setattr(self, list_name, list_widget)
        
        return group
    
    def refresh_statistics(self):
        """Rafraîchir les statistiques"""
        try:
            # Obtenir les statistiques
            stats = DocumentController.get_document_statistics()
            
            # Mettre à jour les cards
            self.total_card.value_label.setText(str(stats.get('total', 0)))
            self.verified_card.value_label.setText(str(stats.get('verified', 0)))
            self.expired_card.value_label.setText(str(stats.get('expired', 0)))
            self.expiring_card.value_label.setText(str(stats.get('expiring_soon', 0)))
            
            # Rafraîchir les listes
            self.refresh_expired_list()
            self.refresh_expiring_list()
            self.refresh_type_statistics(stats)
            
        except Exception as e:
            print(f"Erreur refresh statistics: {e}")
    
    def refresh_expired_list(self):
        """Rafraîchir la liste des documents expirés"""
        self.expired_list.clear()
        
        try:
            expired_docs = DocumentController.get_expired_documents()
            
            for doc in expired_docs[:10]:  # Limiter à 10
                item = QListWidgetItem(f"📄 {doc.title} ({doc.document_type.value})")
                item.setData(Qt.UserRole, doc.id)
                item.setToolTip(f"Expiré le {doc.expiry_date.strftime('%d/%m/%Y')}")
                item.setForeground(QColor("#e74c3c"))
                self.expired_list.addItem(item)
            
            if not expired_docs:
                item = QListWidgetItem("✅ Aucun document expiré")
                item.setForeground(QColor("#27ae60"))
                self.expired_list.addItem(item)
                
        except Exception as e:
            print(f"Erreur refresh expired list: {e}")
    
    def refresh_expiring_list(self):
        """Rafraîchir la liste des documents expirant bientôt"""
        self.expiring_list.clear()
        
        try:
            expiring_docs = DocumentController.get_expiring_documents(days=30)
            
            for doc in expiring_docs[:10]:  # Limiter à 10
                days_left = (doc.expiry_date - datetime.now().date()).days
                item = QListWidgetItem(
                    f"⚠️ {doc.title} ({doc.document_type.value}) - {days_left}j restants"
                )
                item.setData(Qt.UserRole, doc.id)
                item.setToolTip(f"Expire le {doc.expiry_date.strftime('%d/%m/%Y')}")
                item.setForeground(QColor("#f39c12"))
                self.expiring_list.addItem(item)
            
            if not expiring_docs:
                item = QListWidgetItem("✅ Aucun document expirant bientôt")
                item.setForeground(QColor("#27ae60"))
                self.expiring_list.addItem(item)
                
        except Exception as e:
            print(f"Erreur refresh expiring list: {e}")
    
    def refresh_type_statistics(self, stats: dict):
        """Rafraîchir les statistiques par type"""
        self.type_stats_list.clear()
        
        by_type = stats.get('by_type', {})
        
        # Trier par nombre de documents
        sorted_types = sorted(by_type.items(), key=lambda x: x[1], reverse=True)
        
        for doc_type, count in sorted_types[:15]:  # Top 15
            item = QListWidgetItem(f"📋 {doc_type}: {count} document(s)")
            self.type_stats_list.addItem(item)
        
        if not sorted_types:
            item = QListWidgetItem("Aucun document disponible")
            item.setForeground(QColor("#95a5a6"))
            self.type_stats_list.addItem(item)
    
    def on_document_selected(self, item: QListWidgetItem):
        """Gérer la sélection d'un document"""
        doc_id = item.data(Qt.UserRole)
        if doc_id:
            self.document_selected.emit(doc_id)
