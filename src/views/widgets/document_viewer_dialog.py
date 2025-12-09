"""
Dialogue pour visualiser un document
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QMessageBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QPixmap, QDesktopServices

from src.controllers import DocumentController
from src.models import DocumentStatus
from src.utils.auth import get_current_user
import os


class DocumentViewerDialog(QDialog):
    """Dialogue pour visualiser les détails d'un document"""
    
    def __init__(self, document_id: int, parent=None):
        super().__init__(parent)
        self.document_id = document_id
        self.document = None
        self.setWindowTitle("📄 Détail Document")
        self.setMinimumSize(700, 600)
        self.load_document()
        self.setup_ui()
    
    def load_document(self):
        """Charger le document"""
        try:
            self.document = DocumentController.get_document_by_id(self.document_id)
            if not self.document:
                QMessageBox.critical(self, "Erreur", "Document non trouvé")
                self.reject()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement: {e}")
            self.reject()
    
    def setup_ui(self):
        """Configurer l'interface"""
        if not self.document:
            return
        
        layout = QVBoxLayout(self)
        
        # Header avec titre
        header = QLabel(f"📄 {self.document.title}")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("padding: 15px; background-color: #ecf0f1; border-radius: 5px;")
        layout.addWidget(header)
        
        # Informations du document
        info_group = QGroupBox("Informations")
        info_layout = QFormLayout(info_group)
        
        info_layout.addRow("ID:", QLabel(str(self.document.id)))
        info_layout.addRow("Type:", QLabel(self.document.document_type.value))
        info_layout.addRow("Statut:", self.create_status_label())
        
        if self.document.reference_number:
            info_layout.addRow("Référence:", QLabel(self.document.reference_number))
        
        if self.document.entity_id:
            entity_text = f"{self.document.entity_type}/{self.document.entity_id}"
            info_layout.addRow("Entité:", QLabel(entity_text))
        
        if self.document.issue_date:
            info_layout.addRow("Date d'émission:", QLabel(self.document.issue_date.strftime("%d/%m/%Y")))
        
        if self.document.expiry_date:
            expiry_label = QLabel(self.document.expiry_date.strftime("%d/%m/%Y"))
            # Vérifier si expiré
            from datetime import datetime
            if self.document.expiry_date < datetime.now().date():
                expiry_label.setStyleSheet("color: red; font-weight: bold;")
                expiry_label.setText(expiry_label.text() + " ⚠️ EXPIRÉ")
            info_layout.addRow("Date d'expiration:", expiry_label)
        
        if self.document.tags:
            tags_label = QLabel(self.document.tags)
            tags_label.setStyleSheet("color: #3498db;")
            info_layout.addRow("Tags:", tags_label)
        
        layout.addWidget(info_group)
        
        # Fichier
        file_group = QGroupBox("Fichier")
        file_layout = QFormLayout(file_group)
        
        file_layout.addRow("Nom:", QLabel(self.document.file_name or "N/A"))
        
        if self.document.file_size:
            size_mb = self.document.file_size / (1024 * 1024)
            file_layout.addRow("Taille:", QLabel(f"{size_mb:.2f} MB"))
        
        if self.document.mime_type:
            file_layout.addRow("Type MIME:", QLabel(self.document.mime_type))
        
        layout.addWidget(file_group)
        
        # Description
        if self.document.description:
            desc_group = QGroupBox("Description")
            desc_layout = QVBoxLayout(desc_group)
            desc_text = QTextEdit()
            desc_text.setPlainText(self.document.description)
            desc_text.setReadOnly(True)
            desc_text.setMaximumHeight(100)
            desc_layout.addWidget(desc_text)
            layout.addWidget(desc_group)
        
        # Dates de création/modification
        dates_group = QGroupBox("Dates")
        dates_layout = QFormLayout(dates_group)
        
        if self.document.created_at:
            dates_layout.addRow("Créé le:", QLabel(self.document.created_at.strftime("%d/%m/%Y %H:%M")))
        
        if self.document.created_by:
            dates_layout.addRow("Créé par:", QLabel(self.document.created_by))
        
        if self.document.verified:
            verified_label = QLabel("✅ Oui")
            verified_label.setStyleSheet("color: green; font-weight: bold;")
            dates_layout.addRow("Vérifié:", verified_label)
            
            if self.document.verified_by:
                dates_layout.addRow("Vérifié par:", QLabel(self.document.verified_by))
            
            if self.document.verified_at:
                dates_layout.addRow("Vérifié le:", QLabel(self.document.verified_at.strftime("%d/%m/%Y %H:%M")))
        
        layout.addWidget(dates_group)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        
        # Bouton Ouvrir fichier
        if self.document.file_path and os.path.exists(self.document.file_path):
            open_btn = QPushButton("📂 Ouvrir le Fichier")
            open_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            open_btn.clicked.connect(self.open_file)
            button_layout.addWidget(open_btn)
        
        # Bouton Vérifier
        if not self.document.verified:
            verify_btn = QPushButton("✅ Marquer comme Vérifié")
            verify_btn.setStyleSheet("""
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
            verify_btn.clicked.connect(self.verify_document)
            button_layout.addWidget(verify_btn)
        
        button_layout.addStretch()
        
        # Bouton Fermer
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def create_status_label(self):
        """Créer le label de statut avec couleur"""
        label = QLabel(self.document.status.value)
        
        colors = {
            DocumentStatus.ACTIVE: "#27ae60",
            DocumentStatus.EXPIRED: "#e74c3c",
            DocumentStatus.PENDING_VALIDATION: "#f39c12",
            DocumentStatus.VALIDATED: "#3498db",
            DocumentStatus.REJECTED: "#c0392b",
            DocumentStatus.ARCHIVED: "#95a5a6",
        }
        
        color = colors.get(self.document.status, "#000000")
        label.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        return label
    
    def open_file(self):
        """Ouvrir le fichier avec l'application par défaut"""
        try:
            if self.document.file_path and os.path.exists(self.document.file_path):
                url = QUrl.fromLocalFile(self.document.file_path)
                QDesktopServices.openUrl(url)
            else:
                QMessageBox.warning(self, "Erreur", "Fichier introuvable")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le fichier:\n{e}")
    
    def _get_current_username(self) -> str:
        """Récupérer le nom d'utilisateur actuel"""
        user = get_current_user()
        return user.full_name if user and user.full_name else (user.username if user else "Système")
    
    def verify_document(self):
        """Marquer le document comme vérifié"""
        try:
            success = DocumentController.verify_document(
                self.document_id,
                verified_by=self._get_current_username()
            )
            
            if success:
                QMessageBox.information(self, "Succès", "Document marqué comme vérifié!")
                self.accept()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de vérifier le document")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {e}")
