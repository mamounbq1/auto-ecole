"""
Planning Week View - Vue hebdomadaire avec grille
Phase 2 Planning Improvements
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from datetime import datetime, timedelta, date

from src.controllers.session_controller import SessionController
from src.models import SessionStatus
from src.views.widgets.session_detail_view import SessionDetailViewDialog


class PlanningWeekView(QWidget):
    """
    Vue hebdomadaire du planning avec grille
    - Affichage 7 jours × heures
    - Sessions affichées dans les créneaux
    - Indicateurs de charge
    - Navigation semaine précédente/suivante
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_week_start = self.get_week_start(date.today())
        self.setup_ui()
        self.load_week_sessions()
    
    def get_week_start(self, target_date):
        """Obtenir le lundi de la semaine"""
        # target_date.weekday() retourne 0=Lundi, 6=Dimanche
        days_since_monday = target_date.weekday()
        monday = target_date - timedelta(days=days_since_monday)
        return monday
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header avec navigation
        self.create_header(layout)
        
        # Grille semaine
        self.create_week_grid(layout)
    
    def create_header(self, layout):
        """Créer l'en-tête avec navigation"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        # Bouton semaine précédente
        prev_btn = QPushButton("◀ Semaine Précédente")
        prev_btn.clicked.connect(self.previous_week)
        prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        header_layout.addWidget(prev_btn)
        
        # Label semaine courante
        self.week_label = QLabel()
        self.week_label.setAlignment(Qt.AlignCenter)
        self.update_week_label()
        self.week_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header_layout.addWidget(self.week_label, stretch=1)
        
        # Bouton aujourd'hui
        today_btn = QPushButton("📅 Aujourd'hui")
        today_btn.clicked.connect(self.go_to_today)
        today_btn.setStyleSheet("""
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
        header_layout.addWidget(today_btn)
        
        # Bouton semaine suivante
        next_btn = QPushButton("Semaine Suivante ▶")
        next_btn.clicked.connect(self.next_week)
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        header_layout.addWidget(next_btn)
        
        layout.addWidget(header_frame)
    
    def create_week_grid(self, layout):
        """Créer la grille de la semaine"""
        # Scroll area pour la grille
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #ecf0f1;
            }
        """)
        
        # Widget conteneur
        grid_widget = QWidget()
        grid_widget.setStyleSheet("background-color: white;")
        
        # Table pour la grille
        self.week_table = QTableWidget()
        self.week_table.setColumnCount(8)  # Heure + 7 jours
        
        # Heures de 8h à 19h
        hours = list(range(8, 20))
        self.week_table.setRowCount(len(hours))
        
        # En-têtes colonnes (jours)
        headers = ["Heure"]
        days_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        for i, day_name in enumerate(days_fr):
            day_date = self.current_week_start + timedelta(days=i)
            header = f"{day_name}\n{day_date.strftime('%d/%m')}"
            headers.append(header)
        
        self.week_table.setHorizontalHeaderLabels(headers)
        
        # En-têtes lignes (heures)
        hour_labels = [f"{h}:00" for h in hours]
        self.week_table.setVerticalHeaderLabels(hour_labels)
        
        # Style table
        self.week_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
                border: 1px solid #ecf0f1;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #2980b9;
            }
        """)
        
        # Ajuster colonnes
        self.week_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.week_table.setColumnWidth(0, 80)  # Colonne heure
        for i in range(1, 8):
            self.week_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        
        # Ajuster hauteur lignes
        for row in range(len(hours)):
            self.week_table.setRowHeight(row, 80)
        
        # Click sur cellule
        self.week_table.cellClicked.connect(self.cell_clicked)
        
        # Layout
        grid_layout = QVBoxLayout(grid_widget)
        grid_layout.addWidget(self.week_table)
        
        scroll.setWidget(grid_widget)
        layout.addWidget(scroll)
    
    def update_week_label(self):
        """Mettre à jour le label de la semaine"""
        week_end = self.current_week_start + timedelta(days=6)
        
        # Vérifier si semaine actuelle
        today = date.today()
        is_current_week = (self.get_week_start(today) == self.current_week_start)
        
        prefix = "📅 " if is_current_week else ""
        
        self.week_label.setText(
            f"{prefix}Semaine du {self.current_week_start.strftime('%d/%m/%Y')} "
            f"au {week_end.strftime('%d/%m/%Y')}"
        )
    
    def load_week_sessions(self):
        """Charger les sessions de la semaine"""
        # Effacer table
        for row in range(self.week_table.rowCount()):
            for col in range(self.week_table.columnCount()):
                self.week_table.setItem(row, col, QTableWidgetItem(""))
        
        # Obtenir sessions de la semaine
        week_end = self.current_week_start + timedelta(days=6)
        sessions = SessionController.get_sessions_by_date_range(
            self.current_week_start, 
            week_end
        )
        
        # Organiser sessions par jour et heure
        for session in sessions:
            # Calculer jour (colonne)
            session_date = session.start_datetime.date()
            days_from_monday = (session_date - self.current_week_start).days
            col = days_from_monday + 1  # +1 car colonne 0 = heures
            
            if col < 1 or col > 7:
                continue  # Session hors de la semaine
            
            # Calculer heure (ligne)
            hour = session.start_datetime.hour
            if hour < 8 or hour >= 20:
                continue  # Heure hors plage
            
            row = hour - 8  # 8h = ligne 0
            
            # Créer contenu cellule
            student_name = session.student.full_name if session.student else "N/A"
            instructor_name = session.instructor.full_name if session.instructor else "N/A"
            
            # Emoji statut
            status_emoji = {
                SessionStatus.SCHEDULED: "⏰",
                SessionStatus.COMPLETED: "✅",
                SessionStatus.CANCELLED: "❌",
                SessionStatus.IN_PROGRESS: "🔄"
            }.get(session.status, "📝")
            
            # Texte
            time_str = session.start_datetime.strftime('%H:%M')
            duration = (session.end_datetime - session.start_datetime).total_seconds() / 3600
            
            cell_text = (
                f"{status_emoji} {time_str} ({duration:.1f}h)\n"
                f"👤 {student_name}\n"
                f"👨‍🏫 {instructor_name[:15]}"
            )
            
            # Créer item
            item = QTableWidgetItem(cell_text)
            item.setData(Qt.UserRole, session.id)  # Stocker ID session
            
            # Couleur selon statut
            if session.status == SessionStatus.COMPLETED:
                item.setBackground(QColor("#d5f4e6"))  # Vert clair
                item.setForeground(QColor("#27ae60"))
            elif session.status == SessionStatus.CANCELLED:
                item.setBackground(QColor("#fadbd8"))  # Rouge clair
                item.setForeground(QColor("#e74c3c"))
            elif session.status == SessionStatus.SCHEDULED:
                item.setBackground(QColor("#ebf5fb"))  # Bleu clair
                item.setForeground(QColor("#2c3e50"))
            
            item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
            
            # Ajouter à table
            existing_item = self.week_table.item(row, col)
            if existing_item and existing_item.text():
                # Multiple sessions dans même créneau
                item.setText(existing_item.text() + "\n---\n" + cell_text)
                item.setBackground(QColor("#fff3cd"))  # Jaune (warning)
            
            self.week_table.setItem(row, col, item)
        
        # Mettre jour d'aujourd'hui en surbrillance
        self.highlight_today()
    
    def highlight_today(self):
        """Mettre en surbrillance la colonne du jour actuel"""
        today = date.today()
        
        # Vérifier si aujourd'hui est dans cette semaine
        if not (self.current_week_start <= today <= self.current_week_start + timedelta(days=6)):
            return
        
        # Calculer colonne
        days_from_monday = (today - self.current_week_start).days
        col = days_from_monday + 1
        
        # Mettre en surbrillance (bordure épaisse)
        for row in range(self.week_table.rowCount()):
            item = self.week_table.item(row, col)
            if not item:
                item = QTableWidgetItem("")
                self.week_table.setItem(row, col, item)
            
            # Ajouter bordure épaisse
            if item.background().color().name() == "#ffffff":
                item.setBackground(QColor("#f8f9fa"))
    
    def cell_clicked(self, row, col):
        """Gérer clic sur cellule"""
        if col == 0:  # Colonne heures
            return
        
        item = self.week_table.item(row, col)
        if not item or not item.data(Qt.UserRole):
            # Créer nouvelle session à ce créneau
            self.create_session_at(row, col)
        else:
            # Voir session existante
            session_id = item.data(Qt.UserRole)
            self.view_session(session_id)
    
    def create_session_at(self, row, col):
        """Créer session au créneau cliqué"""
        # Calculer date/heure
        day_offset = col - 1  # col 1 = Lundi (offset 0)
        session_date = self.current_week_start + timedelta(days=day_offset)
        hour = row + 8  # row 0 = 8h
        
        # Créer datetime
        session_datetime = datetime.combine(session_date, datetime.min.time().replace(hour=hour))
        
        # Ouvrir dialogue création (on pourrait pré-remplir date/heure)
        dialog = SessionDetailViewDialog(session=None, parent=self, read_only=False)
        if dialog.exec():
            self.load_week_sessions()
    
    def view_session(self, session_id):
        """Voir détails session"""
        session = SessionController.get_session_by_id(session_id)
        if not session:
            QMessageBox.warning(self, "Erreur", "Session introuvable")
            return
        
        dialog = SessionDetailViewDialog(session, parent=self, read_only=True)
        if dialog.exec():
            self.load_week_sessions()
    
    def previous_week(self):
        """Aller à la semaine précédente"""
        self.current_week_start = self.current_week_start - timedelta(days=7)
        self.update_week_label()
        self.load_week_sessions()
    
    def next_week(self):
        """Aller à la semaine suivante"""
        self.current_week_start = self.current_week_start + timedelta(days=7)
        self.update_week_label()
        self.load_week_sessions()
    
    def go_to_today(self):
        """Retourner à la semaine actuelle"""
        self.current_week_start = self.get_week_start(date.today())
        self.update_week_label()
        self.load_week_sessions()
