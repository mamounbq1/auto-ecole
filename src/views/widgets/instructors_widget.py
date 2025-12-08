"""
Widget de gestion des moniteurs avec statistiques et disponibilités
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
    QFileDialog, QGroupBox, QProgressBar, QFrame
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from datetime import datetime

from src.controllers.instructor_controller import InstructorController
from src.controllers.session_controller import SessionController
from src.models import LicenseType
from src.utils import export_to_csv


class InstructorDialog(QDialog):
    """Dialogue de création/édition d'un moniteur"""
    
    def __init__(self, instructor=None, parent=None):
        super().__init__(parent)
        self.instructor = instructor
        self.setWindowTitle("Détail Moniteur" if instructor else "Nouveau Moniteur")
        self.setMinimumSize(700, 650)
        self.setup_ui()
        
        if instructor:
            self.load_instructor_data()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        
        # Informations personnelles
        personal_group = QGroupBox("👤 Informations Personnelles")
        personal_layout = QFormLayout(personal_group)
        
        self.full_name = QLineEdit()
        self.cin = QLineEdit()
        self.date_of_birth = QDateEdit()
        self.date_of_birth.setCalendarPopup(True)
        self.date_of_birth.setDate(QDate.currentDate().addYears(-25))
        
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.address = QTextEdit()
        self.address.setMaximumHeight(60)
        
        personal_layout.addRow("Nom Complet*:", self.full_name)
        personal_layout.addRow("CIN*:", self.cin)
        personal_layout.addRow("Date de Naissance:", self.date_of_birth)
        personal_layout.addRow("Téléphone*:", self.phone)
        personal_layout.addRow("Email:", self.email)
        personal_layout.addRow("Adresse:", self.address)
        
        layout.addWidget(personal_group)
        
        # Informations professionnelles
        prof_group = QGroupBox("💼 Informations Professionnelles")
        prof_layout = QFormLayout(prof_group)
        
        self.license_number = QLineEdit()
        self.license_number.setPlaceholderText("Ex: P123456")
        
        self.license_types = QLineEdit()
        self.license_types.setPlaceholderText("Ex: A, B, C (séparés par virgule)")
        self.license_types.setText("B")
        
        self.hire_date = QDateEdit()
        self.hire_date.setCalendarPopup(True)
        self.hire_date.setDate(QDate.currentDate())
        
        self.is_available = QCheckBox("Disponible")
        self.is_available.setChecked(True)
        
        self.max_students_per_day = QSpinBox()
        self.max_students_per_day.setMinimum(1)
        self.max_students_per_day.setMaximum(20)
        self.max_students_per_day.setValue(8)
        
        prof_layout.addRow("N° Permis Moniteur*:", self.license_number)
        prof_layout.addRow("Types de Permis:", self.license_types)
        prof_layout.addRow("Date d'Embauche:", self.hire_date)
        prof_layout.addRow("", self.is_available)
        prof_layout.addRow("Élèves Max/Jour:", self.max_students_per_day)
        
        layout.addWidget(prof_group)
        
        # Salaire
        salary_group = QGroupBox("💰 Rémunération")
        salary_layout = QFormLayout(salary_group)
        
        self.hourly_rate = QDoubleSpinBox()
        self.hourly_rate.setMinimum(0)
        self.hourly_rate.setMaximum(999999)
        self.hourly_rate.setValue(50)
        self.hourly_rate.setSuffix(" DH")
        
        self.monthly_salary = QDoubleSpinBox()
        self.monthly_salary.setMinimum(0)
        self.monthly_salary.setMaximum(999999)
        self.monthly_salary.setValue(5000)
        self.monthly_salary.setSuffix(" DH")
        
        salary_layout.addRow("Taux Horaire:", self.hourly_rate)
        salary_layout.addRow("Salaire Mensuel:", self.monthly_salary)
        
        layout.addWidget(salary_group)
        
        # Contact d'urgence
        emergency_group = QGroupBox("🚨 Contact d'Urgence")
        emergency_layout = QFormLayout(emergency_group)
        
        self.emergency_contact_name = QLineEdit()
        self.emergency_contact_phone = QLineEdit()
        
        emergency_layout.addRow("Nom:", self.emergency_contact_name)
        emergency_layout.addRow("Téléphone:", self.emergency_contact_phone)
        
        layout.addWidget(emergency_group)
        
        # Notes
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(60)
        self.notes.setPlaceholderText("Notes ou remarques...")
        layout.addWidget(QLabel("📝 Notes:"))
        layout.addWidget(self.notes)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.clicked.connect(self.save_instructor)
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
    
    def load_instructor_data(self):
        """Charger les données du moniteur"""
        if not self.instructor:
            return
        
        self.full_name.setText(self.instructor.full_name)
        self.cin.setText(self.instructor.cin or "")
        
        if self.instructor.date_of_birth:
            self.date_of_birth.setDate(QDate(
                self.instructor.date_of_birth.year,
                self.instructor.date_of_birth.month,
                self.instructor.date_of_birth.day
            ))
        
        self.phone.setText(self.instructor.phone or "")
        self.email.setText(self.instructor.email or "")
        self.address.setPlainText(self.instructor.address or "")
        
        self.license_number.setText(self.instructor.license_number or "")
        self.license_types.setText(self.instructor.license_types or "B")
        
        if self.instructor.hire_date:
            self.hire_date.setDate(QDate(
                self.instructor.hire_date.year,
                self.instructor.hire_date.month,
                self.instructor.hire_date.day
            ))
        
        self.is_available.setChecked(self.instructor.is_available)
        self.max_students_per_day.setValue(self.instructor.max_students_per_day or 8)
        
        self.hourly_rate.setValue(self.instructor.hourly_rate or 50)
        self.monthly_salary.setValue(self.instructor.monthly_salary or 5000)
        
        self.emergency_contact_name.setText(self.instructor.emergency_contact_name or "")
        self.emergency_contact_phone.setText(self.instructor.emergency_contact_phone or "")
        
        self.notes.setPlainText(self.instructor.notes or "")
    
    def save_instructor(self):
        """Enregistrer le moniteur"""
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
        
        if not self.license_number.text().strip():
            QMessageBox.warning(self, "Erreur", "Le numéro de permis moniteur est requis")
            return
        
        # Collecter les données
        data = {
            'full_name': self.full_name.text().strip(),
            'cin': self.cin.text().strip(),
            'date_of_birth': self.date_of_birth.date().toPython(),
            'phone': self.phone.text().strip(),
            'email': self.email.text().strip() or None,
            'address': self.address.toPlainText().strip() or None,
            'license_number': self.license_number.text().strip(),
            'license_types': self.license_types.text().strip() or "B",
            'hire_date': self.hire_date.date().toPython(),
            'is_available': self.is_available.isChecked(),
            'max_students_per_day': self.max_students_per_day.value(),
            'hourly_rate': self.hourly_rate.value(),
            'monthly_salary': self.monthly_salary.value(),
            'emergency_contact_name': self.emergency_contact_name.text().strip() or None,
            'emergency_contact_phone': self.emergency_contact_phone.text().strip() or None,
            'notes': self.notes.toPlainText().strip() or None,
        }
        
        try:
            if self.instructor:
                # Mise à jour
                InstructorController.update_instructor(self.instructor.id, data)
                QMessageBox.information(self, "Succès", "Moniteur mis à jour avec succès")
            else:
                # Création
                InstructorController.create_instructor(data)
                QMessageBox.information(self, "Succès", "Moniteur créé avec succès")
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement : {str(e)}")


class InstructorsWidget(QWidget):
    """Widget de gestion des moniteurs"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.instructors = []
        self.setup_ui()
        self.load_instructors()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        self.create_header(layout)
        
        # Barre de recherche
        self.create_search_bar(layout)
        
        # Statistiques
        self.create_stats(layout)
        
        # Tableau
        self.create_table(layout)
    
    def create_header(self, layout):
        """Créer l'en-tête"""
        header_layout = QHBoxLayout()
        
        title = QLabel("👨‍🏫 Gestion des Moniteurs")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Boutons
        add_btn = QPushButton("➕ Nouveau Moniteur")
        add_btn.clicked.connect(self.add_instructor)
        add_btn.setStyleSheet("""
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
        add_btn.setCursor(Qt.PointingHandCursor)
        
        export_btn = QPushButton("📤 Exporter CSV")
        export_btn.clicked.connect(self.export_csv)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #1abc9c;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
        """)
        export_btn.setCursor(Qt.PointingHandCursor)
        
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.clicked.connect(self.load_instructors)
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
    
    def create_search_bar(self, layout):
        """Créer la barre de recherche"""
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par nom, CIN ou téléphone...")
        self.search_input.textChanged.connect(self.apply_filters)
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
        
        self.availability_filter = QComboBox()
        self.availability_filter.addItem("📊 Tous", None)
        self.availability_filter.addItem("✅ Disponibles", True)
        self.availability_filter.addItem("❌ Indisponibles", False)
        self.availability_filter.currentIndexChanged.connect(self.apply_filters)
        self.availability_filter.setMinimumHeight(40)
        
        search_layout.addWidget(self.search_input, stretch=3)
        search_layout.addWidget(self.availability_filter, stretch=1)
        
        layout.addLayout(search_layout)
    
    def create_stats(self, layout):
        """Créer les statistiques"""
        stats_layout = QHBoxLayout()
        
        self.total_label = QLabel("Total: 0")
        self.available_label = QLabel("Disponibles: 0")
        self.avg_success_label = QLabel("Taux Moyen: 0%")
        self.total_hours_label = QLabel("Heures Total: 0")
        
        for label in [self.total_label, self.available_label, self.avg_success_label, self.total_hours_label]:
            label.setStyleSheet("""
                QLabel {
                    background-color: white;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                    color: #2c3e50;
                    border: 2px solid #ecf0f1;
                }
            """)
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.available_label)
        stats_layout.addWidget(self.avg_success_label)
        stats_layout.addWidget(self.total_hours_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
    
    def create_table(self, layout):
        """Créer le tableau"""
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom Complet", "CIN", "Téléphone", "Permis",
            "Disponible", "Élèves/Jour", "Heures", "Taux Réussite", "Actions"
        ])
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(400)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.table)
    
    def load_instructors(self):
        """Charger tous les moniteurs"""
        self.instructors = InstructorController.get_all_instructors()
        self.update_stats()
        self.populate_table()
    
    def update_stats(self):
        """Mettre à jour les statistiques"""
        total = len(self.instructors)
        available = len([i for i in self.instructors if i.is_available])
        
        total_hours = sum(i.total_hours_taught or 0 for i in self.instructors)
        avg_success = sum(i.success_rate or 0 for i in self.instructors) / total if total > 0 else 0
        
        self.total_label.setText(f"Total: {total}")
        self.available_label.setText(f"Disponibles: {available}")
        self.avg_success_label.setText(f"Taux Moyen: {avg_success:.1f}%")
        self.total_hours_label.setText(f"Heures Total: {total_hours}")
    
    def apply_filters(self):
        """Appliquer les filtres"""
        search_text = self.search_input.text().lower()
        availability = self.availability_filter.currentData()
        
        filtered = []
        
        for instructor in self.instructors:
            # Filtre texte
            if search_text:
                if not (search_text in instructor.full_name.lower() or
                       (instructor.cin and search_text in instructor.cin.lower()) or
                       (instructor.phone and search_text in instructor.phone)):
                    continue
            
            # Filtre disponibilité
            if availability is not None and instructor.is_available != availability:
                continue
            
            filtered.append(instructor)
        
        self.populate_table(filtered)
    
    def populate_table(self, instructors=None):
        """Remplir le tableau"""
        if instructors is None:
            instructors = self.instructors
        
        self.table.setRowCount(0)
        
        for row, instructor in enumerate(instructors):
            self.table.insertRow(row)
            
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(instructor.id)))
            
            # Nom
            self.table.setItem(row, 1, QTableWidgetItem(instructor.full_name))
            
            # CIN
            self.table.setItem(row, 2, QTableWidgetItem(instructor.cin or ""))
            
            # Téléphone
            self.table.setItem(row, 3, QTableWidgetItem(instructor.phone or ""))
            
            # Types de permis
            self.table.setItem(row, 4, QTableWidgetItem(instructor.license_types or "B"))
            
            # Disponible
            avail_item = QTableWidgetItem("✅ Oui" if instructor.is_available else "❌ Non")
            if instructor.is_available:
                avail_item.setForeground(QColor("#27ae60"))
            else:
                avail_item.setForeground(QColor("#e74c3c"))
            self.table.setItem(row, 5, avail_item)
            
            # Élèves/jour
            self.table.setItem(row, 6, QTableWidgetItem(str(instructor.max_students_per_day or 8)))
            
            # Heures enseignées
            self.table.setItem(row, 7, QTableWidgetItem(str(instructor.total_hours_taught or 0)))
            
            # Taux de réussite
            success_item = QTableWidgetItem(f"{instructor.success_rate or 0}%")
            if (instructor.success_rate or 0) >= 80:
                success_item.setForeground(QColor("#27ae60"))
            elif (instructor.success_rate or 0) >= 60:
                success_item.setForeground(QColor("#f39c12"))
            else:
                success_item.setForeground(QColor("#e74c3c"))
            self.table.setItem(row, 8, success_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 0, 5, 0)
            
            view_btn = QPushButton("👁️")
            view_btn.setToolTip("Voir détails")
            view_btn.clicked.connect(lambda checked, i=instructor: self.view_instructor(i))
            view_btn.setCursor(Qt.PointingHandCursor)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Modifier")
            edit_btn.clicked.connect(lambda checked, i=instructor: self.edit_instructor(i))
            edit_btn.setCursor(Qt.PointingHandCursor)
            
            stats_btn = QPushButton("📊")
            stats_btn.setToolTip("Statistiques")
            stats_btn.clicked.connect(lambda checked, i=instructor: self.view_stats(i))
            stats_btn.setCursor(Qt.PointingHandCursor)
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(stats_btn)
            
            self.table.setCellWidget(row, 9, actions_widget)
    
    def add_instructor(self):
        """Ajouter un moniteur"""
        dialog = InstructorDialog(parent=self)
        if dialog.exec():
            self.load_instructors()
    
    def edit_instructor(self, instructor):
        """Modifier un moniteur"""
        dialog = InstructorDialog(instructor, parent=self)
        if dialog.exec():
            self.load_instructors()
    
    def view_instructor(self, instructor):
        """Voir les détails d'un moniteur"""
        info = f"""
        <h3>{instructor.full_name}</h3>
        <p><b>CIN:</b> {instructor.cin}</p>
        <p><b>Téléphone:</b> {instructor.phone}</p>
        <p><b>Email:</b> {instructor.email or 'N/A'}</p>
        <p><b>Permis Moniteur:</b> {instructor.license_number}</p>
        <p><b>Types de Permis:</b> {instructor.license_types}</p>
        <p><b>Date d'Embauche:</b> {instructor.hire_date.strftime('%d/%m/%Y') if instructor.hire_date else 'N/A'}</p>
        <p><b>Disponible:</b> {'Oui' if instructor.is_available else 'Non'}</p>
        <p><b>Heures Enseignées:</b> {instructor.total_hours_taught or 0}h</p>
        <p><b>Taux de Réussite:</b> {instructor.success_rate or 0}%</p>
        <p><b>Taux Horaire:</b> {instructor.hourly_rate or 0} DH</p>
        <p><b>Salaire Mensuel:</b> {instructor.monthly_salary or 0} DH</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Détail Moniteur")
        msg.setTextFormat(Qt.RichText)
        msg.setText(info)
        msg.exec()
    
    def view_stats(self, instructor):
        """Voir les statistiques d'un moniteur"""
        # Récupérer ses sessions
        all_sessions = SessionController.get_all_sessions()
        instructor_sessions = [s for s in all_sessions if s.instructor_id == instructor.id]
        
        from src.models import SessionStatus
        completed = len([s for s in instructor_sessions if s.status == SessionStatus.COMPLETED])
        cancelled = len([s for s in instructor_sessions if s.status == SessionStatus.CANCELLED])
        no_show = len([s for s in instructor_sessions if s.status == SessionStatus.NO_SHOW])
        
        info = f"""
        <h3>📊 Statistiques - {instructor.full_name}</h3>
        <hr>
        <p><b>Sessions Totales:</b> {len(instructor_sessions)}</p>
        <p><b>Sessions Terminées:</b> {completed}</p>
        <p><b>Sessions Annulées:</b> {cancelled}</p>
        <p><b>Absences:</b> {no_show}</p>
        <p><b>Heures Enseignées:</b> {instructor.total_hours_taught or 0}h</p>
        <p><b>Élèves Formés:</b> {instructor.total_students_taught or 0}</p>
        <p><b>Taux de Réussite:</b> {instructor.success_rate or 0}%</p>
        <hr>
        <p><b>Rémunération:</b></p>
        <p>- Taux Horaire: {instructor.hourly_rate or 0} DH</p>
        <p>- Salaire Mensuel: {instructor.monthly_salary or 0} DH</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Statistiques Moniteur")
        msg.setTextFormat(Qt.RichText)
        msg.setText(info)
        msg.exec()
    
    def export_csv(self):
        """Exporter en CSV"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exporter les moniteurs",
                f"exports/moniteurs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if filename:
                success, result = export_to_csv(self.instructors, filename, 'instructors')
                
                if success:
                    QMessageBox.information(self, "Succès", f"Export réussi: {result}")
                else:
                    QMessageBox.warning(self, "Erreur", result)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
