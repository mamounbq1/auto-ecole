"""
Planning Statistics Widget - Dashboard statistiques planning SIMPLIFIÉ
Nouvelle version propre créée de zéro
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGroupBox, QGridLayout, QProgressBar, QComboBox, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datetime import datetime, timedelta, date

from src.controllers.session_controller import SessionController
from src.controllers.instructor_controller import InstructorController
from src.controllers.vehicle_controller import VehicleController
from src.models import SessionStatus, SessionType


class PlanningStatsWidget(QWidget):
    """Widget de statistiques du planning - VERSION SIMPLIFIÉE"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_period = "week"
        self.setup_ui()
        # Charger APRÈS que l'UI soit complète
        self.load_all_stats()
    
    def setup_ui(self):
        """Configurer l'interface"""
        # Layout principal du widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Créer un scroll area pour tout le contenu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #3498db;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #2980b9;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Widget de contenu qui sera scrollable
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Header
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 8px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("📊 Statistiques Planning")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Sélecteur période
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Cette semaine", "Ce mois", "Cette année"])
        self.period_combo.setCurrentIndex(0)
        self.period_combo.currentIndexChanged.connect(self.on_period_changed)
        self.period_combo.setFixedHeight(35)
        self.period_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: #2c3e50;
                padding: 5px 15px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        header_layout.addWidget(self.period_combo)
        
        content_layout.addWidget(header)
        
        # Grille de 6 cartes statistiques SIMPLES
        cards_container = QFrame()
        cards_container.setStyleSheet("QFrame { background-color: transparent; }")
        cards_layout = QGridLayout(cards_container)
        cards_layout.setSpacing(15)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        
        # 6 cartes vides pour l'instant (seront remplies dans load_all_stats)
        self.card_total = self.create_empty_card("📅 SESSIONS TOTALES", "#3498db")
        self.card_completed = self.create_empty_card("✅ TERMINÉES", "#27ae60")
        self.card_cancelled = self.create_empty_card("❌ ANNULÉES", "#e74c3c")
        self.card_planned = self.create_empty_card("⏰ HEURES PLANIFIÉES", "#9b59b6")
        self.card_realized = self.create_empty_card("✅ HEURES RÉALISÉES", "#27ae60")
        self.card_utilization = self.create_empty_card("📊 TAUX UTILISATION", "#f39c12")
        
        cards_layout.addWidget(self.card_total, 0, 0)
        cards_layout.addWidget(self.card_completed, 0, 1)
        cards_layout.addWidget(self.card_cancelled, 0, 2)
        cards_layout.addWidget(self.card_planned, 1, 0)
        cards_layout.addWidget(self.card_realized, 1, 1)
        cards_layout.addWidget(self.card_utilization, 1, 2)
        
        content_layout.addWidget(cards_container)
        
        # Détails (2 colonnes)
        details = QWidget()
        details_layout = QHBoxLayout(details)
        details_layout.setSpacing(15)
        details_layout.setContentsMargins(0, 0, 0, 0)
        
        # Colonne gauche
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Top moniteurs
        self.instructors_group = QGroupBox("👨‍🏫 Top Moniteurs")
        self.instructors_group.setMinimumHeight(180)
        self.instructors_group.setMaximumHeight(250)
        self.instructors_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        self.instructors_layout = QVBoxLayout(self.instructors_group)
        left_layout.addWidget(self.instructors_group)
        
        # Répartition types
        self.types_group = QGroupBox("📚 Répartition par Type")
        self.types_group.setMinimumHeight(200)
        self.types_group.setMaximumHeight(280)
        self.types_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        self.types_layout = QVBoxLayout(self.types_group)
        left_layout.addWidget(self.types_group)
        
        left_layout.addStretch()
        details_layout.addWidget(left)
        
        # Colonne droite
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setSpacing(15)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Top véhicules
        self.vehicles_group = QGroupBox("🚗 Top Véhicules")
        self.vehicles_group.setMinimumHeight(180)
        self.vehicles_group.setMaximumHeight(250)
        self.vehicles_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        self.vehicles_layout = QVBoxLayout(self.vehicles_group)
        right_layout.addWidget(self.vehicles_group)
        
        # Performance
        self.performance_group = QGroupBox("⚡ Performance")
        self.performance_group.setMinimumHeight(200)
        self.performance_group.setMaximumHeight(280)
        self.performance_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        self.performance_layout = QVBoxLayout(self.performance_group)
        right_layout.addWidget(self.performance_group)
        
        right_layout.addStretch()
        details_layout.addWidget(right)
        
        content_layout.addWidget(details)
        
        # Ajouter le widget de contenu au scroll area
        scroll.setWidget(content_widget)
        
        # Ajouter le scroll area au layout principal
        main_layout.addWidget(scroll)
    
    def create_empty_card(self, title_text, border_color):
        """Créer une carte vide (sera remplie après)"""
        card = QFrame()
        card.setFixedHeight(100)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid #ecf0f1;
                border-left: 6px solid {border_color};
                border-radius: 8px;
            }}
            QFrame:hover {{
                border: 2px solid {border_color};
                border-left: 6px solid {border_color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        
        # Titre
        title = QLabel(title_text)
        title_font = QFont()
        title_font.setPointSize(9)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(title)
        
        # Valeur (grande et colorée)
        value = QLabel("0")
        value.setObjectName("value_label")  # IMPORTANT pour retrouver
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setBold(True)
        value.setFont(value_font)
        value.setStyleSheet(f"color: {border_color};")
        layout.addWidget(value)
        
        layout.addStretch()
        
        return card
    
    def update_card_value(self, card, new_value):
        """Mettre à jour la valeur d'une carte"""
        value_label = card.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(str(new_value))
            # FORCER le repaint
            value_label.update()
            value_label.repaint()
    
    def load_all_stats(self):
        """Charger TOUTES les statistiques"""
        start_date, end_date = self.get_date_range()
        sessions = SessionController.get_sessions_by_date_range(start_date, end_date)
        sessions = sessions if sessions else []
        
        # Calculs de base
        total = len(sessions)
        completed = len([s for s in sessions if s.status == SessionStatus.COMPLETED])
        cancelled = len([s for s in sessions if s.status == SessionStatus.CANCELLED])
        
        completed_pct = int((completed / total * 100)) if total > 0 else 0
        cancelled_pct = int((cancelled / total * 100)) if total > 0 else 0
        
        planned_hours = sum([
            (s.end_datetime - s.start_datetime).total_seconds() / 3600
            for s in sessions
        ]) if sessions else 0
        
        realized_hours = sum([
            (s.end_datetime - s.start_datetime).total_seconds() / 3600
            for s in sessions if s.status == SessionStatus.COMPLETED
        ]) if sessions else 0
        
        utilization = int((realized_hours / planned_hours * 100)) if planned_hours > 0 else 0
        
        # Mettre à jour les 6 cartes
        self.update_card_value(self.card_total, str(total))
        self.update_card_value(self.card_completed, f"{completed} ({completed_pct}%)")
        self.update_card_value(self.card_cancelled, f"{cancelled} ({cancelled_pct}%)")
        self.update_card_value(self.card_planned, f"{planned_hours:.1f}h")
        self.update_card_value(self.card_realized, f"{realized_hours:.1f}h")
        self.update_card_value(self.card_utilization, f"{utilization}%")
        
        # Charger sections du bas
        self.load_instructors(sessions)
        self.load_types(sessions)
        self.load_vehicles(sessions)
        self.load_performance(sessions, start_date, end_date)
    
    def load_instructors(self, sessions):
        """Charger top moniteurs"""
        # Nettoyer
        while self.instructors_layout.count():
            child = self.instructors_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Calculer heures par moniteur
        instructor_hours = {}
        for s in sessions:
            if s.instructor_id:
                hours = (s.end_datetime - s.start_datetime).total_seconds() / 3600
                instructor_hours[s.instructor_id] = instructor_hours.get(s.instructor_id, 0) + hours
        
        # Top 5
        sorted_inst = sorted(instructor_hours.items(), key=lambda x: x[1], reverse=True)[:5]
        all_inst = {i.id: i for i in InstructorController.get_all_instructors()}
        
        for i, (inst_id, hours) in enumerate(sorted_inst):
            inst = all_inst.get(inst_id)
            if not inst:
                continue
            
            # Créer un conteneur pour éviter le chevauchement
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(0, 2, 0, 2)
            row.setSpacing(8)
            
            rank = QLabel(f"{i+1}.")
            rank.setFixedWidth(20)
            rank.setStyleSheet("color: #f39c12; font-weight: bold;")
            row.addWidget(rank)
            
            name = QLabel(inst.full_name[:22])
            name.setWordWrap(False)
            name.setStyleSheet("color: #2c3e50; font-size: 11px;")
            row.addWidget(name, stretch=1)
            
            hrs = QLabel(f"{hours:.1f}h")
            hrs.setFixedWidth(50)
            hrs.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            hrs.setStyleSheet("color: #3498db; font-weight: bold; font-size: 11px;")
            row.addWidget(hrs)
            
            self.instructors_layout.addWidget(row_widget)
        
        if not sorted_inst:
            no_data = QLabel("Aucune donnée")
            no_data.setStyleSheet("color: #95a5a6; font-style: italic;")
            self.instructors_layout.addWidget(no_data)
    
    def load_types(self, sessions):
        """Charger répartition par type"""
        # Nettoyer
        while self.types_layout.count():
            child = self.types_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        total = len(sessions)
        type_counts = {}
        for s in sessions:
            type_counts[s.session_type] = type_counts.get(s.session_type, 0) + 1
        
        type_labels = {
            SessionType.PRACTICAL_DRIVING: "Pratique",
            SessionType.THEORETICAL_CLASS: "Théorie",
            SessionType.CODE_EXAM: "Examen Code",
            SessionType.PRACTICAL_EXAM: "Examen Pratique"
        }
        
        for stype in [SessionType.PRACTICAL_DRIVING, SessionType.THEORETICAL_CLASS, SessionType.CODE_EXAM]:
            count = type_counts.get(stype, 0)
            pct = int((count / total * 100)) if total > 0 else 0
            
            label = QLabel(f"{type_labels[stype]}: {count} ({pct}%)")
            label.setStyleSheet("color: #2c3e50; font-size: 12px;")
            self.types_layout.addWidget(label)
            
            bar = QProgressBar()
            bar.setValue(pct)
            bar.setFixedHeight(20)
            bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    background-color: #f5f5f5;
                    text-align: center;
                    color: #2c3e50;
                    font-weight: bold;
                    font-size: 10px;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #3498db, stop:1 #2980b9);
                    border-radius: 3px;
                }
            """)
            self.types_layout.addWidget(bar)
        
        if total == 0:
            no_data = QLabel("Aucune session")
            no_data.setStyleSheet("color: #95a5a6; font-style: italic;")
            self.types_layout.addWidget(no_data)
    
    def load_vehicles(self, sessions):
        """Charger top véhicules"""
        # Nettoyer
        while self.vehicles_layout.count():
            child = self.vehicles_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Calculer heures par véhicule
        vehicle_hours = {}
        for s in sessions:
            if s.vehicle_id:
                hours = (s.end_datetime - s.start_datetime).total_seconds() / 3600
                vehicle_hours[s.vehicle_id] = vehicle_hours.get(s.vehicle_id, 0) + hours
        
        # Top 5
        sorted_veh = sorted(vehicle_hours.items(), key=lambda x: x[1], reverse=True)[:5]
        all_veh = {v.id: v for v in VehicleController.get_all_vehicles()}
        
        for i, (veh_id, hours) in enumerate(sorted_veh):
            veh = all_veh.get(veh_id)
            if not veh:
                continue
            
            # Créer un conteneur pour éviter le chevauchement
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(0, 2, 0, 2)
            row.setSpacing(8)
            
            rank = QLabel(f"{i+1}.")
            rank.setFixedWidth(20)
            rank.setStyleSheet("color: #f39c12; font-weight: bold;")
            row.addWidget(rank)
            
            # Limiter longueur du nom
            vehicle_name = f"{veh.make} {veh.model}"
            if len(vehicle_name) > 18:
                vehicle_name = vehicle_name[:18] + "..."
            
            name = QLabel(vehicle_name)
            name.setWordWrap(False)
            name.setStyleSheet("color: #2c3e50; font-size: 11px;")
            row.addWidget(name, stretch=1)
            
            hrs = QLabel(f"{hours:.0f}h")
            hrs.setFixedWidth(50)
            hrs.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            hrs.setStyleSheet("color: #3498db; font-weight: bold; font-size: 11px;")
            row.addWidget(hrs)
            
            self.vehicles_layout.addWidget(row_widget)
        
        if not sorted_veh:
            no_data = QLabel("Aucune donnée")
            no_data.setStyleSheet("color: #95a5a6; font-style: italic;")
            self.vehicles_layout.addWidget(no_data)
    
    def load_performance(self, sessions, start_date, end_date):
        """Charger métriques de performance"""
        # Nettoyer
        while self.performance_layout.count():
            child = self.performance_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        total = len(sessions)
        completed = len([s for s in sessions if s.status == SessionStatus.COMPLETED])
        non_cancelled = len([s for s in sessions if s.status != SessionStatus.CANCELLED])
        
        # Taux de présence
        presence = int((completed / non_cancelled * 100)) if non_cancelled > 0 else 0
        
        presence_label = QLabel(f"Taux de Présence: {presence}%")
        presence_label.setStyleSheet("color: #2c3e50; font-size: 12px;")
        self.performance_layout.addWidget(presence_label)
        
        presence_bar = QProgressBar()
        presence_bar.setValue(presence)
        presence_bar.setFixedHeight(20)
        presence_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #f5f5f5;
                text-align: center;
                color: #2c3e50;
                font-weight: bold;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #229954);
                border-radius: 3px;
            }
        """)
        self.performance_layout.addWidget(presence_bar)
        
        # Sessions par jour
        days = (end_date - start_date).days + 1
        avg_per_day = total / days if days > 0 else 0
        avg_label = QLabel(f"Moy. Sessions/Jour: {avg_per_day:.1f}")
        avg_label.setStyleSheet("color: #2c3e50; font-size: 12px; padding-top: 8px;")
        self.performance_layout.addWidget(avg_label)
        
        # Durée moyenne
        if total > 0:
            total_hours = sum([
                (s.end_datetime - s.start_datetime).total_seconds() / 3600
                for s in sessions
            ])
            avg_duration = total_hours / total
            duration_label = QLabel(f"Durée Moyenne: {avg_duration:.1f}h")
        else:
            duration_label = QLabel(f"Durée Moyenne: 0h")
        
        duration_label.setStyleSheet("color: #2c3e50; font-size: 12px;")
        self.performance_layout.addWidget(duration_label)
    
    def on_period_changed(self, index):
        """Changement de période"""
        period_map = {0: "week", 1: "month", 2: "year"}
        self.current_period = period_map.get(index, "week")
        # Recharger
        self.load_all_stats()
    
    def get_date_range(self):
        """Obtenir plage de dates"""
        today = date.today()
        
        if self.current_period == "week":
            days_since_monday = today.weekday()
            start = today - timedelta(days=days_since_monday)
            end = start + timedelta(days=6)
        elif self.current_period == "month":
            start = today.replace(day=1)
            if today.month == 12:
                end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        else:  # year
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
        
        return start, end
