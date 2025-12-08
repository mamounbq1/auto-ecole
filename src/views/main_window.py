"""
Fenêtre principale de l'application avec navigation
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame,
    QMessageBox, QMenuBar, QMenu, QToolBar, QStatusBar
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QFont

from src.utils import logout, get_current_user, get_logger
from src.models import UserRole

logger = get_logger()


class MainWindow(QMainWindow):
    """Fenêtre principale avec navigation et modules"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.current_module = None
        
        self.setWindowTitle(f"🚗 Auto-École Manager - {user.full_name} ({user.role.value})")
        self.setMinimumSize(1200, 700)
        
        self.setup_ui()
        self.create_menu_bar()
        self.create_toolbar()
        self.create_status_bar()
        
        # Afficher le dashboard par défaut
        self.show_dashboard()
        
    def setup_ui(self):
        """Configurer l'interface utilisateur"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar (barre latérale de navigation)
        self.create_sidebar(main_layout)
        
        # Zone de contenu
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, stretch=1)
        
        # Appliquer le style
        self.apply_style()
        
    def create_sidebar(self, layout):
        """Créer la barre latérale de navigation"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setMaximumWidth(250)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(5)
        
        # Header utilisateur
        user_frame = QFrame()
        user_frame.setObjectName("userFrame")
        user_layout = QVBoxLayout(user_frame)
        
        user_name = QLabel(self.user.full_name)
        user_name.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
        user_name.setWordWrap(True)
        
        user_role = QLabel(f"📋 {self.user.role.value.capitalize()}")
        user_role.setStyleSheet("font-size: 11px; color: #bdc3c7;")
        
        user_layout.addWidget(user_name)
        user_layout.addWidget(user_role)
        
        sidebar_layout.addWidget(user_frame)
        sidebar_layout.addSpacing(20)
        
        # Boutons de navigation
        nav_buttons = self.get_navigation_buttons()
        
        for icon, text, callback in nav_buttons:
            btn = self.create_nav_button(icon, text, callback)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        # Bouton de déconnexion
        logout_btn = QPushButton("🚪 Déconnexion")
        logout_btn.setObjectName("logoutButton")
        logout_btn.setMinimumHeight(40)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.handle_logout)
        sidebar_layout.addWidget(logout_btn)
        
        layout.addWidget(sidebar)
        
    def get_navigation_buttons(self):
        """Obtenir les boutons de navigation selon le rôle"""
        buttons = [
            ("📊", "Dashboard", self.show_dashboard),
        ]
        
        # Ajouter les modules selon les permissions
        if self.user.role in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
            buttons.append(("👥", "Élèves", self.show_students))
        
        if self.user.role in [UserRole.ADMIN, UserRole.INSTRUCTOR]:
            buttons.append(("📅", "Planning", self.show_planning))
        
        if self.user.role in [UserRole.ADMIN, UserRole.CASHIER]:
            buttons.append(("💰", "Paiements", self.show_payments))
        
        if self.user.role == UserRole.ADMIN:
            buttons.extend([
                ("👨‍🏫", "Moniteurs", self.show_instructors),
                ("🚗", "Véhicules", self.show_vehicles),
                ("📝", "Examens", self.show_exams),
                ("📈", "Rapports", self.show_reports),
                ("⚙️", "Paramètres", self.show_settings),
            ])
        
        return buttons
        
    def create_nav_button(self, icon, text, callback):
        """Créer un bouton de navigation"""
        btn = QPushButton(f"{icon}  {text}")
        btn.setObjectName("navButton")
        btn.setMinimumHeight(45)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(callback)
        return btn
        
    def create_menu_bar(self):
        """Créer la barre de menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")
        
        export_action = QAction("📤 Exporter les données", self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        backup_action = QAction("💾 Sauvegarder", self)
        backup_action.triggered.connect(self.create_backup)
        file_menu.addAction(backup_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("🚪 Quitter", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        
        doc_action = QAction("📚 Documentation", self)
        doc_action.triggered.connect(self.show_documentation)
        help_menu.addAction(doc_action)
        
        about_action = QAction("ℹ️ À propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Créer la barre d'outils"""
        toolbar = QToolBar("Outils principaux")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Actions rapides selon le rôle
        if self.user.role in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
            add_student = QAction("➕ Nouvel Élève", self)
            add_student.triggered.connect(self.quick_add_student)
            toolbar.addAction(add_student)
        
        if self.user.role in [UserRole.ADMIN, UserRole.CASHIER]:
            add_payment = QAction("💵 Nouveau Paiement", self)
            add_payment.triggered.connect(self.quick_add_payment)
            toolbar.addAction(add_payment)
        
        toolbar.addSeparator()
        
        refresh = QAction("🔄 Actualiser", self)
        refresh.triggered.connect(self.refresh_current_view)
        toolbar.addAction(refresh)
        
    def create_status_bar(self):
        """Créer la barre de statut"""
        status = self.statusBar()
        status.showMessage(f"Connecté en tant que {self.user.full_name}")
        
    def apply_style(self):
        """Appliquer le style CSS"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            
            QFrame#sidebar {
                background-color: #2c3e50;
                border-right: 1px solid #34495e;
            }
            
            QFrame#userFrame {
                background-color: #34495e;
                border-radius: 5px;
                padding: 15px;
            }
            
            QPushButton#navButton {
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 5px;
                text-align: left;
                padding: 10px 15px;
                font-size: 13px;
            }
            
            QPushButton#navButton:hover {
                background-color: #34495e;
            }
            
            QPushButton#navButton:pressed {
                background-color: #1abc9c;
            }
            
            QPushButton#logoutButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            
            QPushButton#logoutButton:hover {
                background-color: #c0392b;
            }
            
            QMenuBar {
                background-color: white;
                border-bottom: 1px solid #bdc3c7;
            }
            
            QMenuBar::item:selected {
                background-color: #3498db;
                color: white;
            }
            
            QToolBar {
                background-color: white;
                border-bottom: 1px solid #bdc3c7;
                spacing: 5px;
                padding: 5px;
            }
            
            QStatusBar {
                background-color: white;
                border-top: 1px solid #bdc3c7;
            }
        """)
        
    # Méthodes pour afficher les différents modules
    def show_dashboard(self):
        """Afficher le dashboard"""
        from .widgets.dashboard_advanced import DashboardAdvancedWidget
        
        self.set_current_module(DashboardAdvancedWidget(self.user))
        self.statusBar().showMessage("Dashboard")
        
    def show_students(self):
        """Afficher la gestion des élèves"""
        from .widgets.students_enhanced import StudentsEnhancedWidget
        
        self.set_current_module(StudentsEnhancedWidget(self.user))
        self.statusBar().showMessage("Gestion des Élèves")
        
    def show_planning(self):
        """Afficher le planning"""
        from .widgets.planning_enhanced import PlanningEnhancedWidget
        
        self.set_current_module(PlanningEnhancedWidget(self.user))
        self.statusBar().showMessage("Planning des Sessions")
        
    def show_payments(self):
        """Afficher les paiements"""
        from .widgets.payments_enhanced import PaymentsEnhancedWidget
        
        self.set_current_module(PaymentsWidget(self.user))
        self.statusBar().showMessage("Gestion des Paiements")
        
    def show_instructors(self):
        """Afficher les moniteurs"""
        self.show_placeholder("Moniteurs", "👨‍🏫")
        
    def show_vehicles(self):
        """Afficher les véhicules"""
        self.show_placeholder("Véhicules", "🚗")
        
    def show_exams(self):
        """Afficher les examens"""
        self.show_placeholder("Examens", "📝")
        
    def show_reports(self):
        """Afficher les rapports"""
        from .widgets.reports_widget import ReportsWidget
        
        self.set_current_module(ReportsWidget(self.user))
        self.statusBar().showMessage("Rapports et Statistiques")
        
    def show_settings(self):
        """Afficher les paramètres"""
        self.show_placeholder("Paramètres", "⚙️")
        
    def show_placeholder(self, title, icon):
        """Afficher un placeholder pour les modules à venir"""
        placeholder = QWidget()
        layout = QVBoxLayout(placeholder)
        layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 72px;")
        
        title_label = QLabel(f"Module {title}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        
        message_label = QLabel("Cette fonctionnalité sera bientôt disponible")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(message_label)
        
        self.set_current_module(placeholder)
        self.statusBar().showMessage(f"{title} - En développement")
        
    def set_current_module(self, widget):
        """Définir le module actuellement affiché"""
        # Supprimer tous les widgets existants
        while self.content_stack.count():
            old_widget = self.content_stack.widget(0)
            self.content_stack.removeWidget(old_widget)
            old_widget.deleteLater()
        
        # Ajouter le nouveau widget
        self.content_stack.addWidget(widget)
        self.current_module = widget
        
    # Actions rapides
    def quick_add_student(self):
        """Action rapide : Ajouter un élève"""
        QMessageBox.information(self, "Action rapide", "Formulaire d'ajout d'élève (à implémenter)")
        
    def quick_add_payment(self):
        """Action rapide : Ajouter un paiement"""
        QMessageBox.information(self, "Action rapide", "Formulaire d'ajout de paiement (à implémenter)")
        
    def refresh_current_view(self):
        """Actualiser la vue actuelle"""
        if hasattr(self.current_module, 'refresh'):
            self.current_module.refresh()
        self.statusBar().showMessage("Actualisé", 2000)
        
    # Actions de menu
    def export_data(self):
        """Exporter les données"""
        QMessageBox.information(self, "Export", "Fonction d'export en cours de développement")
        
    def create_backup(self):
        """Créer une sauvegarde"""
        from src.utils import create_backup
        
        success, result = create_backup()
        if success:
            QMessageBox.information(self, "Sauvegarde", f"Sauvegarde créée avec succès:\n{result}")
        else:
            QMessageBox.critical(self, "Erreur", f"Échec de la sauvegarde:\n{result}")
        
    def show_documentation(self):
        """Afficher la documentation"""
        QMessageBox.information(
            self,
            "Documentation",
            "Consultez les fichiers:\n\n"
            "• README.md\n"
            "• docs/QUICK_START.md\n"
            "• docs/DEVELOPMENT_GUIDE.md"
        )
        
    def show_about(self):
        """Afficher les informations sur l'application"""
        QMessageBox.about(
            self,
            "À propos",
            "🚗 <b>Auto-École Manager</b><br><br>"
            "Version 1.1.0<br><br>"
            "Système de gestion complet pour auto-écoles<br><br>"
            "Développé avec ❤️ en Python & PySide6<br>"
            "© 2024 - Tous droits réservés"
        )
        
    def handle_logout(self):
        """Gérer la déconnexion"""
        reply = QMessageBox.question(
            self,
            "Déconnexion",
            "Êtes-vous sûr de vouloir vous déconnecter ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logout()
            logger.info(f"Déconnexion : {self.user.username}")
            self.close()
            
            # Afficher à nouveau la fenêtre de connexion
            from .login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.login_successful.connect(self.on_login_success)
            self.login_window.show()
            
    def on_login_success(self, user):
        """Gérer la reconnexion après déconnexion"""
        self.user = user
        main_window = MainWindow(user)
        main_window.show()
        
    def closeEvent(self, event):
        """Gérer la fermeture de la fenêtre"""
        reply = QMessageBox.question(
            self,
            "Quitter",
            "Voulez-vous vraiment quitter l'application ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logout()
            event.accept()
        else:
            event.ignore()
