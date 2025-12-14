"""
Widget de gestion des élèves avec fonctionnalités complètes
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QGroupBox,
    QTabWidget, QListWidget, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from datetime import datetime
from functools import partial

from src.controllers.student_controller import StudentController
from src.controllers.payment_controller import PaymentController
from src.controllers.session_controller import SessionController
from src.models import StudentStatus
from src.utils import export_to_csv, get_pdf_generator
from src.views.widgets.student_detail_view import StudentDetailViewDialog
from src.views.widgets.csv_import_dialog import CSVImportDialog

# Types de permis disponibles
LICENSE_TYPES = ['A', 'B', 'C', 'D', 'E']


class StudentDetailDialog(QDialog):
    """Dialogue de détail/édition d'un élève"""
    
    def __init__(self, student=None, parent=None):
        super().__init__(parent)
        self.student = student
        self.setWindowTitle("Détail Élève" if student else "Nouvel Élève")
        self.setMinimumSize(700, 600)
        self.setup_ui()
        
        if student:
            self.load_student_data()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        
        # Onglets
        tabs = QTabWidget()
        
        # Onglet Informations générales
        info_tab = QWidget()
        info_layout = QFormLayout(info_tab)
        
        self.full_name = QLineEdit()
        self.cin = QLineEdit()
        self.date_of_birth = QDateEdit()
        self.date_of_birth.setCalendarPopup(True)
        self.date_of_birth.setDate(QDate.currentDate().addYears(-18))
        
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.address = QTextEdit()
        self.address.setMaximumHeight(80)
        
        self.license_type = QComboBox()
        for lic in LICENSE_TYPES:
            self.license_type.addItem(lic, lic)
        
        self.status = QComboBox()
        for st in StudentStatus:
            self.status.addItem(st.value.capitalize(), st)
        
        info_layout.addRow("Nom Complet*:", self.full_name)
        info_layout.addRow("CIN*:", self.cin)
        info_layout.addRow("Date de Naissance*:", self.date_of_birth)
        info_layout.addRow("Téléphone*:", self.phone)
        info_layout.addRow("Email:", self.email)
        info_layout.addRow("Adresse:", self.address)
        info_layout.addRow("Type de Permis:", self.license_type)
        info_layout.addRow("Statut:", self.status)
        
        tabs.addTab(info_tab, "📋 Informations")
        
        # Onglet Formation
        training_tab = QWidget()
        training_layout = QFormLayout(training_tab)
        
        self.hours_planned = QSpinBox()
        self.hours_planned.setMinimum(1)
        self.hours_planned.setMaximum(100)
        self.hours_planned.setValue(20)
        
        self.hours_completed = QSpinBox()
        self.hours_completed.setMinimum(0)
        self.hours_completed.setMaximum(100)
        
        self.theory_test_attempts = QSpinBox()
        self.theory_test_attempts.setMinimum(0)
        
        self.practical_test_attempts = QSpinBox()
        self.practical_test_attempts.setMinimum(0)
        
        training_layout.addRow("Heures Planifiées:", self.hours_planned)
        training_layout.addRow("Heures Effectuées:", self.hours_completed)
        training_layout.addRow("Tentatives Théorie:", self.theory_test_attempts)
        training_layout.addRow("Tentatives Pratique:", self.practical_test_attempts)
        
        tabs.addTab(training_tab, "🎓 Formation")
        
        # Onglet Paiements
        payment_tab = QWidget()
        payment_layout = QFormLayout(payment_tab)
        
        self.total_due = QDoubleSpinBox()
        self.total_due.setMinimum(0)
        self.total_due.setMaximum(999999)
        self.total_due.setValue(0)
        self.total_due.setSuffix(" DH")
        # Connect signal to recalculate balance when total_due changes
        self.total_due.valueChanged.connect(self.update_balance_display)
        
        self.total_paid = QDoubleSpinBox()
        self.total_paid.setMinimum(0)
        self.total_paid.setMaximum(999999)
        self.total_paid.setEnabled(False)
        self.total_paid.setSuffix(" DH")
        
        self.balance = QDoubleSpinBox()
        self.balance.setMinimum(-999999)
        self.balance.setMaximum(999999)
        self.balance.setEnabled(False)
        self.balance.setSuffix(" DH")
        
        payment_layout.addRow("Montant Total Dû:", self.total_due)
        payment_layout.addRow("Total Payé:", self.total_paid)
        payment_layout.addRow("Solde:", self.balance)
        
        tabs.addTab(payment_tab, "💰 Paiements")
        
        layout.addWidget(tabs)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.clicked.connect(self.save_student)
        save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold;")
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("background-color: #95a5a6; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold;")
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def load_student_data(self):
        """Charger les données de l'élève"""
        if not self.student:
            return
        
        self.full_name.setText(self.student.full_name)
        self.cin.setText(self.student.cin or "")
        
        if self.student.date_of_birth:
            self.date_of_birth.setDate(QDate(
                self.student.date_of_birth.year,
                self.student.date_of_birth.month,
                self.student.date_of_birth.day
            ))
        
        self.phone.setText(self.student.phone or "")
        self.email.setText(self.student.email or "")
        self.address.setPlainText(self.student.address or "")
        
        # License type
        for i in range(self.license_type.count()):
            if self.license_type.itemData(i) == self.student.license_type:
                self.license_type.setCurrentIndex(i)
                break
        
        # Status
        for i in range(self.status.count()):
            if self.status.itemData(i) == self.student.status:
                self.status.setCurrentIndex(i)
                break
        
        self.hours_planned.setValue(self.student.hours_planned or 20)
        self.hours_completed.setValue(self.student.hours_completed or 0)
        self.theory_test_attempts.setValue(self.student.theoretical_exam_attempts or 0)
        self.practical_test_attempts.setValue(self.student.practical_exam_attempts or 0)
        
        self.total_due.setValue(self.student.total_due or 0)
        self.total_paid.setValue(self.student.total_paid or 0)
        self.balance.setValue(self.student.balance or 0)
    
    def update_balance_display(self):
        """Update balance display when total_due changes"""
        try:
            # Calculate new balance: Total Paid - Total Due
            # Positive = CRÉDIT (trop-perçu), Negative = DETTE, Zero = À jour
            total_paid = self.total_paid.value()
            total_due = self.total_due.value()
            new_balance = total_paid - total_due
            
            # Update balance field
            self.balance.setValue(new_balance)
            
        except Exception as e:
            print(f"Error updating balance display: {e}")
    
    def save_student(self):
        """Enregistrer l'élève"""
        # Validation
        if not self.full_name.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom complet est requis")
            return
        
        if not self.cin.text().strip():
            QMessageBox.warning(self, "Erreur", "Le CIN est requis")
            return
        
        if not self.phone.text().strip():
            QMessageBox.warning(self, "Erreur", "Le téléphone est requis")
            return
        
        # Collecter les données
        data = {
            'full_name': self.full_name.text().strip(),
            'cin': self.cin.text().strip(),
            'date_of_birth': self.date_of_birth.date().toPython(),
            'phone': self.phone.text().strip(),
            'email': self.email.text().strip() or None,
            'address': self.address.toPlainText().strip() or None,
            'license_type': self.license_type.currentData(),
            'status': self.status.currentData(),
            'hours_planned': self.hours_planned.value(),
            'hours_completed': self.hours_completed.value(),
            'theoretical_exam_attempts': self.theory_test_attempts.value(),
            'practical_exam_attempts': self.practical_test_attempts.value(),
            'total_due': self.total_due.value(),
        }
        
        try:
            if self.student:
                # Mise à jour
                StudentController.update_student(self.student.id, data)
                QMessageBox.information(self, "Succès", "Élève mis à jour avec succès")
            else:
                # Création
                StudentController.create_student(data)
                QMessageBox.information(self, "Succès", "Élève créé avec succès")
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement : {str(e)}")


class StudentsEnhancedWidget(QWidget):
    """Widget de gestion des élèves avec toutes les fonctionnalités"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.students = []
        self.filtered_students = []
        self.setup_ui()
        self.load_students()
    
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
        
        # Tableau des élèves
        self.create_table(layout)
    
    def create_header(self, layout):
        """Créer l'en-tête"""
        header_layout = QHBoxLayout()
        
        # Barre de recherche à gauche
        self.header_search = QLineEdit()
        self.header_search.setPlaceholderText("🔍 Rechercher par nom, CIN ou téléphone...")
        self.header_search.textChanged.connect(self.apply_filters)
        self.header_search.setMinimumHeight(40)
        self.header_search.setStyleSheet("""
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
        header_layout.addWidget(self.header_search, stretch=2)
        
        header_layout.addStretch()
        
        # Boutons
        add_btn = QPushButton("➕ Nouvel Élève")
        add_btn.clicked.connect(self.add_student)
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
        
        import_btn = QPushButton("📥 Importer CSV")
        import_btn.clicked.connect(self.import_csv)
        import_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        import_btn.setCursor(Qt.PointingHandCursor)
        
        export_btn = QPushButton("📤 Exporter CSV")
        export_btn.clicked.connect(self.export_csv)
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
        refresh_btn.clicked.connect(self.load_students)
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
        header_layout.addWidget(import_btn)
        header_layout.addWidget(export_btn)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
    
    def create_search_bar(self, layout):
        """Créer la barre de filtres"""
        search_layout = QHBoxLayout()
        
        self.status_filter = QComboBox()
        self.status_filter.addItem("📊 Tous les statuts", None)
        for status in StudentStatus:
            self.status_filter.addItem(status.value.capitalize(), status)
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        self.status_filter.setMinimumHeight(40)
        self.status_filter.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 13px;
            }
        """)
        
        self.license_filter = QComboBox()
        self.license_filter.addItem("🚗 Tous les permis", None)
        for lic in LICENSE_TYPES:
            self.license_filter.addItem(f"Permis {lic}", lic)
        self.license_filter.currentIndexChanged.connect(self.apply_filters)
        self.license_filter.setMinimumHeight(40)
        self.license_filter.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 13px;
            }
        """)
        
        search_layout.addWidget(self.status_filter, stretch=1)
        search_layout.addWidget(self.license_filter, stretch=1)
        search_layout.addStretch()
        
        layout.addLayout(search_layout)
    
    def create_stats(self, layout):
        """Créer les statistiques rapides"""
        stats_layout = QHBoxLayout()
        
        self.total_label = QLabel("Total: 0")
        self.active_label = QLabel("Actifs: 0")
        self.debt_label = QLabel("Dettes: 0")
        self.graduated_label = QLabel("Diplômés: 0")
        
        for label in [self.total_label, self.active_label, self.debt_label, self.graduated_label]:
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
        stats_layout.addWidget(self.active_label)
        stats_layout.addWidget(self.debt_label)
        stats_layout.addWidget(self.graduated_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
    
    def create_table(self, layout):
        """Créer le tableau"""
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom Complet", "CIN", "Téléphone", "Permis",
            "Statut", "Heures", "Prochaine Séance", "Solde (DH)", "Actions"
        ])
        
        # Configuration
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(400)
        
        # Style
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
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.table)
    
    def load_students(self):
        """Charger tous les élèves"""
        self.students = StudentController.get_all_students()
        self.filtered_students = self.students.copy()
        self.update_stats()
        self.populate_table()
    
    def apply_filters(self):
        """Appliquer les filtres"""
        search_text = self.header_search.text().lower()
        status_filter = self.status_filter.currentData()
        license_filter = self.license_filter.currentData()
        
        self.filtered_students = []
        
        for student in self.students:
            # Filtre texte
            if search_text:
                if not (search_text in student.full_name.lower() or
                       (student.cin and search_text in student.cin.lower()) or
                       (student.phone and search_text in student.phone)):
                    continue
            
            # Filtre statut
            if status_filter and student.status != status_filter:
                continue
            
            # Filtre permis
            if license_filter and student.license_type != license_filter:
                continue
            
            self.filtered_students.append(student)
        
        self.populate_table()
    
    def update_stats(self):
        """Mettre à jour les statistiques"""
        total = len(self.students)
        active = len([s for s in self.students if s.status == StudentStatus.ACTIVE])
        debt = len([s for s in self.students if s.balance < 0])
        graduated = len([s for s in self.students if s.status == StudentStatus.GRADUATED])
        
        self.total_label.setText(f"Total: {total}")
        self.active_label.setText(f"Actifs: {active}")
        self.debt_label.setText(f"Dettes: {debt}")
        self.graduated_label.setText(f"Diplômés: {graduated}")
    
    def populate_table(self):
        """Remplir le tableau"""
        self.table.setRowCount(0)
        
        for row, student in enumerate(self.filtered_students):
            self.table.insertRow(row)
            
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(student.id)))
            
            # Nom
            self.table.setItem(row, 1, QTableWidgetItem(student.full_name))
            
            # CIN
            self.table.setItem(row, 2, QTableWidgetItem(student.cin or ""))
            
            # Téléphone
            self.table.setItem(row, 3, QTableWidgetItem(student.phone or ""))
            
            # Permis
            license_val = student.license_type if student.license_type else "N/A"
            self.table.setItem(row, 4, QTableWidgetItem(str(license_val)))
            
            # Statut avec badges colorés
            status_icons = {
                StudentStatus.ACTIVE: "🟢",
                StudentStatus.PENDING: "🟡",
                StudentStatus.SUSPENDED: "🔴",
                StudentStatus.GRADUATED: "🎓",
                StudentStatus.ABANDONED: "⚫"
            }
            status_colors = {
                StudentStatus.ACTIVE: "#27ae60",
                StudentStatus.PENDING: "#f39c12",
                StudentStatus.SUSPENDED: "#e74c3c",
                StudentStatus.GRADUATED: "#3498db",
                StudentStatus.ABANDONED: "#95a5a6"
            }
            status_icon = status_icons.get(student.status, "❓")
            status_text = f"{status_icon} {student.status.value.capitalize()}" if student.status else "N/A"
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor(status_colors.get(student.status, "#2c3e50")))
            font = QFont()
            font.setBold(True)
            status_item.setFont(font)
            self.table.setItem(row, 5, status_item)
            
            # Heures
            hours_text = f"{student.hours_completed}/{student.hours_planned}"
            self.table.setItem(row, 6, QTableWidgetItem(hours_text))
            
            # Prochaine séance (à implémenter - pour l'instant placeholder)
            try:
                from datetime import datetime, timedelta
                # TODO: Récupérer vraiment la prochaine séance depuis la DB
                next_session_text = "—"  # Placeholder
                next_session_item = QTableWidgetItem(next_session_text)
                next_session_item.setForeground(QColor("#7f8c8d"))
                self.table.setItem(row, 7, next_session_item)
            except:
                self.table.setItem(row, 7, QTableWidgetItem("—"))
            
            # Solde (Balance = total_paid - total_due, negative = dette)
            # Simple display: just +/- amount, no text
            if student.balance == 0:
                balance_text = "0.00"
            else:
                balance_text = f"{student.balance:+,.2f}"
            balance_item = QTableWidgetItem(balance_text)
            balance_item.setForeground(QColor("#e74c3c") if student.balance < 0 else QColor("#27ae60"))
            font = QFont()
            font.setBold(True)
            balance_item.setFont(font)
            self.table.setItem(row, 8, balance_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 0, 5, 0)
            
            view_btn = QPushButton("👁️")
            view_btn.setToolTip("Voir détails")
            view_btn.clicked.connect(partial(self.view_student, student))
            view_btn.setCursor(Qt.PointingHandCursor)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Modifier")
            edit_btn.clicked.connect(partial(self.edit_student, student))
            edit_btn.setCursor(Qt.PointingHandCursor)
            
            contract_btn = QPushButton("📄")
            contract_btn.setToolTip("Générer contrat")
            contract_btn.clicked.connect(partial(self.generate_contract, student))
            contract_btn.setCursor(Qt.PointingHandCursor)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Supprimer")
            delete_btn.clicked.connect(partial(self.delete_student, student))
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
            actions_layout.addWidget(contract_btn)
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 9, actions_widget)
    
    def add_student(self):
        """Ajouter un élève avec le formulaire simplifié"""
        from src.views.widgets.student_form_simplified import StudentFormSimplified
        dialog = StudentFormSimplified(student=None, parent=self)
        dialog.student_saved.connect(lambda student: self.load_students())
        dialog.exec()
    
    def edit_student(self, student):
        """Modifier un élève avec vue complète"""
        dialog = StudentDetailViewDialog(student, parent=self, read_only=False)
        if dialog.exec():
            self.load_students()
    
    def view_student(self, student):
        """Voir les détails d'un élève avec vue complète"""
        dialog = StudentDetailViewDialog(student, parent=self, read_only=True)
        dialog.exec()
    
    def generate_contract(self, student):
        """Générer un contrat PDF"""
        try:
            pdf_gen = get_pdf_generator()
            
            student_data = {
                'full_name': student.full_name,
                'cin': student.cin,
                'date_of_birth': student.date_of_birth.strftime('%d/%m/%Y') if student.date_of_birth else 'N/A',
                'phone': student.phone,
                'address': student.address or 'N/A',
                'license_type': student.license_type if student.license_type else 'B',
                'hours_planned': student.hours_planned or 20,
                'total_due': student.total_due or 0
            }
            
            success, result = pdf_gen.generate_contract(student_data)
            
            if success:
                QMessageBox.information(self, "Succès", 
                                       f"Contrat généré avec succès:\n{result}")
            else:
                QMessageBox.warning(self, "Erreur", result)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def export_csv(self):
        """Exporter en CSV"""
        try:
            from pathlib import Path
            from src.utils import get_logger
            logger = get_logger()
            
            # Utiliser EXPORTS_DIR depuis config
            try:
                from src.config import EXPORTS_DIR, init_export_folders
                init_export_folders()
                default_dir = str(EXPORTS_DIR) if EXPORTS_DIR else "exports"
            except:
                default_dir = "exports"
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exporter les élèves", 
                f"{default_dir}/eleves_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if filename:
                logger.info(f"Students export: QFileDialog returned filename={filename}")
                # Extract just the filename without extension
                basename = Path(filename).stem
                logger.info(f"Students export: Extracted basename={basename}")
                logger.info(f"Students export: Calling export_to_csv with {len(self.filtered_students)} students")
                success, result = export_to_csv(self.filtered_students, basename)
                
                if success:
                    QMessageBox.information(self, "Succès", f"Export réussi: {result}")
                else:
                    QMessageBox.warning(self, "Erreur", result)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def delete_student(self, student):
        """Supprimer un élève avec confirmation"""
        # Check for related payments
        try:
            payments = PaymentController.get_payments_by_student(student.id)
            sessions = SessionController.get_student_sessions(student.id)
            
            # Build warning message
            warning_parts = []
            if len(payments) > 0:
                total_paid = sum(p.amount for p in payments)
                warning_parts.append(f"• {len(payments)} paiement(s) (Total: {total_paid:,.2f} DH)")
            
            if len(sessions) > 0:
                warning_parts.append(f"• {len(sessions)} séance(s) de formation")
            
            # Confirmation dialog
            if warning_parts:
                warning_msg = (
                    f"⚠️ ATTENTION\n\n"
                    f"L'élève {student.full_name} a des données associées:\n\n" +
                    "\n".join(warning_parts) +
                    f"\n\nLa suppression de cet élève supprimera également "
                    f"toutes ces données associées.\n\n"
                    f"Cette action est IRRÉVERSIBLE!\n\n"
                    f"Êtes-vous absolument sûr de vouloir continuer?"
                )
            else:
                warning_msg = (
                    f"Êtes-vous sûr de vouloir supprimer l'élève:\n\n"
                    f"👤 {student.full_name}\n"
                    f"🆔 CIN: {student.cin}\n\n"
                    f"Cette action est IRRÉVERSIBLE!"
                )
            
            reply = QMessageBox.warning(
                self,
                "⚠️ Confirmer la Suppression",
                warning_msg,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No  # Default to No for safety
            )
            
            if reply == QMessageBox.Yes:
                # Double confirmation for students with data
                if warning_parts:
                    final_reply = QMessageBox.critical(
                        self,
                        "🛑 DERNIÈRE CONFIRMATION",
                        f"DERNIÈRE CHANCE!\n\n"
                        f"Vous êtes sur le point de supprimer {student.full_name} "
                        f"et TOUTES ses données.\n\n"
                        f"Tapez 'SUPPRIMER' pour confirmer:",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    
                    if final_reply != QMessageBox.Yes:
                        return
                
                # Perform deletion
                StudentController.delete_student(student.id)
                QMessageBox.information(
                    self,
                    "Succès",
                    f"L'élève {student.full_name} a été supprimé avec succès."
                )
                self.load_students()
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de la suppression:\n{str(e)}"
            )
    
    def import_csv(self):
        """Importer depuis CSV avec validation complète"""
        dialog = CSVImportDialog(parent=self)
        if dialog.exec():
            # Reload students after successful import
            self.load_students()
            QMessageBox.information(self, "Succès", "Les élèves ont été importés avec succès!")
