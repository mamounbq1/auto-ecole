"""
Dialogue pour uploader un document
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QTextEdit, QDateEdit,
    QFileDialog, QMessageBox, QSpinBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from src.controllers import DocumentController
from src.models import DocumentType
from datetime import datetime


class DocumentUploadDialog(QDialog):
    """Dialogue pour uploader un document"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file = None
        self.setWindowTitle("⬆️ Upload Document")
        self.setMinimumSize(600, 600)
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("📄 Upload d'un Nouveau Document")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Formulaire
        form = QFormLayout()
        form.setSpacing(15)
        
        # Sélection de fichier
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Aucun fichier sélectionné")
        self.file_label.setStyleSheet("color: #95a5a6; font-style: italic;")
        file_layout.addWidget(self.file_label, 1)
        
        select_file_btn = QPushButton("📁 Parcourir...")
        select_file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(select_file_btn)
        
        form.addRow("Fichier*:", file_layout)
        
        # Titre du document
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Ex: Carte d'identité de Mohammed")
        form.addRow("Titre*:", self.title_input)
        
        # Type de document
        self.type_combo = QComboBox()
        for doc_type in DocumentType:
            self.type_combo.addItem(doc_type.value, doc_type)
        form.addRow("Type de Document*:", self.type_combo)
        
        # Type d'entité (Student, Vehicle, etc.)
        self.entity_type_combo = QComboBox()
        self.entity_type_combo.addItems([
            "student", "instructor", "vehicle", "exam", "payment", "session", "other"
        ])
        form.addRow("Type d'Entité:", self.entity_type_combo)
        
        # ID de l'entité
        self.entity_id_input = QSpinBox()
        self.entity_id_input.setMinimum(0)
        self.entity_id_input.setMaximum(999999)
        self.entity_id_input.setSpecialValueText("Aucune entité")
        form.addRow("ID de l'Entité:", self.entity_id_input)
        
        # Numéro de référence
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Ex: AB123456")
        form.addRow("Numéro de Référence:", self.reference_input)
        
        # Date d'émission
        self.issue_date = QDateEdit()
        self.issue_date.setCalendarPopup(True)
        self.issue_date.setDate(QDate.currentDate())
        form.addRow("Date d'Émission:", self.issue_date)
        
        # Date d'expiration
        self.expiry_date = QDateEdit()
        self.expiry_date.setCalendarPopup(True)
        self.expiry_date.setDate(QDate.currentDate().addYears(5))
        self.expiry_date.setSpecialValueText("Pas d'expiration")
        form.addRow("Date d'Expiration:", self.expiry_date)
        
        # Tags
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Ex: identite,obligatoire,urgent (séparés par virgules)")
        form.addRow("Tags:", self.tags_input)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Description optionnelle du document...")
        form.addRow("Description:", self.description_input)
        
        layout.addLayout(form)
        
        # Informations sur les limitations
        info_label = QLabel(
            "ℹ️ Formats acceptés: PDF, JPG, PNG, DOC, DOCX, XLS, XLSX\n"
            "   Taille max: 10 MB (documents), 5 MB (images)"
        )
        info_label.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 10px;")
        layout.addWidget(info_label)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
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
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        upload_btn.clicked.connect(self.upload_document)
        button_layout.addWidget(upload_btn)
        
        layout.addLayout(button_layout)
    
    def select_file(self):
        """Sélectionner un fichier"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un document",
            "",
            "Documents (*.pdf *.jpg *.jpeg *.png *.doc *.docx *.xls *.xlsx);;All Files (*)"
        )
        
        if filename:
            self.selected_file = filename
            # Afficher seulement le nom du fichier
            import os
            self.file_label.setText(os.path.basename(filename))
            self.file_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            
            # Auto-remplir le titre si vide
            if not self.title_input.text():
                basename = os.path.basename(filename)
                title_without_ext = os.path.splitext(basename)[0]
                self.title_input.setText(title_without_ext)
    
    def upload_document(self):
        """Uploader le document"""
        # Validation
        if not self.selected_file:
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner un fichier")
            return
        
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "Validation", "Veuillez saisir un titre")
            return
        
        try:
            # Préparer les données
            doc_type = self.type_combo.currentData()
            entity_type = self.entity_type_combo.currentText()
            entity_id = self.entity_id_input.value() if self.entity_id_input.value() > 0 else None
            
            issue_date_py = self.issue_date.date().toPython()
            expiry_date_py = self.expiry_date.date().toPython() if self.expiry_date.text() != self.expiry_date.specialValueText() else None
            
            # Upload via le contrôleur
            document = DocumentController.upload_document(
                file_path=self.selected_file,
                document_type=doc_type,
                title=self.title_input.text().strip(),
                entity_type=entity_type,
                entity_id=entity_id,
                description=self.description_input.toPlainText().strip() or None,
                reference_number=self.reference_input.text().strip() or None,
                issue_date=issue_date_py,
                expiry_date=expiry_date_py,
                tags=self.tags_input.text().strip() or None,
                created_by="current_user"  # TODO: Obtenir l'utilisateur actuel
            )
            
            if document:
                self.accept()
            else:
                QMessageBox.critical(self, "Erreur", "Échec de l'upload du document")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'upload:\n{str(e)}")
