"""
Widget de gestion des paiements avec génération PDF et historique
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDateEdit, QTextEdit, QDoubleSpinBox, QGroupBox, QCheckBox,
    QFileDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from datetime import datetime

from src.controllers.payment_controller import PaymentController
from src.controllers.student_controller import StudentController
from src.models import PaymentMethod, PaymentCategory
from src.utils import get_pdf_generator, get_notification_manager, export_to_csv


class PaymentDialog(QDialog):
    """Dialogue pour enregistrer un paiement"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouveau Paiement")
        self.setMinimumSize(500, 600)
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Sélection élève
        self.student_combo = QComboBox()
        students = StudentController.get_all_students()
        for student in students:
            self.student_combo.addItem(
                f"{student.full_name} (CIN: {student.cin}) - Solde: {student.balance:,.2f} DH",
                student.id
            )
        
        # Montant
        self.amount = QDoubleSpinBox()
        self.amount.setMinimum(0.01)
        self.amount.setMaximum(999999.99)
        self.amount.setValue(500.0)
        self.amount.setSuffix(" DH")
        self.amount.setDecimals(2)
        
        # Méthode de paiement
        self.payment_method = QComboBox()
        for method in PaymentMethod:
            self.payment_method.addItem(method.value, method)
        
        # Catégorie
        self.category = QComboBox()
        for cat in PaymentCategory:
            self.category.addItem(cat.value.replace('_', ' ').title(), cat)
        
        # Date
        self.payment_date = QDateEdit()
        self.payment_date.setCalendarPopup(True)
        self.payment_date.setDate(QDate.currentDate())
        
        # Description
        self.description = QTextEdit()
        self.description.setMaximumHeight(80)
        self.description.setPlaceholderText("Description du paiement...")
        
        # Référence
        self.reference = QLineEdit()
        self.reference.setPlaceholderText("Numéro de chèque, référence, etc.")
        
        # Générer PDF
        self.generate_pdf = QCheckBox("Générer un reçu PDF")
        self.generate_pdf.setChecked(True)
        
        # Envoyer par email
        self.send_email = QCheckBox("Envoyer le reçu par email")
        
        form_layout.addRow("Élève*:", self.student_combo)
        form_layout.addRow("Montant*:", self.amount)
        form_layout.addRow("Méthode*:", self.payment_method)
        form_layout.addRow("Catégorie:", self.category)
        form_layout.addRow("Date:", self.payment_date)
        form_layout.addRow("Description:", self.description)
        form_layout.addRow("Référence:", self.reference)
        form_layout.addRow("", self.generate_pdf)
        form_layout.addRow("", self.send_email)
        
        layout.addLayout(form_layout)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.clicked.connect(self.save_payment)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
        """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def save_payment(self):
        """Enregistrer le paiement"""
        try:
            student_id = self.student_combo.currentData()
            
            payment_data = {
                'student_id': student_id,
                'amount': self.amount.value(),
                'payment_method': self.payment_method.currentData(),
                'category': self.category.currentData(),
                'payment_date': self.payment_date.date().toPython(),
                'description': self.description.toPlainText().strip() or None,
                'reference_number': self.reference.text().strip() or None,
            }
            
            # Créer le paiement
            payment = PaymentController.create_payment(payment_data)
            
            # Générer PDF si demandé
            pdf_path = None
            if self.generate_pdf.isChecked():
                pdf_gen = get_pdf_generator()
                student = StudentController.get_student_by_id(student_id)
                
                receipt_data = {
                    'receipt_number': payment.receipt_number,
                    'date': payment.payment_date.strftime('%d/%m/%Y'),
                    'student_name': student.full_name,
                    'student_cin': student.cin,
                    'student_phone': student.phone,
                    'amount': payment.amount,
                    'payment_method': payment.payment_method.value,
                    'description': payment.description or 'Paiement',
                    'validated_by': 'Système'
                }
                
                success, result = pdf_gen.generate_receipt(receipt_data)
                if success:
                    pdf_path = result
            
            # Envoyer email si demandé
            if self.send_email.isChecked() and pdf_path:
                student = StudentController.get_student_by_id(student_id)
                if student.email:
                    notif = get_notification_manager()
                    notif.send_payment_receipt_email(
                        student.email,
                        receipt_data,
                        pdf_path
                    )
            
            QMessageBox.information(
                self, "Succès",
                f"Paiement enregistré avec succès!\nReçu: {payment.receipt_number}"
            )
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")


class PaymentsEnhancedWidget(QWidget):
    """Widget de gestion des paiements"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.payments = []
        self.setup_ui()
        self.load_payments()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        self.create_header(layout)
        
        # Filtres
        self.create_filters(layout)
        
        # Statistiques
        self.create_stats(layout)
        
        # Tableau
        self.create_table(layout)
    
    def create_header(self, layout):
        """Créer l'en-tête"""
        header_layout = QHBoxLayout()
        
        title = QLabel("💰 Gestion des Paiements")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Boutons
        add_btn = QPushButton("➕ Nouveau Paiement")
        add_btn.clicked.connect(self.add_payment)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        add_btn.setCursor(Qt.PointingHandCursor)
        
        export_btn = QPushButton("📤 Exporter")
        export_btn.clicked.connect(self.export_payments)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
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
    
    def create_filters(self, layout):
        """Créer les filtres"""
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par nom d'élève ou n° reçu...")
        self.search_input.textChanged.connect(self.apply_filters)
        self.search_input.setMinimumHeight(40)
        
        self.method_filter = QComboBox()
        self.method_filter.addItem("💳 Toutes les méthodes", None)
        for method in PaymentMethod:
            self.method_filter.addItem(method.value, method)
        self.method_filter.currentIndexChanged.connect(self.apply_filters)
        self.method_filter.setMinimumHeight(40)
        
        filter_layout.addWidget(self.search_input, stretch=3)
        filter_layout.addWidget(self.method_filter, stretch=1)
        
        layout.addLayout(filter_layout)
    
    def create_stats(self, layout):
        """Créer les statistiques"""
        stats_layout = QHBoxLayout()
        
        self.total_label = QLabel("Total: 0")
        self.today_label = QLabel("Aujourd'hui: 0 DH")
        self.month_label = QLabel("Ce Mois: 0 DH")
        
        for label in [self.total_label, self.today_label, self.month_label]:
            label.setStyleSheet("""
                QLabel {
                    background-color: white;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                    color: #27ae60;
                    border: 2px solid #ecf0f1;
                }
            """)
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.today_label)
        stats_layout.addWidget(self.month_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
    
    def create_table(self, layout):
        """Créer le tableau"""
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "N° Reçu", "Date", "Élève", "Montant (DH)", 
            "Méthode", "Catégorie", "Statut", "Actions"
        ])
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(400)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.table)
    
    def load_payments(self):
        """Charger tous les paiements"""
        self.payments = PaymentController.get_all_payments()
        self.update_stats()
        self.populate_table()
    
    def update_stats(self):
        """Mettre à jour les statistiques"""
        total = len(self.payments)
        
        today = datetime.now().date()
        today_amount = sum(p.amount for p in self.payments 
                          if p.payment_date.date() == today)
        
        month = datetime.now().month
        year = datetime.now().year
        month_amount = sum(p.amount for p in self.payments 
                          if p.payment_date.month == month and p.payment_date.year == year)
        
        self.total_label.setText(f"Total: {total}")
        self.today_label.setText(f"Aujourd'hui: {today_amount:,.2f} DH")
        self.month_label.setText(f"Ce Mois: {month_amount:,.2f} DH")
    
    def apply_filters(self):
        """Appliquer les filtres"""
        # TODO: Implémenter le filtrage
        self.populate_table()
    
    def populate_table(self):
        """Remplir le tableau"""
        self.table.setRowCount(0)
        
        for row, payment in enumerate(self.payments[:50]):  # Limiter à 50 pour performance
            self.table.insertRow(row)
            
            # N° Reçu
            self.table.setItem(row, 0, QTableWidgetItem(payment.receipt_number or ""))
            
            # Date
            date_str = payment.payment_date.strftime('%d/%m/%Y') if payment.payment_date else ""
            self.table.setItem(row, 1, QTableWidgetItem(date_str))
            
            # Élève
            student_name = payment.student.full_name if payment.student else "N/A"
            self.table.setItem(row, 2, QTableWidgetItem(student_name))
            
            # Montant
            amount_item = QTableWidgetItem(f"{payment.amount:,.2f}")
            amount_item.setForeground(QColor("#27ae60"))
            self.table.setItem(row, 3, amount_item)
            
            # Méthode
            method = payment.payment_method.value if payment.payment_method else "N/A"
            self.table.setItem(row, 4, QTableWidgetItem(method))
            
            # Catégorie
            category = payment.category.value if payment.category else "N/A"
            self.table.setItem(row, 5, QTableWidgetItem(category))
            
            # Statut
            status = "✅ Validé" if payment.is_validated else "⏳ En attente"
            status_item = QTableWidgetItem(status)
            if payment.is_validated:
                status_item.setForeground(QColor("#27ae60"))
            self.table.setItem(row, 6, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 0, 5, 0)
            
            pdf_btn = QPushButton("📄")
            pdf_btn.setToolTip("Générer reçu PDF")
            pdf_btn.clicked.connect(lambda checked, p=payment: self.generate_receipt(p))
            pdf_btn.setCursor(Qt.PointingHandCursor)
            
            email_btn = QPushButton("📧")
            email_btn.setToolTip("Envoyer par email")
            email_btn.clicked.connect(lambda checked, p=payment: self.send_receipt_email(p))
            email_btn.setCursor(Qt.PointingHandCursor)
            
            actions_layout.addWidget(pdf_btn)
            actions_layout.addWidget(email_btn)
            
            self.table.setCellWidget(row, 7, actions_widget)
    
    def add_payment(self):
        """Ajouter un paiement"""
        dialog = PaymentDialog(parent=self)
        if dialog.exec():
            self.load_payments()
    
    def generate_receipt(self, payment):
        """Générer un reçu PDF"""
        try:
            pdf_gen = get_pdf_generator()
            
            receipt_data = {
                'receipt_number': payment.receipt_number,
                'date': payment.payment_date.strftime('%d/%m/%Y'),
                'student_name': payment.student.full_name,
                'student_cin': payment.student.cin,
                'student_phone': payment.student.phone,
                'amount': payment.amount,
                'payment_method': payment.payment_method.value,
                'description': payment.description or 'Paiement',
                'validated_by': 'Système'
            }
            
            success, result = pdf_gen.generate_receipt(receipt_data)
            
            if success:
                QMessageBox.information(self, "Succès", f"Reçu généré: {result}")
            else:
                QMessageBox.warning(self, "Erreur", result)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def send_receipt_email(self, payment):
        """Envoyer reçu par email"""
        if not payment.student.email:
            QMessageBox.warning(self, "Erreur", "L'élève n'a pas d'adresse email")
            return
        
        try:
            # Générer PDF d'abord
            pdf_gen = get_pdf_generator()
            receipt_data = {
                'receipt_number': payment.receipt_number,
                'date': payment.payment_date.strftime('%d/%m/%Y'),
                'student_name': payment.student.full_name,
                'student_cin': payment.student.cin,
                'student_phone': payment.student.phone,
                'amount': payment.amount,
                'payment_method': payment.payment_method.value,
                'description': payment.description or 'Paiement',
            }
            
            success, pdf_path = pdf_gen.generate_receipt(receipt_data)
            
            if success:
                notif = get_notification_manager()
                notif.send_payment_receipt_email(
                    payment.student.email,
                    receipt_data,
                    pdf_path
                )
                QMessageBox.information(self, "Succès", "Email envoyé avec succès")
            else:
                QMessageBox.warning(self, "Erreur", "Erreur génération PDF")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def export_payments(self):
        """Exporter les paiements"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exporter les paiements",
                f"exports/paiements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if filename:
                success, result = export_to_csv(self.payments, filename, 'payments')
                
                if success:
                    QMessageBox.information(self, "Succès", f"Export réussi: {result}")
                else:
                    QMessageBox.warning(self, "Erreur", result)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
