"""
Dialog pour visualiser un document
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox, QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
import os
import subprocess
import platform

from src.controllers.document_controller import DocumentController


class DocumentViewerDialog(QDialog):
    """Dialog pour visualiser les détails d'un document"""
    
    def __init__(self, document_id, parent=None):
        super().__init__(parent)
        self.document_id = document_id
        self.document = DocumentController.get_document(document_id)
        
        if not self.document:
            QMessageBox.critical(self, "Erreur", "Document introuvable")
            self.reject()
            return
        
        self.setWindowTitle(f"📄 {self.document.title}")
        self.setMinimumSize(500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        """Configuration de l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        title = QLabel(f"📄 {self.document.title}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
        layout.addWidget(title)
        
        # Informations
        info_group = QGroupBox("Informations")
        info_layout = QFormLayout(info_group)
        
        # Type
        doc_type_label = QLabel(self.document.document_type.value.replace('_', ' ').title())
        info_layout.addRow("Type:", doc_type_label)
        
        # Statut
        status_map = {
            'valid': ('✅ Valide', '#4CAF50'),
            'expired': ('❌ Expiré', '#f44336'),
            'pending': ('⏳ En attente', '#FF9800'),
            'rejected': ('🚫 Rejeté', '#f44336')
        }
        status_text, status_color = status_map.get(self.document.status.value, ('', '#666'))
        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        info_layout.addRow("Statut:", status_label)
        
        # Date d'upload
        upload_label = QLabel(self.document.upload_date.strftime('%d/%m/%Y %H:%M'))
        info_layout.addRow("Date d'upload:", upload_label)
        
        # Date d'expiration
        if self.document.expiry_date:
            expiry_label = QLabel(self.document.expiry_date.strftime('%d/%m/%Y'))
            if self.document.is_expired:
                expiry_label.setStyleSheet("color: #f44336; font-weight: bold;")
            elif self.document.days_until_expiry and self.document.days_until_expiry < 30:
                expiry_label.setStyleSheet("color: #FF9800; font-weight: bold;")
            info_layout.addRow("Date d'expiration:", expiry_label)
        
        # Fichier
        if self.document.file_name:
            file_label = QLabel(self.document.file_name)
            info_layout.addRow("Fichier:", file_label)
            
            if self.document.file_size_mb:
                size_label = QLabel(f"{self.document.file_size_mb} MB")
                info_layout.addRow("Taille:", size_label)
        
        # Vérifié
        if self.document.is_verified:
            verified_text = f"✅ Oui"
            if self.document.verified_by:
                verified_text += f" (par {self.document.verified_by})"
            verified_label = QLabel(verified_text)
            verified_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            info_layout.addRow("Vérifié:", verified_label)
        
        layout.addWidget(info_group)
        
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
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        # Ouvrir fichier
        if self.document.file_path and os.path.exists(self.document.file_path):
            open_btn = QPushButton("📂 Ouvrir le fichier")
            open_btn.setStyleSheet("""
                QPushButton {
                    background: #2196F3;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #1976D2;
                }
            """)
            open_btn.clicked.connect(self.open_file)
            buttons_layout.addWidget(open_btn)
        
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Fermer")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #666;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #555;
            }
        """)
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def open_file(self):
        """Ouvrir le fichier avec l'application par défaut"""
        try:
            file_path = self.document.file_path
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "Erreur", "Le fichier n'existe pas")
                return
            
            # Ouvrir avec l'application par défaut selon l'OS
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le fichier: {str(e)}")
