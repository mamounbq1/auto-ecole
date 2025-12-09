"""
Centre de notifications avec historique et gestion
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QComboBox, QTabWidget,
    QMessageBox, QMenu, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor

from src.controllers import NotificationController
from src.models import NotificationCategory, NotificationStatus, NotificationPriority
from datetime import datetime


class NotificationCenter(QWidget):
    """Centre de notifications avec onglets et gestion"""
    
    notification_read = Signal(int)  # Signal quand une notification est lue
    
    def __init__(self, user_id=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id  # ID de l'utilisateur (pour IN_APP)
        self.current_notifications = []
        self.setMinimumWidth(400)
        self.setup_ui()
        self.load_notifications()
        
        # Auto-refresh toutes les 30 secondes
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_notifications)
        self.refresh_timer.start(30000)  # 30 secondes
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Onglets
        tabs = QTabWidget()
        
        # Onglet Non lues
        unread_widget = self.create_notification_list("unread")
        tabs.addTab(unread_widget, "📬 Non Lues")
        
        # Onglet Toutes
        all_widget = self.create_notification_list("all")
        tabs.addTab(all_widget, "📋 Toutes")
        
        # Onglet Par catégorie
        category_widget = self.create_category_filter()
        tabs.addTab(category_widget, "🏷️ Par Catégorie")
        
        layout.addWidget(tabs)
        
        self.unread_list = unread_widget.findChild(QListWidget)
        self.all_list = all_widget.findChild(QListWidget)
        self.category_list = category_widget.findChild(QListWidget)
    
    def create_header(self):
        """Créer le header"""
        header = QWidget()
        header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #e74c3c, stop:1 #c0392b);
            padding: 15px;
        """)
        
        layout = QHBoxLayout(header)
        
        # Titre
        title = QLabel("🔔 Centre de Notifications")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Badge compteur
        self.badge_label = QLabel("0")
        self.badge_label.setStyleSheet("""
            background-color: white;
            color: #e74c3c;
            border-radius: 12px;
            padding: 5px 10px;
            font-weight: bold;
            font-size: 14px;
        """)
        layout.addWidget(self.badge_label)
        
        # Bouton Marquer toutes comme lues
        mark_all_btn = QPushButton("✅ Tout Marquer Lu")
        mark_all_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #c0392b;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ecf0f1;
            }
        """)
        mark_all_btn.setCursor(Qt.PointingHandCursor)
        mark_all_btn.clicked.connect(self.mark_all_as_read)
        layout.addWidget(mark_all_btn)
        
        # Bouton Export CSV
        export_btn = QPushButton("📤 Export")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #c0392b;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ecf0f1;
            }
        """)
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.clicked.connect(self.export_notifications)
        layout.addWidget(export_btn)
        
        # Bouton Rafraîchir
        refresh_btn = QPushButton("🔄")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #c0392b;
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ecf0f1;
            }
        """)
        refresh_btn.setToolTip("Rafraîchir")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self.load_notifications)
        layout.addWidget(refresh_btn)
        
        return header
    
    def create_notification_list(self, list_type: str):
        """Créer une liste de notifications"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        list_widget = QListWidget()
        list_widget.setObjectName(f"notif_list_{list_type}")
        list_widget.itemClicked.connect(self.on_notification_clicked)
        list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        list_widget.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(list_widget)
        
        return widget
    
    def create_category_filter(self):
        """Créer le filtre par catégorie"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Sélecteur de catégorie
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Catégorie:"))
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("Toutes les catégories", None)
        for cat in NotificationCategory:
            self.category_combo.addItem(cat.value, cat)
        self.category_combo.currentIndexChanged.connect(self.filter_by_category)
        filter_layout.addWidget(self.category_combo, 1)
        
        layout.addLayout(filter_layout)
        
        # Liste
        list_widget = QListWidget()
        list_widget.itemClicked.connect(self.on_notification_clicked)
        list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        list_widget.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(list_widget)
        
        return widget
    
    def load_notifications(self):
        """Charger les notifications"""
        try:
            if self.user_id:
                # Notifications IN_APP pour cet utilisateur
                notifications = NotificationController.get_in_app_notifications_for_user(
                    self.user_id,
                    unread_only=False
                )
            else:
                # Toutes les notifications récentes (limité)
                from src.models import get_session
                session = get_session()
                notifications = session.query(Notification).order_by(
                    Notification.created_at.desc()
                ).limit(100).all()
            
            self.current_notifications = notifications
            self.display_notifications()
            self.update_badge()
            
        except Exception as e:
            print(f"Erreur chargement notifications: {e}")
    
    def display_notifications(self):
        """Afficher les notifications dans les listes"""
        # Non lues
        self.unread_list.clear()
        unread = [n for n in self.current_notifications if not n.is_read]
        self.populate_list(self.unread_list, unread)
        
        # Toutes
        self.all_list.clear()
        self.populate_list(self.all_list, self.current_notifications)
        
        # Par catégorie (filter appliqué si sélectionné)
        self.filter_by_category()
    
    def populate_list(self, list_widget: QListWidget, notifications):
        """Remplir une liste avec des notifications"""
        for notif in notifications:
            item = self.create_notification_item(notif)
            list_widget.addItem(item)
        
        if not notifications:
            empty_item = QListWidgetItem("📭 Aucune notification")
            empty_item.setForeground(QColor("#95a5a6"))
            empty_item.setFlags(Qt.NoItemFlags)  # Non sélectionnable
            list_widget.addItem(empty_item)
    
    def create_notification_item(self, notif):
        """Créer un item de notification"""
        # Icône selon priorité
        icon = "🔴" if notif.priority == NotificationPriority.URGENT else \
               "🟠" if notif.priority == NotificationPriority.HIGH else \
               "🟡" if notif.priority == NotificationPriority.MEDIUM else "⚪"
        
        # Texte
        time_str = notif.created_at.strftime("%d/%m %H:%M") if notif.created_at else ""
        text = f"{icon} {notif.title or notif.category.value} - {time_str}"
        
        if notif.message and len(notif.message) > 50:
            text += f"\n   {notif.message[:50]}..."
        elif notif.message:
            text += f"\n   {notif.message}"
        
        item = QListWidgetItem(text)
        item.setData(Qt.UserRole, notif.id)
        
        # Style selon statut lu/non lu
        if notif.is_read:
            item.setForeground(QColor("#7f8c8d"))
            font = QFont("Arial", 9)
        else:
            item.setForeground(QColor("#2c3e50"))
            font = QFont("Arial", 9, QFont.Bold)
        
        item.setFont(font)
        
        return item
    
    def filter_by_category(self):
        """Filtrer par catégorie"""
        category = self.category_combo.currentData()
        
        if category:
            filtered = [n for n in self.current_notifications if n.category == category]
        else:
            filtered = self.current_notifications
        
        self.category_list.clear()
        self.populate_list(self.category_list, filtered)
    
    def update_badge(self):
        """Mettre à jour le badge compteur"""
        unread_count = len([n for n in self.current_notifications if not n.is_read])
        self.badge_label.setText(str(unread_count))
    
    def on_notification_clicked(self, item: QListWidgetItem):
        """Gérer le clic sur une notification"""
        notif_id = item.data(Qt.UserRole)
        if notif_id:
            # Marquer comme lue
            try:
                NotificationController.mark_notification_as_read(notif_id)
                self.load_notifications()
                self.notification_read.emit(notif_id)
                
                # Afficher le détail
                notif = next((n for n in self.current_notifications if n.id == notif_id), None)
                if notif:
                    self.show_notification_detail(notif)
            except Exception as e:
                print(f"Erreur mark as read: {e}")
    
    def show_notification_detail(self, notif):
        """Afficher le détail d'une notification"""
        detail_text = f"""
Notification #{notif.id}

Catégorie: {notif.category.value}
Priorité: {notif.priority.value}
Type: {notif.notification_type.value}

Titre: {notif.title or 'N/A'}

Message:
{notif.message or 'Aucun message'}

Destinataire: {notif.recipient_name or 'N/A'}
Créée le: {notif.created_at.strftime('%d/%m/%Y à %H:%M') if notif.created_at else 'N/A'}
Statut: {'Lu' if notif.is_read else 'Non lu'}
"""
        QMessageBox.information(self, "Détail Notification", detail_text)
    
    def show_context_menu(self, position):
        """Menu contextuel"""
        sender = self.sender()
        item = sender.itemAt(position)
        
        if not item or not item.data(Qt.UserRole):
            return
        
        notif_id = item.data(Qt.UserRole)
        notif = next((n for n in self.current_notifications if n.id == notif_id), None)
        
        if not notif:
            return
        
        menu = QMenu(self)
        
        detail_action = menu.addAction("👁️ Voir le détail")
        
        if not notif.is_read:
            read_action = menu.addAction("✅ Marquer comme lu")
        
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Supprimer")
        delete_action.setStyleSheet("color: #e74c3c;")
        
        action = menu.exec(sender.viewport().mapToGlobal(position))
        
        if action == detail_action:
            self.show_notification_detail(notif)
        elif action and action.text() == "✅ Marquer comme lu":
            NotificationController.mark_notification_as_read(notif_id)
            self.load_notifications()
        elif action == delete_action:
            # Confirmation de suppression
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "Voulez-vous vraiment supprimer cette notification ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success = NotificationController.delete_notification(notif_id)
                if success:
                    QMessageBox.information(self, "✅ Succès", "Notification supprimée")
                    self.load_notifications()
                else:
                    QMessageBox.warning(self, "⚠️ Erreur", "Impossible de supprimer la notification")
    
    def mark_all_as_read(self):
        """Marquer toutes les notifications comme lues"""
        try:
            unread = [n for n in self.current_notifications if not n.is_read]
            
            for notif in unread:
                NotificationController.mark_notification_as_read(notif.id)
            
            QMessageBox.information(
                self,
                "Succès",
                f"{len(unread)} notification(s) marquée(s) comme lue(s)"
            )
            self.load_notifications()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {e}")
    
    def export_notifications(self):
        """Exporter les notifications en CSV"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Exporter les notifications",
                f"notifications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if filename:
                # Exporter les notifications actuelles (filtrées)
                success, result = NotificationController.export_to_csv(
                    self.current_notifications,
                    filename
                )
                
                if success:
                    QMessageBox.information(
                        self,
                        "✅ Export réussi",
                        f"{len(self.current_notifications)} notifications exportées vers:\n{result}"
                    )
                else:
                    QMessageBox.warning(self, "⚠️ Erreur", f"Erreur lors de l'export:\n{result}")
                    
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
    
    def get_unread_count(self) -> int:
        """Obtenir le nombre de notifications non lues"""
        return len([n for n in self.current_notifications if not n.is_read])
