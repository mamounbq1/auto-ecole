"""
Module: Tableau de bord des véhicules
Version: 1.0.0 - Créé le 2025-12-08

Description:
    Dashboard moderne affichant les statistiques des véhicules:
    - Statistiques générales (total, disponibles, en maintenance)
    - Top véhicules par utilisation
    - Distribution des véhicules par statut
    - Véhicules nécessitant une attention (alertes)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datetime import datetime, timedelta, date
from collections import defaultdict

from src.controllers.vehicle_controller import VehicleController
from src.controllers.session_controller import SessionController
from src.models import VehicleStatus


class VehiclesDashboard(QWidget):
    """Dashboard des véhicules avec statistiques et analyses"""
    
    def __init__(self):
        super().__init__()
        self.current_period = 'all'  # Par défaut: tous les véhicules
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
        
        title = QLabel("📊 TABLEAU DE BORD VÉHICULES")
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
            "Tous les véhicules",
            "Véhicules actifs",
            "Disponibles",
            "En maintenance",
            "En service"
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
        
        # Statistiques principales (4 cartes)
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(20)
        content_layout.addLayout(self.stats_layout)
        
        # Top véhicules
        top_section = self.create_section("🏆 Top 5 Véhicules par Utilisation")
        self.top_vehicles_layout = QVBoxLayout()
        top_section.layout().addLayout(self.top_vehicles_layout)
        content_layout.addWidget(top_section)
        
        # Trois sections côte à côte
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)
        
        # Distribution par statut
        status_section = self.create_section("📈 Distribution par Statut")
        self.status_layout = QVBoxLayout()
        status_section.layout().addLayout(self.status_layout)
        bottom_row.addWidget(status_section)
        
        # Distribution par type de permis
        license_section = self.create_section("🪪 Distribution par Permis")
        self.license_layout = QVBoxLayout()
        license_section.layout().addLayout(self.license_layout)
        bottom_row.addWidget(license_section)
        
        # Alertes maintenance
        alerts_section = self.create_section("⚠️ Alertes et Maintenance")
        self.alerts_layout = QVBoxLayout()
        alerts_section.layout().addLayout(self.alerts_layout)
        bottom_row.addWidget(alerts_section)
        
        content_layout.addLayout(bottom_row)
        
        # Statistiques d'utilisation
        usage_section = self.create_section("📊 Statistiques d'Utilisation")
        self.usage_layout = QVBoxLayout()
        usage_section.layout().addLayout(self.usage_layout)
        content_layout.addWidget(usage_section)
        
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
            '#00BCD4': '#0097A7'
        }
        return colors.get(color, color)
    
    def on_period_changed(self):
        """Changement de période"""
        period_map = {
            'Tous les véhicules': 'all',
            'Véhicules actifs': 'active',
            'Disponibles': 'available',
            'En maintenance': 'maintenance',
            'En service': 'in_service'
        }
        self.current_period = period_map.get(self.period_combo.currentText(), 'all')
        self.load_stats()
    
    def load_stats(self):
        """Charger les statistiques"""
        # Nettoyer les cartes existantes
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Récupérer tous les véhicules
        all_vehicles = VehicleController.get_all_vehicles()
        
        # Filtrer selon la période
        if self.current_period == 'all':
            vehicles = all_vehicles
        elif self.current_period == 'active':
            vehicles = [v for v in all_vehicles if v.status != VehicleStatus.OUT_OF_SERVICE]
        elif self.current_period == 'available':
            vehicles = [v for v in all_vehicles if v.is_available]
        elif self.current_period == 'maintenance':
            vehicles = [v for v in all_vehicles if v.status == VehicleStatus.MAINTENANCE]
        elif self.current_period == 'in_service':
            vehicles = [v for v in all_vehicles if v.status == VehicleStatus.IN_SERVICE]
        else:
            vehicles = all_vehicles
        
        # Calculer les statistiques
        total = len(vehicles)
        available = sum(1 for v in vehicles if v.is_available)
        in_maintenance = sum(1 for v in vehicles if v.status == VehicleStatus.MAINTENANCE)
        avg_mileage = sum(v.current_mileage or 0 for v in vehicles) / total if total > 0 else 0
        
        # Créer les 4 cartes
        self.stats_layout.addWidget(
            self.create_stat_card("Total Véhicules", total, "🚗", "#2196F3")
        )
        self.stats_layout.addWidget(
            self.create_stat_card("Disponibles", available, "✅", "#4CAF50")
        )
        self.stats_layout.addWidget(
            self.create_stat_card("En Maintenance", in_maintenance, "🔧", "#FF9800")
        )
        self.stats_layout.addWidget(
            self.create_stat_card(
                "Kilométrage Moyen",
                f"{int(avg_mileage):,}",
                "📏",
                "#9C27B0"
            )
        )
        
        # Charger les autres sections
        self.load_top_vehicles(vehicles)
        self.load_status_distribution(vehicles)
        self.load_license_distribution(vehicles)
        self.load_alerts(all_vehicles)
        self.load_usage_stats(vehicles)
    
    def load_top_vehicles(self, vehicles):
        """Charger le top 5 des véhicules"""
        # Nettoyer
        while self.top_vehicles_layout.count():
            item = self.top_vehicles_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Trier par heures d'utilisation
        sorted_vehicles = sorted(
            vehicles,
            key=lambda v: v.total_hours_used or 0,
            reverse=True
        )[:5]
        
        if not sorted_vehicles:
            no_data = QLabel("Aucune donnée disponible")
            no_data.setFont(QFont("Segoe UI", 10))
            no_data.setStyleSheet("color: #999; border: none; padding: 20px;")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.top_vehicles_layout.addWidget(no_data)
            return
        
        for idx, vehicle in enumerate(sorted_vehicles, 1):
            row = QWidget()
            row.setFixedHeight(35)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)
            
            # Rang
            rank = QLabel(f"#{idx}")
            rank.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            rank.setStyleSheet("color: #2196F3; border: none;")
            rank.setFixedWidth(30)
            row_layout.addWidget(rank)
            
            # Plaque + Marque/Modèle
            vehicle_name = f"{vehicle.plate_number} - {vehicle.make} {vehicle.model}"
            if len(vehicle_name) > 35:
                vehicle_name = vehicle_name[:32] + "..."
            
            name = QLabel(vehicle_name)
            name.setFont(QFont("Segoe UI", 11))
            name.setStyleSheet("color: #333; border: none;")
            name.setWordWrap(False)
            row_layout.addWidget(name, 1)
            
            # Heures
            hours = QLabel(f"{vehicle.total_hours_used or 0:.1f}h")
            hours.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            hours.setStyleSheet("color: #4CAF50; border: none;")
            hours.setAlignment(Qt.AlignmentFlag.AlignRight)
            hours.setFixedWidth(70)
            row_layout.addWidget(hours)
            
            self.top_vehicles_layout.addWidget(row)
        
        self.top_vehicles_layout.addStretch()
    
    def load_status_distribution(self, vehicles):
        """Charger la distribution par statut"""
        # Nettoyer
        while self.status_layout.count():
            item = self.status_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Compter par statut
        status_counts = defaultdict(int)
        for vehicle in vehicles:
            status_counts[vehicle.status.value] += 1
        
        if not status_counts:
            no_data = QLabel("Aucune donnée")
            no_data.setFont(QFont("Segoe UI", 10))
            no_data.setStyleSheet("color: #999; border: none;")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.status_layout.addWidget(no_data)
            return
        
        total = len(vehicles)
        
        # Couleurs par statut
        status_colors = {
            'Disponible': '#4CAF50',
            'En service': '#2196F3',
            'En maintenance': '#FF9800',
            'Hors service': '#F44336'
        }
        
        for status_name, count in sorted(status_counts.items(), key=lambda x: -x[1]):
            percentage = (count / total * 100) if total > 0 else 0
            
            row = QWidget()
            row.setFixedHeight(30)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)
            
            # Label
            label = QLabel(status_name)
            label.setFont(QFont("Segoe UI", 10))
            label.setStyleSheet("color: #333; border: none;")
            row_layout.addWidget(label, 1)
            
            # Barre de progression
            bar_container = QFrame()
            bar_container.setFixedHeight(20)
            bar_container.setStyleSheet("background: #f0f0f0; border-radius: 10px; border: none;")
            
            bar = QFrame(bar_container)
            bar.setFixedHeight(20)
            bar_width = int(150 * percentage / 100)
            bar.setFixedWidth(bar_width)
            bar.setStyleSheet(f"""
                background: {status_colors.get(status_name, '#999')};
                border-radius: 10px;
                border: none;
            """)
            
            row_layout.addWidget(bar_container)
            
            # Valeur
            value = QLabel(f"{count} ({percentage:.1f}%)")
            value.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            value.setStyleSheet("color: #666; border: none;")
            value.setFixedWidth(90)
            value.setAlignment(Qt.AlignmentFlag.AlignRight)
            row_layout.addWidget(value)
            
            self.status_layout.addWidget(row)
        
        self.status_layout.addStretch()
    
    def load_license_distribution(self, vehicles):
        """Charger la distribution par type de permis"""
        # Nettoyer
        while self.license_layout.count():
            item = self.license_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Compter par type de permis
        license_counts = defaultdict(int)
        for vehicle in vehicles:
            license_counts[vehicle.license_type or 'Non défini'] += 1
        
        if not license_counts:
            no_data = QLabel("Aucune donnée")
            no_data.setFont(QFont("Segoe UI", 10))
            no_data.setStyleSheet("color: #999; border: none;")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.license_layout.addWidget(no_data)
            return
        
        total = len(vehicles)
        
        # Couleurs par type
        license_colors = {
            'A': '#E91E63',
            'B': '#2196F3',
            'C': '#FF9800',
            'D': '#9C27B0'
        }
        
        for license_type, count in sorted(license_counts.items(), key=lambda x: -x[1]):
            percentage = (count / total * 100) if total > 0 else 0
            
            row = QWidget()
            row.setFixedHeight(30)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)
            
            # Label
            label = QLabel(f"Permis {license_type}")
            label.setFont(QFont("Segoe UI", 10))
            label.setStyleSheet("color: #333; border: none;")
            row_layout.addWidget(label, 1)
            
            # Barre
            bar_container = QFrame()
            bar_container.setFixedHeight(20)
            bar_container.setStyleSheet("background: #f0f0f0; border-radius: 10px; border: none;")
            
            bar = QFrame(bar_container)
            bar.setFixedHeight(20)
            bar_width = int(120 * percentage / 100)
            bar.setFixedWidth(bar_width)
            bar.setStyleSheet(f"""
                background: {license_colors.get(license_type, '#999')};
                border-radius: 10px;
                border: none;
            """)
            
            row_layout.addWidget(bar_container)
            
            # Valeur
            value = QLabel(f"{count} ({percentage:.1f}%)")
            value.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            value.setStyleSheet("color: #666; border: none;")
            value.setFixedWidth(80)
            value.setAlignment(Qt.AlignmentFlag.AlignRight)
            row_layout.addWidget(value)
            
            self.license_layout.addWidget(row)
        
        self.license_layout.addStretch()
    
    def load_alerts(self, vehicles):
        """Charger les alertes de maintenance"""
        # Nettoyer
        while self.alerts_layout.count():
            item = self.alerts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        today = date.today()
        alerts = []
        
        for vehicle in vehicles:
            # Vérifier assurance
            if vehicle.insurance_expiry_date:
                days_until = (vehicle.insurance_expiry_date - today).days
                if 0 <= days_until <= 30:
                    alerts.append((
                        f"{vehicle.plate_number}",
                        f"Assurance expire dans {days_until} jours",
                        '#F44336' if days_until <= 7 else '#FF9800'
                    ))
            
            # Vérifier visite technique
            if vehicle.technical_inspection_date:
                days_until = (vehicle.technical_inspection_date - today).days
                if 0 <= days_until <= 30:
                    alerts.append((
                        f"{vehicle.plate_number}",
                        f"Visite technique dans {days_until} jours",
                        '#F44336' if days_until <= 7 else '#FF9800'
                    ))
            
            # Vérifier kilométrage pour maintenance
            if vehicle.current_mileage and vehicle.last_oil_change_mileage:
                km_since = vehicle.current_mileage - vehicle.last_oil_change_mileage
                if km_since >= 10000:
                    alerts.append((
                        f"{vehicle.plate_number}",
                        f"Vidange nécessaire ({km_since:,} km)",
                        '#FF9800'
                    ))
        
        if not alerts:
            no_data = QLabel("✅ Aucune alerte")
            no_data.setFont(QFont("Segoe UI", 10))
            no_data.setStyleSheet("color: #4CAF50; border: none;")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.alerts_layout.addWidget(no_data)
            return
        
        # Limiter à 5 alertes
        for plate, message, color in alerts[:5]:
            row = QWidget()
            row.setFixedHeight(35)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)
            
            # Icon
            icon = QLabel("⚠️")
            icon.setFont(QFont("Segoe UI", 14))
            icon.setStyleSheet("border: none;")
            row_layout.addWidget(icon)
            
            # Message
            msg = QLabel(f"{plate}: {message}")
            msg.setFont(QFont("Segoe UI", 10))
            msg.setStyleSheet(f"color: {color}; border: none;")
            msg.setWordWrap(True)
            row_layout.addWidget(msg, 1)
            
            self.alerts_layout.addWidget(row)
        
        if len(alerts) > 5:
            more = QLabel(f"... et {len(alerts) - 5} autre(s) alerte(s)")
            more.setFont(QFont("Segoe UI", 9))
            more.setStyleSheet("color: #999; border: none; font-style: italic;")
            self.alerts_layout.addWidget(more)
        
        self.alerts_layout.addStretch()
    
    def load_usage_stats(self, vehicles):
        """Charger les statistiques d'utilisation"""
        # Nettoyer
        while self.usage_layout.count():
            item = self.usage_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not vehicles:
            no_data = QLabel("Aucune donnée disponible")
            no_data.setFont(QFont("Segoe UI", 10))
            no_data.setStyleSheet("color: #999; border: none;")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.usage_layout.addWidget(no_data)
            return
        
        # Calculer les statistiques
        total_hours = sum(v.total_hours_used or 0 for v in vehicles)
        total_sessions = sum(v.total_sessions or 0 for v in vehicles)
        total_mileage = sum(v.current_mileage or 0 for v in vehicles)
        
        avg_hours_per_vehicle = total_hours / len(vehicles) if vehicles else 0
        avg_sessions_per_vehicle = total_sessions / len(vehicles) if vehicles else 0
        
        # Grille de stats
        grid = QHBoxLayout()
        grid.setSpacing(30)
        
        stats = [
            ("Total Heures", f"{total_hours:.1f}h", "#2196F3"),
            ("Total Sessions", str(total_sessions), "#4CAF50"),
            ("Kilométrage Total", f"{total_mileage:,} km", "#FF9800"),
            ("Moy. Heures/Véhicule", f"{avg_hours_per_vehicle:.1f}h", "#9C27B0"),
            ("Moy. Sessions/Véhicule", f"{avg_sessions_per_vehicle:.1f}", "#00BCD4")
        ]
        
        for label_text, value_text, color in stats:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout(stat_widget)
            stat_layout.setContentsMargins(10, 10, 10, 10)
            stat_layout.setSpacing(5)
            
            value = QLabel(value_text)
            value.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            value.setStyleSheet(f"color: {color}; border: none;")
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_layout.addWidget(value)
            
            label = QLabel(label_text)
            label.setFont(QFont("Segoe UI", 9))
            label.setStyleSheet("color: #666; border: none;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True)
            stat_layout.addWidget(label)
            
            grid.addWidget(stat_widget)
        
        self.usage_layout.addLayout(grid)
