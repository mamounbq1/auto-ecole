"""
Fenêtre d'activation de licence
Première fenêtre affichée si l'application n'est pas sous licence
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTextEdit, QGroupBox,
    QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon

from src.utils.license_manager import get_license_manager
from src.utils import get_logger

logger = get_logger()


class LicenseActivationWindow(QDialog):
    """Fenêtre d'activation de licence"""
    
    license_activated = Signal()  # Signal émis quand la licence est activée
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.license_manager = get_license_manager()
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface"""
        self.setWindowTitle("🔐 Activation de Licence - Auto-École")
        self.setMinimumSize(700, 500)
        self.setModal(True)
        
        # Set window icon (prioritize new icon)
        icon_ico = Path(__file__).parent.parent.parent / "assets" / "app_icon.ico"
        icon_new = Path(__file__).parent.parent.parent / "assets" / "app_icon_new.png"
        
        if icon_ico.exists():
            self.setWindowIcon(QIcon(str(icon_ico)))
        elif icon_new.exists():
            self.setWindowIcon(QIcon(str(icon_new)))
        
        # Style global
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QLabel {
                color: #2c3e50;
            }
            QGroupBox {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
                font-weight: bold;
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # === HEADER ===
        header_layout = QVBoxLayout()
        
        # Titre
        title_label = QLabel("🔐 Activation de Licence Requise")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #6c5ce7; margin-bottom: 10px;")
        header_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "Bienvenue ! Cette application nécessite une licence valide pour fonctionner.\n"
            "Veuillez entrer votre clé de licence pour continuer."
        )
        desc_label.setFont(QFont("Arial", 11))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #636e72; margin-bottom: 10px;")
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)
        
        layout.addLayout(header_layout)
        
        # Ligne de séparation
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #dfe6e9;")
        layout.addWidget(line)
        
        # === HARDWARE ID ===
        hardware_group = QGroupBox("📟 Identifiant de cet Ordinateur")
        hardware_layout = QVBoxLayout()
        
        hw_label = QLabel("Pour obtenir une licence, communiquez cet identifiant au support :")
        hw_label.setFont(QFont("Arial", 10))
        hw_label.setStyleSheet("font-weight: normal; color: #636e72;")
        hardware_layout.addWidget(hw_label)
        
        # Hardware ID (lecture seule)
        self.hardware_id_input = QLineEdit()
        hardware_id = self.license_manager.get_hardware_id()
        self.hardware_id_input.setText(hardware_id)
        self.hardware_id_input.setReadOnly(True)
        self.hardware_id_input.setFont(QFont("Courier", 12, QFont.Bold))
        self.hardware_id_input.setAlignment(Qt.AlignCenter)
        self.hardware_id_input.setStyleSheet("""
            QLineEdit {
                background-color: #ecf0f1;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 12px;
                color: #2c3e50;
                font-weight: bold;
            }
        """)
        hardware_layout.addWidget(self.hardware_id_input)
        
        # Bouton copier
        copy_btn = QPushButton("📋 Copier l'Identifiant")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #74b9ff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0984e3;
            }
        """)
        copy_btn.clicked.connect(self.copy_hardware_id)
        hardware_layout.addWidget(copy_btn)
        
        hardware_group.setLayout(hardware_layout)
        layout.addWidget(hardware_group)
        
        # === ACTIVATION ===
        activation_group = QGroupBox("🔑 Activation de la Licence")
        activation_layout = QVBoxLayout()
        
        # Label
        license_label = QLabel("Entrez votre clé de licence :")
        license_label.setFont(QFont("Arial", 11, QFont.Bold))
        license_label.setStyleSheet("color: #2c3e50;")
        activation_layout.addWidget(license_label)
        
        # Input clé de licence
        self.license_key_input = QLineEdit()
        self.license_key_input.setPlaceholderText("XXXXX-XXXXX-XXXXX-XXXXX-XXXXX")
        self.license_key_input.setFont(QFont("Courier", 11))
        self.license_key_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 12px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #6c5ce7;
            }
        """)
        self.license_key_input.textChanged.connect(self.on_license_key_changed)
        activation_layout.addWidget(self.license_key_input)
        
        # Bouton activer
        self.activate_btn = QPushButton("✅ Activer la Licence")
        self.activate_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.activate_btn.setStyleSheet("""
            QPushButton {
                background-color: #00b894;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #00a383;
            }
            QPushButton:disabled {
                background-color: #b2bec3;
            }
        """)
        self.activate_btn.setEnabled(False)
        self.activate_btn.clicked.connect(self.activate_license)
        activation_layout.addWidget(self.activate_btn)
        
        activation_group.setLayout(activation_layout)
        layout.addWidget(activation_group)
        
        # === FOOTER ===
        footer_layout = QHBoxLayout()
        
        # Bouton instructions (à gauche)
        help_btn = QPushButton("❓ Comment obtenir une licence ?")
        help_btn.setStyleSheet("""
            QPushButton {
                background-color: #74b9ff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0984e3;
            }
        """)
        help_btn.clicked.connect(self.show_instructions)
        footer_layout.addWidget(help_btn)
        
        footer_layout.addStretch()
        
        # Bouton quitter
        quit_btn = QPushButton("❌ Quitter")
        quit_btn.setStyleSheet("""
            QPushButton {
                background-color: #d63031;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        quit_btn.clicked.connect(self.reject)
        footer_layout.addWidget(quit_btn)
        
        layout.addLayout(footer_layout)
        
        self.setLayout(layout)
    
    def copy_hardware_id(self):
        """Copie le Hardware ID dans le presse-papiers"""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.hardware_id_input.text())
        QMessageBox.information(
            self,
            "✅ Copié",
            "L'identifiant de cet ordinateur a été copié dans le presse-papiers!"
        )
    
    def show_instructions(self):
        """Affiche les instructions d'obtention de licence dans une popup"""
        instructions_html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; font-size: 12px; }
                h2 { color: #6c5ce7; }
                ol { line-height: 1.8; }
                li { margin-bottom: 8px; }
                b { color: #2c3e50; }
                .note { 
                    background-color: #fff3cd; 
                    border-left: 4px solid #ffc107;
                    padding: 10px;
                    margin-top: 15px;
                    border-radius: 4px;
                }
                .contact {
                    background-color: #e3f2fd;
                    border-left: 4px solid #2196f3;
                    padding: 10px;
                    margin-top: 10px;
                    border-radius: 4px;
                }
            </style>
        </head>
        <body>
            <h2>📋 Comment obtenir votre clé de licence ?</h2>
            
            <ol>
                <li><b>Copiez votre Identifiant d'Ordinateur</b><br>
                    Cliquez sur le bouton "📋 Copier l'Identifiant" dans la fenêtre d'activation.
                </li>
                
                <li><b>Contactez le Support Technique</b><br>
                    Envoyez un email avec votre identifiant d'ordinateur.
                </li>
                
                <li><b>Recevez votre Clé de Licence</b><br>
                    Le support vous enverra votre clé de licence unique par email.
                </li>
                
                <li><b>Activez l'Application</b><br>
                    Copiez la clé reçue et collez-la dans le champ "Clé de licence".<br>
                    Cliquez sur "✅ Activer la Licence".
                </li>
            </ol>
            
            <div class="contact">
                <b>📧 Contact Support:</b><br>
                Email: <b>e.belqasim@gmail.com</b><br>
                Téléphone: <b>+212 637-636146</b>
            </div>
            
            <div class="note">
                <b>⚠️ Important:</b><br>
                • La licence est liée à cet ordinateur uniquement<br>
                • Conservez votre clé de licence en lieu sûr<br>
                • Pour transférer la licence, contactez le support
            </div>
        </body>
        </html>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("ℹ️ Instructions d'Activation")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(instructions_html)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Set window icon
        icon_path = Path(__file__).parent.parent.parent / "assets" / "app_icon.png"
        if icon_path.exists():
            msg_box.setWindowIcon(QIcon(str(icon_path)))
        
        msg_box.exec()
    
    def on_license_key_changed(self, text: str):
        """Active le bouton si la clé a au moins 20 caractères"""
        self.activate_btn.setEnabled(len(text.strip()) >= 20)
    
    def activate_license(self):
        """Active la licence"""
        license_key = self.license_key_input.text().strip()
        
        if not license_key:
            QMessageBox.warning(
                self,
                "⚠️ Champ vide",
                "Veuillez entrer une clé de licence."
            )
            return
        
        # Tenter l'activation
        success, message = self.license_manager.activate_license(license_key)
        
        if success:
            QMessageBox.information(
                self,
                "✅ Activation Réussie",
                message
            )
            logger.info("Licence activée avec succès")
            self.license_activated.emit()
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "❌ Activation Échouée",
                message
            )
            logger.warning(f"Échec activation: {message}")
