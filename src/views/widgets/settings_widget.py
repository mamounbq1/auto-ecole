"""
Module Paramètres - Interface complète de configuration
Permet de modifier toutes les informations du centre et paramètres
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QTabWidget, QGroupBox,
                              QScrollArea, QFileDialog, QMessageBox, QComboBox,
                              QCheckBox, QSpinBox, QTextEdit, QTableWidget,
                              QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
                              QGridLayout, QFrame, QApplication)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont
import json
import shutil
from pathlib import Path
from datetime import datetime


class SettingsWidget(QWidget):
    """Widget principal des paramètres avec onglets"""
    
    settings_changed = Signal()  # Signal émis quand les paramètres changent
    
    def __init__(self):
        super().__init__()
        self.config_path = Path("config.json")
        self.config = self.load_config()
        self.init_ui()
        
    def load_config(self):
        """Charge la configuration depuis config.json"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur de chargement config: {e}")
            return {}
    
    def save_config(self):
        """Sauvegarde la configuration dans config.json"""
        try:
            # Backup avant sauvegarde
            backup_path = self.config_path.with_suffix('.json.bak')
            if self.config_path.exists():
                shutil.copy(self.config_path, backup_path)
            
            # Sauvegarde
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            self.settings_changed.emit()
            QMessageBox.information(self, "Succès", "✅ Configuration sauvegardée avec succès!")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"❌ Erreur de sauvegarde: {e}")
            return False
    
    def init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # En-tête
        header = self.create_header()
        layout.addWidget(header)
        
        # Onglets principaux
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
            }
            QTabBar::tab {
                background: #f5f5f5;
                padding: 12px 24px;
                margin-right: 2px;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
                color: #666;
            }
            QTabBar::tab:selected {
                background: white;
                color: #2196F3;
                border-bottom: 3px solid #2196F3;
            }
            QTabBar::tab:hover {
                background: #e3f2fd;
            }
        """)
        
        # Onglet 1: Informations du Centre
        tabs.addTab(self.create_center_info_tab(), "🏢 Informations du Centre")
        
        # Onglet 2: Paramètres Généraux
        tabs.addTab(self.create_general_settings_tab(), "⚙️ Paramètres Généraux")
        
        # Onglet 3: Formats et Affichage
        tabs.addTab(self.create_formats_tab(), "📋 Formats et Affichage")
        
        # Onglet 4: Sauvegarde et Données
        tabs.addTab(self.create_backup_tab(), "💾 Sauvegarde et Données")
        
        layout.addWidget(tabs)
        
    def create_header(self):
        """Crée l'en-tête du module"""
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background: #2196F3;
                border-radius: 0px;
            }
            QLabel {
                color: white;
                background: transparent;
            }
        """)
        header.setFixedHeight(70)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Icône et titre
        title = QLabel("⚙️ Paramètres")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        layout.addWidget(title)
        layout.addStretch()
        
        # Bouton Sauvegarder
        btn_save = QPushButton("💾 Sauvegarder")
        btn_save.setStyleSheet("""
            QPushButton {
                background: white;
                color: #2196F3;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #f0f0f0;
            }
        """)
        btn_save.clicked.connect(self.save_all_settings)
        layout.addWidget(btn_save)
        
        return header
    
    def create_center_info_tab(self):
        """Onglet: Informations du Centre"""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Groupe: Informations principales
        group_main = QGroupBox("🏢 Centre")
        group_main.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2196F3;
            }
        """)
        
        form_main = QFormLayout(group_main)
        form_main.setSpacing(10)
        form_main.setContentsMargins(15, 20, 15, 15)
        form_main.setLabelAlignment(Qt.AlignRight)
        
        # Initialiser la section 'center' si elle n'existe pas
        if 'center' not in self.config:
            self.config['center'] = {}
        
        # Champs d'information
        self.input_center_name = QLineEdit(self.config['center'].get('name', ''))
        self.input_center_name.setPlaceholderText("Ex: Auto-École Excellence")
        
        self.input_center_address = QTextEdit()
        self.input_center_address.setPlainText(self.config['center'].get('address', ''))
        self.input_center_address.setPlaceholderText("Adresse complète du centre...")
        self.input_center_address.setMaximumHeight(80)
        
        self.input_center_city = QLineEdit(self.config['center'].get('city', ''))
        self.input_center_city.setPlaceholderText("Ex: Casablanca")
        
        self.input_center_postal = QLineEdit(self.config['center'].get('postal_code', ''))
        self.input_center_postal.setPlaceholderText("Ex: 20000")
        
        self.input_center_phone = QLineEdit(self.config['center'].get('phone', ''))
        self.input_center_phone.setPlaceholderText("Ex: +212 5XX-XXXXXX")
        
        self.input_center_email = QLineEdit(self.config['center'].get('email', ''))
        self.input_center_email.setPlaceholderText("Ex: contact@autoecole.ma")
        
        self.input_center_website = QLineEdit(self.config['center'].get('website', ''))
        self.input_center_website.setPlaceholderText("Ex: www.autoecole.ma")
        
        # Style des inputs
        input_style = """
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
                background: white;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #2196F3;
                background: #f8f9fa;
            }
        """
        for widget_input in [self.input_center_name, self.input_center_address, 
                            self.input_center_city, self.input_center_postal,
                            self.input_center_phone, self.input_center_email, 
                            self.input_center_website]:
            widget_input.setStyleSheet(input_style)
        
        form_main.addRow("Nom du Centre:", self.input_center_name)
        form_main.addRow("Adresse:", self.input_center_address)
        form_main.addRow("Ville:", self.input_center_city)
        form_main.addRow("Code Postal:", self.input_center_postal)
        form_main.addRow("Téléphone:", self.input_center_phone)
        form_main.addRow("Email:", self.input_center_email)
        form_main.addRow("Site Web:", self.input_center_website)
        
        layout.addWidget(group_main)
        
        # Groupe: Informations légales
        group_legal = QGroupBox("📜 Légal")
        group_legal.setStyleSheet(group_main.styleSheet())
        
        form_legal = QFormLayout(group_legal)
        form_legal.setSpacing(10)
        form_legal.setContentsMargins(15, 20, 15, 15)
        form_legal.setLabelAlignment(Qt.AlignRight)
        
        self.input_center_siret = QLineEdit(self.config['center'].get('siret', ''))
        self.input_center_siret.setPlaceholderText("Numéro SIRET/ICE")
        
        self.input_center_tva = QLineEdit(self.config['center'].get('tva_number', ''))
        self.input_center_tva.setPlaceholderText("Numéro de TVA")
        
        self.input_center_license = QLineEdit(self.config['center'].get('license_number', ''))
        self.input_center_license.setPlaceholderText("Numéro d'agrément")
        
        self.input_center_director = QLineEdit(self.config['center'].get('director_name', ''))
        self.input_center_director.setPlaceholderText("Nom du directeur")
        
        for widget_input in [self.input_center_siret, self.input_center_tva, 
                            self.input_center_license, self.input_center_director]:
            widget_input.setStyleSheet(input_style)
        
        form_legal.addRow("N° SIRET/ICE:", self.input_center_siret)
        form_legal.addRow("N° TVA:", self.input_center_tva)
        form_legal.addRow("N° Agrément:", self.input_center_license)
        form_legal.addRow("Directeur:", self.input_center_director)
        
        layout.addWidget(group_legal)
        
        # Groupe: Logo du centre
        group_logo = QGroupBox("🖼️ Logo")
        group_logo.setStyleSheet(group_main.styleSheet())
        
        logo_layout = QVBoxLayout(group_logo)
        logo_layout.setContentsMargins(15, 20, 15, 15)
        logo_layout.setSpacing(10)
        
        # Affichage du logo actuel
        self.logo_label = QLabel("Aucun logo défini")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("""
            QLabel {
                border: 1px dashed #ccc;
                border-radius: 6px;
                padding: 15px;
                background: #fafafa;
            }
        """)
        self.logo_label.setMinimumHeight(120)
        self.logo_label.setMaximumHeight(120)
        
        # Charger le logo si existant
        logo_path = self.config.get('pdf', {}).get('company_logo')
        if logo_path and Path(logo_path).exists():
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                self.logo_label.setPixmap(pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        logo_layout.addWidget(self.logo_label)
        
        # Boutons pour le logo
        logo_buttons = QHBoxLayout()
        
        btn_choose_logo = QPushButton("📁 Choisir un logo")
        btn_choose_logo.clicked.connect(self.choose_logo)
        
        btn_remove_logo = QPushButton("🗑️ Supprimer")
        btn_remove_logo.clicked.connect(self.remove_logo)
        
        btn_style = """
            QPushButton {
                padding: 7px 15px;
                border: none;
                border-radius: 4px;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                opacity: 0.85;
            }
        """
        
        btn_choose_logo.setStyleSheet(btn_style + """
            QPushButton {
                background: #2196F3;
                color: white;
            }
        """)
        
        btn_remove_logo.setStyleSheet(btn_style + """
            QPushButton {
                background: #f44336;
                color: white;
            }
        """)
        
        logo_buttons.addWidget(btn_choose_logo)
        logo_buttons.addWidget(btn_remove_logo)
        logo_buttons.addStretch()
        
        logo_layout.addLayout(logo_buttons)
        
        layout.addWidget(group_logo)
        layout.addStretch()
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(scroll)
        
        return container
    
    def create_general_settings_tab(self):
        """Onglet: Paramètres Généraux"""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Groupe: Application
        group_app = QGroupBox("📱 Application")
        group_app.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2196F3;
            }
        """)
        
        form_app = QFormLayout(group_app)
        form_app.setSpacing(10)
        form_app.setContentsMargins(15, 20, 15, 15)
        form_app.setLabelAlignment(Qt.AlignRight)
        
        self.input_app_name = QLineEdit(self.config.get('app', {}).get('name', ''))
        self.input_app_version = QLineEdit(self.config.get('app', {}).get('version', ''))
        
        self.combo_language = QComboBox()
        self.combo_language.addItems(['Français', 'English', 'العربية'])
        current_lang = self.config.get('app', {}).get('language', 'fr')
        lang_map = {'fr': 0, 'en': 1, 'ar': 2}
        self.combo_language.setCurrentIndex(lang_map.get(current_lang, 0))
        
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(['Clair', 'Sombre', 'Auto'])
        theme_map = {'light': 0, 'dark': 1, 'auto': 2}
        current_theme = self.config.get('app', {}).get('theme', 'light')
        self.combo_theme.setCurrentIndex(theme_map.get(current_theme, 0))
        
        input_style = """
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
                background: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #2196F3;
                background: #f8f9fa;
            }
        """
        
        for widget_input in [self.input_app_name, self.input_app_version, 
                            self.combo_language, self.combo_theme]:
            widget_input.setStyleSheet(input_style)
        
        form_app.addRow("Nom de l'application:", self.input_app_name)
        form_app.addRow("Version:", self.input_app_version)
        form_app.addRow("Langue:", self.combo_language)
        form_app.addRow("Thème:", self.combo_theme)
        
        layout.addWidget(group_app)
        
        # Groupe: Horaires
        group_hours = QGroupBox("🕐 Horaires")
        group_hours.setStyleSheet(group_app.styleSheet())
        
        form_hours = QFormLayout(group_hours)
        form_hours.setSpacing(10)
        form_hours.setContentsMargins(15, 20, 15, 15)
        form_hours.setLabelAlignment(Qt.AlignRight)
        
        self.input_start_time = QLineEdit(self.config.get('working_hours', {}).get('start', '08:00'))
        self.input_end_time = QLineEdit(self.config.get('working_hours', {}).get('end', '18:00'))
        self.input_session_duration = QSpinBox()
        self.input_session_duration.setRange(15, 180)
        self.input_session_duration.setSuffix(" minutes")
        self.input_session_duration.setValue(self.config.get('working_hours', {}).get('session_duration', 60))
        
        for widget_input in [self.input_start_time, self.input_end_time, self.input_session_duration]:
            widget_input.setStyleSheet(input_style)
        
        form_hours.addRow("Heure d'ouverture:", self.input_start_time)
        form_hours.addRow("Heure de fermeture:", self.input_end_time)
        form_hours.addRow("Durée session par défaut:", self.input_session_duration)
        
        layout.addWidget(group_hours)
        
        # Groupe: Base de données
        group_db = QGroupBox("💾 Base de Données")
        group_db.setStyleSheet(group_app.styleSheet())
        
        form_db = QFormLayout(group_db)
        form_db.setSpacing(10)
        form_db.setContentsMargins(15, 20, 15, 15)
        form_db.setLabelAlignment(Qt.AlignRight)
        
        self.input_db_path = QLineEdit(self.config.get('database', {}).get('path', ''))
        self.check_backup_start = QCheckBox("Sauvegarde automatique au démarrage")
        self.check_backup_start.setChecked(self.config.get('database', {}).get('backup_on_start', True))
        
        self.input_backup_interval = QSpinBox()
        self.input_backup_interval.setRange(300, 86400)
        self.input_backup_interval.setSuffix(" secondes")
        self.input_backup_interval.setValue(self.config.get('database', {}).get('auto_backup_interval', 3600))
        
        for widget_input in [self.input_db_path, self.input_backup_interval]:
            widget_input.setStyleSheet(input_style)
        
        form_db.addRow("Chemin de la BD:", self.input_db_path)
        form_db.addRow("", self.check_backup_start)
        form_db.addRow("Intervalle de sauvegarde:", self.input_backup_interval)
        
        layout.addWidget(group_db)
        layout.addStretch()
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(scroll)
        
        return container
    
    def create_formats_tab(self):
        """Onglet: Formats et Affichage"""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Groupe: Formats
        group_formats = QGroupBox("📋 Formats")
        group_formats.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2196F3;
            }
        """)
        
        form_formats = QFormLayout(group_formats)
        form_formats.setSpacing(10)
        form_formats.setContentsMargins(15, 20, 15, 15)
        form_formats.setLabelAlignment(Qt.AlignRight)
        
        self.combo_date_format = QComboBox()
        self.combo_date_format.addItems(['DD/MM/YYYY', 'MM/DD/YYYY', 'YYYY-MM-DD'])
        current_date = self.config.get('formats', {}).get('date', 'DD/MM/YYYY')
        self.combo_date_format.setCurrentText(current_date)
        
        self.combo_time_format = QComboBox()
        self.combo_time_format.addItems(['HH:mm', 'HH:mm:ss', 'hh:mm A'])
        current_time = self.config.get('formats', {}).get('time', 'HH:mm')
        self.combo_time_format.setCurrentText(current_time)
        
        self.input_currency = QLineEdit(self.config.get('formats', {}).get('currency', 'DH'))
        
        self.input_decimal_places = QSpinBox()
        self.input_decimal_places.setRange(0, 4)
        self.input_decimal_places.setValue(self.config.get('formats', {}).get('decimal_places', 2))
        
        input_style = """
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
                background: white;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #2196F3;
                background: #f8f9fa;
            }
        """
        
        for widget_input in [self.combo_date_format, self.combo_time_format, 
                            self.input_currency, self.input_decimal_places]:
            widget_input.setStyleSheet(input_style)
        
        form_formats.addRow("Format de date:", self.combo_date_format)
        form_formats.addRow("Format d'heure:", self.combo_time_format)
        form_formats.addRow("Symbole monétaire:", self.input_currency)
        form_formats.addRow("Décimales:", self.input_decimal_places)
        
        layout.addWidget(group_formats)
        
        # Groupe: PDF
        group_pdf = QGroupBox("📄 PDF")
        group_pdf.setStyleSheet(group_formats.styleSheet())
        
        form_pdf = QFormLayout(group_pdf)
        form_pdf.setSpacing(10)
        form_pdf.setContentsMargins(15, 20, 15, 15)
        form_pdf.setLabelAlignment(Qt.AlignRight)
        
        self.combo_page_size = QComboBox()
        self.combo_page_size.addItems(['A4', 'Letter', 'A5'])
        current_page = self.config.get('pdf', {}).get('page_size', 'A4')
        self.combo_page_size.setCurrentText(current_page)
        
        self.check_auto_print = QCheckBox("Imprimer automatiquement après génération")
        self.check_auto_print.setChecked(self.config.get('pdf', {}).get('auto_print', False))
        
        self.combo_page_size.setStyleSheet(input_style)
        
        form_pdf.addRow("Taille de page:", self.combo_page_size)
        form_pdf.addRow("", self.check_auto_print)
        
        layout.addWidget(group_pdf)
        
        # Groupe: Rapports
        group_reports = QGroupBox("📊 Rapports")
        group_reports.setStyleSheet(group_formats.styleSheet())
        
        form_reports = QFormLayout(group_reports)
        form_reports.setSpacing(10)
        form_reports.setContentsMargins(15, 20, 15, 15)
        form_reports.setLabelAlignment(Qt.AlignRight)
        
        self.input_fiscal_year = QLineEdit(self.config.get('reports', {}).get('fiscal_year_start', '01-01'))
        self.input_fiscal_year.setPlaceholderText("MM-DD")
        
        self.input_default_currency = QLineEdit(self.config.get('reports', {}).get('default_currency', 'MAD'))
        
        for widget_input in [self.input_fiscal_year, self.input_default_currency]:
            widget_input.setStyleSheet(input_style)
        
        form_reports.addRow("Début année fiscale:", self.input_fiscal_year)
        form_reports.addRow("Devise par défaut:", self.input_default_currency)
        
        layout.addWidget(group_reports)
        layout.addStretch()
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(scroll)
        
        return container
    
    def create_backup_tab(self):
        """Onglet: Sauvegarde et Données - Organisation en grille"""
        widget = QWidget()
        widget.setStyleSheet("background: #f5f5f5;")
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Grille de cards
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Style pour les cards
        card_style = """
            QFrame {
                background: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            QFrame:hover {
                border: 1px solid #2196F3;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
        """
        
        # Card 1: Créer sauvegarde
        card1 = self._create_action_card(
            "💾",
            "Créer Sauvegarde",
            "Créer une copie de sécurité de toutes vos données",
            "#4CAF50",
            self.create_backup
        )
        grid.addWidget(card1, 0, 0)
        
        # Card 2: Restaurer
        card2 = self._create_action_card(
            "📥",
            "Restaurer",
            "Restaurer depuis une sauvegarde existante",
            "#FF9800",
            self.restore_backup
        )
        grid.addWidget(card2, 0, 1)
        
        # Card 3: Dossier sauvegardes
        card3 = self._create_action_card(
            "📁",
            "Dossier",
            "Ouvrir le dossier contenant les sauvegardes",
            "#2196F3",
            self.open_backup_folder
        )
        grid.addWidget(card3, 0, 2)
        
        # Card 4: Exporter CSV
        card4 = self._create_action_card(
            "📤",
            "Exporter CSV",
            "Exporter toutes les données en format CSV",
            "#9C27B0",
            self.export_all_data
        )
        grid.addWidget(card4, 1, 0)
        
        # Card 5: Optimiser BD
        card5 = self._create_action_card(
            "⚡",
            "Optimiser",
            "Optimiser et nettoyer la base de données",
            "#00BCD4",
            self.optimize_database
        )
        grid.addWidget(card5, 1, 1)
        
        # Card 6: Synchroniser
        card6 = self._create_action_card(
            "🔄",
            "Synchroniser",
            "Synchroniser tous les statuts automatiquement",
            "#FF9800",
            self.sync_all_statuses
        )
        grid.addWidget(card6, 1, 2)
        
        layout.addLayout(grid)
        
        # Section danger
        danger_section = QFrame()
        danger_section.setStyleSheet("""
            QFrame {
                background: #ffebee;
                border-radius: 8px;
                border: 2px solid #f44336;
            }
        """)
        danger_layout = QHBoxLayout(danger_section)
        danger_layout.setContentsMargins(20, 15, 20, 15)
        danger_layout.setSpacing(15)
        
        # Icône et texte
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        danger_title = QLabel("⚠️ Zone Dangereuse")
        danger_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #f44336;")
        text_layout.addWidget(danger_title)
        
        danger_desc = QLabel("Actions irréversibles - Sauvegardez avant de continuer")
        danger_desc.setStyleSheet("font-size: 10px; color: #666;")
        text_layout.addWidget(danger_desc)
        
        danger_layout.addLayout(text_layout)
        danger_layout.addStretch()
        
        btn_reset = QPushButton("🔄 Réinitialiser Configuration")
        btn_reset.setFixedWidth(200)
        btn_reset.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #d32f2f;
            }
        """)
        btn_reset.clicked.connect(self.reset_config)
        danger_layout.addWidget(btn_reset)
        
        layout.addWidget(danger_section)
        
        # Info footer
        info = QLabel("💡 Conseil: Sauvegardez régulièrement vos données et testez vos restaurations.")
        info.setStyleSheet("""
            QLabel {
                background: #e3f2fd;
                padding: 10px;
                border-radius: 6px;
                color: #1976D2;
                font-size: 11px;
            }
        """)
        info.setWordWrap(True)
        layout.addWidget(info)
        
        layout.addStretch()
        
        return widget
    
    def _create_action_card(self, icon, title, description, color, callback):
        """Crée une card d'action cliquable"""
        card = QFrame()
        card.setFixedHeight(180)
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 8px;
                border: 2px solid #e0e0e0;
            }}
            QFrame:hover {{
                border: 2px solid {color};
                background: #fafafa;
            }}
        """)
        card.setCursor(Qt.PointingHandCursor)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(8)
        
        # Icône
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 40px;")
        icon_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(icon_label)
        
        # Titre
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {color};")
        title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 10px; color: #777;")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setFixedHeight(30)
        card_layout.addWidget(desc_label)
        
        # Bouton
        btn = QPushButton("Exécuter")
        btn.setFixedHeight(32)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: {self._darken_color(color)};
            }}
        """)
        btn.clicked.connect(callback)
        card_layout.addWidget(btn)
        
        return card
    
    def _darken_color(self, hex_color):
        """Assombrit une couleur hexadécimale de 10%"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * 0.85))
        g = max(0, int(g * 0.85))
        b = max(0, int(b * 0.85))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def choose_logo(self):
        """Permet de choisir un fichier logo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir le logo du centre",
            "",
            "Images (*.png *.jpg *.jpeg *.svg)"
        )
        
        if file_path:
            # Copier le logo dans le dossier resources
            resources_dir = Path("src/resources")
            resources_dir.mkdir(parents=True, exist_ok=True)
            
            logo_dest = resources_dir / f"logo{Path(file_path).suffix}"
            shutil.copy(file_path, logo_dest)
            
            # Mettre à jour la config
            if 'pdf' not in self.config:
                self.config['pdf'] = {}
            self.config['pdf']['company_logo'] = str(logo_dest)
            
            # Afficher le logo
            pixmap = QPixmap(str(logo_dest))
            if not pixmap.isNull():
                self.logo_label.setPixmap(pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            QMessageBox.information(self, "Succès", "✅ Logo mis à jour avec succès!")
    
    def remove_logo(self):
        """Supprime le logo actuel"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer le logo du centre?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if 'pdf' not in self.config:
                self.config['pdf'] = {}
            self.config['pdf']['company_logo'] = None
            
            self.logo_label.clear()
            self.logo_label.setText("Aucun logo défini")
            
            QMessageBox.information(self, "Succès", "✅ Logo supprimé!")
    
    def save_all_settings(self):
        """Sauvegarde tous les paramètres"""
        try:
            # Informations du centre
            if 'center' not in self.config:
                self.config['center'] = {}
            
            self.config['center']['name'] = self.input_center_name.text()
            self.config['center']['address'] = self.input_center_address.toPlainText()
            self.config['center']['city'] = self.input_center_city.text()
            self.config['center']['postal_code'] = self.input_center_postal.text()
            self.config['center']['phone'] = self.input_center_phone.text()
            self.config['center']['email'] = self.input_center_email.text()
            self.config['center']['website'] = self.input_center_website.text()
            self.config['center']['siret'] = self.input_center_siret.text()
            self.config['center']['tva_number'] = self.input_center_tva.text()
            self.config['center']['license_number'] = self.input_center_license.text()
            self.config['center']['director_name'] = self.input_center_director.text()
            
            # Application
            if 'app' not in self.config:
                self.config['app'] = {}
            self.config['app']['name'] = self.input_app_name.text()
            self.config['app']['version'] = self.input_app_version.text()
            
            lang_reverse_map = {0: 'fr', 1: 'en', 2: 'ar'}
            self.config['app']['language'] = lang_reverse_map.get(self.combo_language.currentIndex(), 'fr')
            
            theme_reverse_map = {0: 'light', 1: 'dark', 2: 'auto'}
            self.config['app']['theme'] = theme_reverse_map.get(self.combo_theme.currentIndex(), 'light')
            
            # Horaires
            if 'working_hours' not in self.config:
                self.config['working_hours'] = {}
            self.config['working_hours']['start'] = self.input_start_time.text()
            self.config['working_hours']['end'] = self.input_end_time.text()
            self.config['working_hours']['session_duration'] = self.input_session_duration.value()
            
            # Base de données
            if 'database' not in self.config:
                self.config['database'] = {}
            self.config['database']['path'] = self.input_db_path.text()
            self.config['database']['backup_on_start'] = self.check_backup_start.isChecked()
            self.config['database']['auto_backup_interval'] = self.input_backup_interval.value()
            
            # Formats
            if 'formats' not in self.config:
                self.config['formats'] = {}
            self.config['formats']['date'] = self.combo_date_format.currentText()
            self.config['formats']['time'] = self.combo_time_format.currentText()
            self.config['formats']['currency'] = self.input_currency.text()
            self.config['formats']['decimal_places'] = self.input_decimal_places.value()
            
            # PDF
            if 'pdf' not in self.config:
                self.config['pdf'] = {}
            self.config['pdf']['page_size'] = self.combo_page_size.currentText()
            self.config['pdf']['auto_print'] = self.check_auto_print.isChecked()
            
            # Rapports
            if 'reports' not in self.config:
                self.config['reports'] = {}
            self.config['reports']['fiscal_year_start'] = self.input_fiscal_year.text()
            self.config['reports']['default_currency'] = self.input_default_currency.text()
            
            # Sauvegarder
            self.save_config()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"❌ Erreur lors de la sauvegarde: {e}")
    
    def create_backup(self):
        """Crée une sauvegarde de la base de données"""
        try:
            db_path = Path(self.config.get('database', {}).get('path', 'data/autoecole.db'))
            if not db_path.exists():
                QMessageBox.warning(self, "Attention", "❌ Base de données introuvable!")
                return
            
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"backup_{timestamp}.db"
            
            shutil.copy(db_path, backup_path)
            
            QMessageBox.information(self, "Succès", f"✅ Sauvegarde créée:\n{backup_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"❌ Erreur lors de la sauvegarde: {e}")
    
    def restore_backup(self):
        """Restaure une sauvegarde"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir une sauvegarde à restaurer",
            "backups",
            "Base de données (*.db)"
        )
        
        if file_path:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "⚠️ La restauration va remplacer toutes les données actuelles!\n\nÊtes-vous sûr de vouloir continuer?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    db_path = Path(self.config.get('database', {}).get('path', 'data/autoecole.db'))
                    shutil.copy(file_path, db_path)
                    
                    QMessageBox.information(
                        self,
                        "Succès",
                        "✅ Restauration effectuée avec succès!\n\n⚠️ Veuillez redémarrer l'application."
                    )
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"❌ Erreur lors de la restauration: {e}")
    
    def open_backup_folder(self):
        """Ouvre le dossier des sauvegardes"""
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        import os
        import subprocess
        
        if os.name == 'nt':  # Windows
            os.startfile(str(backup_dir.absolute()))
        elif os.name == 'posix':  # macOS et Linux
            subprocess.Popen(['xdg-open', str(backup_dir.absolute())])
    
    def export_all_data(self):
        """Exporte toutes les données en CSV"""
        QMessageBox.information(
            self,
            "Export",
            "📤 Fonctionnalité d'export global en cours de développement.\n\n" +
            "Utilisez les exports CSV de chaque module en attendant."
        )
    
    def optimize_database(self):
        """Optimise la base de données"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous optimiser la base de données?\n\nCela peut prendre quelques minutes.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                from src.models import get_session
                
                # Afficher progression
                progress = QMessageBox(self)
                progress.setWindowTitle("Optimisation en cours...")
                progress.setText("Optimisation de la base de données...\nVeuillez patienter.")
                progress.setStandardButtons(QMessageBox.NoButton)
                progress.show()
                QApplication.processEvents()
                
                # Exécuter VACUUM et ANALYZE
                session = get_session()
                engine = session.get_bind()
                
                # VACUUM pour compacter et défragmenter
                with engine.connect() as conn:
                    conn.execute("VACUUM")
                    conn.execute("ANALYZE")
                    conn.commit()
                
                progress.close()
                
                QMessageBox.information(
                    self,
                    "✅ Succès",
                    "Base de données optimisée avec succès!\n\n"
                    "Les opérations VACUUM et ANALYZE ont été exécutées."
                )
                
            except Exception as e:
                progress.close()
                QMessageBox.critical(
                    self,
                    "❌ Erreur",
                    f"Erreur lors de l'optimisation:\n{str(e)}"
                )
    
    def sync_all_statuses(self):
        """Synchroniser tous les statuts de l'application"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Synchroniser tous les statuts?\n\n" +
            "Cette action va mettre à jour automatiquement les statuts basés sur les données actuelles:\n" +
            "• Étudiants (basé sur progression)\n" +
            "• Véhicules (basé sur maintenances)\n" +
            "• Séances (basé sur dates passées)\n" +
            "• Documents (basé sur dates d'expiration)",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                from src.utils.sync_manager import SyncManager
                
                # Afficher progression
                progress = QMessageBox(self)
                progress.setWindowTitle("Synchronisation en cours...")
                progress.setText("Synchronisation des statuts en cours...\nVeuillez patienter.")
                progress.setStandardButtons(QMessageBox.NoButton)
                progress.show()
                QApplication.processEvents()
                
                # Exécuter synchronisation
                results = SyncManager.sync_all()
                report = SyncManager.get_sync_report(results)
                
                progress.close()
                
                QMessageBox.information(
                    self,
                    "✅ Synchronisation terminée",
                    report
                )
                
            except Exception as e:
                progress.close()
                QMessageBox.critical(
                    self,
                    "❌ Erreur",
                    f"Erreur lors de la synchronisation:\n{str(e)}"
                )
    
    def reset_config(self):
        """Réinitialise la configuration"""
        reply = QMessageBox.question(
            self,
            "⚠️ Confirmation",
            "Êtes-vous ABSOLUMENT SÛR de vouloir réinitialiser la configuration?\n\n" +
            "Cette action est IRRÉVERSIBLE et supprimera tous vos paramètres personnalisés.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Double confirmation
            reply2 = QMessageBox.question(
                self,
                "⚠️ Dernière confirmation",
                "Dernière chance pour annuler!\n\nRéinitialiser VRAIMENT la configuration?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply2 == QMessageBox.Yes:
                # TODO: Implémenter la réinitialisation complète
                QMessageBox.information(
                    self,
                    "Information",
                    "❌ Fonctionnalité désactivée pour éviter les erreurs.\n\n" +
                    "Supprimez manuellement le fichier config.json si nécessaire."
                )
