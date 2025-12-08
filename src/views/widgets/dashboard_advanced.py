"""
Widget Dashboard Avancé avec graphiques statistiques
"""

import matplotlib
matplotlib.use('Qt5Agg')  # Backend pour PySide6

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QPushButton, QScrollArea, QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.controllers.student_controller import StudentController
from src.controllers.session_controller import SessionController
from src.controllers.payment_controller import PaymentController
from src.models import StudentStatus, SessionStatus, get_session

# Style seaborn
sns.set_style("whitegrid")
sns.set_palette("husl")


class StatCard(QFrame):
    """Carte de statistique élégante"""
    
    def __init__(self, icon, title, value, subtitle="", color="#3498db"):
        super().__init__()
        self.setObjectName("statCard")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # En-tête
        header = QLabel(f"{icon} {title}")
        header.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {color};")
        
        # Valeur principale
        value_label = QLabel(str(value))
        value_font = QFont()
        value_font.setPointSize(28)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {color};")
        
        # Sous-titre
        subtitle_label = None
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: #95a5a6; font-size: 11px;")
        
        layout.addWidget(header)
        layout.addWidget(value_label)
        if subtitle_label:
            layout.addWidget(subtitle_label)
        layout.addStretch()
        
        # Style
        self.setStyleSheet("""
            QFrame#statCard {
                background-color: white;
                border-radius: 12px;
                border: 2px solid #ecf0f1;
            }
            QFrame#statCard:hover {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
        """)
        self.setMinimumHeight(140)
        self.setMinimumWidth(200)


class ChartWidget(QFrame):
    """Widget pour afficher un graphique matplotlib"""
    
    def __init__(self, title: str):
        super().__init__()
        self.title = title
        self.setup_ui()
        
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Titre
        title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Canvas matplotlib
        self.figure = Figure(figsize=(8, 5), facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Style
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        self.setMinimumHeight(400)


class DashboardAdvancedWidget(QWidget):
    """Dashboard avancé avec graphiques et statistiques"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = get_session()
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Configurer l'interface"""
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Widget de contenu
        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # En-tête
        self.create_header(main_layout)
        
        # Cartes KPI
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(15)
        main_layout.addLayout(self.stats_grid)
        
        main_layout.addSpacing(10)
        
        # Onglets de graphiques
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: white;
                color: #2c3e50;
                padding: 10px 20px;
                margin-right: 5px;
                border-radius: 8px 8px 0 0;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background: #ecf0f1;
            }
        """)
        
        # Onglet Chiffre d'affaires
        self.revenue_chart = ChartWidget("📊 Chiffre d'Affaires Mensuel")
        tabs.addTab(self.revenue_chart, "💰 Chiffre d'Affaires")
        
        # Onglet Évolution élèves
        self.students_chart = ChartWidget("👥 Évolution des Élèves")
        tabs.addTab(self.students_chart, "👥 Élèves")
        
        # Onglet Taux de réussite
        self.success_chart = ChartWidget("🎓 Taux de Réussite aux Examens")
        tabs.addTab(self.success_chart, "🎓 Réussite")
        
        # Onglet Sessions
        self.sessions_chart = ChartWidget("📅 Répartition des Sessions")
        tabs.addTab(self.sessions_chart, "📅 Sessions")
        
        main_layout.addWidget(tabs)
        main_layout.addStretch()
        
        scroll.setWidget(content)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        
    def create_header(self, layout):
        """Créer l'en-tête"""
        header_layout = QVBoxLayout()
        
        # Titre de bienvenue
        welcome = QLabel(f"👋 Bonjour, {self.user.full_name}")
        welcome_font = QFont()
        welcome_font.setPointSize(24)
        welcome_font.setBold(True)
        welcome.setFont(welcome_font)
        welcome.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(welcome)
        
        # Date
        date_label = QLabel(f"📅 {datetime.now().strftime('%A %d %B %Y')}")
        date_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        header_layout.addWidget(date_label)
        
        # Bouton refresh
        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.clicked.connect(self.refresh)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()
        header_layout.addLayout(btn_layout)
        
        layout.addLayout(header_layout)
        
    def load_data(self):
        """Charger toutes les données"""
        self.load_kpi_cards()
        self.load_revenue_chart()
        self.load_students_chart()
        self.load_success_chart()
        self.load_sessions_chart()
        
    def load_kpi_cards(self):
        """Charger les cartes KPI"""
        # Nettoyer
        while self.stats_grid.count():
            item = self.stats_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Élèves actifs
        active_count = StudentController.get_active_students_count()
        self.stats_grid.addWidget(
            StatCard("👥", "Élèves Actifs", active_count, "En formation", "#3498db"),
            0, 0
        )
        
        # CA du mois
        now = datetime.now()
        month_revenue = PaymentController.get_monthly_revenue(now.year, now.month)
        self.stats_grid.addWidget(
            StatCard("💰", "CA du Mois", f"{month_revenue:,.0f} DH", 
                    now.strftime("%B %Y"), "#1abc9c"),
            0, 1
        )
        
        # Sessions aujourd'hui
        today_sessions = SessionController.get_today_sessions()
        self.stats_grid.addWidget(
            StatCard("📅", "Sessions Aujourd'hui", len(today_sessions),
                    datetime.now().strftime("%d/%m/%Y"), "#9b59b6"),
            0, 2
        )
        
        # Dettes totales
        debt_students = StudentController.get_students_with_debt()
        total_debt = sum(abs(s.balance) for s in debt_students)
        self.stats_grid.addWidget(
            StatCard("⚠️", "Dettes", f"{total_debt:,.0f} DH",
                    f"{len(debt_students)} élèves", "#e74c3c"),
            0, 3
        )
        
    def load_revenue_chart(self):
        """Graphique CA mensuel (derniers 6 mois)"""
        self.revenue_chart.figure.clear()
        ax = self.revenue_chart.figure.add_subplot(111)
        
        # Données des 6 derniers mois
        months_data = []
        labels = []
        
        now = datetime.now()
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30*i)
            month_revenue = PaymentController.get_monthly_revenue(
                month_date.year, month_date.month
            )
            months_data.append(month_revenue)
            labels.append(month_date.strftime("%b %Y"))
        
        # Graphique en barres
        bars = ax.bar(labels, months_data, color='#3498db', alpha=0.8, edgecolor='#2980b9', linewidth=2)
        
        # Ajouter les valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:,.0f} DH',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax.set_xlabel('Mois', fontsize=12, fontweight='bold')
        ax.set_ylabel('Chiffre d\'Affaires (DH)', fontsize=12, fontweight='bold')
        ax.set_title('Évolution du CA sur 6 mois', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        
        try:
            self.revenue_chart.figure.tight_layout()
            self.revenue_chart.canvas.draw()
        except RuntimeError:
            pass
        
    def load_students_chart(self):
        """Graphique évolution du nombre d'élèves"""
        self.students_chart.figure.clear()
        ax = self.students_chart.figure.add_subplot(111)
        
        # Répartition par statut
        all_students = StudentController.get_all_students()
        status_counts = {}
        
        for student in all_students:
            status = student.status.value if hasattr(student.status, 'value') else str(student.status)
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Traduction des statuts
        status_labels = {
            'pending': 'En Attente',
            'active': 'Actif',
            'passed': 'Réussi',
            'failed': 'Échoué',
            'suspended': 'Suspendu',
            'graduated': 'Diplômé'
        }
        
        labels = [status_labels.get(k, k) for k in status_counts.keys()]
        values = list(status_counts.values())
        colors = ['#3498db', '#1abc9c', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
        
        # Diagramme en secteurs (pie chart)
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, autopct='%1.1f%%',
            colors=colors[:len(values)], startangle=90,
            textprops={'fontsize': 11, 'fontweight': 'bold'}
        )
        
        # Style des pourcentages
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
            autotext.set_fontweight('bold')
        
        ax.set_title('Répartition des Élèves par Statut', fontsize=14, fontweight='bold', pad=20)
        
        try:
            self.students_chart.figure.tight_layout()
            self.students_chart.canvas.draw()
        except RuntimeError:
            pass
        
    def load_success_chart(self):
        """Graphique taux de réussite"""
        try:
            self.success_chart.figure.clear()
            ax = self.success_chart.figure.add_subplot(111)
        except RuntimeError:
            # Canvas déjà supprimé, ignorer
            return
        
        # Statistiques de réussite
        from src.models import ExamType, ExamResult
        from src.controllers.exam_controller import ExamController
        
        # Réussite code vs conduite
        all_exams = ExamController.get_all_exams()
        
        theory_passed = len([e for e in all_exams 
                            if e.exam_type == ExamType.THEORETICAL 
                            and e.result == ExamResult.PASSED])
        theory_total = len([e for e in all_exams if e.exam_type == ExamType.THEORETICAL])
        
        practical_passed = len([e for e in all_exams 
                               if e.exam_type == ExamType.PRACTICAL 
                               and e.result == ExamResult.PASSED])
        practical_total = len([e for e in all_exams if e.exam_type == ExamType.PRACTICAL])
        
        theory_rate = (theory_passed / theory_total * 100) if theory_total > 0 else 0
        practical_rate = (practical_passed / practical_total * 100) if practical_total > 0 else 0
        
        # Graphique en barres horizontales
        categories = ['Examen Théorique', 'Examen Pratique']
        rates = [theory_rate, practical_rate]
        colors_list = ['#3498db', '#1abc9c']
        
        bars = ax.barh(categories, rates, color=colors_list, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        # Ajouter les valeurs
        for i, (bar, rate) in enumerate(zip(bars, rates)):
            width = bar.get_width()
            ax.text(width + 2, bar.get_y() + bar.get_height()/2.,
                   f'{rate:.1f}%',
                   ha='left', va='center', fontsize=12, fontweight='bold')
        
        ax.set_xlabel('Taux de Réussite (%)', fontsize=12, fontweight='bold')
        ax.set_title('Taux de Réussite aux Examens', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, 110)
        ax.grid(True, axis='x', alpha=0.3)
        
        try:
            self.success_chart.figure.tight_layout()
            self.success_chart.canvas.draw()
        except RuntimeError:
            # Canvas déjà supprimé, ignorer
            pass
        
    def load_sessions_chart(self):
        """Graphique répartition des sessions"""
        self.sessions_chart.figure.clear()
        ax = self.sessions_chart.figure.add_subplot(111)
        
        # Répartition par statut de session
        all_sessions = SessionController.get_all_sessions()
        
        status_counts = {}
        for session in all_sessions:
            status = session.status.value if hasattr(session.status, 'value') else str(session.status)
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Traduction
        status_labels = {
            'scheduled': 'Planifiée',
            'completed': 'Terminée',
            'cancelled': 'Annulée',
            'no_show': 'Absence'
        }
        
        labels = [status_labels.get(k, k) for k in status_counts.keys()]
        values = list(status_counts.values())
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
        
        # Diagramme en barres
        bars = ax.bar(labels, values, color=colors[:len(values)], alpha=0.8, edgecolor='black', linewidth=2)
        
        # Valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax.set_ylabel('Nombre de Sessions', fontsize=12, fontweight='bold')
        ax.set_title('Répartition des Sessions par Statut', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, axis='y', alpha=0.3)
        
        try:
            self.sessions_chart.figure.tight_layout()
            self.sessions_chart.canvas.draw()
        except RuntimeError:
            pass
        
    def refresh(self):
        """Actualiser toutes les données"""
        self.load_data()
    
    def closeEvent(self, event):
        """Nettoyage lors de la fermeture"""
        try:
            if hasattr(self, 'db') and self.db:
                self.db.close()
        except:
            pass
        event.accept()
