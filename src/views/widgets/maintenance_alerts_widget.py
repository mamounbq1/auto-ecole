"""
Widget d'alertes de maintenance
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QGroupBox, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

from src.controllers import MaintenanceController
from datetime import datetime


class MaintenanceAlertsWidget(QWidget):
    """Widget d'alertes pour les maintenances à venir ou en retard"""
    
    maintenance_selected = Signal(int)  # Signal avec ID de la maintenance
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.refresh_alerts()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Titre
        title = QLabel("⚠️ Alertes Maintenance")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Maintenances à venir (30 prochains jours)
        upcoming_group = QGroupBox("📅 À Venir (30 jours)")
        upcoming_layout = QVBoxLayout(upcoming_group)
        
        self.upcoming_list = QListWidget()
        self.upcoming_list.setMaximumHeight(150)
        self.upcoming_list.itemDoubleClicked.connect(self.on_maintenance_selected)
        upcoming_layout.addWidget(self.upcoming_list)
        
        layout.addWidget(upcoming_group)
        
        # Maintenances en retard
        overdue_group = QGroupBox("🔴 En Retard")
        overdue_layout = QVBoxLayout(overdue_group)
        
        self.overdue_list = QListWidget()
        self.overdue_list.setMaximumHeight(150)
        self.overdue_list.itemDoubleClicked.connect(self.on_maintenance_selected)
        overdue_layout.addWidget(self.overdue_list)
        
        layout.addWidget(overdue_group)
        
        # Bouton Rafraîchir
        refresh_btn = QPushButton("🔄 Rafraîchir")
        refresh_btn.clicked.connect(self.refresh_alerts)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
    
    def refresh_alerts(self):
        """Rafraîchir les alertes"""
        try:
            alerts = MaintenanceController.get_maintenance_alerts()
            
            # Maintenances à venir
            self.upcoming_list.clear()
            upcoming = alerts.get('upcoming', [])
            
            for maint in upcoming[:10]:  # Limiter à 10
                days_until = (maint.scheduled_date - datetime.now().date()).days
                vehicle_text = maint.vehicle.plate_number if maint.vehicle else "N/A"
                
                item = QListWidgetItem(
                    f"📅 {vehicle_text} - {maint.maintenance_type.value} "
                    f"(dans {days_until}j)"
                )
                item.setData(Qt.UserRole, maint.id)
                item.setForeground(QColor("#f39c12"))
                self.upcoming_list.addItem(item)
            
            if not upcoming:
                item = QListWidgetItem("✅ Aucune maintenance prochainement")
                item.setForeground(QColor("#27ae60"))
                self.upcoming_list.addItem(item)
            
            # Maintenances en retard
            self.overdue_list.clear()
            overdue = alerts.get('overdue', [])
            
            for maint in overdue[:10]:  # Limiter à 10
                days_late = (datetime.now().date() - maint.scheduled_date).days
                vehicle_text = maint.vehicle.plate_number if maint.vehicle else "N/A"
                
                item = QListWidgetItem(
                    f"🔴 {vehicle_text} - {maint.maintenance_type.value} "
                    f"(en retard de {days_late}j)"
                )
                item.setData(Qt.UserRole, maint.id)
                item.setForeground(QColor("#e74c3c"))
                item.setFont(QFont("Arial", 9, QFont.Bold))
                self.overdue_list.addItem(item)
            
            if not overdue:
                item = QListWidgetItem("✅ Aucune maintenance en retard")
                item.setForeground(QColor("#27ae60"))
                self.overdue_list.addItem(item)
                
        except Exception as e:
            print(f"Erreur refresh alerts: {e}")
    
    def on_maintenance_selected(self, item: QListWidgetItem):
        """Gérer la sélection d'une maintenance"""
        maint_id = item.data(Qt.UserRole)
        if maint_id:
            self.maintenance_selected.emit(maint_id)
