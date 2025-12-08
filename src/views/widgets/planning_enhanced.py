"""
Widget de planning avec calendrier interactif
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCalendarWidget,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox, QDialog,
    QFormLayout, QDateEdit, QTimeEdit, QComboBox, QTextEdit, QFrame
)
from PySide6.QtCore import Qt, QDate, QTime
from PySide6.QtGui import QFont, QColor, QTextCharFormat
from datetime import datetime, timedelta

from src.controllers.session_controller import SessionController
from src.controllers.student_controller import StudentController
from src.controllers.instructor_controller import InstructorController
from src.controllers.vehicle_controller import VehicleController
from src.models import SessionStatus, SessionType


class SessionDialog(QDialog):
    """Dialogue pour créer/modifier une session"""
    
    def __init__(self, session_date=None, parent=None):
        super().__init__(parent)
        self.session_date = session_date or datetime.now()
        self.setWindowTitle("Nouvelle Session")
        self.setMinimumSize(500, 500)
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate(
            self.session_date.year,
            self.session_date.month,
            self.session_date.day
        ))
        
        # Heure de début
        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime(9, 0))
        
        # Durée
        self.duration = QComboBox()
        for mins in [30, 45, 60, 90, 120]:
            self.duration.addItem(f"{mins} minutes", mins)
        self.duration.setCurrentIndex(2)  # 60 min par défaut
        
        # Type de session
        self.session_type = QComboBox()
        for stype in SessionType:
            self.session_type.addItem(stype.value, stype)
        
        # Élève
        self.student_combo = QComboBox()
        students = StudentController.get_active_students()
        for student in students:
            self.student_combo.addItem(
                f"{student.full_name} ({student.hours_completed}/{student.hours_planned}h)",
                student.id
            )
        
        # Moniteur
        self.instructor_combo = QComboBox()
        instructors = InstructorController.get_all_instructors()
        for instructor in instructors:
            self.instructor_combo.addItem(instructor.full_name, instructor.id)
        
        # Véhicule
        self.vehicle_combo = QComboBox()
        vehicles = VehicleController.get_all_vehicles()
        for vehicle in vehicles:
            self.vehicle_combo.addItem(
                f"{vehicle.make} {vehicle.model} ({vehicle.plate_number})",
                vehicle.id
            )
        
        # Notes
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(80)
        self.notes.setPlaceholderText("Notes ou remarques...")
        
        form_layout.addRow("Date*:", self.date_edit)
        form_layout.addRow("Heure de début*:", self.start_time)
        form_layout.addRow("Durée*:", self.duration)
        form_layout.addRow("Type:", self.session_type)
        form_layout.addRow("Élève*:", self.student_combo)
        form_layout.addRow("Moniteur*:", self.instructor_combo)
        form_layout.addRow("Véhicule:", self.vehicle_combo)
        form_layout.addRow("Notes:", self.notes)
        
        layout.addLayout(form_layout)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Créer Session")
        save_btn.clicked.connect(self.save_session)
        save_btn.setStyleSheet("""
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
    
    def save_session(self):
        """Enregistrer la session"""
        try:
            # Construire datetime
            date = self.date_edit.date().toPython()
            time = self.start_time.time().toPython()
            start_dt = datetime.combine(date, time)
            
            duration_mins = self.duration.currentData()
            end_dt = start_dt + timedelta(minutes=duration_mins)
            
            session_data = {
                'student_id': self.student_combo.currentData(),
                'instructor_id': self.instructor_combo.currentData(),
                'vehicle_id': self.vehicle_combo.currentData() if self.vehicle_combo.currentData() else None,
                'session_type': self.session_type.currentData(),
                'start_datetime': start_dt,
                'end_datetime': end_dt,
                'status': SessionStatus.SCHEDULED,
                'notes': self.notes.toPlainText().strip() or None
            }
            
            SessionController.create_session(session_data)
            
            QMessageBox.information(self, "Succès", "Session créée avec succès!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")


class PlanningEnhancedWidget(QWidget):
    """Widget de planning avec calendrier"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.selected_date = datetime.now()
        self.setup_ui()
        self.load_sessions()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        self.create_header(layout)
        
        # Layout principal (calendrier + liste)
        main_layout = QHBoxLayout()
        
        # Calendrier
        calendar_frame = QFrame()
        calendar_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 2px solid #ecf0f1;
            }
        """)
        calendar_layout = QVBoxLayout(calendar_frame)
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_selected)
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
            }
            QCalendarWidget QToolButton {
                color: white;
                background-color: #3498db;
                font-weight: bold;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #3498db;
            }
        """)
        
        calendar_layout.addWidget(self.calendar)
        main_layout.addWidget(calendar_frame, stretch=2)
        
        # Liste des sessions du jour
        sessions_frame = QFrame()
        sessions_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 2px solid #ecf0f1;
            }
        """)
        sessions_layout = QVBoxLayout(sessions_frame)
        
        self.date_label = QLabel()
        self.date_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
        """)
        sessions_layout.addWidget(self.date_label)
        
        self.sessions_list = QListWidget()
        self.sessions_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: #f8f9fa;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 10px;
                margin: 5px;
                background-color: white;
                border-radius: 5px;
                border-left: 4px solid #3498db;
            }
            QListWidget::item:selected {
                background-color: #e8f4f8;
            }
        """)
        sessions_layout.addWidget(self.sessions_list)
        
        # Boutons d'action
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Nouvelle Session")
        add_btn.clicked.connect(self.add_session)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        mark_completed_btn = QPushButton("✅ Marquer Terminée")
        mark_completed_btn.clicked.connect(self.mark_completed)
        mark_completed_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.clicked.connect(self.cancel_session)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(mark_completed_btn)
        btn_layout.addWidget(cancel_btn)
        
        sessions_layout.addLayout(btn_layout)
        
        main_layout.addWidget(sessions_frame, stretch=1)
        
        layout.addLayout(main_layout)
    
    def create_header(self, layout):
        """Créer l'en-tête"""
        header_layout = QHBoxLayout()
        
        title = QLabel("📅 Planning des Sessions")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Vues
        day_btn = QPushButton("Jour")
        week_btn = QPushButton("Semaine")
        month_btn = QPushButton("Mois")
        
        for btn in [day_btn, week_btn, month_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ecf0f1;
                    color: #2c3e50;
                    padding: 8px 15px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #bdc3c7;
                }
            """)
            btn.setCursor(Qt.PointingHandCursor)
        
        header_layout.addWidget(day_btn)
        header_layout.addWidget(week_btn)
        header_layout.addWidget(month_btn)
        
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.clicked.connect(self.load_sessions)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
    
    def load_sessions(self):
        """Charger les sessions"""
        # Marquer les jours avec sessions sur le calendrier
        all_sessions = SessionController.get_all_sessions()
        
        # Réinitialiser le format
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # Marquer les jours avec sessions
        for session in all_sessions:
            date = QDate(
                session.start_datetime.year,
                session.start_datetime.month,
                session.start_datetime.day
            )
            
            fmt = QTextCharFormat()
            fmt.setBackground(QColor("#e8f4f8"))
            fmt.setFontWeight(QFont.Bold)
            
            self.calendar.setDateTextFormat(date, fmt)
        
        # Charger les sessions du jour sélectionné
        self.on_date_selected(self.calendar.selectedDate())
    
    def on_date_selected(self, qdate):
        """Quand une date est sélectionnée"""
        self.selected_date = datetime(qdate.year(), qdate.month(), qdate.day())
        
        # Mettre à jour le label
        self.date_label.setText(
            f"📅 {self.selected_date.strftime('%A %d %B %Y')}"
        )
        
        # Charger les sessions (utiliser get_sessions_by_date_range avec même date)
        target_date = self.selected_date.date()
        sessions = SessionController.get_sessions_by_date_range(target_date, target_date)
        
        self.sessions_list.clear()
        
        if not sessions:
            item = QListWidgetItem("Aucune session prévue")
            item.setForeground(QColor("#95a5a6"))
            self.sessions_list.addItem(item)
        else:
            for session in sessions:
                time_str = session.start_datetime.strftime('%H:%M')
                student = session.student.full_name if session.student else "N/A"
                instructor = session.instructor.full_name if session.instructor else "N/A"
                
                status_emoji = {
                    SessionStatus.SCHEDULED: "⏰",
                    SessionStatus.COMPLETED: "✅",
                    SessionStatus.CANCELLED: "❌",
                    SessionStatus.NO_SHOW: "⚠️"
                }.get(session.status, "📝")
                
                text = f"{status_emoji} {time_str} - {student}\n   Moniteur: {instructor}"
                
                item = QListWidgetItem(text)
                item.setData(Qt.UserRole, session.id)
                
                # Couleur selon statut
                if session.status == SessionStatus.COMPLETED:
                    item.setForeground(QColor("#27ae60"))
                elif session.status == SessionStatus.CANCELLED:
                    item.setForeground(QColor("#e74c3c"))
                
                self.sessions_list.addItem(item)
    
    def add_session(self):
        """Ajouter une session"""
        dialog = SessionDialog(self.selected_date, parent=self)
        if dialog.exec():
            self.load_sessions()
    
    def mark_completed(self):
        """Marquer session comme terminée"""
        current_item = self.sessions_list.currentItem()
        if not current_item or not current_item.data(Qt.UserRole):
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une session")
            return
        
        session_id = current_item.data(Qt.UserRole)
        
        try:
            SessionController.update_session(session_id, {'status': SessionStatus.COMPLETED})
            QMessageBox.information(self, "Succès", "Session marquée comme terminée")
            self.load_sessions()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def cancel_session(self):
        """Annuler une session"""
        current_item = self.sessions_list.currentItem()
        if not current_item or not current_item.data(Qt.UserRole):
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une session")
            return
        
        session_id = current_item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self, "Confirmation",
            "Êtes-vous sûr de vouloir annuler cette session?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                SessionController.update_session(session_id, {'status': SessionStatus.CANCELLED})
                QMessageBox.information(self, "Succès", "Session annulée")
                self.load_sessions()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
