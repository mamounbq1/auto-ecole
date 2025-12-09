"""
Gestion complète des documents (CRUD)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, QLabel,
    QMessageBox, QFileDialog, QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from src.controllers import DocumentController
from src.models import DocumentType, DocumentStatus
from .document_upload_dialog import DocumentUploadDialog
from .document_viewer_dialog import DocumentViewerDialog
from datetime import datetime


class DocumentsManagementWidget(QWidget):
    """Widget de gestion des documents avec CRUD complet"""
    
    document_changed = Signal()  # Signal quand un document change
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_documents = []
        self.setup_ui()
        self.load_documents()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header avec recherche et filtres
        header_layout = self.create_header()
        layout.addLayout(header_layout)
        
        # Table des documents
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Titre", "Type", "Entité", "Statut",
            "Créé le", "Expire le", "Actions"
        ])
        
        # Configuration de la table
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.cellDoubleClicked.connect(self.view_document)
        
        layout.addWidget(self.table)
        
        # Footer avec statistiques
        footer = QLabel("Total: 0 document(s)")
        footer.setObjectName("footerLabel")
        self.footer_label = footer
        layout.addWidget(footer)
    
    def create_header(self):
        """Créer le header avec recherche et filtres"""
        layout = QHBoxLayout()
        
        # Bouton Upload
        upload_btn = QPushButton("⬆️ Upload Document")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        upload_btn.setCursor(Qt.PointingHandCursor)
        upload_btn.clicked.connect(self.upload_document)
        layout.addWidget(upload_btn)
        
        # Recherche
        search_label = QLabel("🔍 Rechercher:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Titre, référence...")
        self.search_input.textChanged.connect(self.filter_documents)
        layout.addWidget(search_label)
        layout.addWidget(self.search_input)
        
        # Filtre par type
        type_label = QLabel("Type:")
        self.type_filter = QComboBox()
        self.type_filter.addItem("Tous les types", None)
        for doc_type in DocumentType:
            self.type_filter.addItem(doc_type.value, doc_type)
        self.type_filter.currentIndexChanged.connect(self.filter_documents)
        layout.addWidget(type_label)
        layout.addWidget(self.type_filter)
        
        # Filtre par statut
        status_label = QLabel("Statut:")
        self.status_filter = QComboBox()
        self.status_filter.addItem("Tous les statuts", None)
        for status in DocumentStatus:
            self.status_filter.addItem(status.value, status)
        self.status_filter.currentIndexChanged.connect(self.filter_documents)
        layout.addWidget(status_label)
        layout.addWidget(self.status_filter)
        
        # Bouton Rafraîchir
        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Rafraîchir la liste")
        refresh_btn.clicked.connect(self.load_documents)
        layout.addWidget(refresh_btn)
        
        # Bouton Export
        export_btn = QPushButton("📤 Export CSV")
        export_btn.clicked.connect(self.export_to_csv)
        layout.addWidget(export_btn)
        
        return layout
    
    def load_documents(self):
        """Charger tous les documents"""
        try:
            # Obtenir tous les documents
            documents = DocumentController.search_documents()
            self.current_documents = documents
            self.display_documents(documents)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement documents: {e}")
    
    def display_documents(self, documents):
        """Afficher les documents dans la table"""
        self.table.setRowCount(0)
        
        for row, doc in enumerate(documents):
            self.table.insertRow(row)
            
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(doc.id)))
            
            # Titre
            title_item = QTableWidgetItem(doc.title)
            title_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.table.setItem(row, 1, title_item)
            
            # Type
            self.table.setItem(row, 2, QTableWidgetItem(doc.document_type.value))
            
            # Entité
            entity_text = f"{doc.entity_type}/{doc.entity_id}" if doc.entity_id else "N/A"
            self.table.setItem(row, 3, QTableWidgetItem(entity_text))
            
            # Statut
            status_item = QTableWidgetItem(doc.status.value)
            status_item.setForeground(self.get_status_color(doc.status))
            self.table.setItem(row, 4, status_item)
            
            # Créé le
            created_text = doc.created_at.strftime("%d/%m/%Y") if doc.created_at else ""
            self.table.setItem(row, 5, QTableWidgetItem(created_text))
            
            # Expire le
            expiry_text = doc.expiry_date.strftime("%d/%m/%Y") if doc.expiry_date else "N/A"
            expiry_item = QTableWidgetItem(expiry_text)
            
            # Colorer si expiré ou expirant bientôt
            if doc.expiry_date:
                today = datetime.now().date()
                if doc.expiry_date < today:
                    expiry_item.setForeground(QColor("#e74c3c"))
                    expiry_item.setFont(QFont("Arial", 9, QFont.Bold))
                elif (doc.expiry_date - today).days <= 30:
                    expiry_item.setForeground(QColor("#f39c12"))
            
            self.table.setItem(row, 6, expiry_item)
            
            # Actions
            actions_widget = self.create_actions_widget(doc)
            self.table.setCellWidget(row, 7, actions_widget)
        
        # Ajuster les colonnes
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        
        # Mettre à jour le footer
        self.footer_label.setText(f"Total: {len(documents)} document(s)")
    
    def create_actions_widget(self, document):
        """Créer les boutons d'actions pour un document"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Bouton Voir
        view_btn = QPushButton("👁️")
        view_btn.setToolTip("Voir le document")
        view_btn.setMaximumWidth(30)
        view_btn.clicked.connect(lambda: self.view_document_by_id(document.id))
        layout.addWidget(view_btn)
        
        # Bouton Supprimer
        delete_btn = QPushButton("🗑️")
        delete_btn.setToolTip("Supprimer")
        delete_btn.setMaximumWidth(30)
        delete_btn.setStyleSheet("QPushButton { color: #e74c3c; }")
        delete_btn.clicked.connect(lambda: self.delete_document(document.id))
        layout.addWidget(delete_btn)
        
        return widget
    
    def get_status_color(self, status: DocumentStatus):
        """Obtenir la couleur selon le statut"""
        colors = {
            DocumentStatus.ACTIVE: QColor("#27ae60"),
            DocumentStatus.EXPIRED: QColor("#e74c3c"),
            DocumentStatus.PENDING_VALIDATION: QColor("#f39c12"),
            DocumentStatus.VALIDATED: QColor("#3498db"),
            DocumentStatus.REJECTED: QColor("#c0392b"),
            DocumentStatus.ARCHIVED: QColor("#95a5a6"),
        }
        return colors.get(status, QColor("#000000"))
    
    def filter_documents(self):
        """Filtrer les documents selon les critères"""
        search_text = self.search_input.text().lower()
        doc_type = self.type_filter.currentData()
        status = self.status_filter.currentData()
        
        filtered = self.current_documents
        
        # Filtrer par recherche
        if search_text:
            filtered = [
                doc for doc in filtered
                if search_text in doc.title.lower() or
                   (doc.reference_number and search_text in doc.reference_number.lower())
            ]
        
        # Filtrer par type
        if doc_type:
            filtered = [doc for doc in filtered if doc.document_type == doc_type]
        
        # Filtrer par statut
        if status:
            filtered = [doc for doc in filtered if doc.status == status]
        
        self.display_documents(filtered)
    
    def upload_document(self):
        """Ouvrir le dialogue d'upload"""
        dialog = DocumentUploadDialog(parent=self)
        if dialog.exec():
            self.load_documents()
            self.document_changed.emit()
            QMessageBox.information(self, "Succès", "Document uploadé avec succès!")
    
    def view_document(self, row, col):
        """Voir un document (double-clic)"""
        doc_id = int(self.table.item(row, 0).text())
        self.view_document_by_id(doc_id)
    
    def view_document_by_id(self, doc_id: int):
        """Voir un document par son ID"""
        dialog = DocumentViewerDialog(doc_id, self)
        dialog.exec()
    
    def delete_document(self, doc_id: int):
        """Supprimer un document"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer ce document?\n"
            "Le fichier sera également supprimé du disque.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = DocumentController.delete_document(doc_id, delete_file=True)
                if success:
                    QMessageBox.information(self, "Succès", "Document supprimé!")
                    self.load_documents()
                    self.document_changed.emit()
                else:
                    QMessageBox.warning(self, "Erreur", "Impossible de supprimer le document")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur suppression: {e}")
    
    def show_context_menu(self, position):
        """Afficher le menu contextuel"""
        row = self.table.rowAt(position.y())
        if row < 0:
            return
        
        doc_id = int(self.table.item(row, 0).text())
        
        menu = QMenu(self)
        
        view_action = menu.addAction("👁️ Voir le document")
        verify_action = menu.addAction("✅ Marquer comme vérifié")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Supprimer")
        delete_action.setStyleSheet("color: #e74c3c;")
        
        action = menu.exec(self.table.viewport().mapToGlobal(position))
        
        if action == view_action:
            self.view_document_by_id(doc_id)
        elif action == verify_action:
            self.verify_document(doc_id)
        elif action == delete_action:
            self.delete_document(doc_id)
    
    def verify_document(self, doc_id: int):
        """Marquer un document comme vérifié"""
        try:
            success = DocumentController.verify_document(doc_id, verified_by="admin")
            if success:
                QMessageBox.information(self, "Succès", "Document marqué comme vérifié!")
                self.load_documents()
                self.document_changed.emit()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de vérifier le document")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur vérification: {e}")
    
    def export_to_csv(self):
        """Exporter les documents en CSV"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Exporter les documents",
                f"documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if filename:
                # Récupérer les documents filtrés actuels
                documents = []
                for row in range(self.table.rowCount()):
                    doc_id = self.table.item(row, 0).data(Qt.UserRole)
                    if doc_id:
                        doc = DocumentController.get_document(doc_id)
                        if doc:
                            documents.append(doc)
                
                # Exporter via le contrôleur
                success, result = DocumentController.export_to_csv(documents, filename)
                
                if success:
                    QMessageBox.information(
                        self,
                        "✅ Export réussi",
                        f"{len(documents)} documents exportés vers:\n{result}"
                    )
                else:
                    QMessageBox.warning(self, "⚠️ Erreur", f"Erreur lors de l'export:\n{result}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
