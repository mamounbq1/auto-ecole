"""
Comprehensive Student Detail View Dialog with 7 tabs
All tabs are fully functional except 'Progression' (to be improved later)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QGroupBox,
    QTabWidget, QListWidget, QFileDialog, QScrollArea
)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QFont, QColor, QPixmap
from datetime import datetime
import os

from src.controllers.student_controller import StudentController
from src.controllers.payment_controller import PaymentController
from src.controllers.session_controller import SessionController
from src.controllers.document_controller import DocumentController
from src.controllers.exam_controller import ExamController
from src.models import StudentStatus
from src.utils.validators import StudentValidator

# Types de permis disponibles
LICENSE_TYPES = ['A', 'B', 'C', 'D', 'E']


class StudentDetailViewDialog(QDialog):
    """
    Comprehensive Student Detail View Dialog with 7 tabs:
    1. Informations - General information with profile photo
    2. Paiements - Payment history and financial summary
    3. Séances - Training session history
    4. Progression - Visual progress tracking (to be improved later)
    5. Documents - Document management
    6. Historique - Complete activity history
    7. Notes - Administrative notes
    """
    
    def __init__(self, student=None, parent=None, read_only=False):
        super().__init__(parent)
        self.read_only = read_only
        self.photo_path = None
        
        # CRITICAL: Reload student from database BEFORE creating UI
        if student:
            from src.models import get_session, Student
            from decimal import Decimal
            
            # Get current session and commit any pending changes
            session = get_session()
            try:
                session.commit()  # Commit any pending changes first
            except:
                session.rollback()
            
            # Expire all and force fresh query
            session.expire_all()
            
            # Query directly - this will hit the database, not cache
            self.student = session.query(Student).filter(Student.id == student.id).first()
            
            if self.student:
                # Force recalculate balance from DB values to ensure accuracy
                paid = Decimal(str(float(self.student.total_paid) if self.student.total_paid else 0.0))
                due = Decimal(str(float(self.student.total_due) if self.student.total_due else 0.0))
                calculated_balance = paid - due
                
                # Use the freshly calculated balance (this is correct from DB)
                self.student.balance = calculated_balance
                
                print(f"[DEBUG] Student {self.student.full_name}: balance={self.student.balance}")
            else:
                self.student = student  # Fallback to passed object
        else:
            self.student = None
        
        # Set window properties AFTER reloading student
        self.setWindowTitle("Vue Détaillée - " + (self.student.full_name if self.student else "Nouvel Élève"))
        self.setMinimumSize(900, 700)
        
        # Setup UI (NOW self.student has the correct balance)
        self.setup_ui()
        
        # Load data if editing
        if self.student:
            try:
                self.load_student_data()
            except Exception as e:
                QMessageBox.warning(self, "Avertissement", 
                    f"Erreur lors du chargement des données: {str(e)}")
                print(f"Error loading student data: {e}")
    
    def setup_ui(self):
        """Setup the complete user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header with student info
        if self.student:
            self.create_header(main_layout)
        
        # Tab widget with all tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #bdc3c7;
            }
        """)
        
        # Create all tabs
        self.create_info_tab()
        self.create_payments_tab()
        self.create_sessions_tab()
        self.create_progress_tab()
        self.create_documents_tab()
        self.create_history_tab()
        self.create_notes_tab()
        
        main_layout.addWidget(self.tabs)
        
        # Bottom buttons
        self.create_buttons(main_layout)
    
    def create_header(self, layout):
        """Create header with student summary"""
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        
        # Student name and status
        info_layout = QVBoxLayout()
        
        name_label = QLabel(self.student.full_name)
        name_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        
        status_text = self.student.status.value.capitalize() if self.student.status else "N/A"
        status_label = QLabel(f"Statut: {status_text} | Permis: {self.student.license_type or 'N/A'}")
        status_label.setStyleSheet("color: white; font-size: 14px;")
        
        progress_text = f"Progression: {self.student.hours_completed}/{self.student.hours_planned} heures"
        progress_label = QLabel(progress_text)
        progress_label.setStyleSheet("color: white; font-size: 14px;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(status_label)
        info_layout.addWidget(progress_label)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        # Quick stats
        stats_layout = QVBoxLayout()
        
        # Balance = total_paid - total_due
        # Simple display: just show +/- amount (no "Dette"/"Crédit" text)
        # CRITICAL: Convert to float to ensure we get the latest value
        balance_val = float(self.student.balance) if self.student.balance else 0.0
        balance_color = "#e74c3c" if balance_val < 0 else "#27ae60"
        if balance_val == 0:
            balance_text = "0.00 DH"
        else:
            balance_text = f"{balance_val:+,.2f} DH"
        self.balance_label = QLabel(balance_text)
        self.balance_label.setStyleSheet(f"color: {balance_color}; font-size: 18px; font-weight: bold; background-color: white; padding: 8px 15px; border-radius: 5px;")
        
        completion = (self.student.hours_completed / self.student.hours_planned * 100) if self.student.hours_planned > 0 else 0
        completion_label = QLabel(f"Taux de complétion: {completion:.1f}%")
        completion_label.setStyleSheet("color: white; font-size: 14px;")
        
        # Refresh button next to balance
        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Rafraîchir le solde")
        refresh_btn.setFixedSize(40, 40)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #ecf0f1;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_balance)
        
        balance_with_refresh = QHBoxLayout()
        balance_with_refresh.addWidget(self.balance_label)
        balance_with_refresh.addWidget(refresh_btn)
        
        stats_layout.addLayout(balance_with_refresh)
        stats_layout.addWidget(completion_label)
        
        header_layout.addLayout(stats_layout)
        
        layout.addWidget(header_widget)
    
    def create_info_tab(self):
        """Tab 1: General Information with Profile Photo"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Left side: Photo
        photo_layout = QVBoxLayout()
        photo_layout.setAlignment(Qt.AlignTop)
        
        # Photo display
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(200, 200)
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 3px solid #3498db;
                border-radius: 10px;
                background-color: #ecf0f1;
            }
        """)
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setScaledContents(True)
        
        # Set default photo or load existing
        if self.student and hasattr(self.student, 'photo_path') and self.student.photo_path:
            if os.path.exists(self.student.photo_path):
                pixmap = QPixmap(self.student.photo_path)
                self.photo_label.setPixmap(pixmap)
            else:
                self.photo_label.setText("Aucune\nPhoto")
        else:
            self.photo_label.setText("Aucune\nPhoto")
        
        photo_layout.addWidget(self.photo_label)
        
        # Photo buttons
        if not self.read_only:
            upload_photo_btn = QPushButton("📷 Télécharger Photo")
            upload_photo_btn.clicked.connect(self.upload_photo)
            upload_photo_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            photo_layout.addWidget(upload_photo_btn)
            
            delete_photo_btn = QPushButton("🗑️ Supprimer Photo")
            delete_photo_btn.clicked.connect(self.delete_photo)
            delete_photo_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            photo_layout.addWidget(delete_photo_btn)
        
        photo_layout.addStretch()
        layout.addLayout(photo_layout)
        
        # Right side: Form
        form_scroll = QScrollArea()
        form_scroll.setWidgetResizable(True)
        form_scroll.setFrameShape(QScrollArea.NoFrame)
        
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)
        
        # Personal Information Group
        personal_group = QGroupBox("Informations Personnelles")
        personal_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        personal_layout = QFormLayout()
        
        self.full_name = QLineEdit()
        self.full_name.setReadOnly(self.read_only)
        self.cin = QLineEdit()
        self.cin.setReadOnly(self.read_only)
        self.date_of_birth = QDateEdit()
        self.date_of_birth.setCalendarPopup(True)
        self.date_of_birth.setDate(QDate.currentDate().addYears(-18))
        self.date_of_birth.setReadOnly(self.read_only)
        
        self.phone = QLineEdit()
        self.phone.setReadOnly(self.read_only)
        self.email = QLineEdit()
        self.email.setReadOnly(self.read_only)
        self.address = QTextEdit()
        self.address.setMaximumHeight(80)
        self.address.setReadOnly(self.read_only)
        
        personal_layout.addRow("📝 Nom Complet*:", self.full_name)
        personal_layout.addRow("🆔 CIN*:", self.cin)
        personal_layout.addRow("📅 Date de Naissance*:", self.date_of_birth)
        personal_layout.addRow("📱 Téléphone*:", self.phone)
        personal_layout.addRow("📧 Email:", self.email)
        personal_layout.addRow("🏠 Adresse:", self.address)
        
        personal_group.setLayout(personal_layout)
        form_layout.addRow(personal_group)
        
        # License Information Group
        license_group = QGroupBox("Informations Permis")
        license_group.setStyleSheet(personal_group.styleSheet())
        license_layout = QFormLayout()
        
        self.license_type = QComboBox()
        self.license_type.setEnabled(not self.read_only)
        for lic in LICENSE_TYPES:
            self.license_type.addItem(f"Permis {lic}", lic)
        
        self.status = QComboBox()
        self.status.setEnabled(not self.read_only)
        for st in StudentStatus:
            self.status.addItem(st.value.capitalize(), st)
        
        license_layout.addRow("🚗 Type de Permis:", self.license_type)
        license_layout.addRow("📊 Statut:", self.status)
        
        license_group.setLayout(license_layout)
        form_layout.addRow(license_group)
        
        # Training Information Group
        training_group = QGroupBox("Formation")
        training_group.setStyleSheet(personal_group.styleSheet())
        training_layout = QFormLayout()
        
        self.hours_planned = QSpinBox()
        self.hours_planned.setMinimum(1)
        self.hours_planned.setMaximum(100)
        self.hours_planned.setValue(20)
        self.hours_planned.setReadOnly(self.read_only)
        
        self.hours_completed = QSpinBox()
        self.hours_completed.setMinimum(0)
        self.hours_completed.setMaximum(100)
        self.hours_completed.setReadOnly(self.read_only)
        
        self.theory_test_attempts = QSpinBox()
        self.theory_test_attempts.setMinimum(0)
        self.theory_test_attempts.setReadOnly(self.read_only)
        
        self.practical_test_attempts = QSpinBox()
        self.practical_test_attempts.setMinimum(0)
        self.practical_test_attempts.setReadOnly(self.read_only)
        
        training_layout.addRow("🎯 Heures Planifiées:", self.hours_planned)
        training_layout.addRow("✅ Heures Effectuées:", self.hours_completed)
        training_layout.addRow("📝 Tentatives Théorie:", self.theory_test_attempts)
        training_layout.addRow("🚗 Tentatives Pratique:", self.practical_test_attempts)
        
        training_group.setLayout(training_layout)
        form_layout.addRow(training_group)
        
        # Financial Information Group
        financial_group = QGroupBox("Informations Financières")
        financial_group.setStyleSheet(personal_group.styleSheet())
        financial_layout = QFormLayout()
        
        self.total_due = QDoubleSpinBox()
        self.total_due.setMinimum(0)
        self.total_due.setMaximum(999999)
        self.total_due.setValue(0)
        self.total_due.setSuffix(" DH")
        self.total_due.setReadOnly(self.read_only)
        # Connect signal to recalculate balance when total_due changes
        self.total_due.valueChanged.connect(self.update_balance_display)
        
        self.total_paid = QDoubleSpinBox()
        self.total_paid.setMinimum(0)
        self.total_paid.setMaximum(999999)
        self.total_paid.setSuffix(" DH")
        self.total_paid.setEnabled(False)
        
        self.balance = QDoubleSpinBox()
        self.balance.setMinimum(-999999)
        self.balance.setMaximum(999999)
        self.balance.setSuffix(" DH")
        self.balance.setEnabled(False)
        
        financial_layout.addRow("💵 Montant Total Dû:", self.total_due)
        financial_layout.addRow("✅ Total Payé:", self.total_paid)
        financial_layout.addRow("💰 Solde:", self.balance)
        
        financial_group.setLayout(financial_layout)
        form_layout.addRow(financial_group)
        
        form_scroll.setWidget(form_widget)
        layout.addWidget(form_scroll, stretch=1)
        
        self.tabs.addTab(tab, "📋 Informations")
    
    def create_payments_tab(self):
        """Tab 2: Payment History"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Summary section
        summary_widget = QWidget()
        summary_widget.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        summary_layout = QHBoxLayout(summary_widget)
        
        self.payments_total_label = QLabel("Total Payé: 0.00 DH")
        self.payments_total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60;")
        
        self.payments_count_label = QLabel("Nombre de Paiements: 0")
        self.payments_count_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498db;")
        
        summary_layout.addWidget(self.payments_total_label)
        summary_layout.addStretch()
        summary_layout.addWidget(self.payments_count_label)
        
        layout.addWidget(summary_widget)
        
        # Payments table
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(5)
        self.payments_table.setHorizontalHeaderLabels([
            "Date", "Montant (DH)", "Méthode", "Référence", "Notes"
        ])
        self.payments_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.payments_table.setAlternatingRowColors(True)
        self.payments_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)
        
        layout.addWidget(self.payments_table)
        
        self.tabs.addTab(tab, "💰 Paiements")
    
    def create_sessions_tab(self):
        """Tab 3: Training Sessions History"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Summary section
        summary_widget = QWidget()
        summary_widget.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        summary_layout = QHBoxLayout(summary_widget)
        
        self.sessions_count_label = QLabel("Nombre de Séances: 0")
        self.sessions_count_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498db;")
        
        self.sessions_hours_label = QLabel("Total Heures: 0")
        self.sessions_hours_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60;")
        
        summary_layout.addWidget(self.sessions_count_label)
        summary_layout.addStretch()
        summary_layout.addWidget(self.sessions_hours_label)
        
        layout.addWidget(summary_widget)
        
        # Sessions table
        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(6)
        self.sessions_table.setHorizontalHeaderLabels([
            "Date", "Heure Début", "Heure Fin", "Type", "Instructeur", "Remarques"
        ])
        self.sessions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sessions_table.setAlternatingRowColors(True)
        self.sessions_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)
        
        layout.addWidget(self.sessions_table)
        
        self.tabs.addTab(tab, "🎓 Séances")
    
    def create_progress_tab(self):
        """Tab 4: Progress & Statistics - Placeholder (to be improved later)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Simple placeholder message
        placeholder_widget = QWidget()
        placeholder_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 15px;
                padding: 40px;
            }
        """)
        placeholder_layout = QVBoxLayout(placeholder_widget)
        
        icon_label = QLabel("📈")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 64px;")
        
        title_label = QLabel("Onglet Progression")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #495057; margin-top: 20px;")
        
        message_label = QLabel("Cet onglet sera amélioré prochainement avec :\n\n"
                               "• Progression des heures de conduite\n"
                               "• Suivi des paiements\n"
                               "• Statistiques de formation\n"
                               "• Statistiques d'examens\n"
                               "• Jalons et objectifs")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("font-size: 14px; color: #6c757d; margin-top: 20px; line-height: 1.6;")
        
        placeholder_layout.addWidget(icon_label)
        placeholder_layout.addWidget(title_label)
        placeholder_layout.addWidget(message_label)
        placeholder_layout.addStretch()
        
        layout.addWidget(placeholder_widget)
        layout.addStretch()
        
        self.tabs.addTab(tab, "📈 Progression")
    
    def create_documents_tab(self):
        """Tab 4: Documents Management - Real Documents Integration"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Summary section
        summary_widget = QWidget()
        summary_widget.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        summary_layout = QHBoxLayout(summary_widget)
        
        self.documents_count_label = QLabel("Nombre de Documents: 0")
        self.documents_count_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498db;")
        
        self.documents_size_label = QLabel("Taille Totale: 0 MB")
        self.documents_size_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60;")
        
        summary_layout.addWidget(self.documents_count_label)
        summary_layout.addStretch()
        summary_layout.addWidget(self.documents_size_label)
        
        layout.addWidget(summary_widget)
        
        # Documents table
        self.documents_table = QTableWidget()
        self.documents_table.setColumnCount(5)
        self.documents_table.setHorizontalHeaderLabels([
            "Titre", "Type", "Date d'Ajout", "Taille", "Statut"
        ])
        self.documents_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.documents_table.setAlternatingRowColors(True)
        self.documents_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)
        
        layout.addWidget(self.documents_table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_doc_btn = QPushButton("➕ Ajouter Document")
        add_doc_btn.clicked.connect(self.add_document)
        add_doc_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        view_doc_btn = QPushButton("👁️ Voir Document")
        view_doc_btn.clicked.connect(self.view_document)
        view_doc_btn.setStyleSheet("""
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
        
        delete_doc_btn = QPushButton("🗑️ Supprimer")
        delete_doc_btn.clicked.connect(self.delete_document)
        delete_doc_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        refresh_doc_btn = QPushButton("🔄 Actualiser")
        refresh_doc_btn.clicked.connect(self.load_documents)
        refresh_doc_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        
        btn_layout.addWidget(add_doc_btn)
        btn_layout.addWidget(view_doc_btn)
        btn_layout.addWidget(delete_doc_btn)
        btn_layout.addWidget(refresh_doc_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        self.tabs.addTab(tab, "📁 Documents")
    
    def create_history_tab(self):
        """Tab 5: Complete Activity History - Real Activity Tracking"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Filter section
        filter_widget = QWidget()
        filter_widget.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        filter_layout = QHBoxLayout(filter_widget)
        
        filter_label = QLabel("Filtrer par type:")
        filter_label.setStyleSheet("font-weight: bold;")
        
        self.history_filter = QComboBox()
        self.history_filter.addItem("🔍 Tous", "all")
        self.history_filter.addItem("💰 Paiements", "payments")
        self.history_filter.addItem("🎓 Séances", "sessions")
        self.history_filter.addItem("📝 Examens", "exams")
        self.history_filter.addItem("📄 Documents", "documents")
        self.history_filter.currentIndexChanged.connect(self.load_history)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.history_filter)
        filter_layout.addStretch()
        
        layout.addWidget(filter_widget)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([
            "Date", "Type", "Description", "Détails"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)
        
        layout.addWidget(self.history_table)
        
        self.tabs.addTab(tab, "📜 Historique")
    
    def create_notes_tab(self):
        """Tab 6: Administrative Notes"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Notes editor
        notes_label = QLabel("📝 Notes Administratives:")
        notes_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Ajoutez des notes administratives ici...")
        self.notes_edit.setReadOnly(self.read_only)
        self.notes_edit.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        
        layout.addWidget(notes_label)
        layout.addWidget(self.notes_edit)
        
        self.tabs.addTab(tab, "📝 Notes")
    
    def create_buttons(self, layout):
        """Create bottom action buttons"""
        if self.read_only:
            # Read-only mode: only close button
            btn_layout = QHBoxLayout()
            
            close_btn = QPushButton("❌ Fermer")
            close_btn.clicked.connect(self.reject)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    padding: 12px 30px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            
            btn_layout.addStretch()
            btn_layout.addWidget(close_btn)
            
            layout.addLayout(btn_layout)
        else:
            # Edit mode: save and cancel buttons
            btn_layout = QHBoxLayout()
            
            cancel_btn = QPushButton("❌ Annuler")
            cancel_btn.clicked.connect(self.reject)
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    padding: 12px 30px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            
            save_btn = QPushButton("💾 Enregistrer")
            save_btn.clicked.connect(self.save_student)
            save_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    padding: 12px 30px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            
            btn_layout.addStretch()
            btn_layout.addWidget(cancel_btn)
            btn_layout.addWidget(save_btn)
            
            layout.addLayout(btn_layout)
    
    def load_student_data(self):
        """Load student data into all form fields"""
        if not self.student:
            return
        
        # CRITICAL: Update balance label in header immediately
        if hasattr(self, 'balance_label') and self.balance_label:
            from decimal import Decimal
            balance_val = float(self.student.balance) if self.student.balance else 0.0
            balance_color = "#e74c3c" if balance_val < 0 else "#27ae60"
            if balance_val == 0:
                balance_text = "0.00 DH"
            else:
                balance_text = f"{balance_val:+,.2f} DH"
            self.balance_label.setText(balance_text)
            self.balance_label.setStyleSheet(f"color: {balance_color}; font-size: 18px; font-weight: bold; background-color: white; padding: 8px 15px; border-radius: 5px;")
        
        # Tab 1: Information
        self.full_name.setText(self.student.full_name or "")
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
        
        # Training
        self.hours_planned.setValue(self.student.hours_planned or 20)
        self.hours_completed.setValue(self.student.hours_completed or 0)
        self.theory_test_attempts.setValue(self.student.theoretical_exam_attempts or 0)
        self.practical_test_attempts.setValue(self.student.practical_exam_attempts or 0)
        
        # Financial - disconnect signal to avoid triggering update during load
        self.total_due.valueChanged.disconnect()
        self.total_paid.valueChanged.disconnect()
        
        self.total_due.setValue(float(self.student.total_due) if self.student.total_due else 0.0)
        self.total_paid.setValue(float(self.student.total_paid) if self.student.total_paid else 0.0)
        self.balance.setValue(float(self.student.balance) if self.student.balance else 0.0)
        
        # Reconnect signals after loading
        self.total_due.valueChanged.connect(self.update_balance_display)
        self.total_paid.valueChanged.connect(self.update_balance_display)
        
        # Tab 2: Load Payments
        try:
            self.load_payments()
        except Exception as e:
            print(f"Error loading payments: {e}")
        
        # Tab 3: Load Sessions
        try:
            self.load_sessions()
        except Exception as e:
            print(f"Error loading sessions: {e}")
        
        # Tab 4: Load Progress Statistics (to be improved later)
        try:
            self.load_progress_stats()
        except Exception as e:
            print(f"Error loading progress stats: {e}")
        
        # Tab 5: Load Documents
        try:
            self.load_documents()
        except Exception as e:
            print(f"Error loading documents: {e}")
        
        # Tab 6: Load History
        try:
            self.load_history()
        except Exception as e:
            print(f"Error loading history: {e}")
        
        # Tab 7: Load Notes
        try:
            if hasattr(self.student, 'notes'):
                self.notes_edit.setPlainText(self.student.notes or "")
        except Exception as e:
            print(f"Error loading notes: {e}")
    
    def load_payments(self):
        """Load payment history for the student"""
        if not self.student:
            return
        
        try:
            payments = PaymentController.get_payments_by_student(self.student.id)
            self.payments_table.setRowCount(0)
            
            total_paid = 0
            payment_count = 0
            
            for payment in payments:
                # Exclure les paiements annulés
                if payment.is_cancelled:
                    continue
                
                row = self.payments_table.rowCount()
                self.payments_table.insertRow(row)
                
                # Date
                date_str = payment.payment_date.strftime('%d/%m/%Y') if payment.payment_date else "N/A"
                self.payments_table.setItem(row, 0, QTableWidgetItem(date_str))
                
                # Amount (convertir Decimal en float)
                amount_value = float(payment.amount) if payment.amount else 0.0
                amount_item = QTableWidgetItem(f"{amount_value:,.2f}")
                amount_item.setForeground(QColor("#27ae60"))
                self.payments_table.setItem(row, 1, amount_item)
                total_paid += amount_value
                payment_count += 1
                
                # Method
                method_text = payment.payment_method.value if payment.payment_method else "N/A"
                self.payments_table.setItem(row, 2, QTableWidgetItem(method_text))
                
                # Reference
                self.payments_table.setItem(row, 3, QTableWidgetItem(payment.reference_number or ""))
                
                # Notes/Description
                self.payments_table.setItem(row, 4, QTableWidgetItem(payment.description or ""))
            
            # Update summary
            self.payments_total_label.setText(f"Total Payé: {total_paid:,.2f} DH")
            self.payments_count_label.setText(f"Nombre de Paiements: {payment_count}")
            
        except Exception as e:
            print(f"Error loading payments: {e}")
    
    def load_sessions(self):
        """Load training sessions for the student"""
        if not self.student:
            return
        
        try:
            sessions = SessionController.get_sessions_by_student(self.student.id)
            self.sessions_table.setRowCount(0)
            
            total_hours = 0
            for row, session in enumerate(sessions):
                self.sessions_table.insertRow(row)
                
                # Date
                date_str = session.start_datetime.strftime('%d/%m/%Y') if session.start_datetime else "N/A"
                self.sessions_table.setItem(row, 0, QTableWidgetItem(date_str))
                
                # Start time
                start_time = session.start_datetime.strftime('%H:%M') if session.start_datetime else "N/A"
                self.sessions_table.setItem(row, 1, QTableWidgetItem(start_time))
                
                # End time
                end_time = session.end_datetime.strftime('%H:%M') if session.end_datetime else "N/A"
                self.sessions_table.setItem(row, 2, QTableWidgetItem(end_time))
                
                # Calculate hours
                if session.start_datetime and session.end_datetime:
                    duration = (session.end_datetime - session.start_datetime).seconds / 3600
                    total_hours += duration
                
                # Type
                session_type = getattr(session, 'session_type', 'N/A')
                self.sessions_table.setItem(row, 3, QTableWidgetItem(str(session_type)))
                
                # Instructor
                instructor = getattr(session, 'instructor_name', 'N/A')
                self.sessions_table.setItem(row, 4, QTableWidgetItem(str(instructor)))
                
                # Notes
                notes = getattr(session, 'notes', '')
                self.sessions_table.setItem(row, 5, QTableWidgetItem(str(notes)))
            
            # Update summary
            self.sessions_count_label.setText(f"Nombre de Séances: {len(sessions)}")
            self.sessions_hours_label.setText(f"Total Heures: {total_hours:.1f}")
            
        except Exception as e:
            print(f"Error loading sessions: {e}")
    
    def load_progress_stats(self):
        """Load progress statistics for the student - Placeholder (to be improved later)"""
        # This method is currently disabled as the progress tab is being redesigned
        pass
    
    def upload_photo(self):
        """Upload a profile photo"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une Photo",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if filename:
            try:
                # Load and resize image
                pixmap = QPixmap(filename)
                if not pixmap.isNull():
                    # Scale to 200x200
                    scaled_pixmap = pixmap.scaled(
                        200, 200,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.photo_label.setPixmap(scaled_pixmap)
                    self.photo_path = filename
                    QMessageBox.information(self, "Succès", "Photo téléchargée avec succès")
                else:
                    QMessageBox.warning(self, "Erreur", "Impossible de charger l'image")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors du téléchargement: {str(e)}")
    
    def delete_photo(self):
        """Delete the profile photo"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer la photo?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.photo_label.clear()
            self.photo_label.setText("Aucune\nPhoto")
            self.photo_path = None
            QMessageBox.information(self, "Succès", "Photo supprimée")
    
    def load_documents(self):
        """Load documents for the student"""
        if not self.student:
            return
        
        try:
            # Charger les documents de l'élève
            documents = DocumentController.get_documents_by_student(self.student.id)
            self.documents_table.setRowCount(0)
            
            total_size = 0
            for row, doc in enumerate(documents):
                self.documents_table.insertRow(row)
                
                # Title
                self.documents_table.setItem(row, 0, QTableWidgetItem(doc.title or "Sans titre"))
                
                # Type
                doc_type = doc.document_type.value if doc.document_type else "N/A"
                self.documents_table.setItem(row, 1, QTableWidgetItem(doc_type))
                
                # Date
                date_str = doc.created_at.strftime('%d/%m/%Y') if doc.created_at else "N/A"
                self.documents_table.setItem(row, 2, QTableWidgetItem(date_str))
                
                # Size
                size_mb = (doc.file_size / (1024 * 1024)) if doc.file_size else 0
                total_size += size_mb
                self.documents_table.setItem(row, 3, QTableWidgetItem(f"{size_mb:.2f} MB"))
                
                # Status
                status_item = QTableWidgetItem(doc.status.value if doc.status else "N/A")
                if doc.status and doc.status.value == 'verified':
                    status_item.setForeground(QColor("#27ae60"))
                elif doc.status and doc.status.value == 'expired':
                    status_item.setForeground(QColor("#e74c3c"))
                self.documents_table.setItem(row, 4, status_item)
            
            # Update summary
            self.documents_count_label.setText(f"Nombre de Documents: {len(documents)}")
            self.documents_size_label.setText(f"Taille Totale: {total_size:.2f} MB")
            
        except Exception as e:
            print(f"Error loading documents: {e}")
    
    def add_document(self):
        """Add a new document"""
        if not self.student:
            QMessageBox.warning(self, "Erreur", "Sauvegardez l'élève d'abord")
            return
        
        try:
            from src.views.widgets.document_upload_dialog import DocumentUploadDialog
            dialog = DocumentUploadDialog(
                student_id=self.student.id,
                parent=self
            )
            dialog.document_saved.connect(self.load_documents)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def view_document(self):
        """View selected document"""
        selected_row = self.documents_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Attention", "Sélectionnez un document")
            return
        
        try:
            documents = DocumentController.get_documents_by_student(self.student.id)
            if selected_row < len(documents):
                doc = documents[selected_row]
                from src.views.widgets.document_viewer_dialog import DocumentViewerDialog
                dialog = DocumentViewerDialog(doc.id, parent=self)
                dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def delete_document(self):
        """Delete selected document"""
        selected_row = self.documents_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Attention", "Sélectionnez un document")
            return
        
        try:
            documents = DocumentController.get_documents_by_student(self.student.id)
            if selected_row < len(documents):
                doc = documents[selected_row]
                
                reply = QMessageBox.question(
                    self,
                    "Confirmation",
                    f"Supprimer le document '{doc.title}'?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    DocumentController.delete_document(doc.id)
                    self.load_documents()
                    QMessageBox.information(self, "Succès", "Document supprimé")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def load_history(self):
        """Load complete activity history for the student"""
        if not self.student:
            return
        
        try:
            self.history_table.setRowCount(0)
            filter_type = self.history_filter.currentData() if hasattr(self, 'history_filter') else 'all'
            
            all_activities = []
            
            # Load payments
            if filter_type in ['all', 'payments']:
                try:
                    payments = PaymentController.get_payments_by_student(self.student.id)
                    for payment in payments:
                        method_text = payment.payment_method.value if payment.payment_method else 'N/A'
                        all_activities.append({
                            'date': payment.payment_date,
                            'type': '💰 Paiement',
                            'description': f"Paiement de {payment.amount:,.2f} DH",
                            'details': f"Méthode: {method_text}"
                        })
                except Exception as e:
                    print(f"Error loading payment history: {e}")
            
            # Load sessions
            if filter_type in ['all', 'sessions']:
                try:
                    sessions = SessionController.get_sessions_by_student(self.student.id)
                    for session in sessions:
                        all_activities.append({
                            'date': session.start_datetime,
                            'type': '🎓 Séance',
                            'description': f"Séance de conduite",
                            'details': f"Instructeur: {getattr(session, 'instructor_name', 'N/A')}"
                        })
                except Exception as e:
                    print(f"Error loading session history: {e}")
            
            # Load exams
            if filter_type in ['all', 'exams']:
                try:
                    exams = ExamController.get_exams_by_student(self.student.id)
                    for exam in exams:
                        result_text = "Réussi" if getattr(exam, 'passed', False) else "Échoué"
                        all_activities.append({
                            'date': getattr(exam, 'exam_date', datetime.now()),
                            'type': '📝 Examen',
                            'description': f"Examen {getattr(exam, 'exam_type', 'N/A')}",
                            'details': f"Résultat: {result_text}"
                        })
                except Exception as e:
                    print(f"Error loading exam history: {e}")
            
            # Load documents
            if filter_type in ['all', 'documents']:
                try:
                    documents = DocumentController.get_documents_by_student(self.student.id)
                    for doc in documents:
                        all_activities.append({
                            'date': doc.created_at,
                            'type': '📄 Document',
                            'description': f"Document ajouté: {doc.title}",
                            'details': f"Type: {doc.document_type.value if doc.document_type else 'N/A'}"
                        })
                except Exception as e:
                    print(f"Error loading document history: {e}")
            
            # Sort by date (most recent first) - convert all to datetime for comparison
            def get_sortable_date(activity):
                date_val = activity['date']
                if date_val is None:
                    return datetime.min
                # Convert date to datetime if needed
                if hasattr(date_val, 'hour'):  # It's already datetime
                    return date_val
                else:  # It's a date, convert to datetime
                    from datetime import date as date_type
                    if isinstance(date_val, date_type):
                        return datetime.combine(date_val, datetime.min.time())
                return datetime.min
            
            all_activities.sort(key=get_sortable_date, reverse=True)
            
            # Populate table
            for row, activity in enumerate(all_activities):
                self.history_table.insertRow(row)
                
                # Date
                date_str = activity['date'].strftime('%d/%m/%Y %H:%M') if activity['date'] else "N/A"
                self.history_table.setItem(row, 0, QTableWidgetItem(date_str))
                
                # Type
                self.history_table.setItem(row, 1, QTableWidgetItem(activity['type']))
                
                # Description
                self.history_table.setItem(row, 2, QTableWidgetItem(activity['description']))
                
                # Details
                self.history_table.setItem(row, 3, QTableWidgetItem(activity['details']))
            
        except Exception as e:
            print(f"Error loading history: {e}")
    
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
            
            # Update balance label in header if student exists
            if hasattr(self, 'balance_label') and self.balance_label:
                balance_color = "#e74c3c" if new_balance < 0 else "#27ae60"
                if new_balance == 0:
                    balance_text = "0.00 DH"
                else:
                    balance_text = f"{new_balance:+,.2f} DH"
                self.balance_label.setText(balance_text)
                self.balance_label.setStyleSheet(f"color: {balance_color}; font-size: 18px; font-weight: bold; background-color: white; padding: 8px 15px; border-radius: 5px;")
                
        except Exception as e:
            print(f"Error updating balance display: {e}")
    
    def refresh_balance(self):
        """Refresh the student balance display after changes"""
        if not self.student:
            return
        
        try:
            # Reload student from database to get updated balance
            updated_student = StudentController.get_student_by_id(self.student.id)
            if updated_student:
                self.student = updated_student
                
                # Update balance label in header
                # Balance = total_paid - total_due (negative = dette)
                balance_color = "#e74c3c" if self.student.balance < 0 else "#27ae60"
                if self.student.balance == 0:
                    balance_text = "0.00 DH"
                else:
                    balance_text = f"{self.student.balance:+,.2f} DH"
                self.balance_label.setText(balance_text)
                self.balance_label.setStyleSheet(f"color: {balance_color}; font-size: 18px; font-weight: bold; background-color: white; padding: 8px 15px; border-radius: 5px;")
                
                # Update financial fields in info tab
                self.balance.setValue(self.student.balance or 0)
                self.total_paid.setValue(self.student.total_paid or 0)
                self.total_due.setValue(self.student.total_due or 0)
                
                # Reload payments tab to show new totals
                self.load_payments()
                
                # Reload history to show new activity
                self.load_history()
                
        except Exception as e:
            print(f"Error refreshing balance: {e}")
    
    def save_student(self):
        """Save student data with comprehensive validation"""
        # Collect data first
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
            'notes': self.notes_edit.toPlainText().strip() or None
        }
        
        # Add photo path if uploaded
        if self.photo_path:
            data['photo_path'] = self.photo_path
        
        # Comprehensive validation using StudentValidator
        is_valid, errors = StudentValidator.validate(data)
        
        if not is_valid:
            # Build error message
            error_msg = "Erreurs de validation:\n\n"
            for field, error in errors.items():
                error_msg += f"• {field}: {error}\n"
            
            QMessageBox.warning(self, "Erreur de Validation", error_msg)
            self.tabs.setCurrentIndex(0)  # Switch to info tab
            return
        
        try:
            if self.student:
                # Update
                success, message, updated_student = StudentController.update_student(self.student.id, data)
                if success and updated_student:
                    # CRITIQUE : Recharger les données de l'étudiant mis à jour
                    self.student = updated_student
                    # Rafraîchir l'affichage du balance dans toutes les sections
                    self.refresh_balance()
                    QMessageBox.information(self, "Succès", f"Élève {data['full_name']} mis à jour avec succès")
                else:
                    QMessageBox.critical(self, "Erreur", message)
                    return
            else:
                # Create
                success, message, new_student = StudentController.create_student(data)
                if success and new_student:
                    self.student = new_student
                    QMessageBox.information(self, "Succès", f"Élève {data['full_name']} créé avec succès")
                else:
                    QMessageBox.critical(self, "Erreur", message)
                    return
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement:\n{str(e)}")
