"""
Dialog pour uploader/ajouter un document pour un élève
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTextEdit, QFileDialog, QMessageBox,
    QDateEdit, QCheckBox, QFormLayout, QGroupBox
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont
from datetime import datetime, date
import os

from src.models import DocumentType, DocumentStatus
from src.controllers.document_controller import DocumentController


class DocumentUploadDialog(QDialog):
    """Dialog pour ajouter/modifier un document"""
    
    document_saved = Signal()
    
    def __init__(self, student_id, document=None, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.document = document
        self.selected_file = None
        
        self.setWindowTitle("📄 Ajouter un Document" if not document else "📄 Modifier le Document")
        self.setMinimumSize(600, 500)
        self.setup_ui()
        
        if document:
            self.load_document_data()
    
    def setup_ui(self):
        """Configuration de l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        title = QLabel("📄 Nouveau Document" if not self.document else "📄 Modifier le Document")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
        layout.addWidget(title)
        
        # Formulaire
        form_group = QGroupBox("Informations du Document")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(12)
        
        # Style des inputs
        input_style = """
            QLineEdit, QComboBox, QTextEdit, QDateEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDateEdit:focus {
                border-color: #2196F3;
            }
        """
        
        # Titre du document
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Ex: Carte d'identité, Certificat médical...")
        self.title_input.setStyleSheet(input_style)
        form_layout.addRow("Titre*:", self.title_input)
        
        # Type de document
        self.type_combo = QComboBox()
        self.type_combo.setStyleSheet(input_style)
        self.type_combo.addItem("Carte d'Identité (CIN)", DocumentType.CIN.value)
        self.type_combo.addItem("Passeport", DocumentType.PASSPORT.value)
        self.type_combo.addItem("Acte de Naissance", DocumentType.BIRTH_CERTIFICATE.value)
        self.type_combo.addItem("Certificat Médical", DocumentType.MEDICAL_CERTIFICATE.value)
        self.type_combo.addItem("Photo d'Identité", DocumentType.PHOTO.value)
        self.type_combo.addItem("Certificat de Résidence", DocumentType.RESIDENCE_CERTIFICATE.value)
        self.type_combo.addItem("Copie Permis", DocumentType.LICENSE_COPY.value)
        self.type_combo.addItem("Signature", DocumentType.SIGNATURE.value)
        self.type_combo.addItem("Contrat", DocumentType.CONTRACT.value)
        self.type_combo.addItem("Preuve de Paiement", DocumentType.PAYMENT_PROOF.value)
        self.type_combo.addItem("Autre", DocumentType.OTHER.value)
        form_layout.addRow("Type*:", self.type_combo)
        
        # Fichier
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Aucun fichier sélectionné")
        self.file_label.setStyleSheet("color: #666; font-size: 11px;")
        file_layout.addWidget(self.file_label)
        
        browse_btn = QPushButton("📁 Parcourir")
        browse_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        
        form_layout.addRow("Fichier:", file_layout)
        
        # Date d'expiration
        self.expiry_check = QCheckBox("Ce document a une date d'expiration")
        self.expiry_check.stateChanged.connect(self.toggle_expiry_date)
        form_layout.addRow("", self.expiry_check)
        
        self.expiry_date = QDateEdit()
        self.expiry_date.setCalendarPopup(True)
        self.expiry_date.setDate(QDate.currentDate().addYears(1))
        self.expiry_date.setStyleSheet(input_style)
        self.expiry_date.setEnabled(False)
        form_layout.addRow("Date d'expiration:", self.expiry_date)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Description ou notes sur ce document...")
        self.description_input.setMaximumHeight(80)
        self.description_input.setStyleSheet(input_style)
        form_layout.addRow("Description:", self.description_input)
        
        # Document requis
        self.required_check = QCheckBox("Document obligatoire")
        form_layout.addRow("", self.required_check)
        
        layout.addWidget(form_group)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #d32f2f;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        save_btn.clicked.connect(self.save_document)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def toggle_expiry_date(self, state):
        """Activer/désactiver le champ date d'expiration"""
        self.expiry_date.setEnabled(state == Qt.Checked)
    
    def browse_file(self):
        """Ouvrir le dialog de sélection de fichier"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un document",
            "",
            "Tous les fichiers (*.*);;PDF (*.pdf);;Images (*.png *.jpg *.jpeg);;Word (*.doc *.docx)"
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.file_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 11px;")
    
    def load_document_data(self):
        """Charger les données du document en mode édition"""
        if not self.document:
            return
        
        self.title_input.setText(self.document.title)
        
        # Sélectionner le type
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == self.document.document_type.value:
                self.type_combo.setCurrentIndex(i)
                break
        
        # Date d'expiration
        if self.document.expiry_date:
            self.expiry_check.setChecked(True)
            self.expiry_date.setDate(QDate(
                self.document.expiry_date.year,
                self.document.expiry_date.month,
                self.document.expiry_date.day
            ))
        
        # Description
        if self.document.description:
            self.description_input.setPlainText(self.document.description)
        
        # Requis
        self.required_check.setChecked(self.document.is_required)
        
        # Fichier
        if self.document.file_name:
            self.file_label.setText(f"Fichier actuel: {self.document.file_name}")
            self.file_label.setStyleSheet("color: #666; font-size: 11px;")
    
    def save_document(self):
        """Enregistrer le document"""
        # Validation
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Validation", "Le titre est obligatoire")
            return
        
        if not self.document and not self.selected_file:
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner un fichier")
            return
        
        try:
            # Récupérer les données
            doc_type = DocumentType(self.type_combo.currentData())
            
            expiry_date = None
            if self.expiry_check.isChecked():
                qdate = self.expiry_date.date()
                expiry_date = date(qdate.year(), qdate.month(), qdate.day())
            
            description = self.description_input.toPlainText().strip() or None
            is_required = self.required_check.isChecked()
            
            if self.document:
                # Mise à jour
                DocumentController.update_document(
                    self.document.id,
                    title=title,
                    document_type=doc_type,
                    expiry_date=expiry_date,
                    description=description,
                    is_required=is_required
                )
                
                # Si nouveau fichier sélectionné, le mettre à jour
                if self.selected_file:
                    # TODO: Gérer le remplacement du fichier
                    pass
                
                QMessageBox.information(self, "Succès", "Document modifié avec succès!")
            else:
                # Création
                document = DocumentController.create_document(
                    student_id=self.student_id,
                    title=title,
                    document_type=doc_type,
                    file_path=self.selected_file,
                    expiry_date=expiry_date,
                    description=description,
                    is_required=is_required
                )
                
                if document:
                    QMessageBox.information(self, "Succès", "Document ajouté avec succès!")
                else:
                    QMessageBox.critical(self, "Erreur", "Erreur lors de l'ajout du document")
                    return
            
            self.document_saved.emit()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
