"""
Onglet RÉSUMÉ pour la vue détaillée élève
Vue d'ensemble avec infos critiques, graphiques et timeline
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QPainter, QPen
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QLineSeries, QValueAxis
from datetime import datetime, timedelta

from src.controllers import PaymentController, SessionController, ExamController
from src.models import StudentStatus


class StatCard(QFrame):
    """Carte statistique compacte"""
    
    def __init__(self, icon, title, value, color="#3498db", subtitle="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 5px solid {color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Icône et valeur
        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 28px; color: {color};")
        
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        
        header.addWidget(icon_label)
        header.addStretch()
        header.addWidget(value_label)
        layout.addLayout(header)
        
        # Titre
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #2c3e50;")
        layout.addWidget(title_label)
        
        # Sous-titre
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
            layout.addWidget(subtitle_label)


class TimelineItem(QWidget):
    """Item de timeline d'activité"""
    
    def __init__(self, icon, title, subtitle, date_str, color="#3498db", parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Icône
        icon_frame = QFrame()
        icon_frame.setFixedSize(40, 40)
        icon_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 20px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("color: white; font-size: 18px;")
        icon_layout.addWidget(icon_label)
        
        layout.addWidget(icon_frame)
        
        # Contenu
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #2c3e50;")
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(subtitle_label)
        
        layout.addLayout(content_layout, stretch=1)
        
        # Date
        date_label = QLabel(date_str)
        date_label.setStyleSheet("font-size: 11px; color: #95a5a6; font-weight: 500;")
        date_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(date_label)
        
        # Style du widget
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 8px;
                margin: 2px 0;
            }
            QWidget:hover {
                background-color: #ecf0f1;
            }
        """)


class StudentSummaryTab(QWidget):
    """Onglet Résumé - Vue d'ensemble de l'élève"""
    
    def __init__(self, student, parent=None):
        super().__init__(parent)
        self.student = student
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Interface utilisateur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Section 1: Cartes statistiques (4 colonnes)
        self.create_stats_section(layout)
        
        # Section 2: Graphiques et Timeline (2 colonnes)
        middle_section = QHBoxLayout()
        middle_section.setSpacing(20)
        
        # Colonne gauche: Graphiques
        self.create_charts_section(middle_section)
        
        # Colonne droite: Timeline récente
        self.create_timeline_section(middle_section)
        
        layout.addLayout(middle_section)
    
    def create_stats_section(self, layout):
        """Section cartes statistiques"""
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)
        
        # Carte 1: Statut
        status_icons = {
            StudentStatus.ACTIVE: ("🟢", "#27ae60", "Actif"),
            StudentStatus.PENDING: ("🟡", "#f39c12", "En attente"),
            StudentStatus.SUSPENDED: ("🔴", "#e74c3c", "Suspendu"),
            StudentStatus.GRADUATED: ("🎓", "#3498db", "Diplômé"),
            StudentStatus.ABANDONED: ("⚫", "#95a5a6", "Abandonné")
        }
        icon, color, text = status_icons.get(self.student.status, ("❓", "#95a5a6", "Inconnu"))
        self.status_card = StatCard(
            icon, "Statut", text, color,
            f"Inscrit le {self.student.registration_date.strftime('%d/%m/%Y')}"
        )
        stats_layout.addWidget(self.status_card, 0, 0)
        
        # Carte 2: Solde
        balance_val = float(self.student.balance) if self.student.balance else 0.0
        balance_color = "#e74c3c" if balance_val < 0 else "#27ae60"
        balance_icon = "💰" if balance_val >= 0 else "⚠️"
        balance_text = f"{balance_val:+,.0f} DH"
        balance_subtitle = "Crédit" if balance_val > 0 else "Dette" if balance_val < 0 else "À jour"
        self.balance_card = StatCard(
            balance_icon, "Solde", balance_text, balance_color, balance_subtitle
        )
        stats_layout.addWidget(self.balance_card, 0, 1)
        
        # Carte 3: Progression
        completion = (self.student.hours_completed / self.student.hours_planned * 100) if self.student.hours_planned > 0 else 0
        progress_color = "#27ae60" if completion >= 80 else "#f39c12" if completion >= 50 else "#e74c3c"
        self.progress_card = StatCard(
            "📊", "Progression", f"{completion:.0f}%", progress_color,
            f"{self.student.hours_completed}/{self.student.hours_planned} heures"
        )
        stats_layout.addWidget(self.progress_card, 0, 2)
        
        # Carte 4: Examens
        exam_passed = self.student.theoretical_exam_passed and self.student.practical_exam_passed
        exam_icon = "✅" if exam_passed else "📝"
        exam_color = "#27ae60" if exam_passed else "#3498db"
        exam_text = "Réussi" if exam_passed else "En cours"
        exam_subtitle = f"Théorie: {self.student.theoretical_exam_attempts} | Pratique: {self.student.practical_exam_attempts}"
        self.exam_card = StatCard(
            exam_icon, "Examens", exam_text, exam_color, exam_subtitle
        )
        stats_layout.addWidget(self.exam_card, 0, 3)
        
        layout.addLayout(stats_layout)
    
    def create_charts_section(self, layout):
        """Section graphiques"""
        charts_widget = QWidget()
        charts_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        charts_layout = QVBoxLayout(charts_widget)
        charts_layout.setSpacing(15)
        
        # Titre
        title = QLabel("📈 Vue Graphique")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        charts_layout.addWidget(title)
        
        # Graphique circulaire: Progression des heures
        pie_chart = self.create_hours_pie_chart()
        charts_layout.addWidget(pie_chart)
        
        layout.addWidget(charts_widget, stretch=1)
    
    def create_hours_pie_chart(self):
        """Graphique circulaire progression heures"""
        series = QPieSeries()
        
        completed = self.student.hours_completed or 0
        planned = self.student.hours_planned or 20
        remaining = max(0, planned - completed)
        
        # Heures complétées
        slice_completed = series.append("Heures Complétées", completed)
        slice_completed.setBrush(QColor("#27ae60"))
        slice_completed.setLabelVisible(True)
        slice_completed.setLabelColor(QColor("#2c3e50"))
        
        # Heures restantes
        slice_remaining = series.append("Heures Restantes", remaining)
        slice_remaining.setBrush(QColor("#ecf0f1"))
        slice_remaining.setLabelVisible(True)
        slice_remaining.setLabelColor(QColor("#7f8c8d"))
        
        # Configuration du chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Progression des Heures de Conduite")
        chart.setTitleFont(QFont("Segoe UI", 12, QFont.Bold))
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.setBackgroundBrush(QColor("white"))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Chart view
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        return chart_view
    
    def create_timeline_section(self, layout):
        """Section timeline des activités récentes"""
        timeline_widget = QWidget()
        timeline_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        timeline_layout = QVBoxLayout(timeline_widget)
        timeline_layout.setSpacing(10)
        
        # Titre
        title = QLabel("📅 Activité Récente")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        timeline_layout.addWidget(title)
        
        # Scroll area pour la timeline
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; }")
        
        timeline_content = QWidget()
        self.timeline_layout = QVBoxLayout(timeline_content)
        self.timeline_layout.setSpacing(8)
        self.timeline_layout.setContentsMargins(0, 0, 0, 0)
        
        # Placeholder - sera rempli par load_data()
        placeholder = QLabel("Chargement de l'activité...")
        placeholder.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 20px;")
        placeholder.setAlignment(Qt.AlignCenter)
        self.timeline_layout.addWidget(placeholder)
        
        self.timeline_layout.addStretch()
        
        scroll.setWidget(timeline_content)
        timeline_layout.addWidget(scroll)
        
        layout.addWidget(timeline_widget, stretch=1)
    
    def load_data(self):
        """Charger les données de timeline"""
        try:
            # Effacer le placeholder
            while self.timeline_layout.count() > 0:
                item = self.timeline_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Collecter toutes les activités récentes
            activities = []
            
            # Paiements récents (3 derniers)
            try:
                payments = PaymentController.get_payments_by_student(self.student.id)
                for payment in payments[:3]:
                    if not payment.is_cancelled:
                        activities.append({
                            'date': payment.payment_date,
                            'icon': '💰',
                            'title': f'Paiement de {float(payment.amount):,.0f} DH',
                            'subtitle': f'{payment.payment_method.value if payment.payment_method else "N/A"}',
                            'color': '#27ae60'
                        })
            except Exception as e:
                print(f"Error loading payments for timeline: {e}")
            
            # Séances récentes (3 dernières)
            try:
                sessions = SessionController.get_sessions_by_student(self.student.id)
                for session in sessions[:3]:
                    date_val = session.start_datetime if session.start_datetime else datetime.now()
                    instructor_name = getattr(session, 'instructor_name', 'N/A')
                    activities.append({
                        'date': date_val,
                        'icon': '🚗',
                        'title': 'Séance de conduite',
                        'subtitle': f'Avec {instructor_name}',
                        'color': '#3498db'
                    })
            except Exception as e:
                print(f"Error loading sessions for timeline: {e}")
            
            # Examens récents
            try:
                exams = ExamController.get_exams_by_student(self.student.id)
                for exam in exams[:2]:
                    exam_date = getattr(exam, 'exam_date', datetime.now())
                    exam_type = getattr(exam, 'exam_type', 'N/A')
                    result = "Réussi ✅" if getattr(exam, 'passed', False) else "Échoué ❌"
                    activities.append({
                        'date': exam_date,
                        'icon': '📝',
                        'title': f'Examen {exam_type}',
                        'subtitle': result,
                        'color': '#f39c12'
                    })
            except Exception as e:
                print(f"Error loading exams for timeline: {e}")
            
            # Trier par date (plus récent d'abord)
            def get_sortable_date(activity):
                date_val = activity['date']
                if date_val is None:
                    return datetime.min
                if hasattr(date_val, 'hour'):
                    return date_val
                else:
                    from datetime import date as date_type
                    if isinstance(date_val, date_type):
                        return datetime.combine(date_val, datetime.min.time())
                return datetime.min
            
            activities.sort(key=get_sortable_date, reverse=True)
            
            # Limiter à 5 dernières activités
            activities = activities[:5]
            
            # Afficher dans la timeline
            if activities:
                for activity in activities:
                    date_str = activity['date'].strftime('%d/%m/%Y') if activity['date'] else "N/A"
                    item = TimelineItem(
                        activity['icon'],
                        activity['title'],
                        activity['subtitle'],
                        date_str,
                        activity['color']
                    )
                    self.timeline_layout.addWidget(item)
            else:
                # Aucune activité
                no_activity = QLabel("Aucune activité récente")
                no_activity.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 20px;")
                no_activity.setAlignment(Qt.AlignCenter)
                self.timeline_layout.addWidget(no_activity)
            
            self.timeline_layout.addStretch()
            
        except Exception as e:
            print(f"Error loading timeline data: {e}")
            error_label = QLabel(f"Erreur de chargement: {str(e)}")
            error_label.setStyleSheet("color: #e74c3c; padding: 20px;")
            self.timeline_layout.addWidget(error_label)
