"""
Widget Dashboard avec statistiques et KPIs
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QPushButton, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.controllers import StudentController, SessionController, PaymentController
from src.models import StudentStatus
from datetime import date, datetime, timedelta


class StatsCard(QFrame):
    """Carte de statistique"""
    
    def __init__(self, icon, title, value, subtitle="", color="#3498db"):
        super().__init__()
        self.setObjectName("statsCard")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # En-tête avec icône
        header = QLabel(f"{icon}  {title}")
        header.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {color};")
        
        # Valeur principale
        value_label = QLabel(str(value))
        value_font = QFont()
        value_font.setPointSize(32)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {color};")
        
        # Sous-titre
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        
        layout.addWidget(header)
        layout.addWidget(value_label)
        if subtitle:
            layout.addWidget(subtitle_label)
        layout.addStretch()
        
        # Style de la carte
        self.setStyleSheet("""
            QFrame#statsCard {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                border: 1px solid #ecf0f1;
            }
            QFrame#statsCard:hover {
                border: 1px solid #3498db;
            }
        """)
        self.setMinimumHeight(150)


class DashboardWidget(QWidget):
    """Widget du dashboard principal"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Configurer l'interface"""
        # Scroll area pour le contenu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Widget de contenu
        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Titre
        title = QLabel(f"👋 Bienvenue, {self.user.full_name} !")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Date du jour
        today = QLabel(f"📅 {datetime.now().strftime('%A %d %B %Y')}")
        today.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-bottom: 20px;")
        main_layout.addWidget(today)
        
        # Grille de statistiques
        self.stats_layout = QGridLayout()
        self.stats_layout.setSpacing(15)
        main_layout.addLayout(self.stats_layout)
        
        # Section actions rapides
        main_layout.addSpacing(20)
        self.create_quick_actions(main_layout)
        
        # Section activité récente
        main_layout.addSpacing(20)
        self.create_recent_activity(main_layout)
        
        main_layout.addStretch()
        
        scroll.setWidget(content)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        
    def load_data(self):
        """Charger les données statistiques"""
        # Élèves actifs
        active_students = StudentController.get_active_students_count()
        self.add_stats_card(0, 0, "👥", "Élèves Actifs", active_students, "Inscrits et en formation", "#3498db")
        
        # Sessions aujourd'hui
        today_sessions = SessionController.get_today_sessions()
        self.add_stats_card(0, 1, "📅", "Sessions Aujourd'hui", len(today_sessions), f"{datetime.now().strftime('%d/%m/%Y')}", "#1abc9c")
        
        # Élèves avec dette
        debt_students = StudentController.get_students_with_debt()
        total_debt = sum(abs(s.balance) for s in debt_students)
        self.add_stats_card(0, 2, "⚠️", "Dettes en cours", f"{len(debt_students)}", f"{total_debt:,.0f} DH total", "#e74c3c")
        
        # Sessions à venir (7 jours)
        upcoming = SessionController.get_upcoming_sessions(7)
        self.add_stats_card(1, 0, "📆", "Sessions à venir", len(upcoming), "Prochains 7 jours", "#9b59b6")
        
        # Élèves total
        all_students = StudentController.get_all_students()
        self.add_stats_card(1, 1, "📊", "Total Élèves", len(all_students), "Toutes catégories", "#34495e")
        
        # Diplômés ce mois
        graduated_this_month = len([s for s in all_students 
                                    if s.status == StudentStatus.GRADUATED 
                                    and s.updated_at.month == datetime.now().month])
        self.add_stats_card(1, 2, "🎓", "Diplômés ce mois", graduated_this_month, datetime.now().strftime("%B %Y"), "#f39c12")
        
    def add_stats_card(self, row, col, icon, title, value, subtitle, color):
        """Ajouter une carte de statistique"""
        card = StatsCard(icon, title, value, subtitle, color)
        self.stats_layout.addWidget(card, row, col)
        
    def create_quick_actions(self, layout):
        """Créer la section actions rapides"""
        section_label = QLabel("⚡ Actions Rapides")
        section_font = QFont()
        section_font.setPointSize(16)
        section_font.setBold(True)
        section_label.setFont(section_font)
        section_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(section_label)
        
        # Boutons d'actions
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        from src.models import UserRole
        
        if self.user.role in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
            btn1 = self.create_action_button("➕ Nouvel Élève", "#3498db")
            actions_layout.addWidget(btn1)
        
        if self.user.role in [UserRole.ADMIN, UserRole.CASHIER]:
            btn2 = self.create_action_button("💵 Nouveau Paiement", "#1abc9c")
            actions_layout.addWidget(btn2)
        
        if self.user.role in [UserRole.ADMIN, UserRole.INSTRUCTOR]:
            btn3 = self.create_action_button("📅 Planifier Session", "#9b59b6")
            actions_layout.addWidget(btn3)
        
        if self.user.role == UserRole.ADMIN:
            btn4 = self.create_action_button("💾 Sauvegarder", "#f39c12")
            actions_layout.addWidget(btn4)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
    def create_action_button(self, text, color):
        """Créer un bouton d'action rapide"""
        btn = QPushButton(text)
        btn.setMinimumHeight(50)
        btn.setMinimumWidth(180)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 15px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
        """)
        return btn
        
    def darken_color(self, hex_color):
        """Assombrir une couleur hex"""
        # Simplification - retourner des couleurs prédéfinies
        colors = {
            "#3498db": "#2980b9",
            "#1abc9c": "#16a085",
            "#9b59b6": "#8e44ad",
            "#f39c12": "#e67e22",
        }
        return colors.get(hex_color, hex_color)
        
    def create_recent_activity(self, layout):
        """Créer la section activité récente"""
        section_label = QLabel("🕐 Activité Récente")
        section_font = QFont()
        section_font.setPointSize(16)
        section_font.setBold(True)
        section_label.setFont(section_font)
        section_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(section_label)
        
        # Frame pour l'activité
        activity_frame = QFrame()
        activity_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        activity_layout = QVBoxLayout(activity_frame)
        
        # Sessions du jour
        today_sessions = SessionController.get_today_sessions()
        
        if today_sessions:
            for session in today_sessions[:5]:  # Afficher les 5 premières
                item = QLabel(
                    f"📅 {session.start_datetime.strftime('%H:%M')} - "
                    f"{session.student.full_name if session.student else 'N/A'} "
                    f"avec {session.instructor.full_name if session.instructor else 'N/A'}"
                )
                item.setStyleSheet("color: #2c3e50; padding: 8px; font-size: 13px;")
                activity_layout.addWidget(item)
        else:
            no_activity = QLabel("Aucune session programmée aujourd'hui")
            no_activity.setStyleSheet("color: #95a5a6; font-style: italic;")
            activity_layout.addWidget(no_activity)
        
        activity_layout.addStretch()
        layout.addWidget(activity_frame)
        
    def refresh(self):
        """Actualiser les données"""
        # Effacer les cartes existantes
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Recharger les données
        self.load_data()
