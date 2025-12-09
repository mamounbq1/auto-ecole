"""
Widget de gestion complète des maintenances véhicules
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, QLabel,
    QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from src.controllers import MaintenanceController, VehicleController
from src.models import MaintenanceType, MaintenanceStatus
from .maintenance_dialog import MaintenanceDialog
from datetime import datetime


class MaintenanceManagementWidget(QWidget):
    """Widget de gestion des maintenances avec CRUD complet"""
    
    maintenance_changed = Signal()  # Signal quand une maintenance change
    
    def __init__(self, vehicle_id=None, parent=None):
        super().__init__(parent)
        self.vehicle_id = vehicle_id  # Optionnel: filter par véhicule
        self.current_maintenances = []
        self.setup_ui()
        self.load_maintenances()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = self.create_header()
        layout.addLayout(header_layout)
        
        # Table des maintenances
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Véhicule", "Type", "Date Planifiée",
            "Statut", "Coût", "Fournisseur", "Créé le", "Actions"
        ])
        
        # Configuration
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.cellDoubleClicked.connect(self.edit_maintenance)
        
        layout.addWidget(self.table)
        
        # Footer
        footer = QLabel("Total: 0 maintenance(s)")
        footer.setObjectName("footerLabel")
        self.footer_label = footer
        layout.addWidget(footer)
    
    def create_header(self):
        """Créer le header"""
        layout = QHBoxLayout()
        
        # Bouton Nouvelle maintenance
        new_btn = QPushButton("🔧 Nouvelle Maintenance")
        new_btn.setStyleSheet("""
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
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.clicked.connect(self.create_maintenance)
        layout.addWidget(new_btn)
        
        # Recherche
        search_label = QLabel("🔍")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.textChanged.connect(self.filter_maintenances)
        layout.addWidget(search_label)
        layout.addWidget(self.search_input)
        
        # Filtre par type
        type_label = QLabel("Type:")
        self.type_filter = QComboBox()
        self.type_filter.addItem("Tous", None)
        for mtype in MaintenanceType:
            self.type_filter.addItem(mtype.value, mtype)
        self.type_filter.currentIndexChanged.connect(self.filter_maintenances)
        layout.addWidget(type_label)
        layout.addWidget(self.type_filter)
        
        # Filtre par statut
        status_label = QLabel("Statut:")
        self.status_filter = QComboBox()
        self.status_filter.addItem("Tous", None)
        for status in MaintenanceStatus:
            self.status_filter.addItem(status.value, status)
        self.status_filter.currentIndexChanged.connect(self.filter_maintenances)
        layout.addWidget(status_label)
        layout.addWidget(self.status_filter)
        
        # Bouton Rafraîchir
        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Rafraîchir")
        refresh_btn.clicked.connect(self.load_maintenances)
        layout.addWidget(refresh_btn)
        
        return layout
    
    def load_maintenances(self):
        """Charger les maintenances"""
        try:
            if self.vehicle_id:
                # Filtrer par véhicule
                maintenances = MaintenanceController.get_maintenances_by_vehicle(self.vehicle_id)
            else:
                # Toutes les maintenances
                maintenances = MaintenanceController.get_all_maintenances()
            
            self.current_maintenances = maintenances
            self.display_maintenances(maintenances)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement: {e}")
    
    def display_maintenances(self, maintenances):
        """Afficher les maintenances"""
        self.table.setRowCount(0)
        
        for row, maint in enumerate(maintenances):
            self.table.insertRow(row)
            
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(maint.id)))
            
            # Véhicule
            vehicle_text = "N/A"
            if maint.vehicle:
                vehicle_text = f"{maint.vehicle.plate_number} ({maint.vehicle.make})"
            self.table.setItem(row, 1, QTableWidgetItem(vehicle_text))
            
            # Type
            type_item = QTableWidgetItem(maint.maintenance_type.value)
            type_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.table.setItem(row, 2, type_item)
            
            # Date planifiée
            date_text = maint.scheduled_date.strftime("%d/%m/%Y") if maint.scheduled_date else "N/A"
            self.table.setItem(row, 3, QTableWidgetItem(date_text))
            
            # Statut
            status_item = QTableWidgetItem(maint.status.value)
            status_item.setForeground(self.get_status_color(maint.status))
            self.table.setItem(row, 4, status_item)
            
            # Coût
            cost = maint.actual_cost if maint.actual_cost else maint.estimated_cost
            cost_text = f"{cost:.2f} DH" if cost else "N/A"
            self.table.setItem(row, 5, QTableWidgetItem(cost_text))
            
            # Fournisseur
            provider = maint.provider if maint.provider else "N/A"
            self.table.setItem(row, 6, QTableWidgetItem(provider))
            
            # Créé le
            created_text = maint.created_at.strftime("%d/%m/%Y") if maint.created_at else ""
            self.table.setItem(row, 7, QTableWidgetItem(created_text))
            
            # Actions
            actions_widget = self.create_actions_widget(maint)
            self.table.setCellWidget(row, 8, actions_widget)
        
        # Ajuster colonnes
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        
        # Footer
        self.footer_label.setText(f"Total: {len(maintenances)} maintenance(s)")
    
    def create_actions_widget(self, maintenance):
        """Créer les boutons d'actions"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Bouton Éditer
        edit_btn = QPushButton("✏️")
        edit_btn.setToolTip("Modifier")
        edit_btn.setMaximumWidth(30)
        edit_btn.clicked.connect(lambda: self.edit_maintenance_by_id(maintenance.id))
        layout.addWidget(edit_btn)
        
        # Bouton Supprimer
        delete_btn = QPushButton("🗑️")
        delete_btn.setToolTip("Supprimer")
        delete_btn.setMaximumWidth(30)
        delete_btn.setStyleSheet("QPushButton { color: #e74c3c; }")
        delete_btn.clicked.connect(lambda: self.delete_maintenance(maintenance.id))
        layout.addWidget(delete_btn)
        
        return widget
    
    def get_status_color(self, status: MaintenanceStatus):
        """Obtenir la couleur selon le statut"""
        colors = {
            MaintenanceStatus.SCHEDULED: QColor("#f39c12"),
            MaintenanceStatus.IN_PROGRESS: QColor("#3498db"),
            MaintenanceStatus.COMPLETED: QColor("#27ae60"),
            MaintenanceStatus.CANCELLED: QColor("#95a5a6"),
        }
        return colors.get(status, QColor("#000000"))
    
    def filter_maintenances(self):
        """Filtrer les maintenances"""
        search_text = self.search_input.text().lower()
        mtype = self.type_filter.currentData()
        status = self.status_filter.currentData()
        
        filtered = self.current_maintenances
        
        # Filtre recherche
        if search_text:
            filtered = [
                m for m in filtered
                if (m.vehicle and search_text in m.vehicle.plate_number.lower()) or
                   (m.provider and search_text in m.provider.lower())
            ]
        
        # Filtre type
        if mtype:
            filtered = [m for m in filtered if m.maintenance_type == mtype]
        
        # Filtre statut
        if status:
            filtered = [m for m in filtered if m.status == status]
        
        self.display_maintenances(filtered)
    
    def create_maintenance(self):
        """Créer une nouvelle maintenance"""
        dialog = MaintenanceDialog(vehicle_id=self.vehicle_id, parent=self)
        dialog.maintenance_saved.connect(self.on_maintenance_saved)
        dialog.exec()
    
    def edit_maintenance(self, row, col):
        """Éditer une maintenance (double-clic)"""
        maint_id = int(self.table.item(row, 0).text())
        self.edit_maintenance_by_id(maint_id)
    
    def edit_maintenance_by_id(self, maint_id: int):
        """Éditer une maintenance par son ID"""
        try:
            maintenance = MaintenanceController.get_maintenance_by_id(maint_id)
            if maintenance:
                dialog = MaintenanceDialog(maintenance=maintenance, parent=self)
                dialog.maintenance_saved.connect(self.on_maintenance_saved)
                dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {e}")
    
    def delete_maintenance(self, maint_id: int):
        """Supprimer une maintenance"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer cette maintenance?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = MaintenanceController.delete_maintenance(maint_id)
                if success:
                    QMessageBox.information(self, "Succès", "Maintenance supprimée!")
                    self.load_maintenances()
                    self.maintenance_changed.emit()
                else:
                    QMessageBox.warning(self, "Erreur", "Impossible de supprimer")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur: {e}")
    
    def show_context_menu(self, position):
        """Menu contextuel"""
        row = self.table.rowAt(position.y())
        if row < 0:
            return
        
        maint_id = int(self.table.item(row, 0).text())
        maint = next((m for m in self.current_maintenances if m.id == maint_id), None)
        
        if not maint:
            return
        
        menu = QMenu(self)
        
        edit_action = menu.addAction("✏️ Modifier")
        menu.addSeparator()
        
        if maint.status == MaintenanceStatus.SCHEDULED:
            start_action = menu.addAction("▶️ Démarrer")
        
        if maint.status == MaintenanceStatus.IN_PROGRESS:
            complete_action = menu.addAction("✅ Terminer")
        
        cancel_action = menu.addAction("❌ Annuler")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Supprimer")
        delete_action.setStyleSheet("color: #e74c3c;")
        
        action = menu.exec(self.table.viewport().mapToGlobal(position))
        
        if action == edit_action:
            self.edit_maintenance_by_id(maint_id)
        elif action and action.text() == "▶️ Démarrer":
            self.start_maintenance(maint_id)
        elif action and action.text() == "✅ Terminer":
            self.complete_maintenance(maint_id)
        elif action == cancel_action:
            self.cancel_maintenance(maint_id)
        elif action == delete_action:
            self.delete_maintenance(maint_id)
    
    def start_maintenance(self, maint_id: int):
        """Démarrer une maintenance"""
        try:
            success = MaintenanceController.start_maintenance(maint_id)
            if success:
                QMessageBox.information(self, "Succès", "Maintenance démarrée!")
                self.load_maintenances()
                self.maintenance_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {e}")
    
    def complete_maintenance(self, maint_id: int):
        """Terminer une maintenance"""
        try:
            # Récupérer les infos de la maintenance
            maint = MaintenanceController.get_maintenance(maint_id)
            if not maint:
                return
            
            # Dialogue pour saisir coût final et pièces
            dialog = QDialog(self)
            dialog.setWindowTitle("🏁 Terminer la maintenance")
            dialog.setMinimumWidth(500)
            
            layout = QVBoxLayout(dialog)
            
            # Info maintenance
            info_label = QLabel(f"<b>Véhicule:</b> {maint.vehicle.immatriculation}<br>"
                              f"<b>Type:</b> {maint.maintenance_type.value}<br>"
                              f"<b>Coût estimé:</b> {maint.estimated_cost or 0:.2f} DH")
            layout.addWidget(info_label)
            
            # Coût final
            cost_group = QGroupBox("💰 Coût final")
            cost_layout = QFormLayout()
            cost_input = QDoubleSpinBox()
            cost_input.setRange(0, 999999)
            cost_input.setDecimals(2)
            cost_input.setSuffix(" DH")
            cost_input.setValue(maint.estimated_cost or 0)
            cost_layout.addRow("Coût final:", cost_input)
            cost_group.setLayout(cost_layout)
            layout.addWidget(cost_group)
            
            # Pièces remplacées
            parts_group = QGroupBox("🔧 Pièces remplacées")
            parts_layout = QVBoxLayout()
            parts_text = QTextEdit()
            parts_text.setPlaceholderText("Liste des pièces remplacées (une par ligne):\nEx: Plaquettes de frein x2\nFiltre à huile x1")
            parts_text.setMaximumHeight(100)
            parts_layout.addWidget(parts_text)
            parts_group.setLayout(parts_layout)
            layout.addWidget(parts_group)
            
            # Notes finales
            notes_group = QGroupBox("📝 Notes finales")
            notes_layout = QVBoxLayout()
            notes_text = QTextEdit()
            notes_text.setPlaceholderText("Notes sur l'intervention...")
            notes_text.setMaximumHeight(80)
            notes_layout.addWidget(notes_text)
            notes_group.setLayout(notes_layout)
            layout.addWidget(notes_group)
            
            # Boutons
            btn_layout = QHBoxLayout()
            btn_ok = QPushButton("✅ Terminer")
            btn_cancel = QPushButton("❌ Annuler")
            btn_ok.clicked.connect(dialog.accept)
            btn_cancel.clicked.connect(dialog.reject)
            btn_layout.addWidget(btn_ok)
            btn_layout.addWidget(btn_cancel)
            layout.addLayout(btn_layout)
            
            if dialog.exec() == QDialog.Accepted:
                # Mettre à jour avec les données finales
                success = MaintenanceController.update_maintenance(
                    maint_id,
                    actual_cost=cost_input.value(),
                    parts_replaced=parts_text.toPlainText(),
                    notes=(maint.notes or "") + "\n\nNotes finales:\n" + notes_text.toPlainText()
                )
                
                if success:
                    # Marquer comme terminée
                    success = MaintenanceController.complete_maintenance(maint_id)
                    if success:
                        QMessageBox.information(self, "✅ Succès", "Maintenance terminée avec succès!")
                        self.load_maintenances()
                        self.maintenance_changed.emit()
                        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {e}")
    
    def cancel_maintenance(self, maint_id: int):
        """Annuler une maintenance"""
        try:
            success = MaintenanceController.cancel_maintenance(maint_id)
            if success:
                QMessageBox.information(self, "Succès", "Maintenance annulée!")
                self.load_maintenances()
                self.maintenance_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {e}")
    
    def on_maintenance_saved(self):
        """Callback quand une maintenance est sauvegardée"""
        self.load_maintenances()
        self.maintenance_changed.emit()
