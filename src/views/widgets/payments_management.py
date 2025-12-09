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

from src.controllers.payment_controller import PaymentController
from src.controllers.student_controller import StudentController
from src.models import PaymentMethod


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
            if student.balance < 0:
                balance_text = f"Dette: {abs(student.balance):,.0f} DH"
            elif student.balance > 0:
                balance_text = f"Crédit: {abs(student.balance):,.0f} DH"
            else:
                balance_text = "À jour"
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
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Barre d'outils (recherche, filtres, actions)
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Table des paiements
        self.table = self.create_table()
        main_layout.addWidget(self.table)
        
        # Footer (statistiques rapides)
        footer = self.create_footer()
        main_layout.addWidget(footer)
    
    def create_header(self) -> QFrame:
        """Créer l'en-tête"""
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #229954);
                border-radius: 8px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("💳 Gestion des Paiements")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Bouton ajouter
        add_btn = QPushButton("➕ Nouveau Paiement")
        add_btn.setMinimumHeight(35)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #27ae60;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
            }
        """)
        add_btn.clicked.connect(self.add_payment)
        layout.addWidget(add_btn)
        
        return header
    
    def create_toolbar(self) -> QFrame:
        """Créer la barre d'outils"""
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setSpacing(10)
        
        # Recherche
        search_label = QLabel("🔍")
        layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par nom, reçu, montant...")
        self.search_input.setMinimumHeight(35)
        self.search_input.textChanged.connect(self.filter_payments)
        layout.addWidget(self.search_input, stretch=1)
        
        # Filtre méthode
        self.method_filter = QComboBox()
        self.method_filter.setMinimumHeight(35)
        self.method_filter.addItem("Toutes les méthodes", None)
        for method in PaymentMethod:
            self.method_filter.addItem(method.value.replace('_', ' ').title(), method)
        self.method_filter.currentIndexChanged.connect(self.filter_payments)
        layout.addWidget(self.method_filter)
        
        # Filtre statut
        self.status_filter = QComboBox()
        self.status_filter.setMinimumHeight(35)
        self.status_filter.addItem("Tous les statuts", None)
        self.status_filter.addItem("✅ Validés", "validated")
        self.status_filter.addItem("⏳ En attente", "pending")
        self.status_filter.addItem("❌ Annulés", "cancelled")
        self.status_filter.currentIndexChanged.connect(self.filter_payments)
        layout.addWidget(self.status_filter)
        
        # Bouton exporter
        export_btn = QPushButton("📊 Exporter")
        export_btn.setMinimumHeight(35)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        export_btn.clicked.connect(self.export_payments)
        layout.addWidget(export_btn)
        
        # Bouton rafraîchir
        refresh_btn = QPushButton("🔄")
        refresh_btn.setMinimumHeight(35)
        refresh_btn.setFixedWidth(45)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        refresh_btn.clicked.connect(self.load_payments)
        layout.addWidget(refresh_btn)
        
        return toolbar
    
    def create_table(self) -> QTableWidget:
        """Créer la table des paiements"""
        table = QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels([
            "Date", "N° Reçu", "Élève", "Montant", "Méthode",
            "Catégorie", "Statut", "Validé par", "Actions"
        ])
        
        # Style
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setStyleSheet("""
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
                background-color: #27ae60;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Ajuster colonnes
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Reçu
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Élève
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Montant
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Méthode
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Catégorie
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Statut
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Validé par
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Actions
        
        table.verticalHeader().setVisible(False)
        
        return table
    
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
    
    def display_payments(self, payments: list):
        """Afficher les paiements dans la table"""
        self.table.setRowCount(0)
        
        # Récupérer infos élèves
        all_students = {s.id: s for s in StudentController.get_all_students()}
        
        total_amount = 0
        
        for payment in payments:
            if payment.is_cancelled:
                continue  # Ne pas afficher les annulés pour l'instant
            
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
            
            # Montant
            amount_item = QTableWidgetItem(f"{payment.amount:,.2f} DH")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amount_item.setForeground(QColor("#27ae60"))
            amount_font = QFont()
            amount_font.setBold(True)
            amount_item.setFont(amount_font)
            self.table.setItem(row, 3, amount_item)
            total_amount += payment.amount
            
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
            
            # Actions (bouton PDF)
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            pdf_btn = QPushButton("📄")
            pdf_btn.setFixedSize(30, 30)
            pdf_btn.setToolTip("Générer PDF")
            pdf_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            pdf_btn.clicked.connect(lambda checked, p=payment: self.generate_pdf(p))
            actions_layout.addWidget(pdf_btn)
            
            self.table.setCellWidget(row, 8, actions_widget)
        
        # Mettre à jour footer
        self.total_label.setText(f"Total: {len(payments)} paiements")
        self.sum_label.setText(f"Montant total: {total_amount:,.2f} DH")
    
    def filter_payments(self):
        """Filtrer les paiements selon critères"""
        search_text = self.search_input.text().lower()
        method_filter = self.method_filter.currentData()
        status_filter = self.status_filter.currentData()
        
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
            
            filtered.append(payment)
        
        self.display_payments(filtered)
    
    def add_payment(self):
        """Ouvrir dialogue ajout paiement"""
        dialog = AddPaymentDialog(self)
        dialog.payment_added.connect(self.load_payments)
        dialog.exec()
    
    def generate_pdf(self, payment):
        """Générer PDF pour un paiement"""
        if not payment.receipt_number:
            QMessageBox.warning(self, "Erreur", "Ce paiement n'a pas de numéro de reçu")
            return
        
        success, result = PaymentController.generate_receipt_pdf(payment.id)
        if success:
            QMessageBox.information(self, "Succès", f"Reçu PDF généré :\n{result}")
        else:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération :\n{result}")
    
    def export_payments(self):
        """Exporter les paiements en CSV"""
        if not self.all_payments:
            QMessageBox.warning(self, "Erreur", "Aucun paiement à exporter")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les paiements",
            f"paiements_{date.today().strftime('%Y%m%d')}.csv",
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
                        student = all_students.get(p.student_id)
                        writer.writerow([
                            p.payment_date.strftime('%d/%m/%Y') if p.payment_date else '',
                            p.receipt_number or '',
                            student.full_name if student else '',
                            p.amount,
                            p.payment_method.value,
                            p.category or '',
                            p.status,
                            p.validated_by or '',
                            p.reference_number or ''
                        ])
                
                QMessageBox.information(self, "Succès", f"Paiements exportés vers :\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export :\n{str(e)}")
