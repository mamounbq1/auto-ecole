"""
Formulaire d'ajout/édition élève SIMPLIFIÉ avec toutes les améliorations UX
- Mode création : Formulaire minimaliste (4 champs obligatoires)
- Mode édition : Vue complète avec onglet Résumé
- Validation temps réel
- Indicateurs visuels
- Raccourcis clavier
- Autocomplétion
- Messages toast
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox,
    QMessageBox, QDialog, QFormLayout, QDateEdit, QTextEdit, QSpinBox, 
    QDoubleSpinBox, QGroupBox, QTabWidget, QScrollArea, QFrame, QApplication,
    QSizePolicy
)
from PySide6.QtCore import Qt, QDate, QTimer, Signal, QPropertyAnimation, QRect
from PySide6.QtGui import QFont, QColor, QPalette, QKeySequence, QShortcut, QIcon
from datetime import datetime, date
import re

from src.controllers.student_controller import StudentController
from src.models import StudentStatus
from src.views.widgets.student_detail_view import StudentDetailViewDialog
from functools import partial

# Types de permis disponibles
LICENSE_TYPES = ['A', 'B', 'C', 'D', 'E']

# Montants standards configurables
STANDARD_AMOUNTS = [4000, 5000, 6000, 7000, 8000]


class ToastNotification(QFrame):
    """Notification toast moderne (coin écran)"""
    
    def __init__(self, message, type="success", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Style selon le type
        colors = {
            "success": ("#27ae60", "#ffffff"),
            "error": ("#e74c3c", "#ffffff"),
            "warning": ("#f39c12", "#ffffff"),
            "info": ("#3498db", "#ffffff")
        }
        bg_color, text_color = colors.get(type, colors["success"])
        
        icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        icon = icons.get(type, "✅")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px;")
        
        message_label = QLabel(message)
        message_label.setStyleSheet(f"color: {text_color}; font-size: 13px; font-weight: 500;")
        message_label.setWordWrap(True)
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label, stretch=1)
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 10px;
                border: none;
            }}
        """)
        
        self.setFixedWidth(350)
        self.adjustSize()
        
        # Animation de fermeture automatique
        QTimer.singleShot(3000, self.fade_out)
    
    def fade_out(self):
        """Animation de disparition"""
        self.close()
        self.deleteLater()
    
    def showEvent(self, event):
        """Position en haut à droite de l'écran"""
        super().showEvent(event)
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 20, 70)


class ValidationIndicator(QLabel):
    """Indicateur de validation temps réel (✅ / ❌)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("font-size: 16px;")
        self.set_neutral()
    
    def set_valid(self):
        self.setText("✅")
        self.setToolTip("Valide")
    
    def set_invalid(self, error=""):
        self.setText("❌")
        self.setToolTip(error or "Invalide")
    
    def set_neutral(self):
        self.setText("")
        self.setToolTip("")


class StudentFormSimplified(QDialog):
    """
    Formulaire simplifié pour ajout/édition élève
    - Mode CRÉATION : Formulaire minimaliste
    - Mode ÉDITION : Redirection vers vue complète (StudentDetailViewDialog)
    """
    
    student_saved = Signal(object)  # Émet l'élève sauvegardé
    
    def __init__(self, student=None, parent=None):
        super().__init__(parent)
        self.student = student
        self.is_editing = student is not None
        
        # Si édition, rediriger vers la vue complète
        if self.is_editing:
            self.redirect_to_full_view()
            return
        
        # Mode création : Formulaire simplifié
        self.setWindowTitle("➕ Nouvel Élève - Inscription Rapide")
        self.setMinimumSize(600, 700)
        self.setMaximumSize(700, 900)
        
        # Validation indicators
        self.validators = {}
        
        self.setup_ui()
        self.setup_shortcuts()
        self.setup_validators()
        
        # Focus sur le premier champ
        QTimer.singleShot(100, lambda: self.full_name.setFocus())
    
    def redirect_to_full_view(self):
        """Rediriger vers la vue complète en mode édition"""
        full_dialog = StudentDetailViewDialog(
            student=self.student,
            parent=self.parent(),
            read_only=False
        )
        
        if full_dialog.exec():
            self.student_saved.emit(self.student)
            self.accept()
        else:
            self.reject()
    
    def setup_ui(self):
        """Interface utilisateur simplifiée"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Header avec guide
        self.create_header(main_layout)
        
        # Formulaire principal
        form_scroll = QScrollArea()
        form_scroll.setWidgetResizable(True)
        form_scroll.setFrameShape(QScrollArea.NoFrame)
        
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(20)
        
        # Section 1 : Informations obligatoires
        self.create_required_section(form_layout)
        
        # Section 2 : Informations optionnelles (repliable)
        self.create_optional_section(form_layout)
        
        # Section 3 : Configuration de la formation
        self.create_training_section(form_layout)
        
        form_scroll.setWidget(form_widget)
        main_layout.addWidget(form_scroll)
        
        # Boutons d'action
        self.create_buttons(main_layout)
        
        # Appliquer le style global
        self.apply_style()
    
    def create_header(self, layout):
        """En-tête SANS zone bleue - simple et épuré"""
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        title = QLabel("➕ Nouvel Élève")
        title.setStyleSheet("color: #2c3e50; font-size: 20px; font-weight: bold; padding: 10px 0;")
        
        subtitle = QLabel("💡 Remplissez les 4 champs obligatoires marqués *")
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
    
    def create_required_section(self, layout):
        """Section informations obligatoires"""
        group = QGroupBox("📋 Informations Obligatoires")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #3498db;
            }
        """)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # Nom complet
        name_container = QHBoxLayout()
        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("Ex: Ahmed Bennani")
        self.full_name.textChanged.connect(lambda: self.validate_field('full_name'))
        self.full_name.setMinimumHeight(40)
        self.validators['full_name'] = ValidationIndicator()
        name_container.addWidget(self.full_name, stretch=1)
        name_container.addWidget(self.validators['full_name'])
        form_layout.addRow("📝 Nom Complet*:", name_container)
        
        # CIN
        cin_container = QHBoxLayout()
        self.cin = QLineEdit()
        self.cin.setPlaceholderText("Ex: AA123456")
        self.cin.setMaxLength(10)
        self.cin.textChanged.connect(lambda: self.validate_field('cin'))
        self.cin.setMinimumHeight(40)
        self.validators['cin'] = ValidationIndicator()
        cin_container.addWidget(self.cin, stretch=1)
        cin_container.addWidget(self.validators['cin'])
        form_layout.addRow("🆔 CIN*:", cin_container)
        
        # Date de naissance (avec calcul âge auto)
        dob_container = QHBoxLayout()
        self.date_of_birth = QDateEdit()
        self.date_of_birth.setCalendarPopup(True)
        self.date_of_birth.setDate(QDate.currentDate().addYears(-18))
        self.date_of_birth.setDisplayFormat("dd/MM/yyyy")
        self.date_of_birth.dateChanged.connect(self.update_age_display)
        self.date_of_birth.setMinimumHeight(40)
        self.age_label = QLabel("(18 ans)")
        self.age_label.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-left: 10px;")
        dob_container.addWidget(self.date_of_birth, stretch=1)
        dob_container.addWidget(self.age_label)
        form_layout.addRow("📅 Date de Naissance*:", dob_container)
        
        # Téléphone (avec autocomplétion indicatif)
        phone_container = QHBoxLayout()
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("+212 6XX-XXXXXX")
        self.phone.textChanged.connect(lambda: self.validate_field('phone'))
        self.phone.textChanged.connect(self.format_phone_number)
        self.phone.setMinimumHeight(40)
        self.validators['phone'] = ValidationIndicator()
        phone_container.addWidget(self.phone, stretch=1)
        phone_container.addWidget(self.validators['phone'])
        form_layout.addRow("📱 Téléphone*:", phone_container)
        
        group.setLayout(form_layout)
        layout.addWidget(group)
    
    def create_optional_section(self, layout):
        """Section informations optionnelles (repliable)"""
        self.optional_group = QGroupBox("➕ Plus d'informations (optionnel)")
        self.optional_group.setCheckable(True)
        self.optional_group.setChecked(False)
        self.optional_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #95a5a6;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #95a5a6;
            }
            QGroupBox::indicator {
                width: 15px;
                height: 15px;
            }
        """)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # Email
        email_container = QHBoxLayout()
        self.email = QLineEdit()
        self.email.setPlaceholderText("exemple@email.com")
        self.email.textChanged.connect(lambda: self.validate_field('email'))
        self.email.setMinimumHeight(40)
        self.validators['email'] = ValidationIndicator()
        email_container.addWidget(self.email, stretch=1)
        email_container.addWidget(self.validators['email'])
        form_layout.addRow("📧 Email:", email_container)
        
        # Adresse
        self.address = QTextEdit()
        self.address.setPlaceholderText("Adresse complète (optionnel)")
        self.address.setMaximumHeight(80)
        form_layout.addRow("🏠 Adresse:", self.address)
        
        # Contact d'urgence
        self.emergency_name = QLineEdit()
        self.emergency_name.setPlaceholderText("Nom du contact")
        self.emergency_name.setMinimumHeight(40)
        form_layout.addRow("🆘 Contact Urgence:", self.emergency_name)
        
        self.emergency_phone = QLineEdit()
        self.emergency_phone.setPlaceholderText("+212 6XX-XXXXXX")
        self.emergency_phone.setMinimumHeight(40)
        form_layout.addRow("📞 Téléphone Urgence:", self.emergency_phone)
        
        self.optional_group.setLayout(form_layout)
        layout.addWidget(self.optional_group)
    
    def create_training_section(self, layout):
        """Section configuration de la formation"""
        group = QGroupBox("🎓 Configuration de la Formation")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #27ae60;
            }
        """)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # Type de permis
        self.license_type = QComboBox()
        self.license_type.setMinimumHeight(40)
        for lic in LICENSE_TYPES:
            self.license_type.addItem(f"🚗 Permis {lic}", lic)
        self.license_type.setCurrentIndex(1)  # Défaut: Permis B
        form_layout.addRow("🚗 Type de Permis:", self.license_type)
        
        # Heures planifiées
        self.hours_planned = QSpinBox()
        self.hours_planned.setMinimum(10)
        self.hours_planned.setMaximum(100)
        self.hours_planned.setValue(20)
        self.hours_planned.setSuffix(" heures")
        self.hours_planned.setMinimumHeight(40)
        form_layout.addRow("⏱️ Heures Planifiées:", self.hours_planned)
        
        # Montant total dû (avec boutons montants standards)
        amount_layout = QVBoxLayout()
        
        # Spinbox
        self.total_due = QDoubleSpinBox()
        self.total_due.setMinimum(0)
        self.total_due.setMaximum(999999)
        self.total_due.setValue(5000)
        self.total_due.setSuffix(" DH")
        self.total_due.setMinimumHeight(40)
        amount_layout.addWidget(self.total_due)
        
        # Boutons montants standards
        standard_layout = QHBoxLayout()
        standard_label = QLabel("💡 Montants standards:")
        standard_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        standard_layout.addWidget(standard_label)
        
        for amount in STANDARD_AMOUNTS:
            btn = QPushButton(f"{amount}")
            btn.setMaximumWidth(70)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ecf0f1;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    padding: 5px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #3498db;
                    color: white;
                    border-color: #3498db;
                }
            """)
            btn.clicked.connect(lambda checked, a=amount: self.total_due.setValue(a))
            standard_layout.addWidget(btn)
        
        standard_layout.addStretch()
        amount_layout.addLayout(standard_layout)
        
        form_layout.addRow("💵 Montant Total Dû:", amount_layout)
        
        group.setLayout(form_layout)
        layout.addWidget(group)
    
    def create_buttons(self, layout):
        """Boutons d'action avec raccourcis"""
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        # Info raccourcis
        info_label = QLabel("💡 Ctrl+S: Enregistrer | Échap: Annuler")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 11px; font-style: italic;")
        btn_layout.addWidget(info_label)
        
        btn_layout.addStretch()
        
        # Bouton Annuler
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.setMinimumSize(140, 50)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        # Bouton Enregistrer
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setMinimumSize(140, 50)
        save_btn.clicked.connect(self.save_student)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def setup_shortcuts(self):
        """Configurer les raccourcis clavier"""
        # Ctrl+S pour sauvegarder
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_student)
        
        # Échap pour annuler
        cancel_shortcut = QShortcut(QKeySequence("Esc"), self)
        cancel_shortcut.activated.connect(self.reject)
    
    def setup_validators(self):
        """Configurer la validation temps réel"""
        # Initialiser tous les indicateurs en neutre
        for validator in self.validators.values():
            validator.set_neutral()
    
    def validate_field(self, field_name):
        """Valider un champ en temps réel"""
        if field_name == 'full_name':
            value = self.full_name.text().strip()
            if len(value) >= 3:
                self.validators['full_name'].set_valid()
            elif len(value) > 0:
                self.validators['full_name'].set_invalid("Minimum 3 caractères")
            else:
                self.validators['full_name'].set_neutral()
        
        elif field_name == 'cin':
            value = self.cin.text().strip()
            # Format CIN marocain: 2 lettres + 6 chiffres
            if re.match(r'^[A-Z]{1,2}\d{5,8}$', value, re.IGNORECASE):
                self.validators['cin'].set_valid()
            elif len(value) > 0:
                self.validators['cin'].set_invalid("Format: XX123456")
            else:
                self.validators['cin'].set_neutral()
        
        elif field_name == 'phone':
            value = self.phone.text().strip()
            # Format: +212 6XX-XXXXXX ou variations
            if re.match(r'^\+?212[\s-]?[5-7]\d{2}[\s-]?\d{6}$', value) or \
               re.match(r'^0[5-7]\d{2}[\s-]?\d{6}$', value):
                self.validators['phone'].set_valid()
            elif len(value) > 0:
                self.validators['phone'].set_invalid("Format: +212 6XX-XXXXXX")
            else:
                self.validators['phone'].set_neutral()
        
        elif field_name == 'email':
            value = self.email.text().strip()
            if not value:
                self.validators['email'].set_neutral()
            elif re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                self.validators['email'].set_valid()
            else:
                self.validators['email'].set_invalid("Email invalide")
    
    def update_age_display(self):
        """Mettre à jour l'affichage de l'âge"""
        birth_date = self.date_of_birth.date().toPython()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        self.age_label.setText(f"({age} ans)")
        
        # Valider l'âge (minimum 18 ans)
        if age < 18:
            self.age_label.setStyleSheet("color: #e74c3c; font-size: 12px; font-weight: bold;")
        else:
            self.age_label.setStyleSheet("color: #27ae60; font-size: 12px; font-weight: bold;")
    
    def format_phone_number(self):
        """Formater automatiquement le numéro de téléphone"""
        text = self.phone.text()
        
        # Ajouter +212 automatiquement si commence par 0
        if text.startswith('0') and len(text) > 1:
            text = '+212 ' + text[1:]
            self.phone.blockSignals(True)
            self.phone.setText(text)
            self.phone.blockSignals(False)
    
    def save_student(self):
        """Enregistrer l'élève avec validation complète"""
        # Validation des champs obligatoires
        errors = []
        
        full_name = self.full_name.text().strip()
        if len(full_name) < 3:
            errors.append("• Nom complet : Minimum 3 caractères")
        
        cin = self.cin.text().strip()
        if not re.match(r'^[A-Z]{1,2}\d{5,8}$', cin, re.IGNORECASE):
            errors.append("• CIN : Format invalide (Ex: AA123456)")
        
        phone = self.phone.text().strip()
        if not (re.match(r'^\+?212[\s-]?[5-7]\d{2}[\s-]?\d{6}$', phone) or \
                re.match(r'^0[5-7]\d{2}[\s-]?\d{6}$', phone)):
            errors.append("• Téléphone : Format invalide")
        
        # Vérifier l'âge
        birth_date = self.date_of_birth.date().toPython()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 18:
            errors.append("• Âge : Minimum 18 ans requis")
        
        # Valider l'email si fourni
        email = self.email.text().strip()
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append("• Email : Format invalide")
        
        if errors:
            error_msg = "❌ Erreurs de validation:\n\n" + "\n".join(errors)
            QMessageBox.warning(self, "Validation", error_msg)
            return
        
        # Collecter les données
        data = {
            'full_name': full_name,
            'cin': cin,
            'date_of_birth': birth_date,
            'phone': phone,
            'email': email or None,
            'address': self.address.toPlainText().strip() or None,
            'license_type': self.license_type.currentData(),
            'status': StudentStatus.PENDING,  # Statut initial : En attente
            'hours_planned': self.hours_planned.value(),
            'hours_completed': 0,
            'total_due': self.total_due.value(),
            'total_paid': 0,
            'balance': -self.total_due.value(),  # Négatif = dette
            'emergency_contact_name': self.emergency_name.text().strip() or None,
            'emergency_contact_phone': self.emergency_phone.text().strip() or None
        }
        
        try:
            # Créer l'élève
            success, message, new_student = StudentController.create_student(data)
            
            if success and new_student:
                # Toast de succès
                toast = ToastNotification(
                    f"✅ Élève {full_name} créé avec succès!",
                    "success",
                    self
                )
                toast.show()
                
                # Proposition d'actions rapides
                reply = QMessageBox.question(
                    self,
                    "🎉 Élève Créé!",
                    f"L'élève {full_name} a été ajouté avec succès.\n\n"
                    f"📋 CIN: {cin}\n"
                    f"💰 Montant dû: {self.total_due.value():,.2f} DH\n\n"
                    f"Voulez-vous enregistrer le premier paiement maintenant?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                self.student_saved.emit(new_student)
                
                if reply == QMessageBox.Yes:
                    # Ouvrir dialogue de paiement (à implémenter)
                    QMessageBox.information(
                        self,
                        "Info",
                        "Fonctionnalité de paiement rapide à venir!\n"
                        "Utilisez le module Paiements pour enregistrer un paiement."
                    )
                
                self.accept()
            else:
                # Toast d'erreur
                toast = ToastNotification(message, "error", self)
                toast.show()
                QMessageBox.critical(self, "Erreur", message)
        
        except Exception as e:
            toast = ToastNotification(f"Erreur: {str(e)}", "error", self)
            toast.show()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement:\n{str(e)}")
    
    def apply_style(self):
        """Appliquer le style global"""
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLineEdit, QDateEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                padding: 8px 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus, QDateEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
            QTextEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
            QLabel {
                font-size: 13px;
                color: #2c3e50;
            }
        """)
