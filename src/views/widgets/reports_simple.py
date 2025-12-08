"""
Module: Rapports simplifiés SANS matplotlib
Version: 1.0.0 - Créé le 2025-12-08

Description:
    Version simplifiée du dashboard de rapports sans dépendance matplotlib
    - KPIs globaux
    - Statistiques textuelles
    - Fonctionne sur tous les systèmes
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QComboBox, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datetime import datetime, timedelta, date
from collections import defaultdict

from src.controllers.student_controller import StudentController
from src.controllers.session_controller import SessionController
from src.controllers.payment_controller import PaymentController
from src.controllers.exam_controller import ExamController
from src.controllers.instructor_controller import InstructorController
from src.controllers.vehicle_controller import VehicleController
from src.models import StudentStatus, SessionStatus, ExamResult, ExamType


class ReportsSimpleWidget(QWidget):
    """Widget de rapports simplifié SANS matplotlib"""
    
    def __init__(self):
        super().__init__()
        self.current_period = 'month'
        self.setup_ui()
        self.load_reports()
    
    def setup_ui(self):
        """Configuration de l'interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                background: #f5f5f5; width: 10px; border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #2196F3; border-radius: 5px; min-height: 30px;
            }
        """)
        
        container = QWidget()
        container.setStyleSheet("background: #f5f7fa;")
        content = QVBoxLayout(container)
        content.setSpacing(20)
        content.setContentsMargins(20, 20, 20, 20)
        
        # En-tête
        header = QHBoxLayout()
        
        title = QLabel("📊 RAPPORTS ET ANALYSES")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a1a1a; padding: 10px;")
        header.addWidget(title)
        header.addStretch()
        
        # Période
        period_label = QLabel("Période:")
        period_label.setFont(QFont("Segoe UI", 10))
        period_label.setStyleSheet("color: #666; padding-right: 8px;")
        header.addWidget(period_label)
        
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Cette semaine", "Ce mois", "Ce trimestre", "Cette année", "Tout"
        ])
        self.period_combo.setCurrentText("Ce mois")
        self.period_combo.setStyleSheet("""
            QComboBox {
                background: white; border: 2px solid #e0e0e0;
                border-radius: 8px; padding: 8px 15px;
                font-size: 11pt; min-width: 150px; color: #333;
            }
        """)
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        header.addWidget(self.period_combo)
        
        # Rafraîchir
        refresh_btn = QPushButton("🔄")
        refresh_btn.clicked.connect(self.load_reports)
        refresh_btn.setFixedSize(45, 45)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3; color: white;
                border-radius: 8px; font-size: 14pt; border: none;
            }
            QPushButton:hover { background: #1976D2; }
        """)
        header.addWidget(refresh_btn)
        
        content.addLayout(header)
        
        # KPIs
        self.kpis_layout = QHBoxLayout()
        self.kpis_layout.setSpacing(20)
        content.addLayout(self.kpis_layout)
        
        # Sections de statistiques
        stats_row1 = QHBoxLayout()
        stats_row1.setSpacing(20)
        
        self.students_frame = self.create_section("👥 Élèves par Statut")
        stats_row1.addWidget(self.students_frame)
        
        self.sessions_frame = self.create_section("📅 Sessions (7 derniers jours)")
        stats_row1.addWidget(self.sessions_frame)
        
        content.addLayout(stats_row1)
        
        stats_row2 = QHBoxLayout()
        stats_row2.setSpacing(20)
        
        self.revenue_frame = self.create_section("💰 Revenus (6 derniers mois)")
        stats_row2.addWidget(self.revenue_frame)
        
        self.exams_frame = self.create_section("📝 Résultats Examens")
        stats_row2.addWidget(self.exams_frame)
        
        content.addLayout(stats_row2)
        
        stats_row3 = QHBoxLayout()
        stats_row3.setSpacing(20)
        
        self.instructors_frame = self.create_section("👨‍🏫 Top 5 Moniteurs")
        stats_row3.addWidget(self.instructors_frame)
        
        self.vehicles_frame = self.create_section("🚗 Top 5 Véhicules")
        stats_row3.addWidget(self.vehicles_frame)
        
        content.addLayout(stats_row3)
        
        content.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
    
    def create_section(self, title):
        """Créer une section"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white; border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        frame.setMinimumHeight(250)
        
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
        
        frame.content_layout = layout
        return frame
    
    def create_kpi_card(self, label, value, icon, color, subtitle=""):
        """Créer une carte KPI"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {color}; border-radius: 12px; border: none;
            }}
        """)
        card.setMinimumHeight(140)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 28))
        icon_label.setStyleSheet("color: white; border: none;")
        layout.addWidget(icon_label)
        
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        value_label.setStyleSheet("color: white; border: none;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        text_label = QLabel(label)
        text_label.setFont(QFont("Segoe UI", 11))
        text_label.setStyleSheet("color: white; border: none;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setWordWrap(True)
        layout.addWidget(text_label)
        
        if subtitle:
            sub_label = QLabel(subtitle)
            sub_label.setFont(QFont("Segoe UI", 9))
            sub_label.setStyleSheet("color: rgba(255,255,255,0.8); border: none;")
            sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(sub_label)
        
        return card
    
    def on_period_changed(self):
        """Changement de période"""
        period_map = {
            'Cette semaine': 'week', 'Ce mois': 'month',
            'Ce trimestre': 'quarter', 'Cette année': 'year', 'Tout': 'all'
        }
        self.current_period = period_map.get(self.period_combo.currentText(), 'month')
        self.load_reports()
    
    def get_date_range(self):
        """Plage de dates"""
        today = date.today()
        if self.current_period == 'all':
            return date(2000, 1, 1), date(2099, 12, 31)
        elif self.current_period == 'week':
            start = today - timedelta(days=today.weekday())
            return start, start + timedelta(days=6)
        elif self.current_period == 'month':
            start = today.replace(day=1)
            if today.month == 12:
                end = today.replace(day=31)
            else:
                end = (today.replace(month=today.month + 1, day=1) - timedelta(days=1))
            return start, end
        elif self.current_period == 'quarter':
            quarter = (today.month - 1) // 3
            start = today.replace(month=quarter * 3 + 1, day=1)
            end_month = quarter * 3 + 3
            if end_month == 12:
                end = today.replace(month=12, day=31)
            else:
                end = (today.replace(month=end_month + 1, day=1) - timedelta(days=1))
            return start, end
        elif self.current_period == 'year':
            return today.replace(month=1, day=1), today.replace(month=12, day=31)
        return today, today
    
    def load_reports(self):
        """Charger rapports"""
        # KPIs
        while self.kpis_layout.count():
            item = self.kpis_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        start_date, end_date = self.get_date_range()
        students = StudentController.get_all_students()
        all_sessions = SessionController.get_all_sessions()
        sessions = [s for s in all_sessions if s.start_datetime and start_date <= s.start_datetime.date() <= end_date]
        
        active = len([s for s in students if s.status == StudentStatus.ACTIVE])
        completed = len([s for s in sessions if s.status == SessionStatus.COMPLETED])
        
        from src.models import Payment, get_session
        db = get_session()
        payments = [p for p in db.query(Payment).all() if p.payment_date and start_date <= p.payment_date <= end_date]
        revenue = sum(p.amount for p in payments)
        
        exams = [e for e in ExamController.get_all_exams() if start_date <= e.scheduled_date <= end_date]
        passed = len([e for e in exams if e.result == ExamResult.PASSED])
        total_exams = len([e for e in exams if e.result in [ExamResult.PASSED, ExamResult.FAILED]])
        rate = (passed / total_exams * 100) if total_exams > 0 else 0
        
        self.kpis_layout.addWidget(self.create_kpi_card("Élèves Actifs", active, "👥", "#2196F3", f"sur {len(students)} total"))
        self.kpis_layout.addWidget(self.create_kpi_card("Sessions Terminées", completed, "✅", "#4CAF50", f"sur {len(sessions)} total"))
        self.kpis_layout.addWidget(self.create_kpi_card("Revenus", f"{revenue:,.0f}", "💰", "#FF9800", "DH"))
        self.kpis_layout.addWidget(self.create_kpi_card("Taux Réussite", f"{rate:.1f}%", "📈", "#9C27B0", f"{passed}/{total_exams}"))
        
        # Charger sections
        self.load_students_stats(students)
        self.load_sessions_stats()
        self.load_revenue_stats()
        self.load_exams_stats(exams)
        self.load_instructors_stats()
        self.load_vehicles_stats()
    
    def load_students_stats(self, students):
        """Stats élèves"""
        while self.students_frame.content_layout.count() > 2:
            item = self.students_frame.content_layout.takeAt(2)
            if item.widget():
                item.widget().deleteLater()
        
        status_counts = defaultdict(int)
        for s in students:
            status_counts[s.status.value] += 1
        
        for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
            label = QLabel(f"• {status}: {count}")
            label.setFont(QFont("Segoe UI", 10))
            label.setStyleSheet("color: #333; border: none; padding: 5px;")
            self.students_frame.content_layout.addWidget(label)
        
        self.students_frame.content_layout.addStretch()
    
    def load_sessions_stats(self):
        """Stats sessions 7 jours"""
        while self.sessions_frame.content_layout.count() > 2:
            item = self.sessions_frame.content_layout.takeAt(2)
            if item.widget():
                item.widget().deleteLater()
        
        today = date.today()
        for i in range(7):
            day = today - timedelta(days=6 - i)
            sessions = SessionController.get_sessions_by_date_range(day, day)
            label = QLabel(f"• {day.strftime('%d/%m')}: {len(sessions)} sessions")
            label.setFont(QFont("Segoe UI", 10))
            label.setStyleSheet("color: #333; border: none; padding: 5px;")
            self.sessions_frame.content_layout.addWidget(label)
        
        self.sessions_frame.content_layout.addStretch()
    
    def load_revenue_stats(self):
        """Stats revenus 6 mois"""
        while self.revenue_frame.content_layout.count() > 2:
            item = self.revenue_frame.content_layout.takeAt(2)
            if item.widget():
                item.widget().deleteLater()
        
        from src.models import Payment, get_session
        db = get_session()
        today = date.today()
        
        for i in range(6):
            month_offset = 5 - i
            target_month = today.month - month_offset
            target_year = today.year
            while target_month < 1:
                target_month += 12
                target_year -= 1
            
            start = date(target_year, target_month, 1)
            if target_month == 12:
                end = date(target_year, 12, 31)
            else:
                end = date(target_year, target_month + 1, 1) - timedelta(days=1)
            
            payments = db.query(Payment).filter(Payment.payment_date >= start, Payment.payment_date <= end).all()
            total = sum(p.amount for p in payments)
            
            label = QLabel(f"• {start.strftime('%m/%Y')}: {total:,.0f} DH")
            label.setFont(QFont("Segoe UI", 10))
            label.setStyleSheet("color: #333; border: none; padding: 5px;")
            self.revenue_frame.content_layout.addWidget(label)
        
        self.revenue_frame.content_layout.addStretch()
    
    def load_exams_stats(self, exams):
        """Stats examens"""
        while self.exams_frame.content_layout.count() > 2:
            item = self.exams_frame.content_layout.takeAt(2)
            if item.widget():
                item.widget().deleteLater()
        
        result_counts = defaultdict(int)
        for e in exams:
            result_counts[e.result.value] += 1
        
        labels_map = {'reussi': '✅ Réussi', 'echoue': '❌ Échoué', 'absent': '👻 Absent', 'en_attente': '⏳ En Attente'}
        
        for result, count in sorted(result_counts.items(), key=lambda x: -x[1]):
            label_text = labels_map.get(result, result)
            label = QLabel(f"• {label_text}: {count}")
            label.setFont(QFont("Segoe UI", 10))
            label.setStyleSheet("color: #333; border: none; padding: 5px;")
            self.exams_frame.content_layout.addWidget(label)
        
        self.exams_frame.content_layout.addStretch()
    
    def load_instructors_stats(self):
        """Top moniteurs"""
        while self.instructors_frame.content_layout.count() > 2:
            item = self.instructors_frame.content_layout.takeAt(2)
            if item.widget():
                item.widget().deleteLater()
        
        instructors = sorted(InstructorController.get_all_instructors(), key=lambda x: x.total_hours_taught or 0, reverse=True)[:5]
        
        for i, inst in enumerate(instructors, 1):
            label = QLabel(f"#{i}. {inst.full_name}: {inst.total_hours_taught or 0:.1f}h")
            label.setFont(QFont("Segoe UI", 10))
            label.setStyleSheet("color: #333; border: none; padding: 5px;")
            self.instructors_frame.content_layout.addWidget(label)
        
        self.instructors_frame.content_layout.addStretch()
    
    def load_vehicles_stats(self):
        """Top véhicules"""
        while self.vehicles_frame.content_layout.count() > 2:
            item = self.vehicles_frame.content_layout.takeAt(2)
            if item.widget():
                item.widget().deleteLater()
        
        vehicles = sorted(VehicleController.get_all_vehicles(), key=lambda x: x.total_hours_used or 0, reverse=True)[:5]
        
        for i, v in enumerate(vehicles, 1):
            label = QLabel(f"#{i}. {v.plate_number} ({v.make}): {v.total_hours_used or 0:.1f}h")
            label.setFont(QFont("Segoe UI", 10))
            label.setStyleSheet("color: #333; border: none; padding: 5px;")
            self.vehicles_frame.content_layout.addWidget(label)
        
        self.vehicles_frame.content_layout.addStretch()
