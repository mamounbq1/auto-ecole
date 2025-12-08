"""
Planning Statistics Widget - Dashboard statistiques planning
Phase 2 Planning Improvements
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGroupBox, QGridLayout, QProgressBar, QComboBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPalette
from datetime import datetime, timedelta, date

from src.controllers.session_controller import SessionController
from src.controllers.instructor_controller import InstructorController
from src.controllers.vehicle_controller import VehicleController
from src.models import SessionStatus, SessionType


class PlanningStatsWidget(QWidget):
    """
    Widget de statistiques du planning
    - Sessions totales/terminées/annulées
    - Heures planifiées vs réalisées
    - Top moniteurs
    - Répartition par type
    - Véhicules les plus utilisés
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_period = "week"  # week, month, year
        
        # Calculer les stats AVANT de créer l'UI
        self.stats_data = self.calculate_stats()
        
        self.setup_ui()
        
        # Plus besoin de load_stats ici, les cartes sont créées avec les bonnes valeurs
    
    def clear_layout(self, layout):
        """Nettoyer un layout récursivement"""
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    self.clear_layout(child.layout())
    
    def calculate_stats(self):
        """Calculer statistiques SANS modifier l'UI"""
        start_date, end_date = self.get_date_range()
        sessions = SessionController.get_sessions_by_date_range(start_date, end_date)
        
        total = len(sessions) if sessions else 0
        completed = len([s for s in sessions if s.status == SessionStatus.COMPLETED]) if sessions else 0
        cancelled = len([s for s in sessions if s.status == SessionStatus.CANCELLED]) if sessions else 0
        
        completed_pct = int((completed / total * 100)) if total > 0 else 0
        cancelled_pct = int((cancelled / total * 100)) if total > 0 else 0
        
        planned_hours = 0
        realized_hours = 0
        if sessions:
            planned_hours = sum([
                (s.end_datetime - s.start_datetime).total_seconds() / 3600
                for s in sessions
            ])
            realized_hours = sum([
                (s.end_datetime - s.start_datetime).total_seconds() / 3600
                for s in sessions if s.status == SessionStatus.COMPLETED
            ])
        
        utilization = int((realized_hours / planned_hours * 100)) if planned_hours > 0 else 0
        
        return {
            'total': total,
            'completed': completed,
            'completed_pct': completed_pct,
            'cancelled': cancelled,
            'cancelled_pct': cancelled_pct,
            'planned_hours': planned_hours,
            'realized_hours': realized_hours,
            'utilization': utilization,
            'sessions': sessions if sessions else []
        }
    
    def setup_ui(self):
        """Configurer l'interface"""
        # Créer le layout principal seulement s'il n'existe pas
        if not self.layout():
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(15, 15, 15, 15)
            main_layout.setSpacing(15)
        else:
            main_layout = self.layout()
            # Vider le layout existant
            while main_layout.count():
                child = main_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    self.clear_layout(child.layout())
        
        # Header avec sélecteur période
        self.create_header(main_layout)
        
        # Stats principales (6 cartes en grille)
        self.create_main_stats(main_layout)
        
        # Graphiques et détails (2 colonnes)
        details_container = QWidget()
        details_layout = QHBoxLayout(details_container)
        details_layout.setSpacing(15)
        details_layout.setContentsMargins(0, 0, 0, 0)
        
        # Colonne gauche (Top moniteurs + Répartition types)
        left_widget = QWidget()
        left_widget.setMinimumWidth(350)
        left_widget.setMaximumWidth(600)
        left_col = QVBoxLayout(left_widget)
        left_col.setSpacing(15)
        left_col.setContentsMargins(0, 0, 0, 0)
        
        self.create_instructor_stats(left_col)
        self.create_type_distribution(left_col)
        left_col.addStretch()
        
        details_layout.addWidget(left_widget)
        
        # Colonne droite (Véhicules + Performance)
        right_widget = QWidget()
        right_widget.setMinimumWidth(350)
        right_widget.setMaximumWidth(600)
        right_col = QVBoxLayout(right_widget)
        right_col.setSpacing(15)
        right_col.setContentsMargins(0, 0, 0, 0)
        
        self.create_vehicle_stats(right_col)
        self.create_performance_metrics(right_col)
        right_col.addStretch()
        
        details_layout.addWidget(right_widget)
        
        main_layout.addWidget(details_container)
        main_layout.addStretch()
    
    def create_header(self, layout):
        """Créer l'en-tête"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        header_layout = QHBoxLayout(header)
        
        title = QLabel("📊 Statistiques Planning")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Sélecteur période
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Cette semaine", "Ce mois", "Cette année"])
        self.period_combo.setCurrentIndex(0)
        self.period_combo.currentIndexChanged.connect(self.on_period_changed)
        self.period_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: #2c3e50;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 150px;
            }
        """)
        header_layout.addWidget(self.period_combo)
        
        layout.addWidget(header)
    
    def create_main_stats(self, layout):
        """Créer les statistiques principales"""
        stats_container = QWidget()
        stats_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        stats_layout = QGridLayout(stats_container)
        stats_layout.setSpacing(12)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sessions - CRÉER avec les VRAIES valeurs dès le début
        stats = self.stats_data
        
        print(f"\n📊 [DEBUG] create_main_stats - Données calculées:")
        print(f"   Total: {stats['total']}")
        print(f"   Completed: {stats['completed']} ({stats['completed_pct']}%)")
        print(f"   Cancelled: {stats['cancelled']} ({stats['cancelled_pct']}%)")
        print(f"   Planned hours: {stats['planned_hours']:.1f}h")
        print(f"   Realized hours: {stats['realized_hours']:.1f}h")
        print(f"   Utilization: {stats['utilization']}%")
        
        # Créer et ajouter toutes les cartes
        cards = [
            (self, 'total_sessions_card', "📅 SESSIONS TOTALES", str(stats['total']), "#3498db", 0, 0),
            (self, 'completed_sessions_card', "✅ TERMINÉES", f"{stats['completed']} ({stats['completed_pct']}%)", "#27ae60", 0, 1),
            (self, 'cancelled_sessions_card', "❌ ANNULÉES", f"{stats['cancelled']} ({stats['cancelled_pct']}%)", "#e74c3c", 0, 2),
            (self, 'planned_hours_card', "⏰ HEURES PLANIFIÉES", f"{stats['planned_hours']:.1f}h", "#9b59b6", 1, 0),
            (self, 'realized_hours_card', "✅ HEURES RÉALISÉES", f"{stats['realized_hours']:.1f}h", "#27ae60", 1, 1),
            (self, 'utilization_card', "📊 TAUX UTILISATION", f"{stats['utilization']}%", "#f39c12", 1, 2),
        ]
        
        for obj, attr_name, title, value, color, row, col in cards:
            card = self.create_stat_card(title, value, color)
            setattr(obj, attr_name, card)
            stats_layout.addWidget(card, row, col)
            # FORCER la visibilité immédiatement après ajout
            self.force_widget_visibility(card)
            print(f"✓ Carte {title[:20]} ajoutée et forcée visible à ({row},{col})")
        
        layout.addWidget(stats_container)
        
        # FORCER la visibilité du container stats
        stats_container.setVisible(True)
        stats_container.show()
        stats_container.updateGeometry()
        
        # FORCER aussi le widget principal
        self.setVisible(True)
        self.show()
        self.updateGeometry()
        
        print(f"\n📊 [DEBUG] Visibilité finale:")
        print(f"   PlanningStatsWidget visible: {self.isVisible()}")
        print(f"   stats_container visible: {stats_container.isVisible()}")
        print(f"   total_sessions_card visible: {self.total_sessions_card.isVisible()}")
        
        # Vérifier les labels
        for label in self.total_sessions_card.findChildren(QLabel):
            print(f"   Label '{label.text()[:20]}' visible: {label.isVisible()}")
    
    def force_widget_visibility(self, widget):
        """Forcer la visibilité d'un widget et ses enfants"""
        widget.setVisible(True)
        widget.show()
        widget.updateGeometry()
        widget.update()
        
        # Forcer aussi tous les labels enfants
        for child in widget.findChildren(QLabel):
            child.setVisible(True)
            child.show()
            child.updateGeometry()
            child.update()
    
    def create_stat_card(self, title, value, color):
        """Créer une carte statistique"""
        print(f"\n🎨 [DEBUG] create_stat_card appelée")
        print(f"   Title: {title}")
        print(f"   Value: {value}")
        print(f"   Color: {color}")
        
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid #ecf0f1;
                border-left: 6px solid {color};
                border-radius: 10px;
                padding: 12px;
                min-width: 180px;
                min-height: 80px;
            }}
            QFrame:hover {{
                border: 2px solid {color};
                border-left: 6px solid {color};
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(5)
        card_layout.setContentsMargins(10, 8, 10, 8)
        
        title_label = QLabel(title.upper())  # Uppercase directement
        title_label.setWordWrap(True)
        
        # TOUT dans setStyleSheet
        title_label.setStyleSheet("""
            color: #7f8c8d;
            font-size: 11pt;
            font-weight: bold;
        """)
        
        print(f"   ✓ Title label créé: '{title_label.text()}'")
        print(f"     Font: {title_font.pointSize()}pt, Bold: {title_font.bold()}")
        
        card_layout.addWidget(title_label)
        
        value_label = QLabel(str(value))
        value_label.setObjectName("value")
        value_label.setTextFormat(Qt.PlainText)
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # TOUT dans setStyleSheet - plus fiable !
        value_label.setStyleSheet(f"""
            color: {color};
            font-size: 28pt;
            font-weight: bold;
        """)
        
        print(f"   ✓ Value label créé: '{value_label.text()}'")
        print(f"     Font: {font.pointSize()}pt, Bold: {font.bold()}")
        print(f"     StyleSheet: color: {color}")
        print(f"     Label visible: {value_label.isVisible()}")
        print(f"     Label enabled: {value_label.isEnabled()}")
        
        card_layout.addWidget(value_label)
        
        card_layout.addStretch()
        
        # Stocker la couleur pour les mises à jour
        card.setProperty("color", color)
        
        print(f"   ✓ Carte créée avec {card_layout.count()} widgets")
        print(f"   ✓ Carte size: {card.minimumWidth()}x{card.minimumHeight()}")
        
        return card
    
    def create_instructor_stats(self, layout):
        """Créer statistiques moniteurs"""
        group = QGroupBox("👨‍🏫 Top Moniteurs (par heures)")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                color: #2c3e50;
            }
        """)
        group.setMinimumHeight(200)
        group.setMaximumHeight(400)
        
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(8)
        
        # Liste moniteurs (sera remplie dans load_stats)
        self.instructors_container = QVBoxLayout()
        self.instructors_container.setSpacing(5)
        group_layout.addLayout(self.instructors_container)
        
        group_layout.addStretch()
        
        layout.addWidget(group)
    
    def create_type_distribution(self, layout):
        """Créer répartition par type"""
        group = QGroupBox("📚 Répartition par Type")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                color: #2c3e50;
            }
        """)
        group.setMinimumHeight(200)
        group.setMaximumHeight(350)
        
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)
        
        # Barres de progression pour chaque type
        self.type_bars = {}
        
        # Mapping types vers labels français
        type_labels = {
            SessionType.PRACTICAL_DRIVING: "Pratique",
            SessionType.THEORETICAL_CLASS: "Théorie",
            SessionType.CODE_EXAM: "Examen Code",
            SessionType.PRACTICAL_EXAM: "Examen Pratique"
        }
        
        for session_type in [SessionType.PRACTICAL_DRIVING, SessionType.THEORETICAL_CLASS, SessionType.CODE_EXAM]:
            type_layout = QVBoxLayout()
            
            type_label_fr = type_labels.get(session_type, session_type.value)
            label = QLabel(f"{type_label_fr}: 0 (0%)")
            label.setStyleSheet("color: #2c3e50; font-size: 13px; font-weight: 500;")
            type_layout.addWidget(label)
            
            bar = QProgressBar()
            bar.setValue(0)
            bar.setMinimumHeight(25)
            bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #e0e0e0;
                    border-radius: 6px;
                    text-align: center;
                    background-color: #f5f5f5;
                    color: #2c3e50;
                    font-weight: bold;
                    font-size: 11px;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #3498db, stop:1 #2980b9);
                    border-radius: 4px;
                }
            """)
            type_layout.addWidget(bar)
            
            self.type_bars[session_type] = (label, bar)
            group_layout.addLayout(type_layout)
        
        group_layout.addStretch()
        
        layout.addWidget(group)
    
    def create_vehicle_stats(self, layout):
        """Créer statistiques véhicules"""
        group = QGroupBox("🚗 Véhicules Les Plus Utilisés")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                color: #2c3e50;
            }
        """)
        group.setMinimumHeight(200)
        group.setMaximumHeight(400)
        
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(8)
        
        # Liste véhicules (sera remplie dans load_stats)
        self.vehicles_container = QVBoxLayout()
        group_layout.addLayout(self.vehicles_container)
        
        group_layout.addStretch()
        
        layout.addWidget(group)
    
    def create_performance_metrics(self, layout):
        """Créer métriques de performance"""
        group = QGroupBox("⚡ Métriques de Performance")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                color: #2c3e50;
            }
        """)
        group.setMinimumHeight(200)
        group.setMaximumHeight(350)
        
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)
        
        # Taux de présence
        presence_layout = QVBoxLayout()
        self.presence_label = QLabel("Taux de Présence: 0%")
        self.presence_label.setStyleSheet("color: #2c3e50; font-size: 13px; font-weight: 500;")
        presence_layout.addWidget(self.presence_label)
        
        self.presence_bar = QProgressBar()
        self.presence_bar.setValue(0)
        self.presence_bar.setMinimumHeight(25)
        self.presence_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                text-align: center;
                background-color: #f5f5f5;
                color: #2c3e50;
                font-weight: bold;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #229954);
                border-radius: 4px;
            }
        """)
        presence_layout.addWidget(self.presence_bar)
        group_layout.addLayout(presence_layout)
        
        # Sessions par jour (moyenne)
        self.avg_sessions_label = QLabel("Moyenne Sessions/Jour: 0")
        self.avg_sessions_label.setStyleSheet("color: #2c3e50; font-size: 13px; font-weight: 500; padding: 8px 0;")
        group_layout.addWidget(self.avg_sessions_label)
        
        # Durée moyenne session
        self.avg_duration_label = QLabel("Durée Moyenne: 0h")
        self.avg_duration_label.setStyleSheet("color: #2c3e50; font-size: 13px; font-weight: 500; padding: 8px 0;")
        group_layout.addWidget(self.avg_duration_label)
        
        group_layout.addStretch()
        
        layout.addWidget(group)
    
    def on_period_changed(self, index):
        """Changement de période - RECRÉER toute l'UI"""
        period_map = {0: "week", 1: "month", 2: "year"}
        self.current_period = period_map.get(index, "week")
        
        # Recalculer stats
        self.stats_data = self.calculate_stats()
        
        # Recréer l'UI avec les nouvelles valeurs (setup_ui gère le nettoyage)
        self.setup_ui()
    
    def get_date_range(self):
        """Obtenir plage de dates selon période"""
        today = date.today()
        
        if self.current_period == "week":
            # Semaine actuelle (lundi à dimanche)
            days_since_monday = today.weekday()
            start = today - timedelta(days=days_since_monday)
            end = start + timedelta(days=6)
        elif self.current_period == "month":
            # Mois actuel
            start = today.replace(day=1)
            # Dernier jour du mois
            if today.month == 12:
                end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        else:  # year
            # Année actuelle
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
        
        return start, end
    
    def load_stats(self):
        """Charger les statistiques - UTILISE stats_data déjà calculées"""
        print("📊 [DEBUG] load_stats() appelée")
        
        # Recalculer
        self.stats_data = self.calculate_stats()
        stats = self.stats_data
        
        print(f"📊 [DEBUG] {stats['total']} sessions trouvées")
        print(f"📊 [DEBUG] Mise à jour cartes: total={stats['total']}, completed={stats['completed']}, cancelled={stats['cancelled']}")
        
        # Les cartes du bas (moniteurs, véhicules, etc.)
        start_date, end_date = self.get_date_range()
        sessions = stats['sessions']
        
        # Stats moniteurs
        self.load_instructor_stats(sessions)
        
        # Répartition par type
        self.load_type_distribution(sessions)
        
        # Stats véhicules
        self.load_vehicle_stats(sessions)
        
        # Métriques performance
        self.load_performance_metrics(sessions, start_date, end_date)
        
        print("📊 [DEBUG] Chargement stats terminé")
    
    def update_stat_card(self, card, value):
        """Mettre à jour valeur carte stat - MÉTHODE RADICALE"""
        # Récupérer le layout de la carte
        layout = card.layout()
        if not layout:
            print(f"⚠️ [DEBUG] Carte sans layout!")
            return
        
        # Récupérer la couleur stockée
        color = card.property("color") or "#3498db"
        
        # Trouver et SUPPRIMER l'ancien label de valeur
        old_value_label = None
        for label in card.findChildren(QLabel):
            if label.objectName() == "value":
                old_value_label = label
                break
        
        if old_value_label:
            print(f"📊 [DEBUG] Suppression ancien label: '{old_value_label.text()}'")
            layout.removeWidget(old_value_label)
            old_value_label.deleteLater()
        
        # CRÉER un NOUVEAU label avec la valeur
        new_value_label = QLabel(str(value))
        new_value_label.setStyleSheet(f"""
            color: {color}; 
            font-size: 28px; 
            font-weight: bold;
        """)
        new_value_label.setObjectName("value")
        new_value_label.setTextFormat(Qt.PlainText)
        new_value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Insérer à la position 1 (après le titre)
        layout.insertWidget(1, new_value_label)
        
        print(f"✅ [DEBUG] Nouveau label créé: '{value}'")
    
    def load_instructor_stats(self, sessions):
        """Charger stats moniteurs"""
        # Clear existing
        while self.instructors_container.count():
            item = self.instructors_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Compter heures par moniteur
        instructor_hours = {}
        for session in sessions:
            if session.instructor_id:
                hours = (session.end_datetime - session.start_datetime).total_seconds() / 3600
                instructor_hours[session.instructor_id] = instructor_hours.get(session.instructor_id, 0) + hours
        
        # Trier et afficher top 5
        sorted_instructors = sorted(instructor_hours.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Obtenir infos moniteurs
        all_instructors = {i.id: i for i in InstructorController.get_all_instructors()}
        
        for i, (instructor_id, hours) in enumerate(sorted_instructors):
            instructor = all_instructors.get(instructor_id)
            if not instructor:
                continue
            
            row = QHBoxLayout()
            
            rank_label = QLabel(f"{i+1}.")
            rank_label.setStyleSheet("font-weight: bold; color: #f39c12; min-width: 20px;")
            row.addWidget(rank_label)
            
            name_label = QLabel(instructor.full_name[:20])
            name_label.setStyleSheet("color: #2c3e50;")
            row.addWidget(name_label, stretch=1)
            
            hours_label = QLabel(f"{hours:.1f}h")
            hours_label.setStyleSheet("font-weight: bold; color: #3498db;")
            row.addWidget(hours_label)
            
            self.instructors_container.addLayout(row)
    
    def load_type_distribution(self, sessions):
        """Charger répartition par type"""
        total = len(sessions)
        
        # Mapping types vers labels français
        type_labels = {
            SessionType.PRACTICAL_DRIVING: "Pratique",
            SessionType.THEORETICAL_CLASS: "Théorie",
            SessionType.CODE_EXAM: "Examen Code",
            SessionType.PRACTICAL_EXAM: "Examen Pratique"
        }
        
        type_counts = {}
        if sessions:
            for session in sessions:
                type_counts[session.session_type] = type_counts.get(session.session_type, 0) + 1
        
        # TOUJOURS afficher, même si vide
        for session_type, (label, bar) in self.type_bars.items():
            count = type_counts.get(session_type, 0)
            pct = int((count / total * 100)) if total > 0 else 0
            
            type_label_fr = type_labels.get(session_type, session_type.value)
            label.setText(f"{type_label_fr}: {count} ({pct}%)")
            bar.setValue(pct)
    
    def load_vehicle_stats(self, sessions):
        """Charger stats véhicules"""
        # Clear existing
        while self.vehicles_container.count():
            item = self.vehicles_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Compter heures par véhicule
        vehicle_hours = {}
        for session in sessions:
            if session.vehicle_id:
                hours = (session.end_datetime - session.start_datetime).total_seconds() / 3600
                vehicle_hours[session.vehicle_id] = vehicle_hours.get(session.vehicle_id, 0) + hours
        
        # Trier et afficher top 5
        sorted_vehicles = sorted(vehicle_hours.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Obtenir infos véhicules
        all_vehicles = {v.id: v for v in VehicleController.get_all_vehicles()}
        
        for i, (vehicle_id, hours) in enumerate(sorted_vehicles):
            vehicle = all_vehicles.get(vehicle_id)
            if not vehicle:
                continue
            
            row = QHBoxLayout()
            
            rank_label = QLabel(f"{i+1}.")
            rank_label.setStyleSheet("font-weight: bold; color: #f39c12; min-width: 20px;")
            row.addWidget(rank_label)
            
            name_label = QLabel(f"{vehicle.make} {vehicle.model} ({vehicle.plate_number})")
            name_label.setStyleSheet("color: #2c3e50; font-size: 11px;")
            row.addWidget(name_label, stretch=1)
            
            hours_label = QLabel(f"{hours:.0f}h")
            hours_label.setStyleSheet("font-weight: bold; color: #3498db;")
            row.addWidget(hours_label)
            
            self.vehicles_container.addLayout(row)
    
    def load_performance_metrics(self, sessions, start_date, end_date):
        """Charger métriques performance"""
        total = len(sessions) if sessions else 0
        completed = len([s for s in sessions if s.status == SessionStatus.COMPLETED]) if sessions else 0
        
        # Taux présence (complétées / total non annulées)
        non_cancelled = len([s for s in sessions if s.status != SessionStatus.CANCELLED]) if sessions else 0
        presence_rate = int((completed / non_cancelled * 100)) if non_cancelled > 0 else 0
        
        self.presence_label.setText(f"Taux de Présence: {presence_rate}%")
        self.presence_bar.setValue(presence_rate)
        
        # Sessions par jour (moyenne)
        days = (end_date - start_date).days + 1
        avg_per_day = total / days if days > 0 else 0
        self.avg_sessions_label.setText(f"Moyenne Sessions/Jour: {avg_per_day:.1f}")
        
        # Durée moyenne
        if sessions and total > 0:
            total_hours = sum([
                (s.end_datetime - s.start_datetime).total_seconds() / 3600
                for s in sessions
            ])
            avg_duration = total_hours / total
            self.avg_duration_label.setText(f"Durée Moyenne: {avg_duration:.1f}h")
        else:
            self.avg_duration_label.setText(f"Durée Moyenne: 0h")
