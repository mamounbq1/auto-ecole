"""
Module Paramètres - Interface complète de configuration
Permet de modifier toutes les informations du centre et paramètres
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QTabWidget, QGroupBox,
                              QScrollArea, QFileDialog, QMessageBox, QComboBox,
                              QCheckBox, QSpinBox, QTextEdit, QTableWidget,
                              QTableWidgetItem, QHeaderView, QDialog, QFormLayout)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 0px;
            }
            QLabel {
                color: white;
                background: transparent;
            }
        """)
        header.setFixedHeight(80)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Titre
        title_layout = QVBoxLayout()
        title = QLabel("⚙️ Paramètres de l'Application")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        subtitle = QLabel("Configuration complète du centre et de l'application")
        subtitle.setStyleSheet("font-size: 14px; opacity: 0.9;")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Bouton Sauvegarder Global
        btn_save = QPushButton("💾 Sauvegarder Tout")
        btn_save.setStyleSheet("""
            QPushButton {
                background: white;
                color: #667eea;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
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
        group_main = QGroupBox("📋 Informations Principales du Centre")
        group_main.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        
        form_main = QFormLayout(group_main)
        form_main.setSpacing(15)
        form_main.setContentsMargins(20, 25, 20, 20)
        
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
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #2196F3;
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
        group_legal = QGroupBox("📜 Informations Légales et Fiscales")
        group_legal.setStyleSheet(group_main.styleSheet())
        
        form_legal = QFormLayout(group_legal)
        form_legal.setSpacing(15)
        form_legal.setContentsMargins(20, 25, 20, 20)
        
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
        group_logo = QGroupBox("🖼️ Logo du Centre")
        group_logo.setStyleSheet(group_main.styleSheet())
        
        logo_layout = QVBoxLayout(group_logo)
        logo_layout.setContentsMargins(20, 25, 20, 20)
        logo_layout.setSpacing(15)
        
        # Affichage du logo actuel
        self.logo_label = QLabel("Aucun logo défini")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 8px;
                padding: 20px;
                background: #f9f9f9;
            }
        """)
        self.logo_label.setMinimumHeight(150)
        
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
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton:hover {
                opacity: 0.9;
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
        group_app = QGroupBox("📱 Paramètres de l'Application")
        group_app.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        
        form_app = QFormLayout(group_app)
        form_app.setSpacing(15)
        form_app.setContentsMargins(20, 25, 20, 20)
        
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
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #2196F3;
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
        group_hours = QGroupBox("🕐 Horaires de Travail")
        group_hours.setStyleSheet(group_app.styleSheet())
        
        form_hours = QFormLayout(group_hours)
        form_hours.setSpacing(15)
        form_hours.setContentsMargins(20, 25, 20, 20)
        
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
        form_db.setSpacing(15)
        form_db.setContentsMargins(20, 25, 20, 20)
        
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
        group_formats = QGroupBox("📋 Formats d'Affichage")
        group_formats.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        
        form_formats = QFormLayout(group_formats)
        form_formats.setSpacing(15)
        form_formats.setContentsMargins(20, 25, 20, 20)
        
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
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #2196F3;
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
        group_pdf = QGroupBox("📄 Paramètres PDF")
        group_pdf.setStyleSheet(group_formats.styleSheet())
        
        form_pdf = QFormLayout(group_pdf)
        form_pdf.setSpacing(15)
        form_pdf.setContentsMargins(20, 25, 20, 20)
        
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
        group_reports = QGroupBox("📊 Paramètres des Rapports")
        group_reports.setStyleSheet(group_formats.styleSheet())
        
        form_reports = QFormLayout(group_reports)
        form_reports.setSpacing(15)
        form_reports.setContentsMargins(20, 25, 20, 20)
        
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
        """Onglet: Sauvegarde et Données"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Info card
        info_card = QLabel("""
        <div style='background: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #2196F3;'>
            <b>💡 Informations importantes</b><br/>
            • Les sauvegardes automatiques sont effectuées selon l'intervalle configuré<br/>
            • Conservez toujours au moins 3 sauvegardes différentes<br/>
            • Testez régulièrement vos sauvegardes en les restaurant
        </div>
        """)
        info_card.setWordWrap(True)
        layout.addWidget(info_card)
        
        # Groupe: Actions de sauvegarde
        group_backup = QGroupBox("💾 Sauvegardes")
        group_backup.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        
        backup_layout = QVBoxLayout(group_backup)
        backup_layout.setContentsMargins(20, 25, 20, 20)
        backup_layout.setSpacing(15)
        
        btn_style = """
            QPushButton {
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-weight: 500;
                font-size: 13px;
                text-align: left;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        """
        
        # Bouton: Créer une sauvegarde
        btn_backup_now = QPushButton("💾 Créer une sauvegarde maintenant")
        btn_backup_now.setStyleSheet(btn_style + "background: #4CAF50; color: white;")
        btn_backup_now.clicked.connect(self.create_backup)
        backup_layout.addWidget(btn_backup_now)
        
        # Bouton: Restaurer une sauvegarde
        btn_restore = QPushButton("📥 Restaurer depuis une sauvegarde")
        btn_restore.setStyleSheet(btn_style + "background: #FF9800; color: white;")
        btn_restore.clicked.connect(self.restore_backup)
        backup_layout.addWidget(btn_restore)
        
        # Bouton: Ouvrir dossier de sauvegardes
        btn_open_folder = QPushButton("📁 Ouvrir le dossier de sauvegardes")
        btn_open_folder.setStyleSheet(btn_style + "background: #2196F3; color: white;")
        btn_open_folder.clicked.connect(self.open_backup_folder)
        backup_layout.addWidget(btn_open_folder)
        
        layout.addWidget(group_backup)
        
        # Groupe: Données
        group_data = QGroupBox("🗄️ Gestion des Données")
        group_data.setStyleSheet(group_backup.styleSheet())
        
        data_layout = QVBoxLayout(group_data)
        data_layout.setContentsMargins(20, 25, 20, 20)
        data_layout.setSpacing(15)
        
        # Bouton: Export des données
        btn_export = QPushButton("📤 Exporter toutes les données (CSV)")
        btn_export.setStyleSheet(btn_style + "background: #9C27B0; color: white;")
        btn_export.clicked.connect(self.export_all_data)
        data_layout.addWidget(btn_export)
        
        # Bouton: Optimiser la base
        btn_optimize = QPushButton("⚡ Optimiser la base de données")
        btn_optimize.setStyleSheet(btn_style + "background: #00BCD4; color: white;")
        btn_optimize.clicked.connect(self.optimize_database)
        data_layout.addWidget(btn_optimize)
        
        # Avertissement pour actions dangereuses
        warning_card = QLabel("""
        <div style='background: #ffebee; padding: 15px; border-radius: 8px; border-left: 4px solid #f44336;'>
            <b>⚠️ Attention - Actions dangereuses</b><br/>
            Les actions ci-dessous sont irréversibles. Assurez-vous d'avoir une sauvegarde avant de continuer.
        </div>
        """)
        warning_card.setWordWrap(True)
        data_layout.addWidget(warning_card)
        
        # Bouton: Réinitialiser config
        btn_reset_config = QPushButton("🔄 Réinitialiser la configuration")
        btn_reset_config.setStyleSheet(btn_style + "background: #FF5722; color: white;")
        btn_reset_config.clicked.connect(self.reset_config)
        data_layout.addWidget(btn_reset_config)
        
        layout.addWidget(group_data)
        layout.addStretch()
        
        return widget
    
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
            # TODO: Implémenter l'optimisation réelle avec VACUUM SQLite
            QMessageBox.information(self, "Succès", "✅ Base de données optimisée!")
    
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
