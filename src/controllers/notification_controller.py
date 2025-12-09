"""
Contrôleur pour la gestion automatique des notifications
Phase 2 - Système de Notifications Automatiques
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from sqlalchemy import and_, or_
import json
import csv
from pathlib import Path
import os

from src.models import (
    Notification, NotificationType, NotificationCategory, NotificationStatus, NotificationPriority,
    Student, Instructor, Session, Exam, Payment, Vehicle, VehicleMaintenance,
    get_session
)
from src.utils import get_logger
from src.utils.notifications import NotificationManager

logger = get_logger()


class NotificationController:
    """Contrôleur pour gérer les notifications automatiques"""
    
    def __init__(self):
        """Initialiser le contrôleur"""
        self.notification_manager = NotificationManager()
    
    # ========== CRUD Operations ==========
    
    @staticmethod
    def create_notification(notification_data: dict) -> Optional[Notification]:
        """
        Créer une nouvelle notification
        
        Args:
            notification_data: Dictionnaire avec les données de la notification
            
        Returns:
            Notification créée ou None si erreur
        """
        try:
            session = get_session()
            
            notification = Notification(
                notification_type=notification_data['notification_type'],
                category=notification_data['category'],
                priority=notification_data.get('priority', NotificationPriority.NORMAL),
                recipient_type=notification_data.get('recipient_type'),
                recipient_id=notification_data.get('recipient_id'),
                recipient_email=notification_data.get('recipient_email'),
                recipient_phone=notification_data.get('recipient_phone'),
                recipient_name=notification_data.get('recipient_name'),
                subject=notification_data.get('subject'),
                message=notification_data['message'],
                html_content=notification_data.get('html_content'),
                title=notification_data.get('title'),
                icon=notification_data.get('icon'),
                action_url=notification_data.get('action_url'),
                scheduled_at=notification_data.get('scheduled_at'),
                context_data=json.dumps(notification_data.get('context_data')) if notification_data.get('context_data') else None,
                created_by=notification_data.get('created_by')
            )
            
            session.add(notification)
            session.commit()
            session.refresh(notification)
            
            logger.info(f"Notification créée : ID {notification.id}, type {notification.notification_type.value}")
            return notification
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la notification : {e}")
            session.rollback()
            return None
    
    @staticmethod
    def get_notification_by_id(notification_id: int) -> Optional[Notification]:
        """Obtenir une notification par ID"""
        try:
            session = get_session()
            return session.query(Notification).filter(
                Notification.id == notification_id
            ).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la notification {notification_id} : {e}")
            return None
    
    @staticmethod
    def get_pending_notifications() -> List[Notification]:
        """Obtenir les notifications en attente d'envoi"""
        try:
            session = get_session()
            now = datetime.now()
            
            return session.query(Notification).filter(
                and_(
                    Notification.status == NotificationStatus.PENDING,
                    or_(
                        Notification.scheduled_at.is_(None),
                        Notification.scheduled_at <= now
                    )
                )
            ).order_by(Notification.priority.desc(), Notification.scheduled_at).all()
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des notifications en attente : {e}")
            return []
    
    @staticmethod
    def get_failed_notifications_for_retry() -> List[Notification]:
        """Obtenir les notifications échouées qui peuvent être réessayées"""
        try:
            session = get_session()
            
            notifications = session.query(Notification).filter(
                Notification.status == NotificationStatus.FAILED
            ).all()
            
            return [n for n in notifications if n.can_retry()]
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des notifications à réessayer : {e}")
            return []
    
    @staticmethod
    def get_in_app_notifications_for_user(
        recipient_type: str,
        recipient_id: int,
        include_read: bool = False
    ) -> List[Notification]:
        """
        Obtenir les notifications in-app pour un utilisateur
        
        Args:
            recipient_type: Type de destinataire (student, instructor, admin)
            recipient_id: ID du destinataire
            include_read: Inclure les notifications lues
        """
        try:
            session = get_session()
            query = session.query(Notification).filter(
                and_(
                    Notification.notification_type == NotificationType.IN_APP,
                    Notification.recipient_type == recipient_type,
                    Notification.recipient_id == recipient_id
                )
            )
            
            if not include_read:
                query = query.filter(Notification.status != NotificationStatus.READ)
            
            return query.order_by(Notification.created_at.desc()).all()
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des notifications in-app : {e}")
            return []
    
    @staticmethod
    def mark_notification_as_read(notification_id: int) -> bool:
        """Marquer une notification in-app comme lue"""
        try:
            session = get_session()
            notification = session.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification:
                notification.mark_as_read()
                session.commit()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors du marquage de la notification comme lue : {e}")
            session.rollback()
            return False
    
    @staticmethod
    def delete_notification(notification_id: int) -> bool:
        """
        Supprimer une notification
        
        Args:
            notification_id: ID de la notification à supprimer
            
        Returns:
            True si succès, False sinon
        """
        try:
            session = get_session()
            notification = session.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification:
                session.delete(notification)
                session.commit()
                logger.info(f"Notification {notification_id} supprimée")
                return True
            
            logger.warning(f"Notification {notification_id} introuvable")
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la notification : {e}")
            session.rollback()
            return False
    
    @staticmethod
    def search_notifications(query: str, category: Optional[NotificationCategory] = None, 
                           priority: Optional[NotificationPriority] = None,
                           is_read: Optional[bool] = None) -> List[Notification]:
        """
        Rechercher des notifications
        
        Args:
            query: Terme de recherche (dans titre, message, destinataire)
            category: Filtrer par catégorie (optionnel)
            priority: Filtrer par priorité (optionnel)
            is_read: Filtrer par statut de lecture (optionnel)
            
        Returns:
            Liste des notifications correspondantes
        """
        try:
            session = get_session()
            
            filters = []
            
            # Recherche textuelle
            if query:
                filters.append(
                    or_(
                        Notification.title.ilike(f"%{query}%"),
                        Notification.message.ilike(f"%{query}%"),
                        Notification.recipient_name.ilike(f"%{query}%")
                    )
                )
            
            # Filtres additionnels
            if category:
                filters.append(Notification.category == category)
            
            if priority:
                filters.append(Notification.priority == priority)
            
            if is_read is not None:
                filters.append(Notification.is_read == is_read)
            
            # Requête
            notifications_query = session.query(Notification)
            
            if filters:
                notifications_query = notifications_query.filter(and_(*filters))
            
            notifications = notifications_query.order_by(
                Notification.created_at.desc()
            ).all()
            
            logger.info(f"{len(notifications)} notifications trouvées pour '{query}'")
            return notifications
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de notifications : {e}")
            return []
    
    @staticmethod
    def export_to_csv(notifications: Optional[List[Notification]] = None, 
                     filename: Optional[str] = None) -> tuple[bool, str]:
        """
        Exporter les notifications vers un fichier CSV
        
        Args:
            notifications: Liste des notifications à exporter (None = toutes)
            filename: Nom du fichier CSV (None = généré automatiquement)
        
        Returns:
            tuple[bool, str]: (succès, message ou chemin du fichier)
        """
        try:
            session = get_session()
            
            # Si aucune notification fournie, récupérer toutes
            if notifications is None:
                notifications = session.query(Notification).order_by(
                    Notification.created_at.desc()
                ).all()
            
            if not notifications:
                return False, "Aucune notification à exporter"
            
            # Générer le nom de fichier si non fourni
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"notifications_export_{timestamp}.csv"
            
            # Assurer l'extension .csv
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            # Créer le répertoire d'export si nécessaire
            export_dir = "exports"
            Path(export_dir).mkdir(parents=True, exist_ok=True)
            filepath = os.path.join(export_dir, filename)
            
            # Écrire le fichier CSV
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = [
                    'ID', 'Type', 'Catégorie', 'Priorité', 'Titre', 'Message',
                    'Destinataire Type', 'Destinataire ID', 'Destinataire Nom',
                    'Lu', 'Lu Le', 'Envoyé', 'Créé Le'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for notif in notifications:
                    writer.writerow({
                        'ID': notif.id,
                        'Type': notif.notification_type.value if notif.notification_type else '',
                        'Catégorie': notif.category.value if notif.category else '',
                        'Priorité': notif.priority.value if notif.priority else '',
                        'Titre': notif.title or '',
                        'Message': notif.message or '',
                        'Destinataire Type': notif.recipient_type or '',
                        'Destinataire ID': notif.recipient_id or '',
                        'Destinataire Nom': notif.recipient_name or '',
                        'Lu': 'Oui' if notif.is_read else 'Non',
                        'Lu Le': notif.read_at.strftime("%Y-%m-%d %H:%M") if notif.read_at else '',
                        'Envoyé': 'Oui' if notif.is_sent else 'Non',
                        'Créé Le': notif.created_at.strftime("%Y-%m-%d %H:%M") if notif.created_at else ''
                    })
            
            logger.info(f"{len(notifications)} notifications exportées vers {filepath}")
            return True, filepath
            
        except Exception as e:
            error_msg = f"Erreur lors de l'export CSV : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    # ========== Envoi de Notifications ==========
    
    def send_notification(self, notification_id: int) -> bool:
        """
        Envoyer une notification
        
        Args:
            notification_id: ID de la notification à envoyer
            
        Returns:
            True si succès, False sinon
        """
        try:
            session = get_session()
            notification = session.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if not notification:
                logger.error(f"Notification {notification_id} introuvable")
                return False
            
            # Si notification in-app, on la marque juste comme envoyée
            if notification.notification_type == NotificationType.IN_APP:
                notification.mark_as_sent()
                session.commit()
                return True
            
            # Envoi selon le type
            success = False
            error_msg = ""
            
            if notification.notification_type == NotificationType.EMAIL:
                success, message = self.notification_manager.send_email(
                    to_email=notification.recipient_email,
                    subject=notification.subject or "Notification",
                    body=notification.message,
                    html=bool(notification.html_content)
                )
                if not success:
                    error_msg = message
            
            elif notification.notification_type == NotificationType.SMS:
                success, message = self.notification_manager.send_sms(
                    to_phone=notification.recipient_phone,
                    message=notification.message
                )
                if not success:
                    error_msg = message
            
            # Mettre à jour le statut
            if success:
                notification.mark_as_sent()
                notification.mark_as_delivered()  # Pour l'instant, on assume livraison immédiate
            else:
                notification.mark_as_failed(error_msg)
            
            session.commit()
            return success
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification {notification_id} : {e}")
            session.rollback()
            return False
    
    def process_pending_notifications(self) -> Dict[str, int]:
        """
        Traiter toutes les notifications en attente
        
        Returns:
            Dictionnaire avec le nombre de succès et d'échecs
        """
        pending = self.get_pending_notifications()
        
        results = {
            'total': len(pending),
            'success': 0,
            'failed': 0
        }
        
        for notification in pending:
            if self.send_notification(notification.id):
                results['success'] += 1
            else:
                results['failed'] += 1
        
        logger.info(f"Traitement des notifications : {results['success']}/{results['total']} envoyées")
        return results
    
    def retry_failed_notifications(self) -> Dict[str, int]:
        """
        Réessayer d'envoyer les notifications échouées
        
        Returns:
            Dictionnaire avec le nombre de succès et d'échecs
        """
        failed = self.get_failed_notifications_for_retry()
        
        results = {
            'total': len(failed),
            'success': 0,
            'failed': 0
        }
        
        for notification in failed:
            if self.send_notification(notification.id):
                results['success'] += 1
            else:
                results['failed'] += 1
        
        logger.info(f"Retry notifications : {results['success']}/{results['total']} envoyées")
        return results
    
    # ========== Notifications Automatiques Spécialisées ==========
    
    def schedule_session_reminder(
        self,
        session_obj: Session,
        hours_before: int = 24,
        notification_types: List[NotificationType] = None
    ) -> List[Notification]:
        """
        Planifier un rappel de session
        
        Args:
            session_obj: Session concernée
            hours_before: Nombre d'heures avant la session
            notification_types: Types de notifications à envoyer
            
        Returns:
            Liste des notifications créées
        """
        if notification_types is None:
            notification_types = [NotificationType.SMS, NotificationType.IN_APP]
        
        notifications = []
        
        if not session_obj.student:
            return notifications
        
        scheduled_at = session_obj.start_datetime - timedelta(hours=hours_before)
        
        # Si la date est dans le passé, envoyer immédiatement
        if scheduled_at < datetime.now():
            scheduled_at = None
        
        message = (
            f"Rappel : Vous avez une session de conduite le "
            f"{session_obj.start_datetime.strftime('%d/%m/%Y à %H:%M')} "
            f"avec {session_obj.instructor.full_name if session_obj.instructor else 'votre moniteur'}."
        )
        
        for notif_type in notification_types:
            notification_data = {
                'notification_type': notif_type,
                'category': NotificationCategory.SESSION_REMINDER,
                'priority': NotificationPriority.HIGH,
                'recipient_type': 'student',
                'recipient_id': session_obj.student_id,
                'recipient_name': session_obj.student.full_name,
                'message': message,
                'title': "📅 Rappel de Session",
                'icon': "📅",
                'scheduled_at': scheduled_at,
                'context_data': {
                    'session_id': session_obj.id,
                    'session_date': session_obj.start_datetime.isoformat()
                }
            }
            
            if notif_type == NotificationType.SMS:
                notification_data['recipient_phone'] = session_obj.student.phone
            elif notif_type == NotificationType.EMAIL:
                notification_data['recipient_email'] = session_obj.student.email
                notification_data['subject'] = "Rappel de Session de Conduite"
            
            notification = self.create_notification(notification_data)
            if notification:
                notifications.append(notification)
        
        return notifications
    
    def schedule_exam_convocation(
        self,
        exam: Exam,
        notification_types: List[NotificationType] = None
    ) -> List[Notification]:
        """Planifier une convocation d'examen"""
        if notification_types is None:
            notification_types = [NotificationType.EMAIL, NotificationType.IN_APP]
        
        notifications = []
        
        if not exam.student:
            return notifications
        
        default_location = "centre d'examen"
        message = (
            f"Convocation à l'examen {exam.exam_type.value} le "
            f"{exam.scheduled_date.strftime('%d/%m/%Y à %H:%M')} "
            f"au {exam.location or default_location}."
        )
        
        for notif_type in notification_types:
            notification_data = {
                'notification_type': notif_type,
                'category': NotificationCategory.EXAM_CONVOCATION,
                'priority': NotificationPriority.URGENT,
                'recipient_type': 'student',
                'recipient_id': exam.student_id,
                'recipient_name': exam.student.full_name,
                'message': message,
                'title': "📝 Convocation d'Examen",
                'icon': "📝",
                'context_data': {
                    'exam_id': exam.id,
                    'exam_type': exam.exam_type.value
                }
            }
            
            if notif_type == NotificationType.EMAIL:
                notification_data['recipient_email'] = exam.student.email
                notification_data['subject'] = f"Convocation - Examen {exam.exam_type.value}"
            
            notification = self.create_notification(notification_data)
            if notification:
                notifications.append(notification)
        
        return notifications
    
    def send_payment_reminder(
        self,
        student: Student,
        notification_types: List[NotificationType] = None
    ) -> List[Notification]:
        """Envoyer un rappel de paiement pour un élève avec une dette
        
        Balance = total_due - total_paid
        Balance > 0 = Dette (l'étudiant doit de l'argent)
        """
        if notification_types is None:
            notification_types = [NotificationType.SMS, NotificationType.IN_APP]
        
        notifications = []
        
        # Balance < 0 signifie dette (balance = total_paid - total_due)
        if student.balance >= 0:
            return notifications
        
        debt_amount = student.balance  # Plus besoin de abs() car balance est déjà positif
        message = (
            f"Rappel : Vous avez une dette de {debt_amount:,.2f} DH. "
            f"Merci de régulariser votre situation."
        )
        
        for notif_type in notification_types:
            notification_data = {
                'notification_type': notif_type,
                'category': NotificationCategory.PAYMENT_REMINDER,
                'priority': NotificationPriority.HIGH,
                'recipient_type': 'student',
                'recipient_id': student.id,
                'recipient_name': student.full_name,
                'message': message,
                'title': "💰 Rappel de Paiement",
                'icon': "💰",
                'context_data': {
                    'student_id': student.id,
                    'debt_amount': debt_amount
                }
            }
            
            if notif_type == NotificationType.SMS:
                notification_data['recipient_phone'] = student.phone
            elif notif_type == NotificationType.EMAIL:
                notification_data['recipient_email'] = student.email
                notification_data['subject'] = "Rappel de Paiement"
            
            notification = self.create_notification(notification_data)
            if notification:
                notifications.append(notification)
        
        return notifications
    
    def send_maintenance_alert(
        self,
        vehicle: Vehicle,
        maintenance: VehicleMaintenance,
        notification_types: List[NotificationType] = None
    ) -> List[Notification]:
        """Envoyer une alerte de maintenance véhicule (pour admin/gestionnaire)"""
        if notification_types is None:
            notification_types = [NotificationType.IN_APP]
        
        notifications = []
        
        message = (
            f"Alerte maintenance : Véhicule {vehicle.plate_number} - "
            f"{maintenance.maintenance_type.value} prévue le "
            f"{maintenance.scheduled_date.strftime('%d/%m/%Y')}."
        )
        
        for notif_type in notification_types:
            notification_data = {
                'notification_type': notif_type,
                'category': NotificationCategory.MAINTENANCE_ALERT,
                'priority': NotificationPriority.NORMAL,
                'recipient_type': 'admin',
                'message': message,
                'title': "🔧 Alerte Maintenance Véhicule",
                'icon': "🔧",
                'context_data': {
                    'vehicle_id': vehicle.id,
                    'maintenance_id': maintenance.id
                }
            }
            
            notification = self.create_notification(notification_data)
            if notification:
                notifications.append(notification)
        
        return notifications
    
    # ========== Statistiques ==========
    
    @staticmethod
    def get_notification_statistics(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """Obtenir les statistiques des notifications"""
        try:
            session = get_session()
            query = session.query(Notification)
            
            if start_date:
                query = query.filter(Notification.created_at >= datetime.combine(start_date, datetime.min.time()))
            if end_date:
                query = query.filter(Notification.created_at <= datetime.combine(end_date, datetime.max.time()))
            
            notifications = query.all()
            
            if not notifications:
                return {
                    'total': 0,
                    'by_type': {},
                    'by_category': {},
                    'by_status': {},
                    'by_priority': {}
                }
            
            stats = {
                'total': len(notifications),
                'by_type': {},
                'by_category': {},
                'by_status': {},
                'by_priority': {}
            }
            
            # Par type
            for notif_type in NotificationType:
                count = len([n for n in notifications if n.notification_type == notif_type])
                stats['by_type'][notif_type.value] = count
            
            # Par catégorie
            for category in NotificationCategory:
                count = len([n for n in notifications if n.category == category])
                stats['by_category'][category.value] = count
            
            # Par statut
            for status in NotificationStatus:
                count = len([n for n in notifications if n.status == status])
                stats['by_status'][status.value] = count
            
            # Par priorité
            for priority in NotificationPriority:
                count = len([n for n in notifications if n.priority == priority])
                stats['by_priority'][priority.value] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques : {e}")
            return {}
