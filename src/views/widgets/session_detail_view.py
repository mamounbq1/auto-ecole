"""
Comprehensive Session Detail View Dialog with 5 tabs
Phase 1 Planning Improvements
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDateEdit, QTimeEdit, QTextEdit, QSpinBox, QGroupBox,
    QTabWidget, QListWidget, QFrame, QScrollArea, QCheckBox
)
from PySide6.QtCore import Qt, QDate, QTime, QDateTime
from PySide6.QtGui import QFont, QColor
from datetime import datetime, timedelta

from functools import partial
from src.controllers.session_controller import SessionController
from src.controllers.student_controller import StudentController
from src.controllers.instructor_controller import InstructorController
from src.controllers.vehicle_controller import VehicleController
from src.models import SessionStatus, SessionType

# Types de permis disponibles
LICENSE_TYPES = ['A', 'B', 'C', 'D', 'E']


class SessionDetailViewDialog(QDialog):
    """
    Comprehensive Session Detail View Dialog with 5 tabs:
    1. Informations - General information (date, time, type, status)
    2. Participants - Student, Instructor, Vehicle with conflict detection
    3. Notes - Pre-session and post-session notes
    4. Statistiques - Statistics and progress
    5. Historique - Complete activity history
    """
    
    def __init__(self, session=None, parent=None, read_only=False):
        super().__init__(parent)
        self.session = session
        self.read_only = read_only
        
        # Set window properties
        title_prefix = "Vue" if read_only else ("Modifier" if session else "Nouvelle")
        session_info = f" - Session #{session.id}" if session else ""
        self.setWindowTitle(f"{title_prefix} Session{session_info}")
        self.setMinimumSize(900, 700)
        
        # Setup UI
        self.setup_ui()
        
        # Load data if editing
        if session:
            self.load_session_data()
    
    def setup_ui(self):
        """Setup the complete user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header with session info
        if self.session:
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
                background-color: #5dade2;
                color: white;
            }
        """)
        
        # Create all tabs
        self.create_info_tab()
        self.create_participants_tab()
        self.create_notes_tab()
        self.create_stats_tab()
        self.create_history_tab()
        
        main_layout.addWidget(self.tabs)
        
        # Buttons
        self.create_buttons(main_layout)
    
    def create_header(self, layout):
        """Create header with session summary"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        
        # Session info
        info_label = QLabel()
        session_date = self.session.start_datetime.strftime('%d/%m/%Y %H:%M')
        student_name = self.session.student.full_name if self.session.student else "N/A"
        instructor_name = self.session.instructor.full_name if self.session.instructor else "N/A"
        
        info_label.setText(
            f"<h2 style='color: white; margin: 0;'>📅 {session_date}</h2>"
            f"<p style='color: white; margin: 5px 0;'>"
            f"<b>Élève:</b> {student_name} | "
            f"<b>Moniteur:</b> {instructor_name}"
            f"</p>"
        )
        header_layout.addWidget(info_label)
        
        # Status badge
        status_widget = self.create_status_badge(self.session.status)
        header_layout.addWidget(status_widget)
        
        layout.addWidget(header)
    
    def create_status_badge(self, status):
        """Create colored status badge"""
        badge = QLabel()
        
        status_config = {
            SessionStatus.SCHEDULED: ("⏰ Planifiée", "#f39c12", "#fef5e7"),
            SessionStatus.COMPLETED: ("✅ Terminée", "#27ae60", "#eafaf1"),
            SessionStatus.CANCELLED: ("❌ Annulée", "#e74c3c", "#fadbd8"),
            SessionStatus.IN_PROGRESS: ("🔄 En cours", "#3498db", "#ebf5fb")
        }
        
        text, border_color, bg_color = status_config.get(status, ("❓ Inconnu", "#95a5a6", "#ecf0f1"))
        
        badge.setText(f"<h3 style='margin: 0;'>{text}</h3>")
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                border: 3px solid {border_color};
                border-radius: 10px;
                padding: 10px 20px;
                color: {border_color};
            }}
        """)
        badge.setAlignment(Qt.AlignCenter)
        
        return badge
    
    def create_info_tab(self):
        """Create Informations tab"""
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setSpacing(15)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setEnabled(not self.read_only)
        
        # Heure début
        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime(9, 0))
        self.start_time.setEnabled(not self.read_only)
        self.start_time.timeChanged.connect(self.calculate_end_time)
        
        # Durée
        duration_layout = QHBoxLayout()
        self.duration = QSpinBox()
        self.duration.setMinimum(1)
        self.duration.setMaximum(4)
        self.duration.setValue(1)
        self.duration.setSuffix(" heure(s)")
        self.duration.setEnabled(not self.read_only)
        self.duration.valueChanged.connect(self.calculate_end_time)
        duration_layout.addWidget(self.duration)
        duration_layout.addStretch()
        
        # Heure fin (calculée automatiquement)
        self.end_time = QTimeEdit()
        self.end_time.setTime(QTime(10, 0))
        self.end_time.setEnabled(False)  # Toujours désactivé (auto-calculé)
        self.end_time.setStyleSheet("QTimeEdit { background-color: #ecf0f1; }")
        
        # Type de session
        self.session_type = QComboBox()
        for stype in SessionType:
            self.session_type.addItem(stype.value.capitalize(), stype)
        self.session_type.setEnabled(not self.read_only)
        
        # Statut
        self.status = QComboBox()
        for status in SessionStatus:
            self.status.addItem(status.value.capitalize(), status)
        self.status.setEnabled(not self.read_only)
        
        # Lieu (optionnel)
        self.location = QLineEdit()
        self.location.setPlaceholderText("Ex: Auto-école, Circuit, Route nationale...")
        self.location.setEnabled(not self.read_only)
        
        # Add fields to form
        layout.addRow("📅 Date*:", self.date_edit)
        layout.addRow("🕐 Heure début*:", self.start_time)
        layout.addRow("⏱️ Durée*:", duration_layout)
        layout.addRow("🕑 Heure fin:", self.end_time)
        layout.addRow("📋 Type*:", self.session_type)
        layout.addRow("⏰ Statut*:", self.status)
        layout.addRow("📍 Lieu:", self.location)
        
        self.tabs.addTab(tab, "📋 Informations")
    
    def create_participants_tab(self):
        """Create Participants & Resources tab"""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setSpacing(15)
        
        # Élèves Section - Mode création vs édition
        if not self.session:  # MODE CRÉATION: sélection multiple
            student_group = QGroupBox("👤 Élèves (sélectionnez un ou plusieurs)")
            student_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    font-size: 14px;
                    border: 2px solid #3498db;
                    border-radius: 8px;
                    margin-top: 12px;
                    padding-top: 15px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 8px;
                    color: #3498db;
                }
            """)
            student_layout = QVBoxLayout(student_group)
            
            # Barre de recherche
            search_layout = QHBoxLayout()
            self.student_search = QLineEdit()
            self.student_search.setPlaceholderText("🔍 Rechercher...")
            self.student_search.textChanged.connect(self.filter_students)
            self.student_search.setStyleSheet("""
                QLineEdit {
                    padding: 6px;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    font-size: 12px;
                }
            """)
            
            select_all_btn = QPushButton("☑️ Tout")
            select_all_btn.setMaximumWidth(55)
            select_all_btn.clicked.connect(lambda: self.toggle_all_students(True))
            select_all_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 4px;
                    border-radius: 3px;
                    font-size: 10px;
                }
                QPushButton:hover { background-color: #229954; }
            """)
            
            deselect_all_btn = QPushButton("☐ Aucun")
            deselect_all_btn.setMaximumWidth(60)
            deselect_all_btn.clicked.connect(lambda: self.toggle_all_students(False))
            deselect_all_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 4px;
                    border-radius: 3px;
                    font-size: 10px;
                }
                QPushButton:hover { background-color: #c0392b; }
            """)
            
            search_layout.addWidget(self.student_search, stretch=1)
            search_layout.addWidget(select_all_btn)
            search_layout.addWidget(deselect_all_btn)
            student_layout.addLayout(search_layout)
            
            # Scroll area
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setMaximumHeight(200)
            scroll_area.setStyleSheet("QScrollArea { border: none; background: white; }")
            
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)
            scroll_layout.setSpacing(6)
            
            # Récupérer ACTIFS en formation
            from src.models import StudentStatus
            all_students = StudentController.get_all_students()
            active_students = [s for s in all_students 
                              if s.status == StudentStatus.ACTIVE 
                              and s.hours_completed < s.hours_planned]
            
            self.student_checkboxes = []
            for student in active_students:
                checkbox = QCheckBox(f"{student.full_name} ({student.hours_completed}/{student.hours_planned}h)")
                checkbox.setProperty('student_id', student.id)
                checkbox.setStyleSheet("""
                    QCheckBox {
                        padding: 4px;
                        font-size: 12px;
                    }
                    QCheckBox::indicator {
                        width: 16px;
                        height: 16px;
                    }
                """)
                checkbox.stateChanged.connect(self.update_selected_count)
                self.student_checkboxes.append(checkbox)
                scroll_layout.addWidget(checkbox)
            
            if not active_students:
                no_students_label = QLabel("⚠️ Aucun élève actif en formation")
                no_students_label.setStyleSheet("color: #e74c3c; padding: 10px; font-style: italic;")
                scroll_layout.addWidget(no_students_label)
            
            scroll_layout.addStretch()
            scroll_area.setWidget(scroll_widget)
            student_layout.addWidget(scroll_area)
            
            # Compteur
            self.selected_count_label = QLabel("👥 0 élève(s)")
            self.selected_count_label.setStyleSheet("color: #3498db; font-weight: bold; padding: 3px;")
            student_layout.addWidget(self.selected_count_label)
            
            main_layout.addWidget(student_group)
            
        else:  # MODE ÉDITION: élève unique
            student_group = QGroupBox("👤 Élève (Obligatoire)")
            student_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
            student_layout = QVBoxLayout(student_group)
            
            self.student_combo = QComboBox()
            self.student_combo.setEnabled(not self.read_only)
            students = StudentController.get_all_students()
            self.student_combo.addItem("-- Sélectionner élève --", None)
            for student in students:
                status_emoji = "✅" if student.status.value == "actif" else "⏸️"
                self.student_combo.addItem(
                    f"{status_emoji} {student.full_name} ({student.license_type})",
                    student.id
                )
            
            self.student_info_label = QLabel()
            self.student_info_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 5px;")
            self.student_combo.currentIndexChanged.connect(self.update_student_info)
            
            student_layout.addWidget(self.student_combo)
            student_layout.addWidget(self.student_info_label)
            main_layout.addWidget(student_group)
        
        # Moniteur Section
        instructor_group = QGroupBox("👨‍🏫 Moniteur (Obligatoire)")
        instructor_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        instructor_layout = QVBoxLayout(instructor_group)
        
        self.instructor_combo = QComboBox()
        self.instructor_combo.setEnabled(not self.read_only)
        instructors = InstructorController.get_all_instructors()
        self.instructor_combo.addItem("-- Sélectionner moniteur --", None)
        for instructor in instructors:
            self.instructor_combo.addItem(instructor.full_name, instructor.id)
        
        self.instructor_conflict_label = QLabel()
        self.instructor_conflict_label.setWordWrap(True)
        self.instructor_combo.currentIndexChanged.connect(self.check_conflicts)
        
        instructor_layout.addWidget(self.instructor_combo)
        instructor_layout.addWidget(self.instructor_conflict_label)
        main_layout.addWidget(instructor_group)
        
        # Véhicule Section
        vehicle_group = QGroupBox("🚗 Véhicule (Optionnel pour théorie)")
        vehicle_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        vehicle_layout = QVBoxLayout(vehicle_group)
        
        self.vehicle_combo = QComboBox()
        self.vehicle_combo.setEnabled(not self.read_only)
        vehicles = VehicleController.get_all_vehicles()
        self.vehicle_combo.addItem("-- Aucun véhicule --", None)
        for vehicle in vehicles:
            status_emoji = "🟢" if vehicle.is_available else "🔴"
            self.vehicle_combo.addItem(
                f"{status_emoji} {vehicle.make} {vehicle.model} ({vehicle.plate_number}) - {vehicle.license_type}",
                vehicle.id
            )
        
        self.vehicle_conflict_label = QLabel()
        self.vehicle_conflict_label.setWordWrap(True)
        self.vehicle_conflict_label.setStyleSheet("padding: 5px;")
        self.vehicle_combo.currentIndexChanged.connect(self.check_conflicts)
        
        vehicle_layout.addWidget(self.vehicle_combo)
        vehicle_layout.addWidget(self.vehicle_conflict_label)
        main_layout.addWidget(vehicle_group)
        
        main_layout.addStretch()
        
        self.tabs.addTab(tab, "👥 Participants")
    
    def create_notes_tab(self):
        """Create Notes tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Notes avant session
        pre_group = QGroupBox("📝 Notes Avant Session (Préparation)")
        pre_layout = QVBoxLayout(pre_group)
        
        pre_label = QLabel("Objectifs, points à travailler, rappels importants...")
        pre_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        pre_layout.addWidget(pre_label)
        
        self.pre_notes = QTextEdit()
        self.pre_notes.setPlaceholderText(
            "Ex:\n"
            "- Travailler créneaux\n"
            "- Réviser priorités à droite\n"
            "- Préparation examen blanc"
        )
        self.pre_notes.setMaximumHeight(150)
        self.pre_notes.setEnabled(not self.read_only)
        pre_layout.addWidget(self.pre_notes)
        
        layout.addWidget(pre_group)
        
        # Notes après session
        post_group = QGroupBox("✅ Notes Après Session (Compte-rendu)")
        post_layout = QVBoxLayout(post_group)
        
        post_label = QLabel("Compétences travaillées, progression, difficultés, recommandations...")
        post_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        post_layout.addWidget(post_label)
        
        self.post_notes = QTextEdit()
        self.post_notes.setPlaceholderText(
            "Ex:\n"
            "- Créneaux: Beaucoup amélioré ✅\n"
            "- Priorités: Encore hésitations ⚠️\n"
            "- Recommandation: 2 séances supplémentaires en ville"
        )
        self.post_notes.setMaximumHeight(150)
        self.post_notes.setEnabled(not self.read_only)
        post_layout.addWidget(self.post_notes)
        
        layout.addWidget(post_group)
        
        # Notes administratives
        admin_group = QGroupBox("🗂️ Remarques Administratives")
        admin_layout = QVBoxLayout(admin_group)
        
        self.admin_notes = QTextEdit()
        self.admin_notes.setPlaceholderText("Notes internes, changements, remarques...")
        self.admin_notes.setMaximumHeight(100)
        self.admin_notes.setEnabled(not self.read_only)
        admin_layout.addWidget(self.admin_notes)
        
        layout.addWidget(admin_group)
        
        self.tabs.addTab(tab, "📝 Notes")
    
    def create_stats_tab(self):
        """Create Statistics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if not self.session:
            placeholder = QLabel("📊 Statistiques disponibles après création de la session")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color: #95a5a6; font-size: 14px; padding: 50px;")
            layout.addWidget(placeholder)
        else:
            # Student stats
            if self.session.student:
                student_group = QGroupBox(f"👤 Statistiques - {self.session.student.full_name}")
                student_layout = QFormLayout(student_group)
                
                student_layout.addRow("Total heures:", QLabel(f"{self.session.student.hours_completed or 0}h"))
                student_layout.addRow("Heures planifiées:", QLabel(f"{self.session.student.hours_planned or 20}h"))
                remaining = (self.session.student.hours_planned or 20) - (self.session.student.hours_completed or 0)
                student_layout.addRow("Heures restantes:", QLabel(f"{remaining}h"))
                
                layout.addWidget(student_group)
            
            # Instructor stats (placeholder)
            instructor_group = QGroupBox("👨‍🏫 Statistiques Moniteur")
            instructor_layout = QLabel("📊 Statistiques détaillées disponibles prochainement...")
            instructor_layout.setStyleSheet("color: #7f8c8d; padding: 20px;")
            instructor_group_container = QVBoxLayout()
            instructor_group_container.addWidget(instructor_layout)
            instructor_group.setLayout(instructor_group_container)
            
            layout.addWidget(instructor_group)
        
        layout.addStretch()
        
        self.tabs.addTab(tab, "📊 Statistiques")
    
    def create_history_tab(self):
        """Create History tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if not self.session:
            placeholder = QLabel("🗂️ Historique disponible après création de la session")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color: #95a5a6; font-size: 14px; padding: 50px;")
            layout.addWidget(placeholder)
        else:
            history_list = QListWidget()
            
            # Add creation entry
            if self.session.created_at:
                item_text = f"📅 {self.session.created_at.strftime('%d/%m/%Y %H:%M')} - Session créée"
                history_list.addItem(item_text)
            
            # Add status changes (placeholder - would need history table in DB)
            item_text = f"⏰ Statut: {self.session.status.value.capitalize()}"
            history_list.addItem(item_text)
            
            layout.addWidget(history_list)
        
        self.tabs.addTab(tab, "🗂️ Historique")
    
    def create_buttons(self, layout):
        """Create action buttons"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        if not self.read_only:
            # Save button
            save_btn = QPushButton("💾 Enregistrer")
            save_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 10px 30px;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            save_btn.clicked.connect(self.save_session)
            button_layout.addWidget(save_btn)
        
        # Cancel/Close button
        close_text = "Fermer" if self.read_only else "Annuler"
        close_btn = QPushButton(f"❌ {close_text}")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 30px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def calculate_end_time(self):
        """Calculate end time based on start time and duration"""
        start = self.start_time.time()
        duration_hours = self.duration.value()
        
        # Convert to datetime for calculation
        start_dt = QDateTime(self.date_edit.date(), start)
        end_dt = start_dt.addSecs(duration_hours * 3600)
        
        self.end_time.setTime(end_dt.time())
    
    def filter_students(self):
        """Filtrer les élèves par recherche"""
        if not hasattr(self, 'student_checkboxes'):
            return
        search_text = self.student_search.text().lower()
        for checkbox in self.student_checkboxes:
            student_name = checkbox.text().lower()
            checkbox.setVisible(search_text in student_name)
    
    def toggle_all_students(self, checked):
        """Sélectionner/Désélectionner tous les élèves visibles"""
        if not hasattr(self, 'student_checkboxes'):
            return
        for checkbox in self.student_checkboxes:
            if checkbox.isVisible():
                checkbox.setChecked(checked)
    
    def update_selected_count(self):
        """Mettre à jour le compteur d'élèves sélectionnés"""
        if not hasattr(self, 'student_checkboxes'):
            return
        count = sum(1 for cb in self.student_checkboxes if cb.isChecked())
        self.selected_count_label.setText(f"👥 {count} élève(s)")
    
    def update_student_info(self):
        """Update student information display"""
        if not hasattr(self, 'student_combo'):
            return
        student_id = self.student_combo.currentData()
        if not student_id:
            self.student_info_label.setText("")
            return
        
        students = StudentController.get_all_students()
        student = next((s for s in students if s.id == student_id), None)
        
        if student:
            hours_done = student.hours_completed or 0
            hours_total = student.hours_planned or 20
            remaining = hours_total - hours_done
            
            info_text = (
                f"📊 Heures: {hours_done}/{hours_total}h "
                f"(Restantes: {remaining}h) | "
                f"Type: {student.license_type} | "
                f"Statut: {student.status.value.capitalize()}"
            )
            self.student_info_label.setText(info_text)
        
        self.check_conflicts()
    
    def check_conflicts(self):
        """Check for scheduling conflicts"""
        if self.read_only:
            return
        
        # Get current selection
        instructor_id = self.instructor_combo.currentData()
        vehicle_id = self.vehicle_combo.currentData()
        
        # Get student_id only if in edit mode (has student_combo)
        student_id = None
        if hasattr(self, 'student_combo'):
            student_id = self.student_combo.currentData()
        
        if not instructor_id and not vehicle_id and not student_id:
            return
        
        # Get datetime range
        date = self.date_edit.date().toPython()
        start_time = self.start_time.time().toPython()
        end_time = self.end_time.time().toPython()
        
        start_dt = datetime.combine(date, start_time)
        end_dt = datetime.combine(date, end_time)
        
        exclude_id = self.session.id if self.session else None
        
        # Check instructor conflicts
        if instructor_id:
            conflicts = SessionController.check_instructor_conflict(
                instructor_id, start_dt, end_dt, exclude_id
            )
            if conflicts:
                conflict_text = f"⚠️ <b>MONITEUR OCCUPÉ</b> - {len(conflicts)} conflit(s):<br>"
                for c in conflicts[:2]:  # Show max 2
                    student_name = c.student.full_name if c.student else "N/A"
                    time_str = c.start_datetime.strftime('%H:%M')
                    conflict_text += f"• {time_str} avec {student_name}<br>"
                self.instructor_conflict_label.setText(conflict_text)
                self.instructor_conflict_label.setStyleSheet(
                    "QLabel { color: #e74c3c; background-color: #fadbd8; "
                    "padding: 10px; border-left: 3px solid #e74c3c; border-radius: 5px; }"
                )
            else:
                self.instructor_conflict_label.setText("✅ Disponible")
                self.instructor_conflict_label.setStyleSheet(
                    "QLabel { color: #27ae60; background-color: #eafaf1; "
                    "padding: 10px; border-left: 3px solid #27ae60; border-radius: 5px; }"
                )
        
        # Check vehicle conflicts
        if vehicle_id:
            conflicts = SessionController.check_vehicle_conflict(
                vehicle_id, start_dt, end_dt, exclude_id
            )
            if conflicts:
                conflict_text = f"⚠️ <b>VÉHICULE OCCUPÉ</b> - {len(conflicts)} conflit(s):<br>"
                for c in conflicts[:2]:
                    student_name = c.student.full_name if c.student else "N/A"
                    time_str = c.start_datetime.strftime('%H:%M')
                    conflict_text += f"• {time_str} avec {student_name}<br>"
                self.vehicle_conflict_label.setText(conflict_text)
                self.vehicle_conflict_label.setStyleSheet(
                    "QLabel { color: #e74c3c; background-color: #fadbd8; "
                    "padding: 10px; border-left: 3px solid #e74c3c; border-radius: 5px; }"
                )
            else:
                self.vehicle_conflict_label.setText("✅ Disponible")
                self.vehicle_conflict_label.setStyleSheet(
                    "QLabel { color: #27ae60; background-color: #eafaf1; "
                    "padding: 10px; border-left: 3px solid #27ae60; border-radius: 5px; }"
                )
    
    def load_session_data(self):
        """Load existing session data"""
        if not self.session:
            return
        
        # Tab 1: Informations
        self.date_edit.setDate(QDate(
            self.session.start_datetime.year,
            self.session.start_datetime.month,
            self.session.start_datetime.day
        ))
        self.start_time.setTime(QTime(
            self.session.start_datetime.hour,
            self.session.start_datetime.minute
        ))
        
        # Calculate duration
        duration = (self.session.end_datetime - self.session.start_datetime).total_seconds() / 3600
        self.duration.setValue(int(duration))
        
        # Set type and status
        for i in range(self.session_type.count()):
            if self.session_type.itemData(i) == self.session.session_type:
                self.session_type.setCurrentIndex(i)
                break
        
        for i in range(self.status.count()):
            if self.status.itemData(i) == self.session.status:
                self.status.setCurrentIndex(i)
                break
        
        # Tab 2: Participants
        if self.session.student_id:
            for i in range(self.student_combo.count()):
                if self.student_combo.itemData(i) == self.session.student_id:
                    self.student_combo.setCurrentIndex(i)
                    break
        
        if self.session.instructor_id:
            for i in range(self.instructor_combo.count()):
                if self.instructor_combo.itemData(i) == self.session.instructor_id:
                    self.instructor_combo.setCurrentIndex(i)
                    break
        
        if self.session.vehicle_id:
            for i in range(self.vehicle_combo.count()):
                if self.vehicle_combo.itemData(i) == self.session.vehicle_id:
                    self.vehicle_combo.setCurrentIndex(i)
                    break
        
        # Tab 3: Notes (parse from existing notes field)
        if self.session.notes:
            # For now, put all in pre_notes
            # In future, could parse JSON to separate pre/post/admin
            self.pre_notes.setPlainText(self.session.notes)
    
    def save_session(self):
        """Save session data"""
        # Validation - MODE CRÉATION (sélection multiple)
        if not self.session:
            if not hasattr(self, 'student_checkboxes'):
                QMessageBox.warning(self, "Erreur", "Erreur de configuration du formulaire")
                return
            
            selected_students = [cb.property('student_id') for cb in self.student_checkboxes if cb.isChecked()]
            if not selected_students:
                QMessageBox.warning(self, "Attention", "Veuillez sélectionner au moins un élève")
                self.tabs.setCurrentIndex(1)
                return
        # Validation - MODE ÉDITION (élève unique)
        else:
            if not self.student_combo.currentData():
                QMessageBox.warning(self, "Erreur", "L'élève est obligatoire")
                self.tabs.setCurrentIndex(1)
                return
        
        if not self.instructor_combo.currentData():
            QMessageBox.warning(self, "Erreur", "Le moniteur est obligatoire")
            self.tabs.setCurrentIndex(1)
            return
        
        # Check for conflicts
        instructor_id = self.instructor_combo.currentData()
        vehicle_id = self.vehicle_combo.currentData()
        
        date = self.date_edit.date().toPython()
        start_time = self.start_time.time().toPython()
        end_time = self.end_time.time().toPython()
        
        start_dt = datetime.combine(date, start_time)
        end_dt = datetime.combine(date, end_time)
        
        exclude_id = self.session.id if self.session else None
        
        # Check conflicts and ask confirmation
        conflicts_found = False
        conflict_messages = []
        
        if instructor_id:
            conflicts = SessionController.check_instructor_conflict(
                instructor_id, start_dt, end_dt, exclude_id
            )
            if conflicts:
                conflicts_found = True
                conflict_messages.append(f"⚠️ MONITEUR occupé ({len(conflicts)} conflit(s))")
        
        if vehicle_id:
            conflicts = SessionController.check_vehicle_conflict(
                vehicle_id, start_dt, end_dt, exclude_id
            )
            if conflicts:
                conflicts_found = True
                conflict_messages.append(f"⚠️ VÉHICULE occupé ({len(conflicts)} conflit(s))")
        
        if conflicts_found:
            conflict_text = "\n".join(conflict_messages)
            reply = QMessageBox.question(
                self, "Conflits Détectés",
                f"{conflict_text}\n\nVoulez-vous quand même enregistrer?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Collect data
        notes_parts = []
        if self.pre_notes.toPlainText().strip():
            notes_parts.append(f"=== AVANT ===\n{self.pre_notes.toPlainText().strip()}")
        if self.post_notes.toPlainText().strip():
            notes_parts.append(f"=== APRÈS ===\n{self.post_notes.toPlainText().strip()}")
        if self.admin_notes.toPlainText().strip():
            notes_parts.append(f"=== ADMIN ===\n{self.admin_notes.toPlainText().strip()}")
        
        try:
            if self.session:
                # MODE ÉDITION: Update single session
                data = {
                    'student_id': self.student_combo.currentData(),
                    'instructor_id': self.instructor_combo.currentData(),
                    'vehicle_id': self.vehicle_combo.currentData(),
                    'session_type': self.session_type.currentData(),
                    'start_datetime': start_dt,
                    'end_datetime': end_dt,
                    'status': self.status.currentData(),
                    'notes': "\n\n".join(notes_parts) if notes_parts else None
                }
                SessionController.update_session(self.session.id, data)
                QMessageBox.information(self, "Succès", "Session mise à jour avec succès")
            else:
                # MODE CRÉATION: Create multiple sessions
                selected_students = [cb.property('student_id') for cb in self.student_checkboxes if cb.isChecked()]
                created_count = 0
                
                for student_id in selected_students:
                    data = {
                        'student_id': student_id,
                        'instructor_id': self.instructor_combo.currentData(),
                        'vehicle_id': self.vehicle_combo.currentData(),
                        'session_type': self.session_type.currentData(),
                        'start_datetime': start_dt,
                        'end_datetime': end_dt,
                        'status': self.status.currentData(),
                        'notes': "\n\n".join(notes_parts) if notes_parts else None
                    }
                    SessionController.create_session(data)
                    created_count += 1
                
                student_text = "élève" if created_count == 1 else "élèves"
                QMessageBox.information(self, "Succès", 
                    f"{created_count} session(s) créée(s) pour {created_count} {student_text}!")
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement:\n{str(e)}")
