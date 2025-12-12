"""
Widget de gestion des utilisateurs/staff (admin seulement)
Permet de créer, modifier, supprimer des utilisateurs et gérer leurs rôles/permissions
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QDialog, QFormLayout, QCheckBox,
    QTextEdit, QMessageBox, QHeaderView, QGroupBox, QGridLayout,
    QComboBox, QListWidget, QListWidgetItem, QAbstractItemView, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon

from src.controllers.user_controller import UserController
from src.models import User, Role
from src.utils.auth import get_current_user, has_permission
from src.utils.logger import get_logger

logger = get_logger()


class UserManagementWidget(QWidget):
    """Widget principal de gestion des utilisateurs"""
    
    # Signal émis quand un utilisateur est modifié
    user_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_user = get_current_user()
        self.users = []
        self.init_ui()
        self.load_users()
    
    def init_ui(self):
        """Initialiser l'interface"""
        layout = QVBoxLayout(self)
        
        # Titre et description
        title_label = QLabel("👥 Gestion des Utilisateurs (Staff)")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        desc_label = QLabel("Créer et gérer les comptes utilisateurs avec leurs rôles et permissions")
        desc_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(desc_label)
        
        # Barre d'outils
        toolbar = QHBoxLayout()
        
        # Bouton Ajouter
        self.btn_add = QPushButton("➕ Ajouter Utilisateur")
        self.btn_add.clicked.connect(self.add_user)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        toolbar.addWidget(self.btn_add)
        
        # Bouton Rafraîchir
        self.btn_refresh = QPushButton("🔄 Rafraîchir")
        self.btn_refresh.clicked.connect(self.load_users)
        toolbar.addWidget(self.btn_refresh)
        
        toolbar.addStretch()
        
        # Statistiques
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("background-color: #f5f5f5; padding: 8px; border-radius: 4px;")
        toolbar.addWidget(self.stats_label)
        
        layout.addLayout(toolbar)
        
        # Table des utilisateurs
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom d'utilisateur", "Nom complet", "Rôles",
            "Email", "Téléphone", "Statut", "Actions"
        ])
        
        # Configuration de la table
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        # Vérifier les permissions
        if not has_permission('manage_users'):
            self.btn_add.setEnabled(False)
            self.btn_add.setToolTip("Permission requise : manage_users")
    
    def load_users(self):
        """Charger la liste des utilisateurs"""
        try:
            self.users = UserController.get_all_users(include_inactive=True)
            self.populate_table()
            self.update_statistics()
        except Exception as e:
            logger.error(f"Erreur lors du chargement des utilisateurs : {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les utilisateurs : {str(e)}")
    
    def populate_table(self):
        """Remplir la table avec les utilisateurs"""
        self.table.setRowCount(0)
        
        for user in self.users:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            
            # Nom d'utilisateur
            self.table.setItem(row, 1, QTableWidgetItem(user.username))
            
            # Nom complet
            self.table.setItem(row, 2, QTableWidgetItem(user.full_name))
            
            # Rôles
            role_names = user.get_role_names()
            roles_text = ", ".join(role_names) if role_names else "Aucun rôle"
            self.table.setItem(row, 3, QTableWidgetItem(roles_text))
            
            # Email
            self.table.setItem(row, 4, QTableWidgetItem(user.email or "-"))
            
            # Téléphone
            self.table.setItem(row, 5, QTableWidgetItem(user.phone or "-"))
            
            # Statut
            if user.is_locked:
                status = "🔒 Verrouillé"
                status_style = "color: red;"
            elif not user.is_active:
                status = "❌ Inactif"
                status_style = "color: orange;"
            else:
                status = "✅ Actif"
                status_style = "color: green;"
            
            status_item = QTableWidgetItem(status)
            status_item.setForeground(Qt.GlobalColor.red if not user.is_active else Qt.GlobalColor.green)
            self.table.setItem(row, 6, status_item)
            
            # Actions
            actions_widget = self.create_action_buttons(user)
            self.table.setCellWidget(row, 7, actions_widget)
    
    def create_action_buttons(self, user: User) -> QWidget:
        """Créer les boutons d'action pour un utilisateur"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Bouton Modifier
        btn_edit = QPushButton("✏️ Modifier")
        btn_edit.clicked.connect(lambda: self.edit_user(user))
        btn_edit.setStyleSheet("padding: 4px 8px;")
        layout.addWidget(btn_edit)
        
        # Bouton Mot de passe
        btn_password = QPushButton("🔑 Mot de passe")
        btn_password.clicked.connect(lambda: self.change_password(user))
        btn_password.setStyleSheet("padding: 4px 8px;")
        layout.addWidget(btn_password)
        
        # Bouton Déverrouiller (si verrouillé)
        if user.is_locked:
            btn_unlock = QPushButton("🔓 Déverrouiller")
            btn_unlock.clicked.connect(lambda: self.unlock_user(user))
            btn_unlock.setStyleSheet("padding: 4px 8px; background-color: #FFA726;")
            layout.addWidget(btn_unlock)
        
        # Bouton Désactiver/Activer
        if user.is_active:
            btn_deactivate = QPushButton("❌")
            btn_deactivate.setToolTip("Désactiver l'utilisateur")
            btn_deactivate.clicked.connect(lambda: self.toggle_active(user))
            btn_deactivate.setStyleSheet("padding: 4px 8px; background-color: #FF5252;")
            layout.addWidget(btn_deactivate)
        else:
            btn_activate = QPushButton("✅")
            btn_activate.setToolTip("Activer l'utilisateur")
            btn_activate.clicked.connect(lambda: self.toggle_active(user))
            btn_activate.setStyleSheet("padding: 4px 8px; background-color: #4CAF50;")
            layout.addWidget(btn_activate)
        
        layout.addStretch()
        return widget
    
    def update_statistics(self):
        """Mettre à jour les statistiques"""
        stats = UserController.get_user_statistics()
        self.stats_label.setText(
            f"📊 Total: {stats['total']} | "
            f"✅ Actifs: {stats['active']} | "
            f"❌ Inactifs: {stats['inactive']} | "
            f"🔒 Verrouillés: {stats['locked']}"
        )
    
    def add_user(self):
        """Ajouter un nouvel utilisateur"""
        dialog = UserEditDialog(None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users()
            self.user_changed.emit()
    
    def edit_user(self, user: User):
        """Modifier un utilisateur"""
        dialog = UserEditDialog(user, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users()
            self.user_changed.emit()
    
    def change_password(self, user: User):
        """Changer le mot de passe d'un utilisateur"""
        dialog = PasswordChangeDialog(user, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.user_changed.emit()
    
    def unlock_user(self, user: User):
        """Déverrouiller un utilisateur"""
        reply = QMessageBox.question(
            self, "Confirmer",
            f"Déverrouiller le compte de '{user.username}' ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = UserController.unlock_user(user.id)
            if success:
                QMessageBox.information(self, "Succès", message)
                self.load_users()
                self.user_changed.emit()
            else:
                QMessageBox.warning(self, "Erreur", message)
    
    def toggle_active(self, user: User):
        """Activer/Désactiver un utilisateur"""
        action = "désactiver" if user.is_active else "activer"
        reply = QMessageBox.question(
            self, "Confirmer",
            f"Voulez-vous {action} le compte de '{user.username}' ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = UserController.update_user(user.id, is_active=not user.is_active)
            if success:
                QMessageBox.information(self, "Succès", message)
                self.load_users()
                self.user_changed.emit()
            else:
                QMessageBox.warning(self, "Erreur", message)


class UserEditDialog(QDialog):
    """Dialog pour ajouter/modifier un utilisateur"""
    
    def __init__(self, user: User = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.is_edit_mode = user is not None
        self.all_roles = UserController.get_all_roles()
        
        self.setWindowTitle("Modifier l'utilisateur" if self.is_edit_mode else "Nouvel utilisateur")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self.init_ui()
        
        if self.is_edit_mode:
            self.load_user_data()
    
    def init_ui(self):
        """Initialiser l'interface"""
        layout = QVBoxLayout(self)
        
        # Formulaire
        form = QFormLayout()
        
        # Nom d'utilisateur
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Ex: jdupont")
        form.addRow("Nom d'utilisateur *:", self.txt_username)
        
        # Nom complet
        self.txt_fullname = QLineEdit()
        self.txt_fullname.setPlaceholderText("Ex: Jean Dupont")
        form.addRow("Nom complet *:", self.txt_fullname)
        
        # Email
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("Ex: jean.dupont@exemple.com")
        form.addRow("Email:", self.txt_email)
        
        # Téléphone
        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("Ex: +212 6XX-XXXXXX")
        form.addRow("Téléphone:", self.txt_phone)
        
        # Mot de passe (seulement en mode création)
        if not self.is_edit_mode:
            self.txt_password = QLineEdit()
            self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.txt_password.setPlaceholderText("Mot de passe")
            form.addRow("Mot de passe *:", self.txt_password)
            
            self.txt_password_confirm = QLineEdit()
            self.txt_password_confirm.setEchoMode(QLineEdit.EchoMode.Password)
            self.txt_password_confirm.setPlaceholderText("Confirmer le mot de passe")
            form.addRow("Confirmer *:", self.txt_password_confirm)
        
        layout.addLayout(form)
        
        # Section Rôles
        roles_group = QGroupBox("Rôles et Permissions")
        roles_layout = QVBoxLayout(roles_group)
        
        roles_label = QLabel("Sélectionnez un ou plusieurs rôles pour cet utilisateur:")
        roles_label.setStyleSheet("font-weight: bold; color: #333;")
        roles_layout.addWidget(roles_label)
        
        # Liste des rôles avec checkboxes
        self.roles_list = QListWidget()
        self.roles_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        
        for role in self.all_roles:
            item = QListWidgetItem()
            checkbox = QCheckBox(f"{role.display_name} - {role.description}")
            checkbox.setProperty("role_id", role.id)
            self.roles_list.addItem(item)
            self.roles_list.setItemWidget(item, checkbox)
        
        roles_layout.addWidget(self.roles_list)
        layout.addWidget(roles_group)
        
        # Notes
        notes_label = QLabel("Notes:")
        layout.addWidget(notes_label)
        self.txt_notes = QTextEdit()
        self.txt_notes.setPlaceholderText("Notes optionnelles...")
        self.txt_notes.setMaximumHeight(80)
        layout.addWidget(self.txt_notes)
        
        # Boutons
        buttons = QHBoxLayout()
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_cancel)
        
        btn_save = QPushButton("Enregistrer")
        btn_save.clicked.connect(self.save_user)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        buttons.addWidget(btn_save)
        
        layout.addLayout(buttons)
    
    def load_user_data(self):
        """Charger les données de l'utilisateur"""
        if not self.user:
            return
        
        self.txt_username.setText(self.user.username)
        self.txt_fullname.setText(self.user.full_name)
        self.txt_email.setText(self.user.email or "")
        self.txt_phone.setText(self.user.phone or "")
        self.txt_notes.setPlainText(self.user.notes or "")
        
        # Cocher les rôles de l'utilisateur
        user_role_ids = {r.id for r in self.user.roles} if hasattr(self.user, 'roles') else set()
        
        for i in range(self.roles_list.count()):
            item = self.roles_list.item(i)
            checkbox = self.roles_list.itemWidget(item)
            if isinstance(checkbox, QCheckBox):
                role_id = checkbox.property("role_id")
                if role_id in user_role_ids:
                    checkbox.setChecked(True)
    
    def get_selected_role_ids(self) -> list:
        """Obtenir les IDs des rôles sélectionnés"""
        role_ids = []
        for i in range(self.roles_list.count()):
            item = self.roles_list.item(i)
            checkbox = self.roles_list.itemWidget(item)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                role_id = checkbox.property("role_id")
                role_ids.append(role_id)
        return role_ids
    
    def save_user(self):
        """Enregistrer l'utilisateur"""
        # Validation
        username = self.txt_username.text().strip()
        fullname = self.txt_fullname.text().strip()
        
        if not username or not fullname:
            QMessageBox.warning(self, "Validation", "Le nom d'utilisateur et le nom complet sont requis")
            return
        
        if not self.is_edit_mode:
            password = self.txt_password.text()
            password_confirm = self.txt_password_confirm.text()
            
            if not password:
                QMessageBox.warning(self, "Validation", "Le mot de passe est requis")
                return
            
            if password != password_confirm:
                QMessageBox.warning(self, "Validation", "Les mots de passe ne correspondent pas")
                return
        
        # Rôles
        role_ids = self.get_selected_role_ids()
        if not role_ids:
            reply = QMessageBox.question(
                self, "Aucun rôle",
                "Aucun rôle sélectionné. L'utilisateur n'aura aucune permission. Continuer ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Enregistrer
        email = self.txt_email.text().strip() or None
        phone = self.txt_phone.text().strip() or None
        notes = self.txt_notes.toPlainText().strip() or None
        
        if self.is_edit_mode:
            # Mise à jour
            success, message = UserController.update_user(
                self.user.id,
                username=username,
                full_name=fullname,
                email=email,
                phone=phone,
                role_ids=role_ids,
                notes=notes
            )
        else:
            # Création
            password = self.txt_password.text()
            success, message, user = UserController.create_user(
                username=username,
                password=password,
                full_name=fullname,
                email=email,
                phone=phone,
                role_ids=role_ids,
                notes=notes
            )
        
        if success:
            QMessageBox.information(self, "Succès", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", message)


class PasswordChangeDialog(QDialog):
    """Dialog pour changer le mot de passe d'un utilisateur"""
    
    def __init__(self, user: User, parent=None):
        super().__init__(parent)
        self.user = user
        
        self.setWindowTitle(f"Changer le mot de passe - {user.username}")
        self.setMinimumWidth(400)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface"""
        layout = QVBoxLayout(self)
        
        # Info utilisateur
        info_label = QLabel(f"Utilisateur: <b>{self.user.full_name}</b> ({self.user.username})")
        info_label.setStyleSheet("background-color: #f5f5f5; padding: 8px; border-radius: 4px;")
        layout.addWidget(info_label)
        
        # Afficher le mot de passe actuel (si disponible)
        if self.user.password_plain:
            current_pwd_label = QLabel(f"🔑 Mot de passe actuel: <b>{self.user.password_plain}</b>")
            current_pwd_label.setStyleSheet("background-color: #FFF9C4; padding: 8px; border-radius: 4px; margin: 10px 0;")
            layout.addWidget(current_pwd_label)
        
        # Formulaire
        form = QFormLayout()
        
        self.txt_new_password = QLineEdit()
        self.txt_new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_new_password.setPlaceholderText("Nouveau mot de passe")
        form.addRow("Nouveau mot de passe *:", self.txt_new_password)
        
        self.txt_confirm_password = QLineEdit()
        self.txt_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_confirm_password.setPlaceholderText("Confirmer le mot de passe")
        form.addRow("Confirmer *:", self.txt_confirm_password)
        
        layout.addLayout(form)
        
        # Checkbox pour afficher les mots de passe
        self.chk_show_password = QCheckBox("Afficher les mots de passe")
        self.chk_show_password.stateChanged.connect(self.toggle_password_visibility)
        layout.addWidget(self.chk_show_password)
        
        # Boutons
        buttons = QHBoxLayout()
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_cancel)
        
        btn_save = QPushButton("Changer le mot de passe")
        btn_save.clicked.connect(self.change_password)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        buttons.addWidget(btn_save)
        
        layout.addLayout(buttons)
    
    def toggle_password_visibility(self):
        """Afficher/Masquer les mots de passe"""
        if self.chk_show_password.isChecked():
            self.txt_new_password.setEchoMode(QLineEdit.EchoMode.Normal)
            self.txt_confirm_password.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.txt_new_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.txt_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
    
    def change_password(self):
        """Changer le mot de passe"""
        new_password = self.txt_new_password.text()
        confirm_password = self.txt_confirm_password.text()
        
        if not new_password:
            QMessageBox.warning(self, "Validation", "Le nouveau mot de passe est requis")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Validation", "Les mots de passe ne correspondent pas")
            return
        
        if len(new_password) < 4:
            QMessageBox.warning(self, "Validation", "Le mot de passe doit contenir au moins 4 caractères")
            return
        
        # Changer le mot de passe (par admin, donc stocké en clair)
        success, message = UserController.change_password(self.user.id, new_password, changed_by_admin=True)
        
        if success:
            QMessageBox.information(self, "Succès", 
                f"Mot de passe changé avec succès!\n\nNouveau mot de passe: {new_password}\n\n"
                "⚠️ Notez ce mot de passe ou communiquez-le à l'utilisateur."
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", message)
