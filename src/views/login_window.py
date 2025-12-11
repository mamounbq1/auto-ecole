"""
Fenêtre de connexion de l'application
"""

from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox,
    QFrame, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont, QIcon

from src.utils import login, get_logger, bypass_login

logger = get_logger()

# ⚠️ Mode temporaire : permet de se connecter sans identifiants lorsque les champs sont vides.
#    Veillez à remettre cette valeur à False une fois les tests terminés.
TEMPORARY_LOGIN_BYPASS_ENABLED = True


class LoginWindow(QMainWindow):
    """Fenêtre de connexion avec authentification"""
    
    # Signal émis lors d'une connexion réussie
    login_successful = Signal(object)  # Émet l'utilisateur connecté
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚗 Auto-École Manager - Connexion")
        self.setFixedSize(450, 550)
        self.setup_ui()
        
    def setup_ui(self):
        """Configurer l'interface utilisateur"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Header avec logo et titre
        self._create_header(main_layout)
        
        # Espace
        main_layout.addSpacing(20)
        
        # Formulaire de connexion
        self._create_form(main_layout)
        
        # Bouton de connexion
        self._create_login_button(main_layout)
        
        # Options supplémentaires
        self._create_options(main_layout)
        
        # Footer
        main_layout.addStretch()
        self._create_footer(main_layout)
        
        # Appliquer le style
        self.apply_style()
        
    def _create_header(self, layout):
        """Créer l'en-tête avec logo et titre"""
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        
        # Titre principal
        title = QLabel("🚗 Auto-École Manager")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        
        # Sous-titre
        subtitle = QLabel("Système de Gestion Intégré")
        subtitle_font = QFont()
        subtitle_font.setPointSize(11)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
        
    def _create_form(self, layout):
        """Créer le formulaire de connexion"""
        # Frame pour le formulaire
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Champ nom d'utilisateur
        username_label = QLabel("👤 Nom d'utilisateur")
        username_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Entrez votre nom d'utilisateur")
        self.username_input.setMinimumHeight(40)
        self.username_input.returnPressed.connect(self.handle_login)
        
        # Champ mot de passe
        password_label = QLabel("🔒 Mot de passe")
        password_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.returnPressed.connect(self.handle_login)
        
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        
        layout.addWidget(form_frame)
        
    def _create_login_button(self, layout):
        """Créer le bouton de connexion"""
        self.login_button = QPushButton("Se Connecter")
        self.login_button.setMinimumHeight(45)
        self.login_button.setObjectName("loginButton")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)
        
        layout.addWidget(self.login_button)
        
    def _create_options(self, layout):
        """Créer les options (se souvenir de moi, etc.)"""
        options_layout = QHBoxLayout()
        
        # Case à cocher "Se souvenir de moi"
        self.remember_checkbox = QCheckBox("Se souvenir de moi")
        self.remember_checkbox.setStyleSheet("color: #7f8c8d;")
        
        options_layout.addWidget(self.remember_checkbox)
        options_layout.addStretch()
        
        layout.addLayout(options_layout)
        
    def _create_footer(self, layout):
        """Créer le pied de page"""
        footer_layout = QVBoxLayout()
        footer_layout.setAlignment(Qt.AlignCenter)
        
        # Message d'aide
        help_label = QLabel("Comptes de démonstration disponibles")
        help_label.setAlignment(Qt.AlignCenter)
        help_label.setStyleSheet("color: #95a5a6; font-size: 11px; margin-top: 10px;")
        
        # Liens vers la documentation
        demo_label = QLabel("Admin: admin / Admin123! | Caissier: caissier / Caisse123!")
        demo_label.setAlignment(Qt.AlignCenter)
        demo_label.setStyleSheet("color: #3498db; font-size: 10px;")
        
        footer_layout.addWidget(help_label)
        footer_layout.addWidget(demo_label)
        
        layout.addLayout(footer_layout)
        
    def apply_style(self):
        """Appliquer le style CSS à la fenêtre"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            
            QFrame#formFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
            
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
            }
            
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            
            QPushButton#loginButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
            }
            
            QPushButton#loginButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton#loginButton:pressed {
                background-color: #21618c;
            }
            
            QCheckBox {
                font-size: 12px;
            }
        """)
        
    def handle_login(self):
        """Gérer la tentative de connexion"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Mode bypass temporaire : connexion automatique si les champs sont vides
        if TEMPORARY_LOGIN_BYPASS_ENABLED and not username and not password:
            success, message, user = bypass_login()
            if success:
                logger.warning(
                    "Connexion bypass utilisée : authentification automatique pour '%s' (rôle: %s)",
                    user.username,
                    user.role.value,
                )
                self._finalize_successful_login(
                    user,
                    (
                        f"Mode bypass activé.\nConnexion automatique en tant que {user.full_name} "
                        f"({user.role.value.capitalize()})."
                    ),
                )
            else:
                QMessageBox.critical(
                    self,
                    "Connexion impossible",
                    message,
                )
            return
        
        # Validation basique
        if not username or not password:
            QMessageBox.warning(
                self,
                "Champs requis",
                "Veuillez remplir tous les champs."
            )
            return
        
        # Désactiver le bouton pendant la connexion
        self.login_button.setEnabled(False)
        self.login_button.setText("Connexion en cours...")
        
        # Tenter la connexion
        success, message, user = login(username, password)
        
        # Réactiver le bouton
        self.login_button.setEnabled(True)
        self.login_button.setText("Se Connecter")
        
        if success:
            logger.info(f"Connexion réussie : {username}")
            self._finalize_successful_login(user)
        else:
            logger.warning(f"Échec de connexion pour : {username}")
            
            # Afficher le message d'erreur
            QMessageBox.critical(
                self,
                "Échec de connexion",
                message
            )
            
            # Effacer le mot de passe
            self.password_input.clear()
            self.password_input.setFocus()
            
    def _finalize_successful_login(self, user, custom_message: Optional[str] = None) -> None:
        """Afficher le message de bienvenue et émettre le signal de connexion."""
        message = custom_message or (
            f"Bienvenue {user.full_name} !\n\nRôle : {user.role.value.capitalize()}"
        )

        # S'assurer que le bouton est réactivé (au cas où)
        self.login_button.setEnabled(True)
        self.login_button.setText("Se Connecter")

        QMessageBox.information(
            self,
            "Connexion réussie",
            message,
        )

        self.login_successful.emit(user)
        self.close()
        
    def keyPressEvent(self, event):
        """Gérer les événements clavier"""
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)
