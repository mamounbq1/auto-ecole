"""
Dialogue pour créer/éditer une maintenance véhicule
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QDateEdit, QTextEdit, QMessageBox, QLineEdit
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont

from src.controllers import MaintenanceController, VehicleController
from src.models import MaintenanceType, MaintenanceStatus
from datetime import datetime, date


class MaintenanceDialog(QDialog):
    """Dialogue pour créer ou éditer une maintenance"""
    
    maintenance_saved = Signal()  # Signal émis quand une maintenance est sauvegardée
    
    def __init__(self, vehicle_id=None, maintenance=None, parent=None):
        super().__init__(parent)
        self.vehicle_id = vehicle_id
        self.maintenance = maintenance
        self.is_edit = maintenance is not None
        
        title = "✏️ Modifier Maintenance" if self.is_edit else "🔧 Nouvelle Maintenance"
        self.setWindowTitle(title)
        self.setMinimumSize(700, 650)
        self.setup_ui()
        
        if self.is_edit:
            self.load_maintenance_data()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("🔧 Planifier une Maintenance Véhicule")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Formulaire
        form = QFormLayout()
        form.setSpacing(15)
        
        # Véhicule
        self.vehicle_combo = QComboBox()
        self.load_vehicles()
        if self.vehicle_id:
            # Trouver et sélectionner le véhicule
            for i in range(self.vehicle_combo.count()):
                if self.vehicle_combo.itemData(i) == self.vehicle_id:
                    self.vehicle_combo.setCurrentIndex(i)
                    self.vehicle_combo.setEnabled(False)  # Désactiver si véhicule pré-sélectionné
                    break
        form.addRow("Véhicule*:", self.vehicle_combo)
        
        # Type de maintenance
        self.type_combo = QComboBox()
        for mtype in MaintenanceType:
            self.type_combo.addItem(mtype.value, mtype)
        form.addRow("Type de Maintenance*:", self.type_combo)
        
        # Date planifiée
        self.scheduled_date = QDateEdit()
        self.scheduled_date.setCalendarPopup(True)
        self.scheduled_date.setDate(QDate.currentDate())
        form.addRow("Date Planifiée*:", self.scheduled_date)
        
        # Kilométrage actuel
        self.mileage_input = QSpinBox()
        self.mileage_input.setMinimum(0)
        self.mileage_input.setMaximum(9999999)
        self.mileage_input.setSuffix(" km")
        form.addRow("Kilométrage Actuel:", self.mileage_input)
        
        # Coût estimé
        self.estimated_cost = QDoubleSpinBox()
        self.estimated_cost.setMinimum(0)
        self.estimated_cost.setMaximum(999999)
        self.estimated_cost.setSuffix(" DH")
        self.estimated_cost.setDecimals(2)
        form.addRow("Coût Estimé:", self.estimated_cost)
        
        # Statut
        self.status_combo = QComboBox()
        for status in MaintenanceStatus:
            self.status_combo.addItem(status.value, status)
        form.addRow("Statut:", self.status_combo)
        
        # Fournisseur/Garage
        self.provider_input = QLineEdit()
        self.provider_input.setPlaceholderText("Ex: Garage Moderne, Casablanca")
        form.addRow("Fournisseur/Garage:", self.provider_input)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        self.notes_input.setPlaceholderText("Notes sur la maintenance (problèmes détectés, pièces à remplacer, etc.)")
        form.addRow("Notes:", self.notes_input)
        
        layout.addLayout(form)
        
        # Informations de complétion (seulement en mode édition et si complétée)
        if self.is_edit and self.maintenance and self.maintenance.status == MaintenanceStatus.COMPLETED:
            completion_group = QFormLayout()
            completion_group.setSpacing(10)
            
            # Date de complétion
            self.completion_date = QDateEdit()
            self.completion_date.setCalendarPopup(True)
            if self.maintenance.completed_date:
                self.completion_date.setDate(QDate(self.maintenance.completed_date))
            completion_group.addRow("Date de Complétion:", self.completion_date)
            
            # Coût final
            self.final_cost = QDoubleSpinBox()
            self.final_cost.setMinimum(0)
            self.final_cost.setMaximum(999999)
            self.final_cost.setSuffix(" DH")
            self.final_cost.setDecimals(2)
            if self.maintenance.actual_cost:
                self.final_cost.setValue(self.maintenance.actual_cost)
            completion_group.addRow("Coût Final:", self.final_cost)
            
            # Pièces remplacées
            self.parts_replaced = QTextEdit()
            self.parts_replaced.setMaximumHeight(80)
            if self.maintenance.parts_replaced:
                self.parts_replaced.setPlainText(self.maintenance.parts_replaced)
            completion_group.addRow("Pièces Remplacées:", self.parts_replaced)
            
            layout.addLayout(completion_group)
        
        # Informations
        info_label = QLabel(
            "ℹ️ Les champs marqués d'un astérisque (*) sont obligatoires.\n"
            "   Le véhicule sera automatiquement marqué comme 'en maintenance' lors de la création."
        )
        info_label.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 10px;")
        layout.addWidget(info_label)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.save_maintenance)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def load_vehicles(self):
        """Charger la liste des véhicules"""
        try:
            vehicles = VehicleController.get_all_vehicles()
            
            for vehicle in vehicles:
                display_text = f"{vehicle.plate_number} - {vehicle.make} {vehicle.model}"
                self.vehicle_combo.addItem(display_text, vehicle.id)
                
        except Exception as e:
            print(f"Erreur chargement véhicules: {e}")
    
    def load_maintenance_data(self):
        """Charger les données de la maintenance (mode édition)"""
        if not self.maintenance:
            return
        
        # Sélectionner le véhicule
        for i in range(self.vehicle_combo.count()):
            if self.vehicle_combo.itemData(i) == self.maintenance.vehicle_id:
                self.vehicle_combo.setCurrentIndex(i)
                break
        
        # Type
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == self.maintenance.maintenance_type:
                self.type_combo.setCurrentIndex(i)
                break
        
        # Date planifiée
        if self.maintenance.scheduled_date:
            self.scheduled_date.setDate(QDate(self.maintenance.scheduled_date))
        
        # Kilométrage
        if self.maintenance.mileage_at_maintenance:
            self.mileage_input.setValue(self.maintenance.mileage_at_maintenance)
        
        # Coût estimé
        if self.maintenance.estimated_cost:
            self.estimated_cost.setValue(self.maintenance.estimated_cost)
        
        # Statut
        for i in range(self.status_combo.count()):
            if self.status_combo.itemData(i) == self.maintenance.status:
                self.status_combo.setCurrentIndex(i)
                break
        
        # Fournisseur
        if self.maintenance.provider:
            self.provider_input.setText(self.maintenance.provider)
        
        # Notes
        if self.maintenance.notes:
            self.notes_input.setPlainText(self.maintenance.notes)
    
    def save_maintenance(self):
        """Enregistrer la maintenance"""
        # Validation
        vehicle_id = self.vehicle_combo.currentData()
        if not vehicle_id:
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner un véhicule")
            return
        
        maintenance_type = self.type_combo.currentData()
        scheduled_date_py = self.scheduled_date.date().toPython()
        
        # Préparer les données
        maintenance_data = {
            'vehicle_id': vehicle_id,
            'maintenance_type': maintenance_type,
            'scheduled_date': scheduled_date_py,
            'mileage_at_maintenance': self.mileage_input.value() if self.mileage_input.value() > 0 else None,
            'estimated_cost': self.estimated_cost.value() if self.estimated_cost.value() > 0 else None,
            'status': self.status_combo.currentData(),
            'provider': self.provider_input.text().strip() or None,
            'notes': self.notes_input.toPlainText().strip() or None,
        }
        
        # Ajouter données de complétion si présentes
        if hasattr(self, 'completion_date'):
            maintenance_data['completed_date'] = self.completion_date.date().toPython()
        
        if hasattr(self, 'final_cost'):
            maintenance_data['actual_cost'] = self.final_cost.value()
        
        if hasattr(self, 'parts_replaced'):
            maintenance_data['parts_replaced'] = self.parts_replaced.toPlainText().strip() or None
        
        try:
            if self.is_edit:
                # Mise à jour
                success = MaintenanceController.update_maintenance(
                    self.maintenance.id,
                    maintenance_data
                )
                if success:
                    QMessageBox.information(self, "Succès", "Maintenance mise à jour avec succès!")
                    self.maintenance_saved.emit()
                    self.accept()
                else:
                    QMessageBox.warning(self, "Erreur", "Impossible de mettre à jour la maintenance")
            else:
                # Création
                maintenance = MaintenanceController.create_maintenance(maintenance_data)
                if maintenance:
                    QMessageBox.information(self, "Succès", "Maintenance créée avec succès!")
                    self.maintenance_saved.emit()
                    self.accept()
                else:
                    QMessageBox.warning(self, "Erreur", "Impossible de créer la maintenance")
                    
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement:\n{str(e)}")
