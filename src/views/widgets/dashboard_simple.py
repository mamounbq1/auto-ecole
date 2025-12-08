"""
Dashboard simple sans graphiques matplotlib (version de débogage)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QGridLayout, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.controllers import StudentController, PaymentController, SessionController
from src.models import get_session


class StatCard(QFrame):
    """Carte statistique simple"""
    
    def __init__(self, title, value, icon="📊", color="#3498db"):
        super().__init__()
        self.setObjectName("statCard")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Icône
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"font-size: 32px; color: {color};")
        
        # Valeur
        value_label = QLabel(str(value))
        value_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        value_label.setFont(font)
        value_label.setStyleSheet(f"color: {color};")
        
        # Titre
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        title_label.setWordWrap(True)
        
        layout.addWidget(icon_label)
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        
        # Style
        self.setStyleSheet("""
            QFrame#statCard {
                background-color: white;
                border: 1px solid #ecf0f1;
                border-radius: 8px;
                padding: 15px;
            }
            QFrame#statCard:hover {
                border: 1px solid #3498db;
            }
        """)


class DashboardSimpleWidget(QWidget):
    """Dashboard simplifié sans graphiques matplotlib"""
    
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.db_session = get_session()
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Titre
        title = QLabel("📊 Dashboard - Vue d'ensemble")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Message informatif
        info = QLabel("✅ Dashboard chargé avec succès (version simplifiée)")
        info.setStyleSheet("color: #27ae60; background-color: #d4edda; padding: 10px; border-radius: 5px;")
        layout.addWidget(info)
        
        # Grille de statistiques
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(15)
        layout.addLayout(self.stats_grid)
        
        # Bouton pour recharger
        refresh_btn = QPushButton("🔄 Actualiser les données")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.clicked.connect(self.load_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        
    def load_data(self):
        """Charger les données statistiques"""
        try:
            # Nettoyer la grille
            for i in reversed(range(self.stats_grid.count())): 
                self.stats_grid.itemAt(i).widget().setParent(None)
            
            # Statistiques élèves
            students = StudentController.get_all_students(self.db_session)
            active_students = sum(1 for s in students if s.status.value == 'active')
            
            # Statistiques financières
            from datetime import datetime, timedelta
            today = datetime.now()
            start_of_month = today.replace(day=1)
            payments = PaymentController.get_payments_by_date_range(
                self.db_session, start_of_month, today
            )
            monthly_revenue = sum(p.amount for p in payments if p.is_validated)
            
            # Statistiques sessions
            sessions_today = SessionController.get_sessions_by_date(
                self.db_session, today.date()
            )
            
            # Élèves avec dette
            students_with_debt = sum(1 for s in students if s.balance < 0)
            
            # Créer les cartes
            cards = [
                ("👥 Élèves actifs", active_students, "👥", "#3498db"),
                ("💰 CA mensuel", f"{monthly_revenue:.0f} DH", "💰", "#27ae60"),
                ("📅 Sessions aujourd'hui", len(sessions_today), "📅", "#f39c12"),
                ("⚠️ Impayés", students_with_debt, "⚠️", "#e74c3c"),
            ]
            
            # Ajouter les cartes à la grille
            for i, (title, value, icon, color) in enumerate(cards):
                card = StatCard(title, value, icon, color)
                self.stats_grid.addWidget(card, 0, i)
            
            # Message de succès
            print(f"✅ Dashboard chargé avec succès: {active_students} élèves actifs")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des données: {e}")
            import traceback
            traceback.print_exc()
            
            # Afficher un message d'erreur
            error_label = QLabel(f"⚠️ Erreur de chargement: {str(e)}")
            error_label.setStyleSheet("color: red; padding: 10px;")
            self.stats_grid.addWidget(error_label, 0, 0, 1, 4)
    
    def closeEvent(self, event):
        """Nettoyer lors de la fermeture"""
        try:
            if hasattr(self, 'db_session') and self.db_session:
                self.db_session.close()
        except:
            pass
        event.accept()
