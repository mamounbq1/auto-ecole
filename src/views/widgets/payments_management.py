"""
Payments Management Widget - Gestion complète des paiements
Table, recherche, filtres, ajout, PDF, exports
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDateEdit, QTextEdit, QDoubleSpinBox, QCheckBox, QFrame,
    QFileDialog
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont, QColor
from datetime import datetime, date

from functools import partial
from src.controllers.payment_controller import PaymentController
from src.controllers.student_controller import StudentController
from src.models import PaymentMethod, Payment


class AddPaymentDialog(QDialog):
    """Dialogue simplifié pour ajouter un paiement"""
    
    payment_added = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("💰 Nouveau Paiement")
        self.setMinimumSize(500, 550)
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Titre
        title = QLabel("Enregistrer un Paiement")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #27ae60; padding: 10px;")
        layout.addWidget(title)
        
        # Formulaire
        form = QFormLayout()
        form.setSpacing(12)
        
        # Élève
        self.student_combo = QComboBox()
        self.student_combo.setMinimumHeight(35)
        students = StudentController.get_all_students()
        for student in students:
            # Balance = total_paid - total_due (negative = dette)
            # Convertir Decimal en float pour affichage
            balance_value = float(student.balance) if student.balance else 0.0
            if balance_value == 0:
                balance_text = "0 DH"
            else:
                balance_text = f"{balance_value:+,.0f} DH"
            self.student_combo.addItem(
                f"{student.full_name} - {balance_text}",
                student.id
            )
        form.addRow("Élève*:", self.student_combo)
        
        # Montant
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMinimum(0.01)
        self.amount_input.setMaximum(999999.99)
        self.amount_input.setValue(500.0)
        self.amount_input.setSuffix(" DH")
        self.amount_input.setDecimals(2)
        self.amount_input.setMinimumHeight(35)
        form.addRow("Montant*:", self.amount_input)
        
        # Méthode de paiement
        self.method_combo = QComboBox()
        self.method_combo.setMinimumHeight(35)
        method_labels = {
            PaymentMethod.CASH: "💵 Espèces",
            PaymentMethod.CARD: "💳 Carte Bancaire",
            PaymentMethod.CHECK: "📝 Chèque",
            PaymentMethod.TRANSFER: "🏦 Virement",
            PaymentMethod.MOBILE_MONEY: "📱 Mobile Money"
        }
        for method, label in method_labels.items():
            self.method_combo.addItem(label, method)
        form.addRow("Méthode*:", self.method_combo)
        
        # Date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setMinimumHeight(35)
        form.addRow("Date:", self.date_input)
        
        # Catégorie
        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(35)
        categories = {
            'inscription': '📋 Inscription',
            'conduite': '🚗 Conduite',
            'examen_theorique': '📚 Examen Théorique',
            'examen_pratique': '🎯 Examen Pratique',
            'materiel_pedagogique': '📖 Matériel Pédagogique',
            'autre': '📦 Autre'
        }
        for cat_key, cat_label in categories.items():
            self.category_combo.addItem(cat_label, cat_key)
        form.addRow("Catégorie:", self.category_combo)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(70)
        self.description_input.setPlaceholderText("Description du paiement...")
        form.addRow("Description:", self.description_input)
        
        # Référence
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("N° chèque, référence...")
        self.reference_input.setMinimumHeight(35)
        form.addRow("Référence:", self.reference_input)
        
        layout.addLayout(form)
        
        # Options
        options_frame = QFrame()
        options_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        options_layout = QVBoxLayout(options_frame)
        
        self.validate_check = QCheckBox("Valider immédiatement le paiement")
        self.validate_check.setChecked(True)
        options_layout.addWidget(self.validate_check)
        
        self.generate_pdf_check = QCheckBox("Générer un reçu PDF")
        self.generate_pdf_check.setChecked(True)
        options_layout.addWidget(self.generate_pdf_check)
        
        layout.addWidget(options_frame)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Enregistrer le Paiement")
        save_btn.setMinimumHeight(40)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.save_payment)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def save_payment(self):
        """Enregistrer le paiement"""
        # Validation
        if self.student_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un élève")
            return
        
        if self.amount_input.value() <= 0:
            QMessageBox.warning(self, "Erreur", "Le montant doit être supérieur à 0")
            return
        
        # Récupérer les données
        student_id = self.student_combo.currentData()
        amount = self.amount_input.value()
        method = self.method_combo.currentData()
        payment_date = self.date_input.date().toPython()
        category = self.category_combo.currentData()
        description = self.description_input.toPlainText()
        reference = self.reference_input.text()
        validated_by = "Administrateur" if self.validate_check.isChecked() else ""
        
        # Créer le paiement
        success, message, payment = PaymentController.create_payment(
            student_id=student_id,
            amount=amount,
            payment_method=method,
            description=description,
            validated_by=validated_by
        )
        
        if success:
            # Mettre à jour les champs supplémentaires
            from src.models import get_session
            session = get_session()
            payment.payment_date = payment_date
            payment.category = category
            payment.reference_number = reference
            session.commit()
            
            # Générer PDF si demandé
            if self.generate_pdf_check.isChecked() and payment.receipt_number:
                pdf_success, pdf_path = PaymentController.generate_receipt_pdf(payment.id)
                if pdf_success:
                    QMessageBox.information(
                        self, 
                        "Succès", 
                        f"Paiement enregistré avec succès !\n\nReçu N°: {payment.receipt_number}\nPDF: {pdf_path}"
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Paiement Enregistré",
                        f"Paiement enregistré avec succès !\n\nReçu N°: {payment.receipt_number}\n\nNote: Erreur lors de la génération du PDF"
                    )
            else:
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Paiement enregistré avec succès !\n\nReçu N°: {payment.receipt_number if payment.receipt_number else 'N/A'}"
                )
            
            self.payment_added.emit()
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement :\n{message}")


class PaymentsManagement(QWidget):
    """Widget de gestion complète des paiements"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_payments()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        self.create_header(layout)
        
        # Barre de recherche et filtres
        self.create_search_bar(layout)
        
        # Statistiques rapides
        self.create_stats(layout)
        
        # Table des paiements
        self.create_table(layout)
    
    def create_header(self, layout):
        """Créer l'en-tête"""
        header_layout = QHBoxLayout()
        
        # Barre de recherche à gauche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par nom, reçu, montant...")
        self.search_input.textChanged.connect(self.filter_payments)
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        header_layout.addWidget(self.search_input, stretch=2)
        
        header_layout.addStretch()
        
        # Boutons
        add_btn = QPushButton("➕ Nouveau Paiement")
        add_btn.clicked.connect(self.add_payment)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        add_btn.setCursor(Qt.PointingHandCursor)
        
        export_btn = QPushButton("📤 Exporter CSV")
        export_btn.clicked.connect(self.export_payments)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #1abc9c;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
        """)
        export_btn.setCursor(Qt.PointingHandCursor)
        
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.clicked.connect(self.load_payments)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        
        header_layout.addWidget(add_btn)
        header_layout.addWidget(export_btn)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
    
    def create_search_bar(self, layout):
        """Créer la barre de filtres par date"""
        search_layout = QHBoxLayout()
        
        date_label_from = QLabel("Du:")
        date_label_from.setStyleSheet("font-weight: bold; font-size: 13px;")
        search_layout.addWidget(date_label_from)
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setMinimumHeight(40)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.dateChanged.connect(self.filter_payments)
        self.date_from.setStyleSheet("""
            QDateEdit {
                padding: 8px 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 13px;
            }
        """)
        search_layout.addWidget(self.date_from)
        
        date_label_to = QLabel("Au:")
        date_label_to.setStyleSheet("font-weight: bold; font-size: 13px; margin-left: 15px;")
        search_layout.addWidget(date_label_to)
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setMinimumHeight(40)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.dateChanged.connect(self.filter_payments)
        self.date_to.setStyleSheet("""
            QDateEdit {
                padding: 8px 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 13px;
            }
        """)
        search_layout.addWidget(self.date_to)
        
        search_layout.addStretch()
        
        self.method_filter = QComboBox()
        self.method_filter.addItem("💳 Toutes les méthodes", None)
        for method in PaymentMethod:
            self.method_filter.addItem(method.value.replace('_', ' ').title(), method)
        self.method_filter.currentIndexChanged.connect(self.filter_payments)
        self.method_filter.setMinimumHeight(40)
        self.method_filter.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 13px;
            }
        """)
        search_layout.addWidget(self.method_filter, stretch=1)
        
        self.status_filter = QComboBox()
        self.status_filter.addItem("📊 Tous les statuts", None)
        self.status_filter.addItem("✅ Validés", "validated")
        self.status_filter.addItem("⏳ En attente", "pending")
        self.status_filter.addItem("❌ Annulés", "cancelled")
        self.status_filter.currentIndexChanged.connect(self.filter_payments)
        self.status_filter.setMinimumHeight(40)
        self.status_filter.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 13px;
            }
        """)
        search_layout.addWidget(self.status_filter, stretch=1)
        
        layout.addLayout(search_layout)
    
    def create_stats(self, layout):
        """Créer les statistiques rapides"""
        stats_layout = QHBoxLayout()
        
        self.total_label = QLabel("Total: 0 paiements")
        self.sum_label = QLabel("Montant: 0.00 DH")
        self.validated_label = QLabel("Validés: 0")
        self.pending_label = QLabel("En attente: 0")
        
        for label in [self.total_label, self.sum_label, self.validated_label, self.pending_label]:
            label.setStyleSheet("""
                QLabel {
                    background-color: white;
                    padding: 10px 20px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                    color: #2c3e50;
                    border: 2px solid #ecf0f1;
                }
            """)
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.sum_label)
        stats_layout.addWidget(self.validated_label)
        stats_layout.addWidget(self.pending_label)
        
        layout.addLayout(stats_layout)
    
    def create_old_toolbar(self) -> QFrame:
        """Créer la barre d'outils"""
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        main_layout = QVBoxLayout(toolbar)
        main_layout.setSpacing(10)
        
        # Première ligne: Recherche
        first_row = QHBoxLayout()
        first_row.setSpacing(10)
        
        search_label = QLabel("🔍")
        search_label.setStyleSheet("font-size: 18px;")
        first_row.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par nom, reçu, montant...")
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ecf0f1;
                border-radius: 5px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #27ae60;
            }
        """)
        self.search_input.textChanged.connect(self.filter_payments)
        first_row.addWidget(self.search_input, stretch=1)
        
        main_layout.addLayout(first_row)
        
        # Deuxième ligne: Filtres et Actions
        second_row = QHBoxLayout()
        second_row.setSpacing(10)
        
        # Filtre méthode
        self.method_filter = QComboBox()
        self.method_filter.setMinimumHeight(40)
        self.method_filter.setMinimumWidth(160)
        self.method_filter.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                border: 2px solid #ecf0f1;
                border-radius: 5px;
                font-size: 13px;
            }
        """)
        self.method_filter.addItem("Toutes les méthodes", None)
        for method in PaymentMethod:
            self.method_filter.addItem(method.value.replace('_', ' ').title(), method)
        self.method_filter.currentIndexChanged.connect(self.filter_payments)
        second_row.addWidget(self.method_filter)
        
        # Filtre statut
        self.status_filter = QComboBox()
        self.status_filter.setMinimumHeight(40)
        self.status_filter.setMinimumWidth(140)
        self.status_filter.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                border: 2px solid #ecf0f1;
                border-radius: 5px;
                font-size: 13px;
            }
        """)
        self.status_filter.addItem("Tous les statuts", None)
        self.status_filter.addItem("✅ Validés", "validated")
        self.status_filter.addItem("⏳ En attente", "pending")
        self.status_filter.addItem("❌ Annulés", "cancelled")
        self.status_filter.currentIndexChanged.connect(self.filter_payments)
        second_row.addWidget(self.status_filter)
        
        # Filtre date début
        date_label_from = QLabel("Du:")
        date_label_from.setStyleSheet("font-weight: bold; font-size: 13px;")
        second_row.addWidget(date_label_from)
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setMinimumHeight(40)
        self.date_from.setMinimumWidth(120)
        self.date_from.setStyleSheet("""
            QDateEdit {
                padding: 5px 10px;
                border: 2px solid #ecf0f1;
                border-radius: 5px;
                font-size: 13px;
            }
        """)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.dateChanged.connect(self.filter_payments)
        second_row.addWidget(self.date_from)
        
        # Filtre date fin
        date_label_to = QLabel("Au:")
        date_label_to.setStyleSheet("font-weight: bold; font-size: 13px;")
        second_row.addWidget(date_label_to)
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setMinimumHeight(40)
        self.date_to.setMinimumWidth(120)
        self.date_to.setStyleSheet("""
            QDateEdit {
                padding: 5px 10px;
                border: 2px solid #ecf0f1;
                border-radius: 5px;
                font-size: 13px;
            }
        """)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.dateChanged.connect(self.filter_payments)
        second_row.addWidget(self.date_to)
        
        second_row.addStretch()
        
        # Bouton nouveau paiement
        add_btn = QPushButton("➕ Nouveau Paiement")
        add_btn.setMinimumHeight(40)
        add_btn.setMinimumWidth(160)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
                padding: 0 15px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        add_btn.clicked.connect(self.add_payment)
        second_row.addWidget(add_btn)
        
        # Bouton exporter
        export_btn = QPushButton("📊 Exporter")
        export_btn.setMinimumHeight(40)
        export_btn.setMinimumWidth(120)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
                padding: 0 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        export_btn.clicked.connect(self.export_payments)
        second_row.addWidget(export_btn)
        
        # Bouton rafraîchir
        refresh_btn = QPushButton("🔄")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.setFixedWidth(50)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        refresh_btn.clicked.connect(self.load_payments)
        second_row.addWidget(refresh_btn)
        
        main_layout.addLayout(second_row)
        
        return toolbar
    
    def create_table(self, layout):
        """Créer la table des paiements"""
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Date", "N° Reçu", "Élève", "Montant", "Méthode",
            "Catégorie", "Statut", "Validé par", "Actions"
        ])
        
        # Style
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #d5f4e6;
                color: #000;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Ajuster colonnes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Reçu
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Élève
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Montant
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Méthode
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Catégorie
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Statut
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Validé par
        header.setSectionResizeMode(8, QHeaderView.Fixed)  # Actions
        header.resizeSection(8, 160)  # Fixer largeur colonne Actions à 160px
        
        # Ajuster hauteur des lignes
        self.table.verticalHeader().setDefaultSectionSize(45)
        
        self.table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.table)
    
    def create_footer(self) -> QFrame:
        """Créer le footer avec stats"""
        footer = QFrame()
        footer.setFixedHeight(50)
        footer.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
            }
        """)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(15, 0, 15, 0)
        
        self.total_label = QLabel("Total: 0 paiements")
        self.total_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.total_label)
        
        layout.addStretch()
        
        self.sum_label = QLabel("Montant total: 0.00 DH")
        self.sum_label.setStyleSheet("font-weight: bold; color: #27ae60; font-size: 13px;")
        layout.addWidget(self.sum_label)
        
        return footer
    
    def load_payments(self):
        """Charger tous les paiements"""
        self.all_payments = PaymentController.get_all_payments()
        self.display_payments(self.all_payments)
        self.update_stats()
    
    def display_payments(self, payments: list):
        """Afficher les paiements dans la table"""
        self.table.setRowCount(0)
        
        # Récupérer infos élèves
        all_students = {s.id: s for s in StudentController.get_all_students()}
        
        total_amount = 0
        
        for payment in payments:
            # Ne pas afficher les paiements annulés
            if payment.is_cancelled:
                continue
            
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            student = all_students.get(payment.student_id)
            student_name = student.full_name if student else "N/A"
            
            # Date
            date_item = QTableWidgetItem(payment.payment_date.strftime('%d/%m/%Y') if payment.payment_date else 'N/A')
            date_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, date_item)
            
            # Reçu
            receipt_item = QTableWidgetItem(payment.receipt_number or 'N/A')
            receipt_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, receipt_item)
            
            # Élève
            self.table.setItem(row, 2, QTableWidgetItem(student_name))
            
            # Montant (convertir Decimal en float)
            amount_value = float(payment.amount) if payment.amount else 0.0
            amount_item = QTableWidgetItem(f"{amount_value:,.2f} DH")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amount_item.setForeground(QColor("#27ae60"))
            amount_font = QFont()
            amount_font.setBold(True)
            amount_item.setFont(amount_font)
            self.table.setItem(row, 3, amount_item)
            total_amount += amount_value
            
            # Méthode
            method_item = QTableWidgetItem(payment.payment_method.value.replace('_', ' ').title())
            method_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, method_item)
            
            # Catégorie
            cat_item = QTableWidgetItem((payment.category or 'autre').replace('_', ' ').title())
            cat_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, cat_item)
            
            # Statut
            if payment.is_validated:
                status_item = QTableWidgetItem("✅ Validé")
                status_item.setForeground(QColor("#27ae60"))
            else:
                status_item = QTableWidgetItem("⏳ En attente")
                status_item.setForeground(QColor("#f39c12"))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 6, status_item)
            
            # Validé par
            self.table.setItem(row, 7, QTableWidgetItem(payment.validated_by or '-'))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(5)
            
            view_btn = QPushButton("👁️")
            view_btn.setToolTip("Voir reçu")
            view_btn.clicked.connect(partial(self.view_receipt, payment))
            view_btn.setCursor(Qt.PointingHandCursor)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Modifier")
            edit_btn.clicked.connect(partial(self.edit_payment, payment))
            edit_btn.setCursor(Qt.PointingHandCursor)
            
            pdf_btn = QPushButton("📄")
            pdf_btn.setToolTip("Générer PDF")
            pdf_btn.clicked.connect(partial(self.generate_pdf, payment))
            pdf_btn.setCursor(Qt.PointingHandCursor)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Annuler/Supprimer")
            delete_btn.clicked.connect(partial(self.delete_payment, payment))
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(pdf_btn)
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 8, actions_widget)
    
    def update_stats(self):
        """Mettre à jour les statistiques"""
        if not self.all_payments:
            return
        
        total = len([p for p in self.all_payments if not p.is_cancelled])
        validated = len([p for p in self.all_payments if p.is_validated and not p.is_cancelled])
        pending = len([p for p in self.all_payments if not p.is_validated and not p.is_cancelled])
        total_amount = sum(float(p.amount) for p in self.all_payments if not p.is_cancelled)
        
        self.total_label.setText(f"Total: {total} paiements")
        self.sum_label.setText(f"Montant: {total_amount:,.2f} DH")
        self.validated_label.setText(f"Validés: {validated}")
        self.pending_label.setText(f"En attente: {pending}")
    
    def filter_payments(self):
        """Filtrer les paiements selon critères"""
        search_text = self.search_input.text().lower()
        method_filter = self.method_filter.currentData()
        status_filter = self.status_filter.currentData()
        date_from = self.date_from.date().toPython()
        date_to = self.date_to.date().toPython()
        
        filtered = []
        all_students = {s.id: s for s in StudentController.get_all_students()}
        
        for payment in self.all_payments:
            # Filtre recherche
            if search_text:
                student = all_students.get(payment.student_id)
                student_name = student.full_name.lower() if student else ''
                receipt = (payment.receipt_number or '').lower()
                amount_str = str(payment.amount)
                
                if not (search_text in student_name or search_text in receipt or search_text in amount_str):
                    continue
            
            # Filtre méthode
            if method_filter and payment.payment_method != method_filter:
                continue
            
            # Filtre statut
            if status_filter:
                if status_filter == "validated" and not payment.is_validated:
                    continue
                if status_filter == "pending" and payment.is_validated:
                    continue
                if status_filter == "cancelled" and not payment.is_cancelled:
                    continue
            
            # Filtre date
            if payment.payment_date:
                payment_date = payment.payment_date.date() if hasattr(payment.payment_date, 'date') else payment.payment_date
                if payment_date < date_from or payment_date > date_to:
                    continue
            
            filtered.append(payment)
        
        self.display_payments(filtered)
        self.update_stats()
    
    def add_payment(self):
        """Ouvrir dialogue ajout paiement"""
        dialog = AddPaymentDialog(self)
        dialog.payment_added.connect(self.load_payments)
        dialog.exec()
    
    def generate_pdf(self, payment):
        """Générer PDF pour un paiement et l'ouvrir automatiquement"""
        import os
        import webbrowser
        
        if not payment.receipt_number:
            QMessageBox.warning(self, "Erreur", "Ce paiement n'a pas de numéro de reçu")
            return
        
        success, result = PaymentController.generate_receipt_pdf(payment.id)
        if success:
            # Ouvrir automatiquement le PDF
            if os.path.exists(result):
                webbrowser.open('file://' + os.path.abspath(result))
                QMessageBox.information(self, "Succès", f"Reçu PDF généré et ouvert :\n{result}")
            else:
                QMessageBox.information(self, "Succès", f"Reçu PDF généré :\n{result}")
        else:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération :\n{result}")
    
    def print_receipt(self, payment):
        """Sauvegarder et ouvrir le reçu HTML"""
        import os
        import webbrowser
        
        if not payment.receipt_number:
            QMessageBox.warning(self, "Erreur", "Ce paiement n'a pas de numéro de reçu")
            return
        
        # Récupérer l'élève
        student = StudentController.get_student_by_id(payment.student_id)
        if not student:
            QMessageBox.warning(self, "Erreur", "Élève introuvable")
            return
        
        # Créer le dossier export s'il n'existe pas
        export_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'export')
        os.makedirs(export_dir, exist_ok=True)
        
        # Nom du fichier
        filename = f"recu_{payment.receipt_number.replace('/', '_')}_{date.today().strftime('%Y%m%d')}.html"
        filepath = os.path.join(export_dir, filename)
        
        # Créer contenu HTML pour le reçu
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Reçu de Paiement - {payment.receipt_number}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }}
        .receipt {{
            background: white;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 5px 0;
            font-size: 32px;
        }}
        .header p {{
            color: #7f8c8d;
            margin: 5px 0;
        }}
        .info-section {{
            margin: 30px 0;
        }}
        .info-row {{
            margin: 15px 0;
            display: flex;
            justify-content: space-between;
            padding: 10px;
            border-bottom: 1px solid #ecf0f1;
        }}
        .label {{
            font-weight: bold;
            color: #34495e;
        }}
        .value {{
            color: #2c3e50;
        }}
        .amount {{
            font-size: 36px;
            font-weight: bold;
            color: #27ae60;
            text-align: center;
            margin: 40px 0;
            padding: 30px;
            background: #ecfdf5;
            border-radius: 10px;
        }}
        .footer {{
            margin-top: 50px;
            text-align: center;
            font-size: 14px;
            color: #7f8c8d;
            border-top: 2px solid #ecf0f1;
            padding-top: 20px;
        }}
        @media print {{
            body {{ background: white; margin: 0; }}
            .receipt {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="receipt">
        <div class="header">
            <h1>REÇU DE PAIEMENT</h1>
            <p>Auto-École</p>
        </div>
        
        <div class="info-section">
            <div class="info-row">
                <span class="label">Numéro de reçu:</span>
                <span class="value">{payment.receipt_number}</span>
            </div>
            <div class="info-row">
                <span class="label">Date:</span>
                <span class="value">{payment.payment_date.strftime('%d/%m/%Y %H:%M') if payment.payment_date else 'N/A'}</span>
            </div>
            <div class="info-row">
                <span class="label">Élève:</span>
                <span class="value">{student.full_name}</span>
            </div>
            <div class="info-row">
                <span class="label">CIN:</span>
                <span class="value">{student.cin or 'N/A'}</span>
            </div>
            <div class="info-row">
                <span class="label">Méthode de paiement:</span>
                <span class="value">{payment.payment_method.value.replace('_', ' ').title()}</span>
            </div>
            <div class="info-row">
                <span class="label">Catégorie:</span>
                <span class="value">{(payment.category or 'autre').replace('_', ' ').title()}</span>
            </div>"""
        
        if payment.reference_number:
            html_content += f"""
            <div class="info-row">
                <span class="label">Référence:</span>
                <span class="value">{payment.reference_number}</span>
            </div>"""
        
        if payment.description:
            html_content += f"""
            <div class="info-row">
                <span class="label">Description:</span>
                <span class="value">{payment.description}</span>
            </div>"""
        
        html_content += f"""
        </div>
        
        <div class="amount">
            MONTANT: {float(payment.amount):,.2f} DH
        </div>
        
        <div class="footer">
            <p><strong>Ce reçu est valide et certifie le paiement effectué.</strong></p>
            <p>Généré le {date.today().strftime('%d/%m/%Y')}</p>
        </div>
    </div>
</body>
</html>"""
        
        # Sauvegarder le fichier
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Ouvrir automatiquement dans le navigateur
            webbrowser.open('file://' + os.path.abspath(filepath))
            
            QMessageBox.information(self, "Succès", f"Reçu sauvegardé et ouvert:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde:\n{str(e)}")
    
    def export_payments(self):
        """Exporter les paiements en CSV"""
        if not self.all_payments:
            QMessageBox.warning(self, "Erreur", "Aucun paiement à exporter")
            return
        
        # Utiliser EXPORTS_DIR depuis config
        try:
            from src.config import EXPORTS_DIR, init_export_folders
            init_export_folders()
            default_dir = str(EXPORTS_DIR) if EXPORTS_DIR else "."
        except:
            default_dir = "."
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les paiements",
            f"{default_dir}/paiements_{date.today().strftime('%Y%m%d')}.csv",
            "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                import csv
                all_students = {s.id: s for s in StudentController.get_all_students()}
                
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'Date', 'Reçu', 'Élève', 'Montant', 'Méthode',
                        'Catégorie', 'Statut', 'Validé par', 'Référence'
                    ])
                    
                    for p in self.all_payments:
                        # Exclure les paiements annulés de l'export
                        if p.is_cancelled:
                            continue
                        student = all_students.get(p.student_id)
                        writer.writerow([
                            p.payment_date.strftime('%d/%m/%Y') if p.payment_date else '',
                            p.receipt_number or '',
                            student.full_name if student else '',
                            float(p.amount) if p.amount else 0.0,
                            p.payment_method.value,
                            p.category or '',
                            p.status,
                            p.validated_by or '',
                            p.reference_number or ''
                        ])
                
                QMessageBox.information(self, "Succès", f"Paiements exportés vers :\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export :\n{str(e)}")
    
    def view_receipt(self, payment):
        """Afficher le reçu dans une fenêtre avec bouton imprimer"""
        from PySide6.QtWidgets import QTextBrowser
        from PySide6.QtPrintSupport import QPrinter, QPrintDialog
        
        if not payment.receipt_number:
            QMessageBox.warning(self, "Erreur", "Ce paiement n'a pas de numéro de reçu")
            return
        
        student = StudentController.get_student_by_id(payment.student_id)
        if not student:
            QMessageBox.warning(self, "Erreur", "Élève introuvable")
            return
        
        # Créer dialogue
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Reçu - {payment.receipt_number}")
        dialog.setMinimumSize(700, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Créer contenu HTML
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }}
                .receipt {{
                    max-width: 600px;
                    margin: 0 auto;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 3px solid #2c3e50;
                    padding-bottom: 20px;
                }}
                .header h1 {{
                    color: #2c3e50;
                    margin: 5px 0;
                }}
                .header p {{
                    color: #7f8c8d;
                    margin: 5px 0;
                }}
                .info-section {{
                    margin: 20px 0;
                }}
                .info-row {{
                    margin: 12px 0;
                    padding: 8px;
                    border-bottom: 1px solid #ecf0f1;
                }}
                .label {{
                    font-weight: bold;
                    color: #34495e;
                }}
                .value {{
                    color: #2c3e50;
                    float: right;
                }}
                .amount {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #27ae60;
                    text-align: center;
                    margin: 30px 0;
                    padding: 20px;
                    background: #ecfdf5;
                    border-radius: 8px;
                }}
                .footer {{
                    margin-top: 40px;
                    text-align: center;
                    font-size: 12px;
                    color: #7f8c8d;
                    border-top: 1px solid #ecf0f1;
                    padding-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="receipt">
                <div class="header">
                    <h1>REÇU DE PAIEMENT</h1>
                    <p>Auto-École</p>
                </div>
                
                <div class="info-section">
                    <div class="info-row">
                        <span class="label">Numéro de reçu:</span>
                        <span class="value">{payment.receipt_number}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Date:</span>
                        <span class="value">{payment.payment_date.strftime('%d/%m/%Y %H:%M') if payment.payment_date else 'N/A'}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Élève:</span>
                        <span class="value">{student.full_name}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">CIN:</span>
                        <span class="value">{student.cin or 'N/A'}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Méthode:</span>
                        <span class="value">{payment.payment_method.value.replace('_', ' ').title()}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Catégorie:</span>
                        <span class="value">{(payment.category or 'autre').replace('_', ' ').title()}</span>
                    </div>
                    {f'<div class="info-row"><span class="label">Référence:</span><span class="value">{payment.reference_number}</span></div>' if payment.reference_number else ''}
                    {f'<div class="info-row"><span class="label">Description:</span><span class="value">{payment.description}</span></div>' if payment.description else ''}
                </div>
                
                <div class="amount">
                    MONTANT: {float(payment.amount):,.2f} DH
                </div>
                
                <div class="footer">
                    <p><strong>Ce reçu est valide et certifie le paiement effectué.</strong></p>
                    <p>Validé par: {payment.validated_by or 'Non validé'}</p>
                    <p>Généré le {date.today().strftime('%d/%m/%Y')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Afficher dans QTextBrowser
        text_browser = QTextBrowser()
        text_browser.setHtml(html_content)
        layout.addWidget(text_browser)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        print_btn = QPushButton("🖨️ Imprimer")
        print_btn.setMinimumHeight(35)
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        def print_document():
            printer = QPrinter(QPrinter.HighResolution)
            print_dialog = QPrintDialog(printer, dialog)
            if print_dialog.exec() == QPrintDialog.Accepted:
                text_browser.print_(printer)
        
        print_btn.clicked.connect(print_document)
        
        close_btn = QPushButton("Fermer")
        close_btn.setMinimumHeight(35)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_btn.clicked.connect(dialog.close)
        
        btn_layout.addWidget(print_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def edit_payment(self, payment):
        """Modifier un paiement"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QComboBox, QTextEdit, QLineEdit, QDateEdit
        from PySide6.QtCore import QDate
        
        if payment.is_cancelled:
            QMessageBox.warning(self, "Erreur", "Impossible de modifier un paiement annulé")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Modifier Paiement - {payment.receipt_number}")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # Élève (non modifiable)
        student = StudentController.get_student_by_id(payment.student_id)
        layout.addWidget(QLabel(f"<b>Élève:</b> {student.full_name if student else 'N/A'}"))
        layout.addWidget(QLabel(f"<b>Reçu N°:</b> {payment.receipt_number}"))
        
        # Montant
        layout.addWidget(QLabel("Montant (DH):"))
        amount_input = QDoubleSpinBox()
        amount_input.setRange(0.01, 100000)
        amount_input.setValue(float(payment.amount))
        amount_input.setDecimals(2)
        layout.addWidget(amount_input)
        
        # Date
        layout.addWidget(QLabel("Date:"))
        date_input = QDateEdit()
        date_input.setCalendarPopup(True)
        date_input.setDate(QDate(payment.payment_date) if payment.payment_date else QDate.currentDate())
        layout.addWidget(date_input)
        
        # Méthode
        layout.addWidget(QLabel("Méthode de paiement:"))
        method_combo = QComboBox()
        for method in PaymentMethod:
            method_combo.addItem(method.value.replace('_', ' ').title(), method)
        method_combo.setCurrentText(payment.payment_method.value.replace('_', ' ').title())
        layout.addWidget(method_combo)
        
        # Catégorie
        layout.addWidget(QLabel("Catégorie:"))
        category_combo = QComboBox()
        categories = [
            ('inscription', 'Inscription'),
            ('conduite', 'Conduite'),
            ('examen_theorique', 'Examen Théorique'),
            ('examen_pratique', 'Examen Pratique'),
            ('materiel_pedagogique', 'Matériel Pédagogique'),
            ('autre', 'Autre')
        ]
        for cat_val, cat_label in categories:
            category_combo.addItem(cat_label, cat_val)
        if payment.category:
            category_combo.setCurrentText(payment.category.replace('_', ' ').title())
        layout.addWidget(category_combo)
        
        # Référence
        layout.addWidget(QLabel("Référence (optionnel):"))
        reference_input = QLineEdit(payment.reference_number or '')
        layout.addWidget(reference_input)
        
        # Description
        layout.addWidget(QLabel("Description (optionnel):"))
        description_input = QTextEdit()
        description_input.setPlainText(payment.description or '')
        description_input.setMaximumHeight(80)
        layout.addWidget(description_input)
        
        # Boutons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setStyleSheet("""
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
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        def save_changes():
            new_amount = amount_input.value()
            new_date = date_input.date().toPython()
            new_method = method_combo.currentData()
            new_category = category_combo.currentData()
            new_reference = reference_input.text()
            new_description = description_input.toPlainText()
            
            # Mettre à jour via controller
            success, message = PaymentController.update_payment(
                payment_id=payment.id,
                amount=new_amount,
                payment_method=new_method,
                description=new_description
            )
            
            if success:
                # Mettre à jour champs supplémentaires
                from src.models import get_session
                session = get_session()
                session.expire_all()
                updated_payment = session.query(Payment).filter_by(id=payment.id).first()
                if updated_payment:
                    updated_payment.payment_date = new_date
                    updated_payment.category = new_category
                    updated_payment.reference_number = new_reference
                    session.commit()
                
                QMessageBox.information(dialog, "Succès", "Paiement modifié avec succès")
                dialog.accept()
                self.load_payments()
            else:
                QMessageBox.critical(dialog, "Erreur", f"Erreur: {message}")
        
        save_btn.clicked.connect(save_changes)
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def delete_payment(self, payment):
        """Annuler/Supprimer un paiement"""
        if payment.is_cancelled:
            QMessageBox.warning(self, "Erreur", "Ce paiement est déjà annulé")
            return
        
        student = StudentController.get_student_by_id(payment.student_id)
        
        reply = QMessageBox.question(
            self,
            "Confirmer l'annulation",
            f"Voulez-vous annuler le paiement ?\n\n"
            f"Reçu: {payment.receipt_number}\n"
            f"Élève: {student.full_name if student else 'N/A'}\n"
            f"Montant: {float(payment.amount):,.2f} DH\n\n"
            f"⚠️ Le solde de l'élève sera ajusté",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Demander raison
            from PySide6.QtWidgets import QInputDialog
            reason, ok = QInputDialog.getText(
                self,
                "Raison de l'annulation",
                "Veuillez indiquer la raison de l'annulation:"
            )
            
            if ok and reason:
                success, message = PaymentController.cancel_payment(payment.id, reason)
                if success:
                    QMessageBox.information(self, "Succès", "Paiement annulé avec succès")
                    self.load_payments()
                else:
                    QMessageBox.critical(self, "Erreur", f"Erreur: {message}")
