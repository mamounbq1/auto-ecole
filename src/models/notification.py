"""
Modèle pour l'historique et la gestion des notifications
Phase 2 - Système de Notifications Automatiques
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import Base


class NotificationType(str, Enum):
    """Types de notifications"""
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"  # Notification dans l'interface


class NotificationCategory(str, Enum):
    """Catégories de notifications"""
    SESSION_REMINDER = "rappel_session"
    EXAM_CONVOCATION = "convocation_examen"
    EXAM_RESULT = "resultat_examen"
    PAYMENT_RECEIPT = "recu_paiement"
    PAYMENT_REMINDER = "rappel_paiement"
    MAINTENANCE_ALERT = "alerte_maintenance"
    DOCUMENT_EXPIRY = "expiration_document"
    BIRTHDAY = "anniversaire"
    GENERAL = "general"


class NotificationStatus(str, Enum):
    """Statuts de notification"""
    PENDING = "en_attente"
    SENT = "envoyee"
    DELIVERED = "delivree"
    FAILED = "echec"
    READ = "lue"  # Pour notifications in-app


class NotificationPriority(str, Enum):
    """Priorités de notification"""
    LOW = "basse"
    NORMAL = "normale"
    HIGH = "haute"
    URGENT = "urgente"


class Notification(Base):
    """
    Modèle pour l'historique et la gestion des notifications
    
    Ce modèle permet de :
    - Stocker l'historique de toutes les notifications envoyées
    - Gérer les notifications in-app (alertes dans l'interface)
    - Planifier des notifications futures
    - Suivre le statut de livraison
    - Réessayer les envois échoués
    """
    
    __tablename__ = 'notifications'
    
    # Clé primaire
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Type et catégorie
    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    category = Column(SQLEnum(NotificationCategory), nullable=False)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL, nullable=False)
    
    # Destinataire (peut être lié à un student, instructor, ou général)
    recipient_type = Column(String(50), nullable=True)  # student, instructor, admin, user
    recipient_id = Column(Integer, nullable=True)  # ID du destinataire
    recipient_email = Column(String(200), nullable=True)
    recipient_phone = Column(String(20), nullable=True)
    recipient_name = Column(String(200), nullable=True)
    
    # Contenu
    subject = Column(String(500), nullable=True)  # Pour emails
    message = Column(Text, nullable=False)
    html_content = Column(Text, nullable=True)  # Pour emails HTML
    
    # Métadonnées
    title = Column(String(200), nullable=True)  # Pour notifications in-app
    icon = Column(String(50), nullable=True)  # Emoji ou icône
    action_url = Column(String(500), nullable=True)  # URL ou action à déclencher
    
    # Statut et timestamps
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)  # Date d'envoi prévue (pour planification)
    sent_at = Column(DateTime, nullable=True)  # Date d'envoi réelle
    delivered_at = Column(DateTime, nullable=True)  # Date de livraison
    read_at = Column(DateTime, nullable=True)  # Date de lecture (in-app)
    
    # Gestion des erreurs et retry
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Données contextuelles (JSON)
    context_data = Column(Text, nullable=True)  # Données additionnelles (JSON serialisé)
    
    # Relations (optionnelles, selon le besoin)
    # student_id = Column(Integer, ForeignKey('students.id', ondelete='SET NULL'), nullable=True)
    # student = relationship('Student', back_populates='notifications')
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    created_by = Column(String(200), nullable=True)  # Utilisateur ayant créé la notification
    
    def __repr__(self):
        return (
            f"<Notification(id={self.id}, type={self.notification_type.value}, "
            f"category={self.category.value}, status={self.status.value}, "
            f"recipient={self.recipient_name}, scheduled={self.scheduled_at})>"
        )
    
    def mark_as_sent(self, sent_at=None):
        """Marquer la notification comme envoyée"""
        self.status = NotificationStatus.SENT
        self.sent_at = sent_at or datetime.now()
    
    def mark_as_delivered(self, delivered_at=None):
        """Marquer la notification comme livrée"""
        self.status = NotificationStatus.DELIVERED
        self.delivered_at = delivered_at or datetime.now()
    
    def mark_as_failed(self, error_message: str):
        """Marquer la notification comme échouée"""
        self.status = NotificationStatus.FAILED
        self.error_message = error_message
        self.retry_count += 1
    
    def mark_as_read(self, read_at=None):
        """Marquer la notification in-app comme lue"""
        self.status = NotificationStatus.READ
        self.read_at = read_at or datetime.now()
    
    def can_retry(self) -> bool:
        """Vérifier si la notification peut être renvoyée"""
        return (
            self.status == NotificationStatus.FAILED and
            self.retry_count < self.max_retries
        )
    
    def is_overdue(self) -> bool:
        """Vérifier si la notification est en retard"""
        if self.status != NotificationStatus.PENDING or not self.scheduled_at:
            return False
        return datetime.now() > self.scheduled_at
    
    def minutes_until_scheduled(self) -> int:
        """Minutes jusqu'à l'envoi prévu"""
        if not self.scheduled_at:
            return 0
        delta = self.scheduled_at - datetime.now()
        return int(delta.total_seconds() / 60)
    
    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'notification_type': self.notification_type.value,
            'category': self.category.value,
            'priority': self.priority.value,
            'recipient_type': self.recipient_type,
            'recipient_id': self.recipient_id,
            'recipient_email': self.recipient_email,
            'recipient_phone': self.recipient_phone,
            'recipient_name': self.recipient_name,
            'subject': self.subject,
            'message': self.message,
            'title': self.title,
            'icon': self.icon,
            'action_url': self.action_url,
            'status': self.status.value,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_overdue': self.is_overdue(),
            'can_retry': self.can_retry(),
            'minutes_until_scheduled': self.minutes_until_scheduled()
        }
