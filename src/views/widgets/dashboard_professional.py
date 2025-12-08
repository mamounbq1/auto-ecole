"""
Dashboard professionnel avec graphiques QtCharts
Version stable sans matplotlib
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QGridLayout, QPushButton, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPainter
from PySide6.QtCharts import (
    QChart, QChartView, QLineSeries, QPieSeries, 
    QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
)

from datetime import datetime, timedelta, date
from src.controllers import StudentController, PaymentController, SessionController
from src.models import StudentStatus, get_session


class ModernStatCard(QFrame):
    """Carte statistique moderne avec animation"""
    
    def __init__(self, title, value, subtitle="", icon="📊", color="#3498db", trend=None):
        super().__init__()
        self.setObjectName("modernStatCard")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header avec icône
        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 36px;")
        header.addWidget(icon_label)
        header.addStretch()
        
        # Indicateur de tendance
        if trend:
            trend_label = QLabel(trend)
            trend_color = "#27ae60" if "↗" in trend else "#e74c3c" if "↘" in trend else "#95a5a6"
            trend_label.setStyleSheet(f"color: {trend_color}; font-size: 14px; font-weight: bold;")
            header.addWidget(trend_label)
        
        layout.addLayout(header)
        
        # Valeur principale
        value_label = QLabel(str(value))
        value_label.setAlignment(Qt.AlignLeft)
        font = QFont()
        font.setPointSize(32)
        font.setBold(True)
        value_label.setFont(font)
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        # Titre
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #2c3e50; font-size: 14px; font-weight: 600;")
        layout.addWidget(title_label)
        
        # Sous-titre
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
            layout.addWidget(subtitle_label)
        
        layout.addStretch()
        
        # Style moderne
        self.setStyleSheet(f"""
            QFrame#modernStatCard {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 10px;
                padding: 0px;
            }}
            QFrame#modernStatCard:hover {{
                background-color: #f8f9fa;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
        """)
        self.setMinimumHeight(150)


class DashboardProfessionalWidget(QWidget):
    """Dashboard professionnel avec graphiques QtCharts"""
    
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.db_session = get_session()
        
        self.setup_ui()
        self.load_data()
        
        # Auto-refresh toutes les 30 secondes
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(30000)
        
    def setup_ui(self):
        """Configurer l'interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Zone scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #ecf0f1; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Titre
        title = QLabel("📊 Dashboard Professionnel")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Bouton refresh
        self.refresh_btn = QPushButton("🔄 Actualiser")
        self.refresh_btn.setMinimumHeight(40)
        self.refresh_btn.clicked.connect(self.load_data)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Sous-titre avec date
        self.date_label = QLabel()
        self.date_label.setStyleSheet("color: #7f8c8d; font-size: 11px; margin-bottom: 5px;")
        self.update_date()
        layout.addWidget(self.date_label)
        
        # Grille de cartes statistiques (KPI)
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(20)
        layout.addLayout(self.stats_grid)
        
        # Grille principale pour tous les graphiques (2x3)
        main_grid = QGridLayout()
        main_grid.setSpacing(10)
        
        # Ligne 1: CA Evolution + Répartition Paiements + Statut Élèves
        self.revenue_chart_view = self.create_revenue_chart()
        self.revenue_chart_view.setMinimumHeight(280)
        self.revenue_chart_view.setMaximumHeight(320)
        main_grid.addWidget(self.revenue_chart_view, 0, 0)
        
        self.payment_chart_view = self.create_payment_pie_chart()
        self.payment_chart_view.setMinimumHeight(280)
        self.payment_chart_view.setMaximumHeight(320)
        main_grid.addWidget(self.payment_chart_view, 0, 1)
        
        self.students_chart_view = self.create_students_chart()
        self.students_chart_view.setMinimumHeight(280)
        self.students_chart_view.setMaximumHeight(320)
        main_grid.addWidget(self.students_chart_view, 0, 2)
        
        # Ligne 2: Sessions Semaine + Activités Récentes + Alertes
        self.sessions_chart_view = self.create_sessions_chart()
        self.sessions_chart_view.setMinimumHeight(280)
        self.sessions_chart_view.setMaximumHeight(320)
        main_grid.addWidget(self.sessions_chart_view, 1, 0)
        
        self.recent_activities = self.create_recent_activities()
        self.recent_activities.setMaximumHeight(320)
        main_grid.addWidget(self.recent_activities, 1, 1)
        
        self.alerts_widget = self.create_alerts_widget()
        self.alerts_widget.setMaximumHeight(320)
        main_grid.addWidget(self.alerts_widget, 1, 2)
        
        layout.addLayout(main_grid)
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
    def update_date(self):
        """Mettre à jour la date"""
        now = datetime.now()
        date_str = now.strftime("%A %d %B %Y, %H:%M")
        # Traduire en français (basique)
        days = {"Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi", 
                "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi", "Sunday": "Dimanche"}
        months = {"January": "Janvier", "February": "Février", "March": "Mars", 
                  "April": "Avril", "May": "Mai", "June": "Juin", "July": "Juillet",
                  "August": "Août", "September": "Septembre", "October": "Octobre",
                  "November": "Novembre", "December": "Décembre"}
        for en, fr in days.items():
            date_str = date_str.replace(en, fr)
        for en, fr in months.items():
            date_str = date_str.replace(en, fr)
        self.date_label.setText(f"📅 {date_str}")
        
    def create_revenue_chart(self):
        """Créer le graphique d'évolution du CA"""
        chart = QChart()
        chart.setTitle("💰 Évolution du Chiffre d'Affaires (7 derniers jours)")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundBrush(QColor("#ffffff"))
        
        # Placeholder series
        series = QLineSeries()
        series.setName("CA journalier")
        
        # Données factices pour l'instant (seront chargées dans load_data)
        for i in range(7):
            series.append(i, 0)
        
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        return chart_view
        
    def create_payment_pie_chart(self):
        """Créer le graphique camembert des paiements"""
        chart = QChart()
        chart.setTitle("💳 Répartition par Méthode de Paiement")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundBrush(QColor("#ffffff"))
        
        # Placeholder series
        series = QPieSeries()
        series.append("Espèces", 1)
        series.append("Carte", 1)
        series.append("Chèque", 1)
        series.append("Virement", 1)
        
        chart.addSeries(series)
        chart.legend().setAlignment(Qt.AlignRight)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        return chart_view
        
    def create_students_chart(self):
        """Créer le graphique des statuts élèves"""
        chart = QChart()
        chart.setTitle("👥 Répartition des Élèves par Statut")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundBrush(QColor("#ffffff"))
        
        # Placeholder
        series = QBarSeries()
        bar_set = QBarSet("Élèves")
        bar_set.append([1, 1, 1, 1])
        series.append(bar_set)
        
        chart.addSeries(series)
        
        categories = ["Actifs", "En attente", "Suspendus", "Terminés"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart.legend().setVisible(False)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        return chart_view
        
    def create_sessions_chart(self):
        """Créer le graphique des sessions"""
        chart = QChart()
        chart.setTitle("📅 Sessions de la Semaine")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundBrush(QColor("#ffffff"))
        
        # Placeholder
        series = QBarSeries()
        bar_set = QBarSet("Sessions")
        bar_set.append([1, 2, 1, 3, 2, 1, 0])
        series.append(bar_set)
        
        chart.addSeries(series)
        
        categories = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart.legend().setVisible(False)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        return chart_view
        
    def create_recent_activities(self):
        """Créer le widget des activités récentes"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        
        # Titre
        title = QLabel("📋 Activités Récentes")
        title.setStyleSheet("color: #2c3e50; font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Table des activités
        self.activities_table = QTableWidget()
        self.activities_table.setColumnCount(3)
        self.activities_table.setHorizontalHeaderLabels(["Date", "Type", "Description"])
        self.activities_table.horizontalHeader().setStretchLastSection(True)
        self.activities_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.activities_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.activities_table.setAlternatingRowColors(True)
        self.activities_table.setMaximumHeight(250)
        
        layout.addWidget(self.activities_table)
        
        return widget
        
    def create_alerts_widget(self):
        """Créer le widget des alertes"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        
        # Titre
        title = QLabel("⚠️ Alertes & Notifications")
        title.setStyleSheet("color: #2c3e50; font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Liste des alertes
        self.alerts_layout = QVBoxLayout()
        layout.addLayout(self.alerts_layout)
        
        layout.addStretch()
        
        return widget
        
    def add_alert(self, icon, message, color="#e74c3c"):
        """Ajouter une alerte"""
        alert = QLabel(f"{icon} {message}")
        alert.setStyleSheet(f"""
            QLabel {{
                color: {color};
                background-color: {color}20;
                padding: 10px;
                border-radius: 5px;
                border-left: 3px solid {color};
                margin-bottom: 5px;
            }}
        """)
        alert.setWordWrap(True)
        self.alerts_layout.addWidget(alert)
        
    def load_data(self):
        """Charger toutes les données du dashboard"""
        try:
            self.update_date()
            self.load_kpi_cards()
            self.load_revenue_chart()
            self.load_payment_pie_chart()
            self.load_students_chart()
            self.load_sessions_chart()
            self.load_recent_activities()
            self.load_alerts()
            
            print("✅ Dashboard professionnel chargé avec succès")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement du dashboard: {e}")
            import traceback
            traceback.print_exc()
            
    def load_kpi_cards(self):
        """Charger les cartes KPI"""
        # Nettoyer la grille
        for i in reversed(range(self.stats_grid.count())): 
            widget = self.stats_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Récupérer les données
        students = StudentController.get_all_students()
        active_students = sum(1 for s in students if s.status == StudentStatus.ACTIVE)
        
        # CA mensuel
        today = datetime.now()
        start_of_month = today.replace(day=1).date()
        all_payments = PaymentController.get_all_payments()
        payments_this_month = [p for p in all_payments if p.payment_date and 
                              p.payment_date >= start_of_month]
        monthly_revenue = sum(p.amount for p in payments_this_month if p.is_validated)
        
        # Calculer le CA du mois précédent pour la tendance
        start_last_month = (start_of_month - timedelta(days=1)).replace(day=1)
        payments_last_month = [p for p in all_payments if p.payment_date and 
                              start_last_month <= p.payment_date < start_of_month]
        last_month_revenue = sum(p.amount for p in payments_last_month if p.is_validated)
        
        revenue_trend = ""
        if last_month_revenue > 0:
            trend_percent = ((monthly_revenue - last_month_revenue) / last_month_revenue) * 100
            if trend_percent > 0:
                revenue_trend = f"↗ +{trend_percent:.1f}%"
            elif trend_percent < 0:
                revenue_trend = f"↘ {trend_percent:.1f}%"
        
        # Sessions aujourd'hui
        sessions_today = SessionController.get_today_sessions()
        
        # Élèves avec dette
        students_with_debt = sum(1 for s in students if s.balance < 0)
        total_debt = sum(abs(s.balance) for s in students if s.balance < 0)
        
        # Créer les cartes
        cards = [
            ModernStatCard(
                "Élèves Actifs", 
                active_students,
                f"sur {len(students)} total",
                "👥", 
                "#3498db"
            ),
            ModernStatCard(
                "CA Mensuel", 
                f"{monthly_revenue:,.0f} DH",
                f"vs mois dernier",
                "💰", 
                "#27ae60",
                revenue_trend
            ),
            ModernStatCard(
                "Sessions Aujourd'hui", 
                len(sessions_today),
                "planifiées",
                "📅", 
                "#f39c12"
            ),
            ModernStatCard(
                "Impayés", 
                students_with_debt,
                f"{total_debt:,.0f} DH de dette",
                "⚠️", 
                "#e74c3c"
            ),
        ]
        
        # Ajouter les cartes à la grille
        for i, card in enumerate(cards):
            self.stats_grid.addWidget(card, 0, i)
            
    def load_revenue_chart(self):
        """Charger le graphique d'évolution du CA"""
        chart = self.revenue_chart_view.chart()
        chart.removeAllSeries()
        
        series = QLineSeries()
        series.setName("CA journalier (DH)")
        
        # Récupérer les paiements des 7 derniers jours
        all_payments = PaymentController.get_all_payments()
        today = datetime.now().date()
        
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            daily_revenue = sum(p.amount for p in all_payments 
                              if p.payment_date == day and p.is_validated)
            series.append(6-i, daily_revenue)
        
        chart.addSeries(series)
        chart.createDefaultAxes()
        
        # Personnaliser les axes
        for axis in chart.axes():
            if isinstance(axis, QValueAxis):
                axis.setTitleText("Montant (DH)")
                
    def load_payment_pie_chart(self):
        """Charger le graphique camembert des paiements"""
        chart = self.payment_chart_view.chart()
        chart.removeAllSeries()
        
        series = QPieSeries()
        
        # Compter par méthode
        all_payments = PaymentController.get_all_payments()
        methods = {}
        for p in all_payments:
            if p.payment_method:
                method = p.payment_method.value
                methods[method] = methods.get(method, 0) + p.amount
        
        # Ajouter au camembert
        colors = {
            "especes": "#27ae60",
            "carte_bancaire": "#3498db",
            "cheque": "#f39c12",
            "virement": "#9b59b6"
        }
        
        for method, amount in methods.items():
            slice = series.append(method.replace('_', ' ').title(), amount)
            if method in colors:
                slice.setBrush(QColor(colors[method]))
            slice.setLabelVisible(True)
        
        chart.addSeries(series)
        
    def load_students_chart(self):
        """Charger le graphique des élèves"""
        chart = self.students_chart_view.chart()
        chart.removeAllSeries()
        
        students = StudentController.get_all_students()
        
        # Compter par statut
        statuses = {
            "active": 0,
            "pending": 0,
            "suspended": 0,
            "completed": 0
        }
        
        for s in students:
            if s.status:
                status_val = s.status.value if hasattr(s.status, 'value') else str(s.status)
                if status_val in statuses:
                    statuses[status_val] += 1
        
        series = QBarSeries()
        bar_set = QBarSet("Élèves")
        bar_set.append([statuses["active"], statuses["pending"], 
                       statuses["suspended"], statuses["completed"]])
        
        # Couleurs
        bar_set.setColor(QColor("#3498db"))
        series.append(bar_set)
        
        chart.addSeries(series)
        
        categories = ["Actifs", "En attente", "Suspendus", "Terminés"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, max(statuses.values()) + 1)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
    def load_sessions_chart(self):
        """Charger le graphique des sessions de la semaine"""
        chart = self.sessions_chart_view.chart()
        chart.removeAllSeries()
        
        # Récupérer toutes les sessions
        from src.controllers.session_controller import SessionController
        all_sessions = SessionController.get_all_sessions()
        
        # Compter par jour de la semaine
        today = datetime.now().date()
        start_week = today - timedelta(days=today.weekday())
        
        sessions_by_day = [0] * 7
        for session in all_sessions:
            if session.session_date >= start_week:
                day_index = (session.session_date - start_week).days
                if 0 <= day_index < 7:
                    sessions_by_day[day_index] += 1
        
        series = QBarSeries()
        bar_set = QBarSet("Sessions")
        bar_set.append(sessions_by_day)
        bar_set.setColor(QColor("#f39c12"))
        series.append(bar_set)
        
        chart.addSeries(series)
        
        categories = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, max(sessions_by_day) + 1 if sessions_by_day else 5)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
    def load_recent_activities(self):
        """Charger les activités récentes"""
        self.activities_table.setRowCount(0)
        
        # Récupérer les derniers paiements
        all_payments = PaymentController.get_all_payments()
        recent_payments = sorted(all_payments, key=lambda p: p.payment_date, reverse=True)[:5]
        
        for payment in recent_payments:
            row = self.activities_table.rowCount()
            self.activities_table.insertRow(row)
            
            # Date
            date_str = payment.payment_date.strftime("%d/%m/%Y")
            self.activities_table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # Type
            self.activities_table.setItem(row, 1, QTableWidgetItem("💰 Paiement"))
            
            # Description
            desc = f"{payment.amount:.0f} DH - {payment.student.full_name if payment.student else 'N/A'}"
            self.activities_table.setItem(row, 2, QTableWidgetItem(desc))
            
    def load_alerts(self):
        """Charger les alertes"""
        # Nettoyer
        while self.alerts_layout.count():
            item = self.alerts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Récupérer les élèves avec dette
        students = StudentController.get_all_students()
        students_with_debt = [s for s in students if s.balance < 0]
        
        if students_with_debt:
            self.add_alert(
                "⚠️", 
                f"{len(students_with_debt)} élève(s) avec impayés",
                "#e74c3c"
            )
        
        # Sessions aujourd'hui
        sessions_today = SessionController.get_today_sessions()
        if sessions_today:
            self.add_alert(
                "📅", 
                f"{len(sessions_today)} session(s) planifiée(s) aujourd'hui",
                "#f39c12"
            )
        else:
            self.add_alert(
                "ℹ️", 
                "Aucune session planifiée aujourd'hui",
                "#3498db"
            )
        
        # Message positif
        active_students = sum(1 for s in students if s.status == StudentStatus.ACTIVE)
        if active_students > 0:
            self.add_alert(
                "✅", 
                f"{active_students} élève(s) actif(s) en formation",
                "#27ae60"
            )
            
    def closeEvent(self, event):
        """Nettoyer lors de la fermeture"""
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        try:
            if hasattr(self, 'db_session') and self.db_session:
                self.db_session.close()
        except:
            pass
        event.accept()

