"""
Module: Gestion des véhicules
Version: 1.0.0 - Créé le 2025-12-08

Description:
    Interface moderne de gestion des véhicules avec:
    - Tableau avec tous les véhicules
    - Recherche et filtres avancés
    - Dialogue d'ajout/édition complet
    - Export CSV
    - Actions rapides (modifier, supprimer)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
    QGroupBox, QFrame
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont, QColor
from datetime import datetime, date

from src.controllers.vehicle_controller import VehicleController
from src.models import VehicleStatus, get_session, Vehicle
from src.utils import export_to_csv


class VehicleDialog(QDialog):
    """Dialogue moderne d'ajout/édition de véhicule"""
    
    saved = Signal()
    
    def __init__(self, vehicle=None, parent=None):
        super().__init__(parent)
        self.vehicle = vehicle
        self.setWindowTitle("✏️ Modifier Véhicule" if vehicle else "➕ Nouveau Véhicule")
        self.setMinimumSize(700, 750)
        self.setup_ui()
        
        if vehicle:
            self.load_vehicle_data()
    
    def setup_ui(self):
        """Configuration de l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Scroll pour les grands formulaires
        from PySide6.QtWidgets import QScrollArea
from functools import partial
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)
        
        # === GROUPE 1: Informations de base ===
        info_group = self.create_group("🚗 Informations du Véhicule")
        info_layout = QFormLayout()
        
        self.plate_number = QLineEdit()
        self.plate_number.setPlaceholderText("Ex: 12345-A-67")
        
        self.make = QLineEdit()
        self.make.setPlaceholderText("Ex: Renault, Peugeot, Dacia...")
        
        self.model = QLineEdit()
        self.model.setPlaceholderText("Ex: Clio, 208, Logan...")
        
        self.year = QSpinBox()
        self.year.setMinimum(2000)
        self.year.setMaximum(2030)
        self.year.setValue(datetime.now().year)
        
        self.color = QLineEdit()
        self.color.setPlaceholderText("Ex: Blanc, Noir, Gris...")
        
        self.license_type = QComboBox()
        self.license_type.addItems(["A", "B", "C", "D"])
        self.license_type.setCurrentText("B")
        
        self.status = QComboBox()
        for status in VehicleStatus:
            self.status.addItem(status.value, status)
        
        self.is_available = QCheckBox("Disponible pour les sessions")
        self.is_available.setChecked(True)
        
        info_layout.addRow("Plaque d'Immatriculation*:", self.plate_number)
        info_layout.addRow("Marque*:", self.make)
        info_layout.addRow("Modèle*:", self.model)
        info_layout.addRow("Année:", self.year)
        info_layout.addRow("Couleur:", self.color)
        info_layout.addRow("Type de Permis:", self.license_type)
        info_layout.addRow("Statut:", self.status)
        info_layout.addRow("", self.is_available)
        
        info_group.setLayout(info_layout)
        container_layout.addWidget(info_group)
        
        # === GROUPE 2: Informations Techniques ===
        tech_group = self.create_group("⚙️ Informations Techniques")
        tech_layout = QFormLayout()
        
        self.vin = QLineEdit()
        self.vin.setPlaceholderText("Numéro de châssis (17 caractères)")
        self.vin.setMaxLength(17)
        
        self.fuel_type = QComboBox()
        self.fuel_type.addItems(["Essence", "Diesel", "Électrique", "Hybride"])
        
        self.transmission = QComboBox()
        self.transmission.addItems(["Manuelle", "Automatique"])
        
        self.current_mileage = QSpinBox()
        self.current_mileage.setMinimum(0)
        self.current_mileage.setMaximum(999999)
        self.current_mileage.setSuffix(" km")
        
        self.last_oil_change = QSpinBox()
        self.last_oil_change.setMinimum(0)
        self.last_oil_change.setMaximum(999999)
        self.last_oil_change.setSuffix(" km")
        
        tech_layout.addRow("N° Châssis (VIN):", self.vin)
        tech_layout.addRow("Type de Carburant:", self.fuel_type)
        tech_layout.addRow("Transmission:", self.transmission)
        tech_layout.addRow("Kilométrage Actuel:", self.current_mileage)
        tech_layout.addRow("Dernier Changement d'Huile:", self.last_oil_change)
        
        tech_group.setLayout(tech_layout)
        container_layout.addWidget(tech_group)
        
        # === GROUPE 3: Dates et Validités ===
        dates_group = self.create_group("📅 Dates Importantes")
        dates_layout = QFormLayout()
        
        self.purchase_date = QDateEdit()
        self.purchase_date.setCalendarPopup(True)
        self.purchase_date.setDate(QDate.currentDate())
        
        self.insurance_expiry = QDateEdit()
        self.insurance_expiry.setCalendarPopup(True)
        self.insurance_expiry.setDate(QDate.currentDate().addYears(1))
        
        self.technical_inspection = QDateEdit()
        self.technical_inspection.setCalendarPopup(True)
        self.technical_inspection.setDate(QDate.currentDate().addYears(1))
        
        self.last_maintenance = QDateEdit()
        self.last_maintenance.setCalendarPopup(True)
        self.last_maintenance.setDate(QDate.currentDate())
        
        self.next_maintenance = QDateEdit()
        self.next_maintenance.setCalendarPopup(True)
        self.next_maintenance.setDate(QDate.currentDate().addMonths(6))
        
        dates_layout.addRow("Date d'Achat:", self.purchase_date)
        dates_layout.addRow("Expiration Assurance:", self.insurance_expiry)
        dates_layout.addRow("Contrôle Technique:", self.technical_inspection)
        dates_layout.addRow("Dernière Maintenance:", self.last_maintenance)
        dates_layout.addRow("Prochaine Maintenance:", self.next_maintenance)
        
        dates_group.setLayout(dates_layout)
        container_layout.addWidget(dates_group)
        
        # === GROUPE 4: Coûts ===
        costs_group = self.create_group("💰 Coûts et Finances")
        costs_layout = QFormLayout()
        
        self.purchase_price = QDoubleSpinBox()
        self.purchase_price.setMinimum(0)
        self.purchase_price.setMaximum(9999999)
        self.purchase_price.setSuffix(" DH")
        self.purchase_price.setDecimals(2)
        
        self.insurance_cost = QDoubleSpinBox()
        self.insurance_cost.setMinimum(0)
        self.insurance_cost.setMaximum(999999)
        self.insurance_cost.setSuffix(" DH")
        self.insurance_cost.setDecimals(2)
        
        self.maintenance_cost = QDoubleSpinBox()
        self.maintenance_cost.setMinimum(0)
        self.maintenance_cost.setMaximum(9999999)
        self.maintenance_cost.setSuffix(" DH")
        self.maintenance_cost.setDecimals(2)
        
        costs_layout.addRow("Prix d'Achat:", self.purchase_price)
        costs_layout.addRow("Coût Assurance Annuel:", self.insurance_cost)
        costs_layout.addRow("Coût Maintenance Total:", self.maintenance_cost)
        
        costs_group.setLayout(costs_layout)
        container_layout.addWidget(costs_group)
        
        # === Notes ===
        notes_label = QLabel("📝 Notes:")
        notes_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        container_layout.addWidget(notes_label)
        
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(80)
        self.notes.setPlaceholderText("Notes ou remarques supplémentaires...")
        container_layout.addWidget(self.notes)
        
        container_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # === Boutons ===
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                padding: 12px 30px;
                border-radius: 8px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
        """)
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.clicked.connect(self.save_vehicle)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                padding: 12px 30px;
                border-radius: 8px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def create_group(self, title):
        """Créer un groupe stylisé"""
        group = QGroupBox(title)
        group.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2196F3;
            }
        """)
        return group
    
    def load_vehicle_data(self):
        """Charger les données du véhicule à éditer"""
        if not self.vehicle:
            return
        
        # Informations de base
        self.plate_number.setText(self.vehicle.plate_number or "")
        self.make.setText(self.vehicle.make or "")
        self.model.setText(self.vehicle.model or "")
        self.year.setValue(self.vehicle.year or datetime.now().year)
        self.color.setText(self.vehicle.color or "")
        self.license_type.setCurrentText(self.vehicle.license_type or "B")
        
        # Status
        for i in range(self.status.count()):
            if self.status.itemData(i) == self.vehicle.status:
                self.status.setCurrentIndex(i)
                break
        
        self.is_available.setChecked(self.vehicle.is_available)
        
        # Informations techniques
        self.vin.setText(self.vehicle.vin or "")
        self.fuel_type.setCurrentText(self.vehicle.fuel_type or "Essence")
        self.transmission.setCurrentText(self.vehicle.transmission or "Manuelle")
        self.current_mileage.setValue(self.vehicle.current_mileage or 0)
        self.last_oil_change.setValue(self.vehicle.last_oil_change_mileage or 0)
        
        # Dates
        if self.vehicle.purchase_date:
            self.purchase_date.setDate(QDate(
                self.vehicle.purchase_date.year,
                self.vehicle.purchase_date.month,
                self.vehicle.purchase_date.day
            ))
        
        if self.vehicle.insurance_expiry_date:
            self.insurance_expiry.setDate(QDate(
                self.vehicle.insurance_expiry_date.year,
                self.vehicle.insurance_expiry_date.month,
                self.vehicle.insurance_expiry_date.day
            ))
        
        if self.vehicle.technical_inspection_date:
            self.technical_inspection.setDate(QDate(
                self.vehicle.technical_inspection_date.year,
                self.vehicle.technical_inspection_date.month,
                self.vehicle.technical_inspection_date.day
            ))
        
        if self.vehicle.last_maintenance_date:
            self.last_maintenance.setDate(QDate(
                self.vehicle.last_maintenance_date.year,
                self.vehicle.last_maintenance_date.month,
                self.vehicle.last_maintenance_date.day
            ))
        
        if self.vehicle.next_maintenance_date:
            self.next_maintenance.setDate(QDate(
                self.vehicle.next_maintenance_date.year,
                self.vehicle.next_maintenance_date.month,
                self.vehicle.next_maintenance_date.day
            ))
        
        # Coûts
        self.purchase_price.setValue(self.vehicle.purchase_price or 0)
        self.insurance_cost.setValue(self.vehicle.insurance_cost or 0)
        self.maintenance_cost.setValue(self.vehicle.maintenance_cost or 0)
        
        # Notes
        self.notes.setPlainText(self.vehicle.notes or "")
    
    def save_vehicle(self):
        """Enregistrer le véhicule"""
        # Validation
        if not self.plate_number.text().strip():
            QMessageBox.warning(self, "Erreur", "La plaque d'immatriculation est obligatoire")
            return
        
        if not self.make.text().strip():
            QMessageBox.warning(self, "Erreur", "La marque est obligatoire")
            return
        
        if not self.model.text().strip():
            QMessageBox.warning(self, "Erreur", "Le modèle est obligatoire")
            return
        
        try:
            session = get_session()
            
            if self.vehicle:
                # Mise à jour
                vehicle = session.query(Vehicle).filter_by(id=self.vehicle.id).first()
                if not vehicle:
                    QMessageBox.critical(self, "Erreur", "Véhicule introuvable")
                    return
            else:
                # Création
                vehicle = Vehicle()
            
            # Remplir les données
            vehicle.plate_number = self.plate_number.text().strip()
            vehicle.make = self.make.text().strip()
            vehicle.model = self.model.text().strip()
            vehicle.year = self.year.value()
            vehicle.color = self.color.text().strip() or None
            vehicle.license_type = self.license_type.currentText()
            vehicle.status = self.status.currentData()
            vehicle.is_available = self.is_available.isChecked()
            
            vehicle.vin = self.vin.text().strip() or None
            vehicle.fuel_type = self.fuel_type.currentText()
            vehicle.transmission = self.transmission.currentText()
            vehicle.current_mileage = self.current_mileage.value()
            vehicle.last_oil_change_mileage = self.last_oil_change.value()
            
            vehicle.purchase_date = self.purchase_date.date().toPython()
            vehicle.insurance_expiry_date = self.insurance_expiry.date().toPython()
            vehicle.technical_inspection_date = self.technical_inspection.date().toPython()
            vehicle.last_maintenance_date = self.last_maintenance.date().toPython()
            vehicle.next_maintenance_date = self.next_maintenance.date().toPython()
            
            vehicle.purchase_price = self.purchase_price.value()
            vehicle.insurance_cost = self.insurance_cost.value()
            vehicle.maintenance_cost = self.maintenance_cost.value()
            
            vehicle.notes = self.notes.toPlainText().strip() or None
            
            if not self.vehicle:
                session.add(vehicle)
            
            session.commit()
            
            QMessageBox.information(
                self,
                "Succès",
                f"Véhicule {'modifié' if self.vehicle else 'ajouté'} avec succès"
            )
            
            self.saved.emit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement: {str(e)}")


class VehiclesManagement(QWidget):
    """Widget de gestion des véhicules avec tableau et actions"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_vehicles()
    
    def setup_ui(self):
        """Configuration de l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        header = QHBoxLayout()
        
        title = QLabel("🚗 GESTION DES VÉHICULES")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a1a1a;")
        header.addWidget(title)
        
        header.addStretch()
        
        # Bouton ajouter
        add_btn = QPushButton("➕ Nouveau Véhicule")
        add_btn.clicked.connect(self.add_vehicle)
        add_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        header.addWidget(add_btn)
        
        layout.addLayout(header)
        
        # Barre de recherche et filtres
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par plaque, marque, modèle...")
        self.search_input.textChanged.connect(self.filter_table)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 11pt;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        search_layout.addWidget(self.search_input, 2)
        
        # Filtre statut
        self.status_filter = QComboBox()
        self.status_filter.addItem("Tous les statuts", None)
        for status in VehicleStatus:
            self.status_filter.addItem(status.value, status)
        self.status_filter.currentIndexChanged.connect(self.filter_table)
        self.status_filter.setStyleSheet("""
            QComboBox {
                padding: 10px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 11pt;
                background: white;
                min-width: 150px;
            }
        """)
        search_layout.addWidget(self.status_filter)
        
        # Filtre disponibilité
        self.availability_filter = QComboBox()
        self.availability_filter.addItems([
            "Toutes disponibilités",
            "Disponibles uniquement",
            "Non disponibles"
        ])
        self.availability_filter.currentIndexChanged.connect(self.filter_table)
        self.availability_filter.setStyleSheet("""
            QComboBox {
                padding: 10px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 11pt;
                background: white;
                min-width: 150px;
            }
        """)
        search_layout.addWidget(self.availability_filter)
        
        # Bouton export
        export_btn = QPushButton("📥 Export CSV")
        export_btn.clicked.connect(self.export_vehicles)
        export_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)
        search_layout.addWidget(export_btn)
        
        # Bouton rafraîchir
        refresh_btn = QPushButton("🔄")
        refresh_btn.clicked.connect(self.load_vehicles)
        refresh_btn.setFixedSize(45, 45)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                border-radius: 8px;
                font-size: 14pt;
                border: none;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
        """)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Plaque", "Marque", "Modèle", "Année", "Permis",
            "Statut", "Disponible", "Kilométrage", "Heures", "Actions"
        ])
        
        # Style du tableau (comme Moniteurs)
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #dfe6e9;
                border-radius: 8px;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item { padding: 5px; }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(45)
        self.table.verticalHeader().setVisible(False)
        
        # Colonnes redimensionnables
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(9, 160)
        
        layout.addWidget(self.table)
        
        # Compteur
        self.count_label = QLabel()
        self.count_label.setFont(QFont("Segoe UI", 10))
        self.count_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.count_label)
    
    def load_vehicles(self):
        """Charger tous les véhicules"""
        self.all_vehicles = VehicleController.get_all_vehicles()
        self.filter_table()
    
    def filter_table(self):
        """Filtrer et afficher les véhicules"""
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentData()
        availability_text = self.availability_filter.currentText()
        
        # Filtrer les véhicules
        filtered = self.all_vehicles
        
        if search_text:
            filtered = [
                v for v in filtered
                if search_text in v.plate_number.lower()
                or search_text in (v.make or '').lower()
                or search_text in (v.model or '').lower()
            ]
        
        if status_filter:
            filtered = [v for v in filtered if v.status == status_filter]
        
        if availability_text == "Disponibles uniquement":
            filtered = [v for v in filtered if v.is_available]
        elif availability_text == "Non disponibles":
            filtered = [v for v in filtered if not v.is_available]
        
        # Remplir le tableau
        self.table.setRowCount(len(filtered))
        
        for row, vehicle in enumerate(filtered):
            # Plaque
            self.table.setItem(row, 0, QTableWidgetItem(vehicle.plate_number))
            
            # Marque
            self.table.setItem(row, 1, QTableWidgetItem(vehicle.make or ""))
            
            # Modèle
            self.table.setItem(row, 2, QTableWidgetItem(vehicle.model or ""))
            
            # Année
            self.table.setItem(row, 3, QTableWidgetItem(str(vehicle.year or "")))
            
            # Permis
            self.table.setItem(row, 4, QTableWidgetItem(vehicle.license_type or ""))
            
            # Statut
            status_item = QTableWidgetItem(vehicle.status.value)
            status_colors = {
                VehicleStatus.AVAILABLE: QColor("#4CAF50"),
                VehicleStatus.IN_SERVICE: QColor("#2196F3"),
                VehicleStatus.MAINTENANCE: QColor("#FF9800"),
                VehicleStatus.OUT_OF_SERVICE: QColor("#F44336")
            }
            status_item.setForeground(status_colors.get(vehicle.status, QColor("#666")))
            self.table.setItem(row, 5, status_item)
            
            # Disponible
            avail_item = QTableWidgetItem("✅" if vehicle.is_available else "❌")
            avail_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 6, avail_item)
            
            # Kilométrage
            km_item = QTableWidgetItem(f"{vehicle.current_mileage or 0:,} km")
            km_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 7, km_item)
            
            # Heures d'utilisation
            hours_item = QTableWidgetItem(f"{vehicle.total_hours_used or 0:.1f}h")
            hours_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 8, hours_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(5)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(30, 30)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #2196F3;
                    color: white;
                    border-radius: 5px;
                    font-size: 12pt;
                    border: none;
                }
                QPushButton:hover {
                    background: #1976D2;
                }
            """)
            edit_btn.clicked.connect(partial(self.edit_vehicle, vehicle))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedSize(30, 30)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: #F44336;
                    color: white;
                    border-radius: 5px;
                    font-size: 12pt;
                    border: none;
                }
                QPushButton:hover {
                    background: #D32F2F;
                }
            """)
            delete_btn.clicked.connect(partial(self.delete_vehicle, vehicle))
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 9, actions_widget)
        
        # Mettre à jour le compteur
        total = len(self.all_vehicles)
        showing = len(filtered)
        self.count_label.setText(f"Affichage de {showing} véhicule(s) sur {total} au total")
    
    def add_vehicle(self):
        """Ajouter un nouveau véhicule"""
        dialog = VehicleDialog(parent=self)
        dialog.saved.connect(self.load_vehicles)
        dialog.exec()
    
    def edit_vehicle(self, vehicle):
        """Modifier un véhicule"""
        dialog = VehicleDialog(vehicle=vehicle, parent=self)
        dialog.saved.connect(self.load_vehicles)
        dialog.exec()
    
    def delete_vehicle(self, vehicle):
        """Supprimer un véhicule"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer le véhicule {vehicle.plate_number} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                session = get_session()
                v = session.query(Vehicle).filter_by(id=vehicle.id).first()
                if v:
                    session.delete(v)
                    session.commit()
                    QMessageBox.information(self, "Succès", "Véhicule supprimé avec succès")
                    self.load_vehicles()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def export_vehicles(self):
        """Exporter les véhicules en CSV"""
        if not self.all_vehicles:
            QMessageBox.warning(self, "Avertissement", "Aucun véhicule à exporter")
            return
        
        data = []
        for v in self.all_vehicles:
            data.append({
                'Plaque': v.plate_number,
                'Marque': v.make or '',
                'Modèle': v.model or '',
                'Année': v.year or '',
                'Couleur': v.color or '',
                'Permis': v.license_type or '',
                'Statut': v.status.value,
                'Disponible': 'Oui' if v.is_available else 'Non',
                'Kilométrage': v.current_mileage or 0,
                'Heures Utilisées': v.total_hours_used or 0,
                'Sessions': v.total_sessions or 0,
                'VIN': v.vin or '',
                'Carburant': v.fuel_type or '',
                'Transmission': v.transmission or ''
            })
        
        filename = f"vehicules_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        try:
            export_to_csv(data, filename)
            QMessageBox.information(
                self,
                "Succès",
                f"Export réussi!\nFichier: {filename}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export: {str(e)}")
