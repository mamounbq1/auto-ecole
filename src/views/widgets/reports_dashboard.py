"""
Module: Tableau de bord des rapports et analyses
Version: 1.0.0 - Créé le 2025-12-08

Description:
    Dashboard avec graphiques et analyses avancées:
    - Vue d'ensemble globale (KPIs)
    - Graphiques matplotlib (camemberts, barres, lignes)
    - Analyses multi-modules (élèves, sessions, paiements, examens)
    - Exports PDF et Excel
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QComboBox, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datetime import datetime, timedelta, date
from collections import defaultdict

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from src.controllers.student_controller import StudentController
from src.controllers.session_controller import SessionController
from src.controllers.payment_controller import PaymentController
from src.controllers.exam_controller import ExamController
from src.controllers.instructor_controller import InstructorController
from src.controllers.vehicle_controller import VehicleController
from src.models import StudentStatus, SessionStatus, ExamResult, ExamType


class MplCanvas(FigureCanvasQTAgg):
    """Canvas matplotlib pour graphiques"""
    
    def __init__(self, parent=None, width=6, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor='white')
        self.axes = fig.add_subplot(111)
        fig.tight_layout(pad=2.0)
        super().__init__(fig)


class ReportsDashboard(QWidget):
    """Dashboard des rapports avec graphiques et analyses"""
    
    def __init__(self):
        super().__init__()
        self.current_period = 'month'  # Par défaut: ce mois
        self.setup_ui()
        self.load_reports()
    
    def setup_ui(self):
        """Configuration de l'interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Zone de défilement
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #f5f5f5;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #2196F3;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #1976D2;
            }
        """)
        
        # Conteneur principal
        container = QWidget()
        container.setStyleSheet("background: #f5f7fa;")
        content_layout = QVBoxLayout(container)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # En-tête avec titre et contrôles
        header = QHBoxLayout()
        
        title = QLabel("📊 RAPPORTS ET ANALYSES")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a1a1a; padding: 10px;")
        header.addWidget(title)
        
        header.addStretch()
        
        # Sélecteur de période
        period_label = QLabel("Période:")
        period_label.setFont(QFont("Segoe UI", 10))
        period_label.setStyleSheet("color: #666; padding-right: 8px;")
        header.addWidget(period_label)
        
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Cette semaine",
            "Ce mois",
            "Ce trimestre",
            "Cette année",
            "Tout"
        ])
        self.period_combo.setCurrentText("Ce mois")
        self.period_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 11pt;
                min-width: 150px;
                color: #333;
            }
            QComboBox:hover {
                border: 2px solid #2196F3;
            }
        """)
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        header.addWidget(self.period_combo)
        
        # Bouton export PDF
        export_pdf_btn = QPushButton("📄 Export PDF")
        export_pdf_btn.clicked.connect(self.export_pdf)
        export_pdf_btn.setStyleSheet("""
            QPushButton {
                background: #F44336;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #D32F2F;
            }
        """)
        header.addWidget(export_pdf_btn)
        
        # Bouton rafraîchir
        refresh_btn = QPushButton("🔄")
        refresh_btn.clicked.connect(self.load_reports)
        refresh_btn.setFixedSize(45, 45)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                border-radius: 8px;
                font-size: 14pt;
                border: none;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)
        header.addWidget(refresh_btn)
        
        content_layout.addLayout(header)
        
        # KPIs globaux (4 cartes)
        self.kpis_layout = QHBoxLayout()
        self.kpis_layout.setSpacing(20)
        content_layout.addLayout(self.kpis_layout)
        
        # Section graphiques ligne 1
        charts_row1 = QHBoxLayout()
        charts_row1.setSpacing(20)
        
        # Graphique 1: Distribution des élèves par statut
        self.students_chart_frame = self.create_chart_frame("👥 Répartition des Élèves par Statut")
        charts_row1.addWidget(self.students_chart_frame)
        
        # Graphique 2: Évolution des sessions (7 jours)
        self.sessions_chart_frame = self.create_chart_frame("📅 Évolution des Sessions (7 jours)")
        charts_row1.addWidget(self.sessions_chart_frame)
        
        content_layout.addLayout(charts_row1)
        
        # Section graphiques ligne 2
        charts_row2 = QHBoxLayout()
        charts_row2.setSpacing(20)
        
        # Graphique 3: Revenus mensuels
        self.revenue_chart_frame = self.create_chart_frame("💰 Évolution des Revenus (6 mois)")
        charts_row2.addWidget(self.revenue_chart_frame)
        
        # Graphique 4: Résultats des examens
        self.exams_chart_frame = self.create_chart_frame("📝 Résultats des Examens")
        charts_row2.addWidget(self.exams_chart_frame)
        
        content_layout.addLayout(charts_row2)
        
        # Section graphiques ligne 3
        charts_row3 = QHBoxLayout()
        charts_row3.setSpacing(20)
        
        # Graphique 5: Top moniteurs
        self.instructors_chart_frame = self.create_chart_frame("👨‍🏫 Top 5 Moniteurs (Heures)")
        charts_row3.addWidget(self.instructors_chart_frame)
        
        # Graphique 6: Top véhicules
        self.vehicles_chart_frame = self.create_chart_frame("🚗 Top 5 Véhicules (Utilisation)")
        charts_row3.addWidget(self.vehicles_chart_frame)
        
        content_layout.addLayout(charts_row3)
        
        content_layout.addStretch()
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
    
    def create_chart_frame(self, title):
        """Créer un cadre pour graphique"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        frame.setMinimumHeight(400)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #333; border: none;")
        layout.addWidget(title_label)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background: #e0e0e0; border: none; max-height: 1px;")
        layout.addWidget(separator)
        
        # Placeholder pour le canvas
        frame.chart_layout = layout
        
        return frame
    
    def create_kpi_card(self, label, value, icon, color, subtitle=""):
        """Créer une carte KPI"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color}, stop:1 {self.darken_color(color)}
                );
                border-radius: 12px;
                border: none;
            }}
        """)
        card.setMinimumHeight(140)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 28))
        icon_label.setStyleSheet("color: white; border: none;")
        layout.addWidget(icon_label)
        
        # Value
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        value_label.setStyleSheet("color: white; border: none;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        # Label
        text_label = QLabel(label)
        text_label.setFont(QFont("Segoe UI", 11))
        text_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); border: none;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setWordWrap(True)
        layout.addWidget(text_label)
        
        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setFont(QFont("Segoe UI", 9))
            subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); border: none; font-style: italic;")
            subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(subtitle_label)
        
        return card
    
    def darken_color(self, color):
        """Assombrir une couleur pour le gradient"""
        colors = {
            '#2196F3': '#1976D2',
            '#4CAF50': '#388E3C',
            '#FF9800': '#F57C00',
            '#F44336': '#D32F2F',
            '#9C27B0': '#7B1FA2',
            '#00BCD4': '#0097A7'
        }
        return colors.get(color, color)
    
    def on_period_changed(self):
        """Changement de période"""
        period_map = {
            'Cette semaine': 'week',
            'Ce mois': 'month',
            'Ce trimestre': 'quarter',
            'Cette année': 'year',
            'Tout': 'all'
        }
        self.current_period = period_map.get(self.period_combo.currentText(), 'month')
        self.load_reports()
    
    def get_date_range(self):
        """Obtenir la plage de dates selon la période"""
        today = date.today()
        
        if self.current_period == 'all':
            return date(2000, 1, 1), date(2099, 12, 31)
        elif self.current_period == 'week':
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            return start, end
        elif self.current_period == 'month':
            start = today.replace(day=1)
            if today.month == 12:
                end = today.replace(day=31)
            else:
                next_month = today.replace(month=today.month + 1, day=1)
                end = next_month - timedelta(days=1)
            return start, end
        elif self.current_period == 'quarter':
            quarter = (today.month - 1) // 3
            start = today.replace(month=quarter * 3 + 1, day=1)
            end_month = quarter * 3 + 3
            if end_month == 12:
                end = today.replace(month=12, day=31)
            else:
                next_quarter = today.replace(month=end_month + 1, day=1)
                end = next_quarter - timedelta(days=1)
            return start, end
        elif self.current_period == 'year':
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
            return start, end
        
        return today, today
    
    def load_reports(self):
        """Charger tous les rapports et graphiques"""
        # Nettoyer KPIs
        while self.kpis_layout.count():
            item = self.kpis_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Charger les données
        start_date, end_date = self.get_date_range()
        
        students = StudentController.get_all_students()
        sessions = SessionController.get_all_sessions()
        
        # Filtrer sessions par période
        sessions_period = [
            s for s in sessions
            if start_date <= s.session_date <= end_date
        ]
        
        # KPIs
        total_students = len(students)
        active_students = len([s for s in students if s.status == StudentStatus.ACTIVE])
        total_sessions = len(sessions_period)
        completed_sessions = len([s for s in sessions_period if s.status == SessionStatus.COMPLETED])
        
        # Créer les KPIs
        self.kpis_layout.addWidget(
            self.create_kpi_card(
                "Élèves Actifs",
                active_students,
                "👥",
                "#2196F3",
                f"sur {total_students} total"
            )
        )
        
        self.kpis_layout.addWidget(
            self.create_kpi_card(
                "Sessions Terminées",
                completed_sessions,
                "✅",
                "#4CAF50",
                f"sur {total_sessions} total"
            )
        )
        
        # Revenus période
        from src.models import Payment, get_session
        session_db = get_session()
        payments = session_db.query(Payment).all()
        payments_period = [
            p for p in payments
            if p.payment_date and start_date <= p.payment_date <= end_date
        ]
        total_revenue = sum(p.amount for p in payments_period)
        
        self.kpis_layout.addWidget(
            self.create_kpi_card(
                "Revenus Période",
                f"{total_revenue:,.0f}",
                "💰",
                "#FF9800",
                "DH"
            )
        )
        
        # Taux de réussite examens
        exams = ExamController.get_all_exams()
        exams_period = [
            e for e in exams
            if start_date <= e.scheduled_date <= end_date
        ]
        passed_exams = len([e for e in exams_period if e.result == ExamResult.PASSED])
        completed_exams = len([e for e in exams_period if e.result in [ExamResult.PASSED, ExamResult.FAILED]])
        success_rate = (passed_exams / completed_exams * 100) if completed_exams > 0 else 0
        
        self.kpis_layout.addWidget(
            self.create_kpi_card(
                "Taux Réussite",
                f"{success_rate:.1f}%",
                "📈",
                "#9C27B0",
                f"{passed_exams}/{completed_exams} examens"
            )
        )
        
        # Charger les graphiques
        self.load_students_chart()
        self.load_sessions_chart()
        self.load_revenue_chart()
        self.load_exams_chart()
        self.load_instructors_chart()
        self.load_vehicles_chart()
    
    def load_students_chart(self):
        """Graphique: Distribution élèves par statut"""
        # Nettoyer
        for i in reversed(range(self.students_chart_frame.chart_layout.count())):
            if i > 1:  # Garder titre et séparateur
                widget = self.students_chart_frame.chart_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
        
        students = StudentController.get_all_students()
        
        # Compter par statut
        status_counts = defaultdict(int)
        for student in students:
            status_counts[student.status.value] += 1
        
        if not status_counts:
            return
        
        # Créer graphique
        canvas = MplCanvas(self, width=5, height=3.5)
        
        labels = list(status_counts.keys())
        sizes = list(status_counts.values())
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#F44336', '#9C27B0']
        
        canvas.axes.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        canvas.axes.set_title('Répartition par statut', fontsize=10, pad=10)
        
        self.students_chart_frame.chart_layout.addWidget(canvas)
    
    def load_sessions_chart(self):
        """Graphique: Évolution sessions 7 derniers jours"""
        # Nettoyer
        for i in reversed(range(self.sessions_chart_frame.chart_layout.count())):
            if i > 1:
                widget = self.sessions_chart_frame.chart_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
        
        # Données 7 jours
        days = []
        counts = []
        today = date.today()
        
        for i in range(7):
            day = today - timedelta(days=6 - i)
            sessions = SessionController.get_sessions_by_date_range(day, day)
            days.append(day.strftime('%d/%m'))
            counts.append(len(sessions))
        
        # Créer graphique
        canvas = MplCanvas(self, width=5, height=3.5)
        
        canvas.axes.bar(days, counts, color='#2196F3', alpha=0.7)
        canvas.axes.set_xlabel('Date', fontsize=9)
        canvas.axes.set_ylabel('Nombre de sessions', fontsize=9)
        canvas.axes.set_title('Activité quotidienne', fontsize=10, pad=10)
        canvas.axes.tick_params(axis='both', which='major', labelsize=8)
        canvas.axes.grid(axis='y', alpha=0.3)
        
        self.sessions_chart_frame.chart_layout.addWidget(canvas)
    
    def load_revenue_chart(self):
        """Graphique: Évolution revenus 6 derniers mois"""
        # Nettoyer
        for i in reversed(range(self.revenue_chart_frame.chart_layout.count())):
            if i > 1:
                widget = self.revenue_chart_frame.chart_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
        
        # Données 6 mois
        months = []
        revenues = []
        today = date.today()
        
        from src.models import Payment, get_session
        session_db = get_session()
        
        for i in range(6):
            # Calculer le mois
            month_offset = 5 - i
            target_month = today.month - month_offset
            target_year = today.year
            
            while target_month < 1:
                target_month += 12
                target_year -= 1
            
            # Début et fin du mois
            start = date(target_year, target_month, 1)
            if target_month == 12:
                end = date(target_year, 12, 31)
            else:
                next_month = date(target_year, target_month + 1, 1)
                end = next_month - timedelta(days=1)
            
            # Calculer revenus
            payments = session_db.query(Payment).filter(
                Payment.payment_date >= start,
                Payment.payment_date <= end
            ).all()
            
            total = sum(p.amount for p in payments)
            
            months.append(start.strftime('%m/%Y'))
            revenues.append(total)
        
        # Créer graphique
        canvas = MplCanvas(self, width=5, height=3.5)
        
        canvas.axes.plot(months, revenues, marker='o', color='#FF9800', linewidth=2, markersize=6)
        canvas.axes.fill_between(range(len(months)), revenues, alpha=0.3, color='#FF9800')
        canvas.axes.set_xlabel('Mois', fontsize=9)
        canvas.axes.set_ylabel('Revenus (DH)', fontsize=9)
        canvas.axes.set_title('Évolution mensuelle', fontsize=10, pad=10)
        canvas.axes.tick_params(axis='both', which='major', labelsize=8)
        canvas.axes.grid(True, alpha=0.3)
        
        self.revenue_chart_frame.chart_layout.addWidget(canvas)
    
    def load_exams_chart(self):
        """Graphique: Résultats examens"""
        # Nettoyer
        for i in reversed(range(self.exams_chart_frame.chart_layout.count())):
            if i > 1:
                widget = self.exams_chart_frame.chart_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
        
        start_date, end_date = self.get_date_range()
        exams = ExamController.get_all_exams()
        exams_period = [e for e in exams if start_date <= e.scheduled_date <= end_date]
        
        # Compter par résultat
        result_counts = defaultdict(int)
        for exam in exams_period:
            result_counts[exam.result.value] += 1
        
        if not result_counts:
            return
        
        # Créer graphique
        canvas = MplCanvas(self, width=5, height=3.5)
        
        labels = []
        sizes = []
        colors_map = {
            'reussi': '#4CAF50',
            'echoue': '#F44336',
            'absent': '#FF9800',
            'en_attente': '#FFC107'
        }
        colors = []
        
        for result, count in result_counts.items():
            labels.append(result.replace('_', ' ').title())
            sizes.append(count)
            colors.append(colors_map.get(result, '#999'))
        
        canvas.axes.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        canvas.axes.set_title('Distribution des résultats', fontsize=10, pad=10)
        
        self.exams_chart_frame.chart_layout.addWidget(canvas)
    
    def load_instructors_chart(self):
        """Graphique: Top 5 moniteurs"""
        # Nettoyer
        for i in reversed(range(self.instructors_chart_frame.chart_layout.count())):
            if i > 1:
                widget = self.instructors_chart_frame.chart_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
        
        instructors = InstructorController.get_all_instructors()
        
        # Trier par heures
        top_5 = sorted(instructors, key=lambda x: x.total_hours_taught or 0, reverse=True)[:5]
        
        if not top_5:
            return
        
        # Créer graphique
        canvas = MplCanvas(self, width=5, height=3.5)
        
        names = [i.full_name[:15] + '...' if len(i.full_name) > 15 else i.full_name for i in top_5]
        hours = [i.total_hours_taught or 0 for i in top_5]
        
        canvas.axes.barh(names, hours, color='#4CAF50', alpha=0.7)
        canvas.axes.set_xlabel('Heures enseignées', fontsize=9)
        canvas.axes.set_title('Classement des moniteurs', fontsize=10, pad=10)
        canvas.axes.tick_params(axis='both', which='major', labelsize=8)
        canvas.axes.grid(axis='x', alpha=0.3)
        
        self.instructors_chart_frame.chart_layout.addWidget(canvas)
    
    def load_vehicles_chart(self):
        """Graphique: Top 5 véhicules"""
        # Nettoyer
        for i in reversed(range(self.vehicles_chart_frame.chart_layout.count())):
            if i > 1:
                widget = self.vehicles_chart_frame.chart_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
        
        vehicles = VehicleController.get_all_vehicles()
        
        # Trier par utilisation
        top_5 = sorted(vehicles, key=lambda x: x.total_hours_used or 0, reverse=True)[:5]
        
        if not top_5:
            return
        
        # Créer graphique
        canvas = MplCanvas(self, width=5, height=3.5)
        
        names = [f"{v.plate_number}\n{v.make}" for v in top_5]
        hours = [v.total_hours_used or 0 for v in top_5]
        
        canvas.axes.barh(names, hours, color='#2196F3', alpha=0.7)
        canvas.axes.set_xlabel('Heures d\'utilisation', fontsize=9)
        canvas.axes.set_title('Véhicules les plus utilisés', fontsize=10, pad=10)
        canvas.axes.tick_params(axis='both', which='major', labelsize=8)
        canvas.axes.grid(axis='x', alpha=0.3)
        
        self.vehicles_chart_frame.chart_layout.addWidget(canvas)
    
    def export_pdf(self):
        """Exporter les rapports en PDF"""
        QMessageBox.information(
            self,
            "Export PDF",
            "Fonctionnalité d'export PDF en cours de développement.\n"
            "Utilisez les exports CSV individuels de chaque module pour le moment."
        )
