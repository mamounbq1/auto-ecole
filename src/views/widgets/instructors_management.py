"""
Instructors Management Widget - Gestion complète des moniteurs
Table, recherche, filtres, ajout, édition
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDateEdit, QTextEdit, QSpinBox, QCheckBox, QFrame,
    QFileDialog
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont, QColor
from datetime import datetime, date

from src.controllers.instructor_controller import InstructorController
from src.models import Instructor


class AddInstructorDialog(QDialog):
    """Dialogue pour ajouter/éditer un moniteur"""
    
    instructor_added = Signal()
    
    def __init__(self, parent=None, instructor=None):
        super().__init__(parent)
        self.instructor = instructor
        self.setWindowTitle("👨‍🏫 Nouveau Moniteur" if not instructor else "✏️ Modifier Moniteur")
        self.setMinimumSize(550, 650)
        self.setup_ui()
        
        if instructor:
            self.load_instructor_data()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Titre
        title = QLabel("Ajouter un Moniteur" if not self.instructor else "Modifier un Moniteur")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #3498db; padding: 10px;")
        layout.addWidget(title)
        
        # Formulaire
        form = QFormLayout()
        form.setSpacing(12)
        
        # Nom complet
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom complet...")
        self.name_input.setMinimumHeight(35)
        form.addRow("Nom complet*:", self.name_input)
        
        # CIN
        self.cin_input = QLineEdit()
        self.cin_input.setPlaceholderText("CIN...")
        self.cin_input.setMinimumHeight(35)
        form.addRow("CIN*:", self.cin_input)
        
        # Téléphone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("06xxxxxxxx")
        self.phone_input.setMinimumHeight(35)
        form.addRow("Téléphone*:", self.phone_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        self.email_input.setMinimumHeight(35)
        form.addRow("Email:", self.email_input)
        
        # N° Permis
        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("N° de permis...")
        self.license_input.setMinimumHeight(35)
        form.addRow("N° Permis*:", self.license_input)
        
        # Types de permis
        self.license_types_input = QLineEdit()
        self.license_types_input.setText("B")
        self.license_types_input.setPlaceholderText("A,B,C,D...")
        self.license_types_input.setMinimumHeight(35)
        form.addRow("Types de Permis:", self.license_types_input)
        
        # Date d'embauche
        self.hire_date_input = QDateEdit()
        self.hire_date_input.setCalendarPopup(True)
        self.hire_date_input.setDate(QDate.currentDate())
        self.hire_date_input.setMinimumHeight(35)
        form.addRow("Date d'embauche:", self.hire_date_input)
        
        # Taux horaire
        self.hourly_rate_input = QSpinBox()
        self.hourly_rate_input.setMinimum(0)
        self.hourly_rate_input.setMaximum(1000)
        self.hourly_rate_input.setValue(100)
        self.hourly_rate_input.setSuffix(" DH/h")
        self.hourly_rate_input.setMinimumHeight(35)
        form.addRow("Taux horaire:", self.hourly_rate_input)
        
        # Disponible
        self.available_check = QCheckBox("Disponible")
        self.available_check.setChecked(True)
        form.addRow("", self.available_check)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(70)
        self.notes_input.setPlaceholderText("Notes...")
        form.addRow("Notes:", self.notes_input)
        
        layout.addLayout(form)
        
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
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setMinimumHeight(40)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        save_btn.clicked.connect(self.save_instructor)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def load_instructor_data(self):
        """Charger les données d'un moniteur existant"""
        if not self.instructor:
            return
        
        self.name_input.setText(self.instructor.full_name)
        self.cin_input.setText(self.instructor.cin)
        self.phone_input.setText(self.instructor.phone)
        self.email_input.setText(self.instructor.email or "")
        self.license_input.setText(self.instructor.license_number)
        self.license_types_input.setText(self.instructor.license_types)
        self.hire_date_input.setDate(QDate(self.instructor.hire_date))
        self.hourly_rate_input.setValue(self.instructor.hourly_rate)
        self.available_check.setChecked(self.instructor.is_available)
        self.notes_input.setText(self.instructor.notes or "")
    
    def save_instructor(self):
        """Enregistrer le moniteur"""
        # Validation
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un nom")
            return
        
        if not self.cin_input.text().strip():
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un CIN")
            return
        
        if not self.phone_input.text().strip():
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un téléphone")
            return
        
        if not self.license_input.text().strip():
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un numéro de permis")
            return
        
        try:
            from src.models import get_session
            session = get_session()
            
            if self.instructor:
                # Modification
                self.instructor.full_name = self.name_input.text().strip()
                self.instructor.cin = self.cin_input.text().strip()
                self.instructor.phone = self.phone_input.text().strip()
                self.instructor.email = self.email_input.text().strip() or None
                self.instructor.license_number = self.license_input.text().strip()
                self.instructor.license_types = self.license_types_input.text().strip()
                self.instructor.hire_date = self.hire_date_input.date().toPython()
                self.instructor.hourly_rate = self.hourly_rate_input.value()
                self.instructor.is_available = self.available_check.isChecked()
                self.instructor.notes = self.notes_input.toPlainText() or None
                
                session.commit()
                QMessageBox.information(self, "Succès", "Moniteur modifié avec succès !")
            else:
                # Création
                new_instructor = Instructor(
                    full_name=self.name_input.text().strip(),
                    cin=self.cin_input.text().strip(),
                    phone=self.phone_input.text().strip(),
                    license_number=self.license_input.text().strip(),
                    email=self.email_input.text().strip() or None,
                    license_types=self.license_types_input.text().strip(),
                    hire_date=self.hire_date_input.date().toPython(),
                    hourly_rate=self.hourly_rate_input.value(),
                    is_available=self.available_check.isChecked(),
                    notes=self.notes_input.toPlainText() or None
                )
                session.add(new_instructor)
                session.commit()
                
                QMessageBox.information(self, "Succès", "Moniteur ajouté avec succès !")
            
            self.instructor_added.emit()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement :\n{str(e)}")


class InstructorsManagement(QWidget):
    """Widget de gestion complète des moniteurs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_instructors()
    
    def setup_ui(self):
        """Configurer l'interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Barre d'outils
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Table
        self.table = self.create_table()
        main_layout.addWidget(self.table)
        
        # Footer
        footer = self.create_footer()
        main_layout.addWidget(footer)
    
    def create_header(self) -> QFrame:
        """Créer l'en-tête"""
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 8px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("👨‍🏫 Gestion des Moniteurs")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Bouton ajouter
        add_btn = QPushButton("➕ Nouveau Moniteur")
        add_btn.setMinimumHeight(35)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #3498db;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
            }
        """)
        add_btn.clicked.connect(self.add_instructor)
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
        self.search_input.setPlaceholderText("Rechercher par nom, CIN, permis...")
        self.search_input.setMinimumHeight(35)
        self.search_input.textChanged.connect(self.filter_instructors)
        layout.addWidget(self.search_input, stretch=1)
        
        # Filtre disponibilité
        self.avail_filter = QComboBox()
        self.avail_filter.setMinimumHeight(35)
        self.avail_filter.addItem("Tous", None)
        self.avail_filter.addItem("✅ Disponibles", True)
        self.avail_filter.addItem("❌ Indisponibles", False)
        self.avail_filter.currentIndexChanged.connect(self.filter_instructors)
        layout.addWidget(self.avail_filter)
        
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
        refresh_btn.clicked.connect(self.load_instructors)
        layout.addWidget(refresh_btn)
        
        return toolbar
    
    def create_table(self) -> QTableWidget:
        """Créer la table des moniteurs"""
        table = QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels([
            "Nom", "CIN", "Téléphone", "N° Permis", "Types",
            "Heures", "Taux Réussite", "Disponibilité", "Actions"
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
                background-color: #d5e8f7;
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
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Nom
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # CIN
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Téléphone
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Permis
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Types
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Heures
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Taux
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Dispo
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Actions
        
        table.verticalHeader().setVisible(False)
        
        return table
    
    def create_footer(self) -> QFrame:
        """Créer le footer"""
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
        
        self.total_label = QLabel("Total: 0 moniteurs")
        self.total_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.total_label)
        
        layout.addStretch()
        
        self.avail_label = QLabel("Disponibles: 0")
        self.avail_label.setStyleSheet("font-weight: bold; color: #27ae60; font-size: 13px;")
        layout.addWidget(self.avail_label)
        
        return footer
    
    def load_instructors(self):
        """Charger tous les moniteurs"""
        self.all_instructors = InstructorController.get_all_instructors()
        self.display_instructors(self.all_instructors)
    
    def display_instructors(self, instructors: list):
        """Afficher les moniteurs dans la table"""
        self.table.setRowCount(0)
        
        available_count = 0
        
        for instructor in instructors:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Nom
            self.table.setItem(row, 0, QTableWidgetItem(instructor.full_name))
            
            # CIN
            self.table.setItem(row, 1, QTableWidgetItem(instructor.cin))
            
            # Téléphone
            self.table.setItem(row, 2, QTableWidgetItem(instructor.phone))
            
            # N° Permis
            self.table.setItem(row, 3, QTableWidgetItem(instructor.license_number))
            
            # Types
            self.table.setItem(row, 4, QTableWidgetItem(instructor.license_types))
            
            # Heures
            hours_item = QTableWidgetItem(f"{instructor.total_hours_taught}h")
            hours_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, hours_item)
            
            # Taux réussite
            rate_item = QTableWidgetItem(f"{instructor.success_rate}%")
            rate_item.setTextAlignment(Qt.AlignCenter)
            rate_item.setForeground(QColor("#27ae60" if instructor.success_rate >= 70 else "#e74c3c"))
            self.table.setItem(row, 6, rate_item)
            
            # Disponibilité
            if instructor.is_available:
                dispo_item = QTableWidgetItem("✅ Disponible")
                dispo_item.setForeground(QColor("#27ae60"))
                available_count += 1
            else:
                dispo_item = QTableWidgetItem("❌ Indisponible")
                dispo_item.setForeground(QColor("#e74c3c"))
            dispo_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 7, dispo_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(30, 30)
            edit_btn.setToolTip("Modifier")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            edit_btn.clicked.connect(lambda checked, i=instructor: self.edit_instructor(i))
            actions_layout.addWidget(edit_btn)
            
            self.table.setCellWidget(row, 8, actions_widget)
        
        # Mettre à jour footer
        self.total_label.setText(f"Total: {len(instructors)} moniteurs")
        self.avail_label.setText(f"Disponibles: {available_count}")
    
    def filter_instructors(self):
        """Filtrer les moniteurs"""
        search_text = self.search_input.text().lower()
        avail_filter = self.avail_filter.currentData()
        
        filtered = []
        for instructor in self.all_instructors:
            # Filtre recherche
            if search_text:
                if not (
                    search_text in instructor.full_name.lower() or
                    search_text in instructor.cin.lower() or
                    search_text in instructor.license_number.lower()
                ):
                    continue
            
            # Filtre disponibilité
            if avail_filter is not None and instructor.is_available != avail_filter:
                continue
            
            filtered.append(instructor)
        
        self.display_instructors(filtered)
    
    def add_instructor(self):
        """Ouvrir dialogue ajout moniteur"""
        dialog = AddInstructorDialog(self)
        dialog.instructor_added.connect(self.load_instructors)
        dialog.exec()
    
    def edit_instructor(self, instructor):
        """Ouvrir dialogue édition moniteur"""
        dialog = AddInstructorDialog(self, instructor)
        dialog.instructor_added.connect(self.load_instructors)
        dialog.exec()
