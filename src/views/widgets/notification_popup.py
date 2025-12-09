"""
Popup de notification pour alertes importantes
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont

from src.models import Notification, NotificationPriority


class NotificationPopup(QDialog):
    """Popup pour afficher une notification importante"""
    
    notification_clicked = Signal(int)  # Signal avec ID de la notification
    
    def __init__(self, notification: Notification, parent=None):
        super().__init__(parent)
        self.notification = notification
        self.setWindowTitle("🔔 Nouvelle Notification")
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setMinimumSize(400, 250)
        self.setup_ui()
        
        # Auto-fermeture après 10 secondes (sauf URGENT)
        if notification.priority != NotificationPriority.URGENT:
            QTimer.singleShot(10000, self.auto_close)
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Couleur selon priorité
        colors = {
            NotificationPriority.URGENT: ("#e74c3c", "#c0392b"),
            NotificationPriority.HIGH: ("#f39c12", "#e67e22"),
            NotificationPriority.MEDIUM: ("#3498db", "#2980b9"),
            NotificationPriority.LOW: ("#95a5a6", "#7f8c8d"),
        }
        color1, color2 = colors.get(self.notification.priority, ("#95a5a6", "#7f8c8d"))
        
        # Header
        header = QWidget()
        header.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {color1}, stop:1 {color2});
            padding: 15px;
        """)
        
        header_layout = QHBoxLayout(header)
        
        # Icône selon priorité
        icon = "🔴" if self.notification.priority == NotificationPriority.URGENT else \
               "🟠" if self.notification.priority == NotificationPriority.HIGH else \
               "🟡" if self.notification.priority == NotificationPriority.MEDIUM else "⚪"
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon_label)
        
        # Titre
        title = QLabel(self.notification.title or "Notification")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title, 1)
        
        # Bouton fermer
        close_btn = QPushButton("✖")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.2);
                border-radius: 3px;
            }
        """)
        close_btn.setMaximumWidth(30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)
        
        layout.addWidget(header)
        
        # Corps
        body = QWidget()
        body.setStyleSheet("background-color: white; padding: 15px;")
        body_layout = QVBoxLayout(body)
        
        # Catégorie et priorité
        info_layout = QHBoxLayout()
        
        category_label = QLabel(f"📋 {self.notification.category.value}")
        category_label.setStyleSheet(f"color: {color1}; font-weight: bold;")
        info_layout.addWidget(category_label)
        
        info_layout.addStretch()
        
        priority_label = QLabel(f"⚡ {self.notification.priority.value}")
        priority_label.setStyleSheet(f"color: {color1}; font-weight: bold;")
        info_layout.addWidget(priority_label)
        
        body_layout.addLayout(info_layout)
        
        # Message
        if self.notification.message:
            message_text = QTextEdit()
            message_text.setPlainText(self.notification.message)
            message_text.setReadOnly(True)
            message_text.setMaximumHeight(120)
            message_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 10px;
                    background-color: #f8f9fa;
                }
            """)
            body_layout.addWidget(message_text)
        
        # Date/heure
        if self.notification.created_at:
            time_label = QLabel(f"🕐 {self.notification.created_at.strftime('%d/%m/%Y à %H:%M')}")
            time_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
            body_layout.addWidget(time_label)
        
        layout.addWidget(body)
        
        # Footer avec boutons
        footer = QWidget()
        footer.setStyleSheet("background-color: #ecf0f1; padding: 10px;")
        footer_layout = QHBoxLayout(footer)
        
        # Bouton Fermer
        close_footer_btn = QPushButton("Fermer")
        close_footer_btn.clicked.connect(self.reject)
        footer_layout.addWidget(close_footer_btn)
        
        footer_layout.addStretch()
        
        # Bouton Voir détails
        details_btn = QPushButton("👁️ Voir Détails")
        details_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color1};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color2};
            }}
        """)
        details_btn.setCursor(Qt.PointingHandCursor)
        details_btn.clicked.connect(self.view_details)
        footer_layout.addWidget(details_btn)
        
        layout.addWidget(footer)
    
    def view_details(self):
        """Voir les détails de la notification"""
        self.notification_clicked.emit(self.notification.id)
        self.accept()
    
    def auto_close(self):
        """Fermeture automatique"""
        if self.isVisible():
            self.reject()
