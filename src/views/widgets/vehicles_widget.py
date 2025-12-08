"""
Widget de gestion des véhicules avec maintenance et alertes
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
    QFileDialog, QGroupBox, QFrame
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from datetime import datetime, date, timedelta

from src.controllers.vehicle_controller import VehicleController
from src.controllers.session_controller import SessionController
from src.models import VehicleStatus
from src.utils import export_to_csv


class VehicleDialog(QDialog):
    """Dialogue de création/édition d'un véhicule"""
    
    def __init__(self, vehicle=None, parent=None):
        super().__init__(parent)
        self.vehicle = vehicle
        self.setWindowTitle("Détail Véhicule" if vehicle else "Nouveau Véhicule")
        self.setMinimumSize(700, 700)
        self.setup_ui()
        
        if vehicle:
            self.load_vehicle_data()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        
        # Informations du véhicule
        info_group = QGroupBox("🚗 Informations du Véhicule")
        info_layout = QFormLayout(info_group)
        
        self.plate_number = QLineEdit()
        self.plate_number.setPlaceholderText("Ex: 12345-A-67")
        
        self.make = QLineEdit()
        self.make.setPlaceholderText("Ex: Renault")
        
        self.model = QLineEdit()
        self.model.setPlaceholderText("Ex: Clio")
        
        self.year = QSpinBox()
        self.year.setMinimum(2000)
        self.year.setMaximum(2030)
        self.year.setValue(2020)
        
        self.color = QLineEdit()
        self.color.setPlaceholderText("Ex: Blanc")
        
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
        
        layout.addWidget(info_group)
        
        # Informations techniques
        tech_group = QGroupBox("⚙️ Informations Techniques")
        tech_layout = QFormLayout(tech_group)
        
        self.vin = QLineEdit()
        self.vin.setPlaceholderText("17 caractères")
        self.vin.setMaxLength(17)
        
        self.fuel_type = QComboBox()
        self.fuel_type.addItems(["Essence", "Diesel", "Électrique", "Hybride"])
        
        self.transmission = QComboBox()
        self.transmission.addItems(["Manuelle", "Automatique"])
        
        self.current_mileage = QSpinBox()
        self.current_mileage.setMinimum(0)
        self.current_mileage.setMaximum(999999)
        self.current_mileage.setSuffix(" km")
        
        self.last_oil_change_mileage = QSpinBox()
        self.last_oil_change_mileage.setMinimum(0)
        self.last_oil_change_mileage.setMaximum(999999)
        self.last_oil_change_mileage.setSuffix(" km")
        
        tech_layout.addRow("N° Châssis (VIN):", self.vin)
        tech_layout.addRow("Type de Carburant:", self.fuel_type)
        tech_layout.addRow("Transmission:", self.transmission)
        tech_layout.addRow("Kilométrage Actuel:", self.current_mileage)
        tech_layout.addRow("Dernier Changement Huile:", self.last_oil_change_mileage)
        
        layout.addWidget(tech_group)
        
        # Dates importantes
        dates_group = QGroupBox("📅 Dates Importantes")
        dates_layout = QFormLayout(dates_group)
        
        self.purchase_date = QDateEdit()
        self.purchase_date.setCalendarPopup(True)
        self.purchase_date.setDate(QDate.currentDate())
        
        self.registration_date = QDateEdit()
        self.registration_date.setCalendarPopup(True)
        self.registration_date.setDate(QDate.currentDate())
        
        self.last_maintenance_date = QDateEdit()
        self.last_maintenance_date.setCalendarPopup(True)
        self.last_maintenance_date.setDate(QDate.currentDate())
        
        self.next_maintenance_date = QDateEdit()
        self.next_maintenance_date.setCalendarPopup(True)
        self.next_maintenance_date.setDate(QDate.currentDate().addMonths(6))
        
        self.insurance_expiry_date = QDateEdit()
        self.insurance_expiry_date.setCalendarPopup(True)
        self.insurance_expiry_date.setDate(QDate.currentDate().addYears(1))
        
        self.technical_inspection_date = QDateEdit()
        self.technical_inspection_date.setCalendarPopup(True)
        self.technical_inspection_date.setDate(QDate.currentDate().addYears(1))
        
        dates_layout.addRow("Date d'Achat:", self.purchase_date)
        dates_layout.addRow("Date d'Immatriculation:", self.registration_date)
        dates_layout.addRow("Dernière Maintenance:", self.last_maintenance_date)
        dates_layout.addRow("Prochaine Maintenance:", self.next_maintenance_date)
        dates_layout.addRow("Expiration Assurance:", self.insurance_expiry_date)
        dates_layout.addRow("Contrôle Technique:", self.technical_inspection_date)
        
        layout.addWidget(dates_group)
        
        # Coûts
        costs_group = QGroupBox("💰 Coûts")
        costs_layout = QFormLayout(costs_group)
        
        self.purchase_price = QDoubleSpinBox()
        self.purchase_price.setMinimum(0)
        self.purchase_price.setMaximum(9999999)
        self.purchase_price.setSuffix(" DH")
        
        self.maintenance_cost = QDoubleSpinBox()
        self.maintenance_cost.setMinimum(0)
        self.maintenance_cost.setMaximum(9999999)
        self.maintenance_cost.setSuffix(" DH")
        
        self.insurance_cost = QDoubleSpinBox()
        self.insurance_cost.setMinimum(0)
        self.insurance_cost.setMaximum(999999)
        self.insurance_cost.setSuffix(" DH")
        
        costs_layout.addRow("Prix d'Achat:", self.purchase_price)
        costs_layout.addRow("Coût Maintenance:", self.maintenance_cost)
        costs_layout.addRow("Coût Assurance:", self.insurance_cost)
        
        layout.addWidget(costs_group)
        
        # Notes
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(60)
        self.notes.setPlaceholderText("Notes ou remarques...")
        layout.addWidget(QLabel("📝 Notes:"))
        layout.addWidget(self.notes)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.clicked.connect(self.save_vehicle)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
        """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def load_vehicle_data(self):
        """Charger les données du véhicule"""
        if not self.vehicle:
            return
        
        self.plate_number.setText(self.vehicle.plate_number)
        self.make.setText(self.vehicle.make or "")
        self.model.setText(self.vehicle.model or "")
        self.year.setValue(self.vehicle.year or 2020)
        self.color.setText(self.vehicle.color or "")
        self.license_type.setCurrentText(self.vehicle.license_type or "B")
        
        # Status
        for i in range(self.status.count()):
            if self.status.itemData(i) == self.vehicle.status:
                self.status.setCurrentIndex(i)
                break
        
        self.is_available.setChecked(self.vehicle.is_available)
        
        self.vin.setText(self.vehicle.vin or "")
        self.fuel_type.setCurrentText(self.vehicle.fuel_type or "Essence")
        self.transmission.setCurrentText(self.vehicle.transmission or "Manuelle")
        self.current_mileage.setValue(self.vehicle.current_mileage or 0)
        self.last_oil_change_mileage.setValue(self.vehicle.last_oil_change_mileage or 0)
        
        # Dates
        if self.vehicle.purchase_date:
            self.purchase_date.setDate(QDate(
                self.vehicle.purchase_date.year,
                self.vehicle.purchase_date.month,
                self.vehicle.purchase_date.day
            ))
        
        if self.vehicle.registration_date:
            self.registration_date.setDate(QDate(
                self.vehicle.registration_date.year,
                self.vehicle.registration_date.month,
                self.vehicle.registration_date.day
            ))
        
        if self.vehicle.last_maintenance_date:
            self.last_maintenance_date.setDate(QDate(
                self.vehicle.last_maintenance_date.year,
                self.vehicle.last_maintenance_date.month,
                self.vehicle.last_maintenance_date.day
            ))
        
        if self.vehicle.next_maintenance_date:
            self.next_maintenance_date.setDate(QDate(
                self.vehicle.next_maintenance_date.year,
                self.vehicle.next_maintenance_date.month,
                self.vehicle.next_maintenance_date.day
            ))
        
        if self.vehicle.insurance_expiry_date:
            self.insurance_expiry_date.setDate(QDate(
                self.vehicle.insurance_expiry_date.year,
                self.vehicle.insurance_expiry_date.month,
                self.vehicle.insurance_expiry_date.day
            ))
        
        if self.vehicle.technical_inspection_date:
            self.technical_inspection_date.setDate(QDate(
                self.vehicle.technical_inspection_date.year,
                self.vehicle.technical_inspection_date.month,
                self.vehicle.technical_inspection_date.day
            ))
        
        # Coûts
        self.purchase_price.setValue(self.vehicle.purchase_price or 0)
        self.maintenance_cost.setValue(self.vehicle.maintenance_cost or 0)
        self.insurance_cost.setValue(self.vehicle.insurance_cost or 0)
        
        self.notes.setPlainText(self.vehicle.notes or "")
    
    def save_vehicle(self):
        """Enregistrer le véhicule"""
        # Validation
        if not self.plate_number.text().strip():
            QMessageBox.warning(self, "Erreur", "La plaque d'immatriculation est requise")
            return
        
        if not self.make.text().strip():
            QMessageBox.warning(self, "Erreur", "La marque est requise")
            return
        
        if not self.model.text().strip():
            QMessageBox.warning(self, "Erreur", "Le modèle est requis")
            return
        
        # Collecter les données
        data = {
            'plate_number': self.plate_number.text().strip(),
            'make': self.make.text().strip(),
            'model': self.model.text().strip(),
            'year': self.year.value(),
            'color': self.color.text().strip() or None,
            'license_type': self.license_type.currentText(),
            'status': self.status.currentData(),
            'is_available': self.is_available.isChecked(),
            'vin': self.vin.text().strip() or None,
            'fuel_type': self.fuel_type.currentText(),
            'transmission': self.transmission.currentText(),
            'current_mileage': self.current_mileage.value(),
            'last_oil_change_mileage': self.last_oil_change_mileage.value(),
            'purchase_date': self.purchase_date.date().toPython(),
            'registration_date': self.registration_date.date().toPython(),
            'last_maintenance_date': self.last_maintenance_date.date().toPython(),
            'next_maintenance_date': self.next_maintenance_date.date().toPython(),
            'insurance_expiry_date': self.insurance_expiry_date.date().toPython(),
            'technical_inspection_date': self.technical_inspection_date.date().toPython(),
            'purchase_price': self.purchase_price.value(),
            'maintenance_cost': self.maintenance_cost.value(),
            'insurance_cost': self.insurance_cost.value(),
            'notes': self.notes.toPlainText().strip() or None,
        }
        
        try:
            if self.vehicle:
                # Mise à jour
                VehicleController.update_vehicle(self.vehicle.id, data)
                QMessageBox.information(self, "Succès", "Véhicule mis à jour avec succès")
            else:
                # Création
                VehicleController.create_vehicle(data)
                QMessageBox.information(self, "Succès", "Véhicule créé avec succès")
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement : {str(e)}")


class VehiclesWidget(QWidget):
    """Widget de gestion des véhicules"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.vehicles = []
        self.setup_ui()
        self.load_vehicles()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        self.create_header(layout)
        
        # Barre de recherche
        self.create_search_bar(layout)
        
        # Alertes
        self.create_alerts(layout)
        
        # Statistiques
        self.create_stats(layout)
        
        # Tableau
        self.create_table(layout)
    
    def create_header(self, layout):
        """Créer l'en-tête"""
        header_layout = QHBoxLayout()
        
        title = QLabel("🚗 Gestion des Véhicules")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Boutons
        add_btn = QPushButton("➕ Nouveau Véhicule")
        add_btn.clicked.connect(self.add_vehicle)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        add_btn.setCursor(Qt.PointingHandCursor)
        
        export_btn = QPushButton("📤 Exporter CSV")
        export_btn.clicked.connect(self.export_csv)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #1abc9c;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
        """)
        export_btn.setCursor(Qt.PointingHandCursor)
        
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.clicked.connect(self.load_vehicles)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        
        header_layout.addWidget(add_btn)
        header_layout.addWidget(export_btn)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
    
    def create_search_bar(self, layout):
        """Créer la barre de recherche"""
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par plaque, marque ou modèle...")
        self.search_input.textChanged.connect(self.apply_filters)
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        
        self.status_filter = QComboBox()
        self.status_filter.addItem("📊 Tous", None)
        for status in VehicleStatus:
            self.status_filter.addItem(status.value.capitalize(), status)
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        self.status_filter.setMinimumHeight(40)
        
        search_layout.addWidget(self.search_input, stretch=3)
        search_layout.addWidget(self.status_filter, stretch=1)
        
        layout.addLayout(search_layout)
    
    def create_alerts(self, layout):
        """Créer les alertes"""
        self.alerts_frame = QFrame()
        self.alerts_frame.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 2px solid #ffc107;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        self.alerts_layout = QVBoxLayout(self.alerts_frame)
        self.alerts_label = QLabel()
        self.alerts_label.setStyleSheet("color: #856404; font-weight: bold;")
        self.alerts_layout.addWidget(self.alerts_label)
        
        layout.addWidget(self.alerts_frame)
        self.alerts_frame.hide()  # Caché par défaut
    
    def create_stats(self, layout):
        """Créer les statistiques"""
        stats_layout = QHBoxLayout()
        
        self.total_label = QLabel("Total: 0")
        self.available_label = QLabel("Disponibles: 0")
        self.maintenance_label = QLabel("En Maintenance: 0")
        self.avg_mileage_label = QLabel("KM Moyen: 0")
        
        for label in [self.total_label, self.available_label, self.maintenance_label, self.avg_mileage_label]:
            label.setStyleSheet("""
                QLabel {
                    background-color: white;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                    color: #2c3e50;
                    border: 2px solid #ecf0f1;
                }
            """)
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.available_label)
        stats_layout.addWidget(self.maintenance_label)
        stats_layout.addWidget(self.avg_mileage_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
    
    def create_table(self, layout):
        """Créer le tableau"""
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Plaque", "Marque", "Modèle", "Type Permis",
            "Statut", "KM", "Proch. Maint.", "Assurance", "Actions"
        ])
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(400)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.table)
    
    def load_vehicles(self):
        """Charger tous les véhicules"""
        self.vehicles = VehicleController.get_all_vehicles()
        self.update_stats()
        self.check_alerts()
        self.populate_table()
    
    def update_stats(self):
        """Mettre à jour les statistiques"""
        total = len(self.vehicles)
        available = len([v for v in self.vehicles if v.is_available and v.status == VehicleStatus.AVAILABLE])
        maintenance = len([v for v in self.vehicles if v.status == VehicleStatus.MAINTENANCE])
        
        avg_mileage = sum(v.current_mileage or 0 for v in self.vehicles) / total if total > 0 else 0
        
        self.total_label.setText(f"Total: {total}")
        self.available_label.setText(f"Disponibles: {available}")
        self.maintenance_label.setText(f"En Maintenance: {maintenance}")
        self.avg_mileage_label.setText(f"KM Moyen: {avg_mileage:,.0f}")
    
    def check_alerts(self):
        """Vérifier les alertes"""
        alerts = []
        today = date.today()
        
        for vehicle in self.vehicles:
            # Assurance expirée ou expire bientôt
            if vehicle.insurance_expiry_date:
                days_until = (vehicle.insurance_expiry_date - today).days
                if days_until < 0:
                    alerts.append(f"⚠️ {vehicle.plate_number} - Assurance expirée!")
                elif days_until <= 30:
                    alerts.append(f"⚠️ {vehicle.plate_number} - Assurance expire dans {days_until} jours")
            
            # Contrôle technique
            if vehicle.technical_inspection_date:
                days_until = (vehicle.technical_inspection_date - today).days
                if days_until < 0:
                    alerts.append(f"⚠️ {vehicle.plate_number} - Contrôle technique expiré!")
                elif days_until <= 30:
                    alerts.append(f"⚠️ {vehicle.plate_number} - Contrôle technique dans {days_until} jours")
            
            # Maintenance
            if vehicle.next_maintenance_date:
                days_until = (vehicle.next_maintenance_date - today).days
                if days_until <= 7:
                    alerts.append(f"🔧 {vehicle.plate_number} - Maintenance prévue dans {days_until} jours")
        
        if alerts:
            self.alerts_label.setText("\n".join(alerts[:5]))  # Max 5 alertes
            self.alerts_frame.show()
        else:
            self.alerts_frame.hide()
    
    def apply_filters(self):
        """Appliquer les filtres"""
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentData()
        
        filtered = []
        
        for vehicle in self.vehicles:
            # Filtre texte
            if search_text:
                if not (search_text in vehicle.plate_number.lower() or
                       search_text in vehicle.make.lower() or
                       search_text in vehicle.model.lower()):
                    continue
            
            # Filtre statut
            if status_filter and vehicle.status != status_filter:
                continue
            
            filtered.append(vehicle)
        
        self.populate_table(filtered)
    
    def populate_table(self, vehicles=None):
        """Remplir le tableau"""
        if vehicles is None:
            vehicles = self.vehicles
        
        self.table.setRowCount(0)
        
        for row, vehicle in enumerate(vehicles):
            self.table.insertRow(row)
            
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(vehicle.id)))
            
            # Plaque
            self.table.setItem(row, 1, QTableWidgetItem(vehicle.plate_number))
            
            # Marque
            self.table.setItem(row, 2, QTableWidgetItem(vehicle.make))
            
            # Modèle
            self.table.setItem(row, 3, QTableWidgetItem(vehicle.model))
            
            # Type de permis
            self.table.setItem(row, 4, QTableWidgetItem(vehicle.license_type or "B"))
            
            # Statut
            status_item = QTableWidgetItem(vehicle.status.value.capitalize() if vehicle.status else "N/A")
            if vehicle.status == VehicleStatus.AVAILABLE:
                status_item.setForeground(QColor("#27ae60"))
            elif vehicle.status == VehicleStatus.MAINTENANCE:
                status_item.setForeground(QColor("#f39c12"))
            elif vehicle.status == VehicleStatus.OUT_OF_SERVICE:
                status_item.setForeground(QColor("#e74c3c"))
            self.table.setItem(row, 5, status_item)
            
            # Kilométrage
            self.table.setItem(row, 6, QTableWidgetItem(f"{vehicle.current_mileage or 0:,}"))
            
            # Prochaine maintenance
            maint_text = vehicle.next_maintenance_date.strftime('%d/%m/%Y') if vehicle.next_maintenance_date else "N/A"
            self.table.setItem(row, 7, QTableWidgetItem(maint_text))
            
            # Assurance
            insurance_text = vehicle.insurance_expiry_date.strftime('%d/%m/%Y') if vehicle.insurance_expiry_date else "N/A"
            insurance_item = QTableWidgetItem(insurance_text)
            
            # Colorer si expire bientôt
            if vehicle.insurance_expiry_date:
                days_until = (vehicle.insurance_expiry_date - date.today()).days
                if days_until < 0:
                    insurance_item.setForeground(QColor("#e74c3c"))
                elif days_until <= 30:
                    insurance_item.setForeground(QColor("#f39c12"))
            
            self.table.setItem(row, 8, insurance_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 0, 5, 0)
            
            view_btn = QPushButton("👁️")
            view_btn.setToolTip("Voir détails")
            view_btn.clicked.connect(lambda checked, v=vehicle: self.view_vehicle(v))
            view_btn.setCursor(Qt.PointingHandCursor)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Modifier")
            edit_btn.clicked.connect(lambda checked, v=vehicle: self.edit_vehicle(v))
            edit_btn.setCursor(Qt.PointingHandCursor)
            
            maint_btn = QPushButton("🔧")
            maint_btn.setToolTip("Historique maintenance")
            maint_btn.clicked.connect(lambda checked, v=vehicle: self.view_maintenance(v))
            maint_btn.setCursor(Qt.PointingHandCursor)
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(maint_btn)
            
            self.table.setCellWidget(row, 9, actions_widget)
    
    def add_vehicle(self):
        """Ajouter un véhicule"""
        dialog = VehicleDialog(parent=self)
        if dialog.exec():
            self.load_vehicles()
    
    def edit_vehicle(self, vehicle):
        """Modifier un véhicule"""
        dialog = VehicleDialog(vehicle, parent=self)
        if dialog.exec():
            self.load_vehicles()
    
    def view_vehicle(self, vehicle):
        """Voir les détails d'un véhicule"""
        info = f"""
        <h3>{vehicle.make} {vehicle.model}</h3>
        <p><b>Plaque:</b> {vehicle.plate_number}</p>
        <p><b>Année:</b> {vehicle.year or 'N/A'}</p>
        <p><b>Couleur:</b> {vehicle.color or 'N/A'}</p>
        <p><b>Type de Permis:</b> {vehicle.license_type}</p>
        <p><b>Statut:</b> {vehicle.status.value}</p>
        <p><b>Carburant:</b> {vehicle.fuel_type}</p>
        <p><b>Transmission:</b> {vehicle.transmission}</p>
        <p><b>Kilométrage:</b> {vehicle.current_mileage:,} km</p>
        <p><b>Sessions:</b> {vehicle.total_sessions or 0}</p>
        <p><b>Heures Utilisées:</b> {vehicle.total_hours_used or 0}h</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Détail Véhicule")
        msg.setTextFormat(Qt.RichText)
        msg.setText(info)
        msg.exec()
    
    def view_maintenance(self, vehicle):
        """Voir l'historique de maintenance"""
        info = f"""
        <h3>🔧 Maintenance - {vehicle.plate_number}</h3>
        <hr>
        <p><b>Dernière Maintenance:</b> {vehicle.last_maintenance_date.strftime('%d/%m/%Y') if vehicle.last_maintenance_date else 'N/A'}</p>
        <p><b>Prochaine Maintenance:</b> {vehicle.next_maintenance_date.strftime('%d/%m/%Y') if vehicle.next_maintenance_date else 'N/A'}</p>
        <p><b>Dernier Changement Huile:</b> {vehicle.last_oil_change_mileage:,} km</p>
        <p><b>KM Actuel:</b> {vehicle.current_mileage:,} km</p>
        <hr>
        <p><b>Coût Maintenance Total:</b> {vehicle.maintenance_cost:,.2f} DH</p>
        <p><b>Assurance (Expiration):</b> {vehicle.insurance_expiry_date.strftime('%d/%m/%Y') if vehicle.insurance_expiry_date else 'N/A'}</p>
        <p><b>Contrôle Technique:</b> {vehicle.technical_inspection_date.strftime('%d/%m/%Y') if vehicle.technical_inspection_date else 'N/A'}</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Historique Maintenance")
        msg.setTextFormat(Qt.RichText)
        msg.setText(info)
        msg.exec()
    
    def export_csv(self):
        """Exporter en CSV"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exporter les véhicules",
                f"exports/vehicules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if filename:
                success, result = export_to_csv(self.vehicles, filename, 'vehicles')
                
                if success:
                    QMessageBox.information(self, "Succès", f"Export réussi: {result}")
                else:
                    QMessageBox.warning(self, "Erreur", result)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
