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
        
        # Afficher le Dashboard professionnel par défaut
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
        """Masquer la barre de menu classique pour une interface moderne"""
        # Cache la menubar pour une interface plus épurée
        self.menuBar().setVisible(False)
        
    def create_toolbar(self):
        """Créer la barre d'actions rapides moderne"""
        toolbar = QToolBar("Actions Rapides")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setStyleSheet("""
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f5f7fa);
                border-bottom: 2px solid #e1e8ed;
                spacing: 8px;
                padding: 8px 15px;
            }
            QToolBar QToolButton {
                background-color: white;
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                padding: 8px 16px;
                margin: 2px;
                font-size: 13px;
                font-weight: 600;
                color: #2c3e50;
            }
            QToolBar QToolButton:hover {
                background-color: #3498db;
                border-color: #2980b9;
                color: white;
            }
            QToolBar QToolButton:pressed {
                background-color: #2980b9;
            }
            QToolBar::separator {
                background-color: #bdc3c7;
                width: 1px;
                margin: 8px 12px;
            }
        """)
        self.addToolBar(toolbar)
        
        # Actions rapides selon le rôle
        if self.user.role in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
            add_student = QAction("👤 Nouvel Élève", self)
            add_student.setToolTip("Créer un nouveau dossier élève")
            add_student.triggered.connect(self.quick_add_student)
            toolbar.addAction(add_student)
        
        if self.user.role in [UserRole.ADMIN, UserRole.CASHIER]:
            add_payment = QAction("💳 Nouveau Paiement", self)
            add_payment.setToolTip("Enregistrer un paiement")
            add_payment.triggered.connect(self.quick_add_payment)
            toolbar.addAction(add_payment)
        
        if self.user.role in [UserRole.ADMIN, UserRole.INSTRUCTOR]:
            add_session = QAction("🚗 Nouvelle Session", self)
            add_session.setToolTip("Planifier une session de conduite")
            add_session.triggered.connect(self.quick_add_session)
            toolbar.addAction(add_session)
        
        if self.user.role in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
            add_exam = QAction("📝 Nouvel Examen", self)
            add_exam.setToolTip("Inscrire un élève à un examen")
            add_exam.triggered.connect(self.quick_add_exam)
            toolbar.addAction(add_exam)
        
        if self.user.role == UserRole.ADMIN:
            add_instructor = QAction("👨‍🏫 Nouveau Moniteur", self)
            add_instructor.setToolTip("Ajouter un moniteur")
            add_instructor.triggered.connect(self.quick_add_instructor)
            toolbar.addAction(add_instructor)
        
        toolbar.addSeparator()
        
        # Actualiser
        refresh = QAction("🔄 Actualiser", self)
        refresh.setToolTip("Rafraîchir la vue actuelle")
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
        # Utiliser le dashboard professionnel avec QtCharts (stable, moderne)
        try:
            from .widgets.dashboard_professional import DashboardProfessionalWidget
            self.set_current_module(DashboardProfessionalWidget(self.user))
            self.statusBar().showMessage("Dashboard Professionnel")
        except Exception as e:
            # Fallback vers dashboard simple en cas d'erreur
            print(f"[ERREUR] Dashboard professionnel: {e}")
            import traceback
            traceback.print_exc()
            from .widgets.dashboard_simple import DashboardSimpleWidget
            self.set_current_module(DashboardSimpleWidget(self.user))
            self.statusBar().showMessage("Dashboard Simple (Fallback)")
        
        # Version avec graphiques matplotlib (désactivée)
        # try:
        #     from .widgets.dashboard_advanced import DashboardAdvancedWidget
        #     self.set_current_module(DashboardAdvancedWidget(self.user))
        #     self.statusBar().showMessage("Dashboard avec graphiques")
        # except Exception as e:
        #     logger.error(f"Erreur dashboard avancé: {e}")
        #     from .widgets.dashboard_simple import DashboardSimpleWidget
        #     self.set_current_module(DashboardSimpleWidget(self.user))
        #     self.statusBar().showMessage("Dashboard (mode simplifié)")
        
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
        """Afficher le module Paiements (Dashboard + Gestion)"""
        from .widgets.payments_main import PaymentsMainWidget
        
        self.set_current_module(PaymentsMainWidget())
        self.statusBar().showMessage("💰 Module Paiements - Dashboard Financier & Gestion")
        
    def show_instructors(self):
        """Afficher le module Moniteurs (Dashboard + Gestion)"""
        from .widgets.instructors_main import InstructorsMainWidget
        
        self.set_current_module(InstructorsMainWidget())
        self.statusBar().showMessage("👨‍🏫 Module Moniteurs - Dashboard & Gestion")
        
    def show_vehicles(self):
        """Afficher le module Véhicules (Dashboard + Gestion)"""
        from .widgets.vehicles_main import VehiclesMainWidget
        
        self.set_current_module(VehiclesMainWidget())
        self.statusBar().showMessage("🚗 Module Véhicules - Dashboard & Gestion du Parc")
        
    def show_exams(self):
        """Afficher le module Examens (Dashboard + Gestion)"""
        from .widgets.exams_main import ExamsMainWidget
        
        self.set_current_module(ExamsMainWidget())
        self.statusBar().showMessage("📝 Module Examens - Dashboard & Gestion Complète")
        

    def show_reports(self):
        """Afficher le module Rapports"""
        try:
            # Essayer version avec graphiques
            from .widgets.reports_main import ReportsMainWidget
            self.set_current_module(ReportsMainWidget())
            self.statusBar().showMessage("📊 Module Rapports - Analyses & Graphiques")
        except (ImportError, ModuleNotFoundError):
            # Fallback: version simplifiée sans matplotlib
            from .widgets.reports_simple import ReportsSimpleWidget
            self.set_current_module(ReportsSimpleWidget())
            self.statusBar().showMessage("📊 Module Rapports - Analyses (mode simplifié)")
        
    def show_settings(self):
        """Afficher les paramètres"""
        from src.views.widgets import SettingsWidget
        
        widget = SettingsWidget()
        self.content_stack.addWidget(widget)
        self.content_stack.setCurrentWidget(widget)
        self.statusBar().showMessage("⚙️ Module Paramètres - Configuration Complète")
        
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
        try:
            from src.views.widgets.students_enhanced import StudentDetailDialog
            from src.controllers import StudentController
            
            dialog = StudentDetailDialog(parent=self)
            if dialog.exec():
                self.statusBar().showMessage("✅ Élève ajouté avec succès", 3000)
                # Actualiser si on est sur le module étudiants
                if hasattr(self.current_module, 'load_students'):
                    self.current_module.load_students()
        except Exception as e:
            logger.error(f"Erreur quick_add_student: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le formulaire:\n{str(e)}")
        
    def quick_add_payment(self):
        """Action rapide : Ajouter un paiement"""
        try:
            from src.views.widgets.payments_management import AddPaymentDialog
            
            dialog = AddPaymentDialog(parent=self)
            if dialog.exec():
                self.statusBar().showMessage("✅ Paiement enregistré avec succès", 3000)
                # Actualiser si on est sur le module paiements
                if hasattr(self.current_module, 'load_payments'):
                    self.current_module.load_payments()
        except Exception as e:
            logger.error(f"Erreur quick_add_payment: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le formulaire:\n{str(e)}")
    
    def quick_add_session(self):
        """Action rapide : Ajouter une session de conduite"""
        try:
            from src.views.widgets.planning_enhanced import SessionDialog
            
            dialog = SessionDialog(self)
            if dialog.exec():
                self.statusBar().showMessage("✅ Session planifiée avec succès", 3000)
                # Actualiser si on est sur le module planning
                if hasattr(self.current_module, 'load_sessions'):
                    self.current_module.load_sessions()
        except Exception as e:
            logger.error(f"Erreur quick_add_session: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le formulaire:\n{str(e)}")
    
    def quick_add_exam(self):
        """Action rapide : Inscrire un élève à un examen"""
        try:
            from src.views.widgets.exams_management import ExamDialog
            
            dialog = ExamDialog(self)
            if dialog.exec():
                self.statusBar().showMessage("✅ Examen enregistré avec succès", 3000)
                # Actualiser si on est sur le module examens
                if hasattr(self.current_module, 'load_exams'):
                    self.current_module.load_exams()
        except Exception as e:
            logger.error(f"Erreur quick_add_exam: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le formulaire:\n{str(e)}")
    
    def quick_add_instructor(self):
        """Action rapide : Ajouter un moniteur"""
        try:
            from src.views.widgets.instructors_management import AddInstructorDialog
            
            dialog = AddInstructorDialog(parent=self)
            if dialog.exec():
                self.statusBar().showMessage("✅ Moniteur ajouté avec succès", 3000)
                # Actualiser si on est sur le module moniteurs
                if hasattr(self.current_module, 'load_instructors'):
                    self.current_module.load_instructors()
        except Exception as e:
            logger.error(f"Erreur quick_add_instructor: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le formulaire:\n{str(e)}")
        
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
