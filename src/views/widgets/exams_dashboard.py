"""
Module: Tableau de bord des examens
Version: 1.0.0 - Créé le 2025-12-08

Description:
    Dashboard moderne affichant les statistiques des examens:
    - Statistiques générales (total, réussis, échoués, en attente)
    - Taux de réussite global
    - Distribution par type (théorique/pratique)
    - Examens à venir
    - Analyses par période
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from datetime import datetime, timedelta, date
from collections import defaultdict

from src.controllers.exam_controller import ExamController
from src.controllers.student_controller import StudentController
from src.models import ExamType, ExamResult, get_session, Exam


class ExamsDashboard(QWidget):
    """Dashboard des examens avec statistiques et analyses"""
    
    def __init__(self):
        super().__init__()
        self.current_period = 'all'  # Par défaut: tous les examens
        self.setup_ui()
        self.load_stats()
    
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
        
        # En-tête avec titre et sélecteur de période
        header = QHBoxLayout()
        
        title = QLabel("📊 TABLEAU DE BORD EXAMENS")
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
            "Tous les examens",
            "Aujourd'hui",
            "Cette semaine",
            "Ce mois",
            "Cette année"
        ])
        self.period_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 11pt;
                min-width: 180px;
                color: #333;
            }
            QComboBox:hover {
                border: 2px solid #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
        """)
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        header.addWidget(self.period_combo)
        
        content_layout.addLayout(header)
        
        # Statistiques principales (5 cartes)
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(20)
        content_layout.addLayout(self.stats_layout)
        
        # Deux sections côte à côte
        middle_row = QHBoxLayout()
        middle_row.setSpacing(20)
        
        # Distribution par type
        type_section = self.create_section("📈 Distribution par Type")
        self.type_layout = QVBoxLayout()
        type_section.layout().addLayout(self.type_layout)
        middle_row.addWidget(type_section)
        
        # Distribution par résultat
        result_section = self.create_section("📊 Distribution par Résultat")
        self.result_layout = QVBoxLayout()
        result_section.layout().addLayout(self.result_layout)
        middle_row.addWidget(result_section)
        
        content_layout.addLayout(middle_row)
        
        # Examens à venir
        upcoming_section = self.create_section("📅 Examens à Venir (7 prochains jours)")
        self.upcoming_layout = QVBoxLayout()
        upcoming_section.layout().addLayout(self.upcoming_layout)
        content_layout.addWidget(upcoming_section)
        
        # Trois sections côte à côte
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)
        
        # Top élèves réussis
        top_students_section = self.create_section("🏆 Top Élèves - Plus de Réussites")
        self.top_students_layout = QVBoxLayout()
        top_students_section.layout().addLayout(self.top_students_layout)
        bottom_row.addWidget(top_students_section)
        
        # Statistiques par tentative
        attempts_section = self.create_section("🔄 Répartition par Tentative")
        self.attempts_layout = QVBoxLayout()
        attempts_section.layout().addLayout(self.attempts_layout)
        bottom_row.addWidget(attempts_section)
        
        # Centres d'examen
        centers_section = self.create_section("🏢 Centres d'Examen")
        self.centers_layout = QVBoxLayout()
        centers_section.layout().addLayout(self.centers_layout)
        bottom_row.addWidget(centers_section)
        
        content_layout.addLayout(bottom_row)
        
        content_layout.addStretch()
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
    
    def create_section(self, title):
        """Créer une section avec titre"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #333; border: none;")
        layout.addWidget(title_label)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background: #e0e0e0; border: none; max-height: 1px;")
        layout.addWidget(separator)
        
        return section
    
    def create_stat_card(self, label, value, icon, color):
        """Créer une carte de statistique"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # Value
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")
        layout.addWidget(value_label)
        
        # Label
        text_label = QLabel(label.replace(icon + " ", ""))
        text_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        layout.addWidget(text_label)
        
        return card
    
    def darken_color(self, color):
        """Assombrir une couleur pour le gradient"""
        colors = {
            '#2196F3': '#1976D2',
            '#4CAF50': '#388E3C',
            '#FF9800': '#F57C00',
            '#F44336': '#D32F2F',
            '#9C27B0': '#7B1FA2',
            '#00BCD4': '#0097A7',
            '#FFC107': '#FFA000'
        }
        return colors.get(color, color)
    
    def on_period_changed(self):
        """Changement de période"""
        period_map = {
            'Tous les examens': 'all',
            "Aujourd'hui": 'day',
            'Cette semaine': 'week',
            'Ce mois': 'month',
            'Cette année': 'year'
        }
        self.current_period = period_map.get(self.period_combo.currentText(), 'all')
        self.load_stats()
    
    def get_date_range(self):
        """Obtenir la plage de dates selon la période"""
        today = date.today()
        
        if self.current_period == 'all':
            return date(2000, 1, 1), date(2099, 12, 31)
        elif self.current_period == 'day':
            return today, today
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
        elif self.current_period == 'year':
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
            return start, end
        
        return today, today
    
    def load_stats(self):
        """Charger les statistiques"""
        # Nettoyer les cartes existantes
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Récupérer tous les examens
        all_exams = ExamController.get_all_exams()
        
        # Filtrer selon la période
        start_date, end_date = self.get_date_range()
        exams = [
            e for e in all_exams
            if start_date <= e.scheduled_date <= end_date
        ]
        
        # Calculer les statistiques
        total = len(exams)
        passed = sum(1 for e in exams if e.result == ExamResult.PASSED)
        failed = sum(1 for e in exams if e.result == ExamResult.FAILED)
        pending = sum(1 for e in exams if e.result == ExamResult.PENDING)
        
        # Taux de réussite
        completed = passed + failed
        success_rate = (passed / completed * 100) if completed > 0 else 0
        
        # Créer les 5 cartes
        self.stats_layout.addWidget(
            self.create_stat_card("Total Examens", total, "📝", "#2196F3")
        )
        self.stats_layout.addWidget(
            self.create_stat_card("Réussis", passed, "✅", "#4CAF50")
        )
        self.stats_layout.addWidget(
            self.create_stat_card("Échoués", failed, "❌", "#F44336")
        )
        self.stats_layout.addWidget(
            self.create_stat_card("En Attente", pending, "⏳", "#FFC107")
        )
        self.stats_layout.addWidget(
            self.create_stat_card(
                "Taux de Réussite",
                f"{success_rate:.1f}%",
                "📈",
                "#9C27B0"
            )
        )
        
        # Charger les autres sections
        self.load_type_distribution(exams)
        self.load_result_distribution(exams)
        self.load_upcoming_exams()
        self.load_top_students(all_exams)
        self.load_attempts_distribution(exams)
        self.load_centers(exams)
    
    def load_type_distribution(self, exams):
        """Charger la distribution par type"""
        # Nettoyer
        while self.type_layout.count():
            item = self.type_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Compter par type
        type_counts = defaultdict(int)
        for exam in exams:
            type_counts[exam.exam_type.value] += 1
        
        if not type_counts:
            no_data = QLabel("Aucune donnée")
            no_data.setFont(QFont("Segoe UI", 10))
            no_data.setStyleSheet("color: #999; border: none;")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.type_layout.addWidget(no_data)
            return
        
        total = len(exams)
        
        # Couleurs par type
        type_colors = {
            'theorique': '#2196F3',
            'pratique': '#4CAF50'
        }
        
        type_labels = {
            'theorique': '📖 Théorique',
            'pratique': '🚗 Pratique'
        }
        
        for exam_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            percentage = (count / total * 100) if total > 0 else 0
            
            row = QWidget()
            row.setFixedHeight(35)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)
            
            # Label
            label = QLabel(type_labels.get(exam_type, exam_type))
            label.setFont(QFont("Segoe UI", 10))
            label.setStyleSheet("color: #333; border: none;")
            row_layout.addWidget(label, 1)
            
            # Barre de progression
            bar_container = QFrame()
            bar_container.setFixedHeight(20)
            bar_container.setStyleSheet("background: #f0f0f0; border-radius: 10px; border: none;")
            
            bar = QFrame(bar_container)
            bar.setFixedHeight(20)
            bar_width = int(200 * percentage / 100)
            bar.setFixedWidth(bar_width)
            bar.setStyleSheet(f"""
                background: {type_colors.get(exam_type, '#999')};
                border-radius: 10px;
                border: none;
            """)
            
            row_layout.addWidget(bar_container)
            
            # Valeur
            value = QLabel(f"{count} ({percentage:.1f}%)")
            value.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            value.setStyleSheet("color: #666; border: none;")
            value.setFixedWidth(100)
            value.setAlignment(Qt.AlignmentFlag.AlignRight)
            row_layout.addWidget(value)
            
            self.type_layout.addWidget(row)
        
        self.type_layout.addStretch()
    
    def load_result_distribution(self, exams):
        """Charger la distribution par résultat"""
        # Nettoyer
        while self.result_layout.count():
            item = self.result_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Compter par résultat
        result_counts = defaultdict(int)
        for exam in exams:
            result_counts[exam.result.value] += 1
        
        if not result_counts:
            no_data = QLabel("Aucune donnée")
            no_data.setFont(QFont("Segoe UI", 10))
            no_data.setStyleSheet("color: #999; border: none;")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.result_layout.addWidget(no_data)
            return
        
        total = len(exams)
        
        # Couleurs et labels par résultat
        result_colors = {
            'reussi': '#4CAF50',
            'echoue': '#F44336',
            'absent': '#FF9800',
            'en_attente': '#FFC107'
        }
        
        result_labels = {
            'reussi': '✅ Réussi',
            'echoue': '❌ Échoué',
            'absent': '👻 Absent',
            'en_attente': '⏳ En Attente'
        }
        
        for result, count in sorted(result_counts.items(), key=lambda x: -x[1]):
            percentage = (count / total * 100) if total > 0 else 0
            
            row = QWidget()
            row.setFixedHeight(35)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)
            
            # Label
            label = QLabel(result_labels.get(result, result))
            label.setFont(QFont("Segoe UI", 10))
            label.setStyleSheet("color: #333; border: none;")
            row_layout.addWidget(label, 1)
            
            # Barre
            bar_container = QFrame()
            bar_container.setFixedHeight(20)
            bar_container.setStyleSheet("background: #f0f0f0; border-radius: 10px; border: none;")
            
            bar = QFrame(bar_container)
            bar.setFixedHeight(20)
            bar_width = int(200 * percentage / 100)
            bar.setFixedWidth(bar_width)
            bar.setStyleSheet(f"""
                background: {result_colors.get(result, '#999')};
                border-radius: 10px;
                border: none;
            """)
            
            row_layout.addWidget(bar_container)
            
            # Valeur
            value = QLabel(f"{count} ({percentage:.1f}%)")
            value.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            value.setStyleSheet("color: #666; border: none;")
            value.setFixedWidth(100)
            value.setAlignment(Qt.AlignmentFlag.AlignRight)
            row_layout.addWidget(value)
            
            self.result_layout.addWidget(row)
        
        self.result_layout.addStretch()
    
    def load_upcoming_exams(self):
        """Charger les examens à venir"""
        # Nettoyer
        while self.upcoming_layout.count():
            item = self.upcoming_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Récupérer les examens des 7 prochains jours
        today = date.today()
        next_week = today + timedelta(days=7)
        
        all_exams = ExamController.get_all_exams()
        upcoming = [
            e for e in all_exams
            if today <= e.scheduled_date <= next_week and e.result == ExamResult.PENDING
        ]
        upcoming.sort(key=lambda x: x.scheduled_date)
        
        if not upcoming:
            no_data = QLabel("✅ Aucun examen prévu dans les 7 prochains jours")
            no_data.setFont(QFont("Segoe UI", 10))
            no_data.setStyleSheet("color: #4CAF50; border: none;")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.upcoming_layout.addWidget(no_data)
            return
        
        # Afficher les 5 premiers
        session = get_session()
        for exam in upcoming[:5]:
            student = session.query(Exam).filter_by(id=exam.id).first().student if exam.id else None
            
            row = QWidget()
            row.setFixedHeight(40)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)
            
            # Date
            date_label = QLabel(exam.scheduled_date.strftime('%d/%m/%Y'))
            date_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            date_label.setStyleSheet("color: #2196F3; border: none;")
            date_label.setFixedWidth(80)
            row_layout.addWidget(date_label)
            
            # Type
            type_icon = "📖" if exam.exam_type == ExamType.THEORETICAL else "🚗"
            type_label = QLabel(type_icon)
            type_label.setFont(QFont("Segoe UI", 14))
            type_label.setStyleSheet("border: none;")
            row_layout.addWidget(type_label)
            
            # Élève
            student_name = student.full_name if student else "Inconnu"
            if len(student_name) > 25:
                student_name = student_name[:22] + "..."
            
            name_label = QLabel(student_name)
            name_label.setFont(QFont("Segoe UI", 10))
            name_label.setStyleSheet("color: #333; border: none;")
            row_layout.addWidget(name_label, 1)
            
            # Centre
            if exam.exam_center:
                center_label = QLabel(exam.exam_center)
                center_label.setFont(QFont("Segoe UI", 9))
                center_label.setStyleSheet("color: #666; border: none; font-style: italic;")
                center_label.setFixedWidth(150)
                row_layout.addWidget(center_label)
            
            self.upcoming_layout.addWidget(row)
        
        if len(upcoming) > 5:
            more = QLabel(f"... et {len(upcoming) - 5} autre(s) examen(s)")
            more.setFont(QFont("Segoe UI", 9))
            more.setStyleSheet("color: #999; border: none; font-style: italic;")
            self.upcoming_layout.addWidget(more)
        
        self.upcoming_layout.addStretch()
    
    def load_top_students(self, exams):
        """Charger les top élèves avec le plus de réussites"""
        # Nettoyer
        while self.top_students_layout.count():
            item = self.top_students_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Compter les réussites par élève
        student_success = defaultdict(int)
        for exam in exams:
            if exam.result == ExamResult.PASSED:
                student_success[exam.student_id] += 1
        
        if not student_success:
            no_data = QLabel("Aucune donnée")
            no_data.setFont(QFont("Segoe UI", 10))
            no_data.setStyleSheet("color: #999; border: none;")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.top_students_layout.addWidget(no_data)
            return
        
        # Top 5
        top_5 = sorted(student_success.items(), key=lambda x: -x[1])[:5]
        
        session = get_session()
        for idx, (student_id, count) in enumerate(top_5, 1):
            from src.models import Student
            student = session.query(Student).filter_by(id=student_id).first()
            if not student:
                continue
            
            row = QWidget()
            row.setFixedHeight(35)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)
            
            # Rang
            rank = QLabel(f"#{idx}")
            rank.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            rank.setStyleSheet("color: #4CAF50; border: none;")
            rank.setFixedWidth(30)
            row_layout.addWidget(rank)
            
            # Nom
            student_name = student.full_name
            if len(student_name) > 25:
                student_name = student_name[:22] + "..."
            
            name = QLabel(student_name)
            name.setFont(QFont("Segoe UI", 11))
            name.setStyleSheet("color: #333; border: none;")
            name.setWordWrap(False)
            row_layout.addWidget(name, 1)
            
            # Réussites
            success = QLabel(f"{count} réussi(s)")
            success.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            success.setStyleSheet("color: #4CAF50; border: none;")
            success.setAlignment(Qt.AlignmentFlag.AlignRight)
            success.setFixedWidth(100)
            row_layout.addWidget(success)
            
            self.top_students_layout.addWidget(row)
        
        self.top_students_layout.addStretch()
    
    def load_attempts_distribution(self, exams):
        """Charger la distribution par numéro de tentative"""
        # Nettoyer
        while self.attempts_layout.count():
            item = self.attempts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Compter par tentative
        attempt_counts = defaultdict(int)
        for exam in exams:
            attempt_counts[exam.attempt_number] += 1
        
        if not attempt_counts:
            no_data = QLabel("Aucune donnée")
            no_data.setFont(QFont("Segoe UI", 10))
            no_data.setStyleSheet("color: #999; border: none;")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.attempts_layout.addWidget(no_data)
            return
        
        total = len(exams)
        
        for attempt_num in sorted(attempt_counts.keys())[:5]:  # Max 5
            count = attempt_counts[attempt_num]
            percentage = (count / total * 100) if total > 0 else 0
            
            row = QWidget()
            row.setFixedHeight(30)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)
            
            # Label
            label = QLabel(f"Tentative #{attempt_num}")
            label.setFont(QFont("Segoe UI", 10))
            label.setStyleSheet("color: #333; border: none;")
            row_layout.addWidget(label, 1)
            
            # Valeur
            value = QLabel(f"{count} ({percentage:.1f}%)")
            value.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            value.setStyleSheet("color: #2196F3; border: none;")
            value.setFixedWidth(90)
            value.setAlignment(Qt.AlignmentFlag.AlignRight)
            row_layout.addWidget(value)
            
            self.attempts_layout.addWidget(row)
        
        self.attempts_layout.addStretch()
    
    def load_centers(self, exams):
        """Charger les centres d'examen"""
        # Nettoyer
        while self.centers_layout.count():
            item = self.centers_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Compter par centre
        center_counts = defaultdict(int)
        for exam in exams:
            if exam.exam_center:
                center_counts[exam.exam_center] += 1
        
        if not center_counts:
            no_data = QLabel("Aucune donnée")
            no_data.setFont(QFont("Segoe UI", 10))
            no_data.setStyleSheet("color: #999; border: none;")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.centers_layout.addWidget(no_data)
            return
        
        # Top 5 centres
        for center, count in sorted(center_counts.items(), key=lambda x: -x[1])[:5]:
            row = QWidget()
            row.setFixedHeight(30)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)
            
            # Icon
            icon = QLabel("🏢")
            icon.setFont(QFont("Segoe UI", 12))
            icon.setStyleSheet("border: none;")
            row_layout.addWidget(icon)
            
            # Centre
            center_name = center
            if len(center_name) > 22:
                center_name = center_name[:19] + "..."
            
            name = QLabel(center_name)
            name.setFont(QFont("Segoe UI", 10))
            name.setStyleSheet("color: #333; border: none;")
            row_layout.addWidget(name, 1)
            
            # Count
            count_label = QLabel(f"{count}")
            count_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            count_label.setStyleSheet("color: #666; border: none;")
            count_label.setFixedWidth(40)
            count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            row_layout.addWidget(count_label)
            
            self.centers_layout.addWidget(row)
        
        self.centers_layout.addStretch()
