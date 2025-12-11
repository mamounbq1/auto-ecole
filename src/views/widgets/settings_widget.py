"""
Module Paramètres - Interface simplifiée de configuration
Contient uniquement les paramètres fonctionnels
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QTabWidget, QGroupBox,
                              QScrollArea, QFileDialog, QMessageBox, QComboBox,
                              QCheckBox, QSpinBox, QTextEdit, QTableWidget,
                              QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
                              QGridLayout, QFrame, QApplication, QProgressDialog)
from PySide6.QtCore import Qt, Signal, QTimer, QThread
from PySide6.QtGui import QPixmap, QFont
import json
import shutil
import os
import threading
from pathlib import Path
from datetime import datetime


class SettingsWidget(QWidget):
    """Widget principal des paramètres avec onglets"""
    
    settings_changed = Signal()  # Signal émis quand les paramètres changent
    
    def __init__(self):
        super().__init__()
        self.config_path = Path("config.json")
        self.config = self.load_config()
        self.backup_timer = None
        self.init_ui()
        self.init_auto_backup()
        
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
        
        # Onglet 2: Base de Données & Backup
        tabs.addTab(self.create_database_tab(), "💾 Base de Données")
        
        # Onglet 3: Actions & Maintenance
        tabs.addTab(self.create_actions_tab(), "🔧 Actions & Maintenance")
        
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
    
    def create_database_tab(self):
        """Onglet: Base de Données & Backup"""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Groupe: Base de données
        group_db = QGroupBox("💾 Base de Données")
        group_db.setStyleSheet("""
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
        
        form_db = QFormLayout(group_db)
        form_db.setSpacing(10)
        form_db.setContentsMargins(15, 20, 15, 15)
        form_db.setLabelAlignment(Qt.AlignRight)
        
        # Chemin BD avec bouton parcourir
        db_path_layout = QHBoxLayout()
        self.input_db_path = QLineEdit(self.config.get('database', {}).get('path', 'data/autoecole.db'))
        self.input_db_path.setPlaceholderText("Chemin de la base de données")
        
        btn_browse_db = QPushButton("📁 Parcourir")
        btn_browse_db.setFixedWidth(100)
        btn_browse_db.clicked.connect(self.browse_database_path)
        
        input_style = """
            QLineEdit, QSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
                background: white;
            }
            QLineEdit:focus, QSpinBox:focus {
                border-color: #2196F3;
                background: #f8f9fa;
            }
        """
        
        self.input_db_path.setStyleSheet(input_style)
        btn_browse_db.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)
        
        db_path_layout.addWidget(self.input_db_path)
        db_path_layout.addWidget(btn_browse_db)
        
        form_db.addRow("Chemin BD:", db_path_layout)
        
        layout.addWidget(group_db)
        
        # Groupe: Backup automatique
        group_backup = QGroupBox("🔄 Backup Automatique")
        group_backup.setStyleSheet(group_db.styleSheet())
        
        form_backup = QFormLayout(group_backup)
        form_backup.setSpacing(10)
        form_backup.setContentsMargins(15, 20, 15, 15)
        form_backup.setLabelAlignment(Qt.AlignRight)
        
        self.check_backup_start = QCheckBox("Créer un backup automatique au démarrage de l'application")
        self.check_backup_start.setChecked(self.config.get('database', {}).get('backup_on_start', False))
        
        self.check_backup_interval = QCheckBox("Activer backup automatique périodique")
        self.check_backup_interval.setChecked(self.config.get('database', {}).get('auto_backup_enabled', False))
        self.check_backup_interval.toggled.connect(self.toggle_backup_interval)
        
        self.input_backup_interval = QSpinBox()
        self.input_backup_interval.setRange(5, 1440)  # 5 min à 24h
        self.input_backup_interval.setSuffix(" minutes")
        self.input_backup_interval.setValue(self.config.get('database', {}).get('auto_backup_interval', 60))
        self.input_backup_interval.setEnabled(self.check_backup_interval.isChecked())
        self.input_backup_interval.setStyleSheet(input_style)
        
        form_backup.addRow("", self.check_backup_start)
        form_backup.addRow("", self.check_backup_interval)
        form_backup.addRow("Intervalle:", self.input_backup_interval)
        
        layout.addWidget(group_backup)
        
        # Info box
        info = QLabel("💡 Les backups sont sauvegardés dans le dossier 'backups/' avec horodatage automatique.")
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
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(scroll)
        
        return container
    
    def create_actions_tab(self):
        """Onglet: Actions & Maintenance"""
        widget = QWidget()
        widget.setStyleSheet("background: #f5f5f5;")
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Grille de cards
        grid = QGridLayout()
        grid.setSpacing(15)
        
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
            "Exporter CSV Global",
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
        
        danger_desc = QLabel("Actions irréversibles - Un backup sera créé automatiquement")
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
    
    def browse_database_path(self):
        """Parcourir pour choisir un emplacement de base de données"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Choisir l'emplacement de la base de données",
            self.input_db_path.text(),
            "Base de données SQLite (*.db)"
        )
        
        if file_path:
            self.input_db_path.setText(file_path)
    
    def toggle_backup_interval(self, checked):
        """Active/désactive l'intervalle de backup"""
        self.input_backup_interval.setEnabled(checked)
    
    def init_auto_backup(self):
        """Initialise le système de backup automatique"""
        # Backup au démarrage si activé
        if self.config.get('database', {}).get('backup_on_start', False):
            QTimer.singleShot(2000, self.silent_backup)  # 2 secondes après le démarrage
        
        # Backup périodique si activé
        if self.config.get('database', {}).get('auto_backup_enabled', False):
            interval_minutes = self.config.get('database', {}).get('auto_backup_interval', 60)
            self.start_auto_backup_timer(interval_minutes)
    
    def start_auto_backup_timer(self, interval_minutes):
        """Démarre le timer de backup automatique"""
        if self.backup_timer:
            self.backup_timer.stop()
        
        self.backup_timer = QTimer()
        self.backup_timer.timeout.connect(self.silent_backup)
        self.backup_timer.start(interval_minutes * 60 * 1000)  # Convertir en millisecondes
    
    def silent_backup(self):
        """Crée un backup silencieux (sans messages)"""
        try:
            from src.utils.config_manager import get_config_manager
            config_mgr = get_config_manager()
            
            from src.config import DATABASE_PATH
            db_path = Path(DATABASE_PATH)
            if not db_path.exists():
                return
            
            backup_dir = Path(config_mgr.get_backup_path())
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"auto_backup_{timestamp}.db"
            
            shutil.copy(db_path, backup_path)
            print(f"✅ Backup automatique créé: {backup_path}")
        except Exception as e:
            print(f"❌ Erreur backup automatique: {e}")
    
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
            
            # Base de données
            if 'database' not in self.config:
                self.config['database'] = {}
            self.config['database']['path'] = self.input_db_path.text()
            self.config['database']['backup_on_start'] = self.check_backup_start.isChecked()
            self.config['database']['auto_backup_enabled'] = self.check_backup_interval.isChecked()
            self.config['database']['auto_backup_interval'] = self.input_backup_interval.value()
            
            # Sauvegarder
            success = self.save_config()
            
            if success:
                # Redémarrer le timer de backup si nécessaire
                if self.check_backup_interval.isChecked():
                    self.start_auto_backup_timer(self.input_backup_interval.value())
                elif self.backup_timer:
                    self.backup_timer.stop()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"❌ Erreur lors de la sauvegarde: {e}")
    
    def create_backup(self):
        """Crée une sauvegarde de la base de données"""
        try:
            from src.utils.config_manager import get_config_manager
            config_mgr = get_config_manager()
            
            from src.config import DATABASE_PATH
            db_path = Path(DATABASE_PATH)
            if not db_path.exists():
                QMessageBox.warning(self, "Attention", "❌ Base de données introuvable!")
                return
            
            backup_dir = Path(config_mgr.get_backup_path())
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"backup_{timestamp}.db"
            
            shutil.copy(db_path, backup_path)
            
            QMessageBox.information(self, "Succès", f"✅ Sauvegarde créée:\n{backup_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"❌ Erreur lors de la sauvegarde: {e}")
    
    def restore_backup(self):
        """Restaure une sauvegarde"""
        from src.utils.config_manager import get_config_manager
        config_mgr = get_config_manager()
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir une sauvegarde à restaurer",
            config_mgr.get_backup_path(),
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
                    from src.config import DATABASE_PATH
                    db_path = Path(DATABASE_PATH)
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
        from src.utils.config_manager import get_config_manager
        config_mgr = get_config_manager()
        
        backup_dir = Path(config_mgr.get_backup_path())
        backup_dir.mkdir(exist_ok=True)
        
        import subprocess
        
        if os.name == 'nt':  # Windows
            os.startfile(str(backup_dir.absolute()))
        elif os.name == 'posix':  # macOS et Linux
            subprocess.Popen(['xdg-open', str(backup_dir.absolute())])
    
    def export_all_data(self):
        """Exporte toutes les données en CSV"""
        try:
            from src.models import get_session, Student, Instructor, Vehicle, Session, Payment, Exam
            from src.utils.export import ExportManager
            
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "Voulez-vous exporter toutes les données en CSV?\n\n" +
                "Cela va créer plusieurs fichiers CSV dans le dossier exports/",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                from src.utils.config_manager import get_config_manager
                config_mgr = get_config_manager()
                
                export_base = Path(config_mgr.get_export_path())
                export_dir = export_base / f"export_global_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                export_dir.mkdir(parents=True, exist_ok=True)
                
                exporter = ExportManager()
                session = get_session()
                
                # Export de chaque entité
                entities = [
                    ("eleves", Student),
                    ("moniteurs", Instructor),
                    ("vehicules", Vehicle),
                    ("sessions", Session),
                    ("paiements", Payment),
                    ("examens", Exam)
                ]
                
                exported_files = []
                for name, model in entities:
                    data = session.query(model).all()
                    if data:
                        file_path = export_dir / f"{name}.csv"
                        success = exporter.export_to_csv(data, str(file_path))
                        if success:
                            exported_files.append(name)
                
                QMessageBox.information(
                    self,
                    "✅ Export terminé",
                    f"Export global réussi!\n\n" +
                    f"Dossier: {export_dir}\n" +
                    f"Fichiers créés: {', '.join(exported_files)}"
                )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"❌ Erreur lors de l'export: {e}")
    
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
                
                # Afficher progression non-bloquante
                progress = QProgressDialog("Synchronisation des statuts en cours...", None, 0, 0, self)
                progress.setWindowTitle("Synchronisation")
                progress.setWindowModality(Qt.WindowModal)
                progress.setCancelButton(None)
                progress.setMinimumDuration(0)
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
                if 'progress' in locals():
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
            "Un backup automatique sera créé avant la réinitialisation.",
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
                try:
                    from src.utils.config_manager import get_config_manager
                    config_mgr = get_config_manager()
                    
                    # Créer un backup de la config actuelle
                    backup_dir = Path(config_mgr.get_backup_path())
                    backup_dir.mkdir(exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    config_backup = backup_dir / f"config_backup_{timestamp}.json"
                    shutil.copy(self.config_path, config_backup)
                    
                    # Charger config.example.json ou créer config minimal
                    example_config_path = Path("config.example.json")
                    if example_config_path.exists():
                        shutil.copy(example_config_path, self.config_path)
                    else:
                        # Config minimal
                        minimal_config = {
                            "center": {},
                            "database": {"path": "data/autoecole.db"},
                            "pdf": {"company_logo": None},
                            "formats": {"currency": "DH"},
                            "paths": {"exports": "exports", "backups": "backups"}
                        }
                        with open(self.config_path, 'w', encoding='utf-8') as f:
                            json.dump(minimal_config, f, indent=4, ensure_ascii=False)
                    
                    QMessageBox.information(
                        self,
                        "✅ Succès",
                        f"Configuration réinitialisée!\n\n" +
                        f"Backup sauvegardé: {config_backup}\n\n" +
                        f"Veuillez redémarrer l'application."
                    )
                    
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "❌ Erreur",
                        f"Erreur lors de la réinitialisation:\n{str(e)}"
                    )
