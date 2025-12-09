"""
Bouton avec badge de notifications
"""

from PySide6.QtWidgets import QPushButton, QLabel
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QColor, QFont


class NotificationBadgeButton(QPushButton):
    """Bouton de notifications avec badge compteur"""
    
    badge_clicked = Signal()  # Signal quand le bouton est cliqué
    
    def __init__(self, parent=None):
        super().__init__("🔔", parent)
        self.unread_count = 0
        self.setMinimumSize(50, 40)
        self.setMaximumSize(50, 40)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Centre de Notifications")
        
        # Style
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 24px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 5px;
            }
        """)
        
        # Connecter le signal
        self.clicked.connect(self.badge_clicked.emit)
    
    def set_unread_count(self, count: int):
        """Définir le nombre de notifications non lues"""
        self.unread_count = count
        self.update()  # Redessiner le widget
        
        # Mettre à jour le tooltip
        if count > 0:
            self.setToolTip(f"🔔 {count} notification(s) non lue(s)")
        else:
            self.setToolTip("🔔 Centre de Notifications")
    
    def paintEvent(self, event):
        """Dessiner le bouton avec le badge"""
        super().paintEvent(event)
        
        # Dessiner le badge si count > 0
        if self.unread_count > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Position du badge (coin supérieur droit)
            badge_x = self.width() - 20
            badge_y = 5
            badge_size = 18
            
            # Cercle rouge
            painter.setBrush(QColor("#e74c3c"))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(badge_x, badge_y, badge_size, badge_size)
            
            # Texte blanc
            painter.setPen(QColor("white"))
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            
            # Limiter à 99+
            text = str(self.unread_count) if self.unread_count < 100 else "99+"
            
            # Centrer le texte dans le cercle
            text_rect = painter.fontMetrics().boundingRect(text)
            text_x = badge_x + (badge_size - text_rect.width()) / 2
            text_y = badge_y + (badge_size + text_rect.height()) / 2 - 2
            
            painter.drawText(int(text_x), int(text_y), text)
