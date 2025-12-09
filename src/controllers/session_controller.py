"""
Contrôleur pour la gestion des sessions de conduite
"""

from typing import List, Optional
from datetime import datetime, date, timedelta

from src.models import Session, SessionStatus, get_session
from src.utils import get_logger, get_export_manager

logger = get_logger()


class SessionController:
    """Contrôleur pour gérer les sessions"""
    
    @staticmethod
    def get_sessions_by_date_range(start_date: date, end_date: date) -> List[Session]:
        """Obtenir les sessions dans une plage de dates"""
        try:
            session_db = get_session()
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            return session_db.query(Session).filter(
                Session.start_datetime >= start_datetime,
                Session.start_datetime <= end_datetime
            ).order_by(Session.start_datetime).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des sessions : {e}")
            return []
    
    @staticmethod
    def get_all_sessions() -> List[Session]:
        """Obtenir toutes les sessions"""
        try:
            session = get_session()
            sessions = session.query(Session).order_by(Session.start_datetime.desc()).all()
            return sessions
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des sessions : {e}")
            return []
    
    @staticmethod
    def get_today_sessions() -> List[Session]:
        """Obtenir les sessions du jour"""
        today = date.today()
        return SessionController.get_sessions_by_date_range(today, today)
    
    @staticmethod
    def get_upcoming_sessions(days: int = 7) -> List[Session]:
        """Obtenir les sessions à venir"""
        today = date.today()
        future_date = today + timedelta(days=days)
        return SessionController.get_sessions_by_date_range(today, future_date)
    
    @staticmethod
    def get_session_by_id(session_id: int) -> Optional[Session]:
        """Obtenir une session par ID"""
        try:
            session_db = get_session()
            return session_db.query(Session).filter(Session.id == session_id).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la session : {e}")
            return None
    
    @staticmethod
    def get_sessions_by_student(student_id: int) -> List[Session]:
        """Obtenir toutes les sessions d'un élève"""
        try:
            session_db = get_session()
            return session_db.query(Session).filter(Session.student_id == student_id).order_by(Session.start_datetime.desc()).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des sessions de l'élève : {e}")
            return []
    
    @staticmethod
    def check_instructor_conflict(instructor_id: int, start_dt: datetime, end_dt: datetime, 
                                  exclude_session_id: Optional[int] = None) -> List[Session]:
        """
        Vérifier les conflits d'horaire pour un moniteur
        
        Args:
            instructor_id: ID du moniteur
            start_dt: Date/heure de début
            end_dt: Date/heure de fin
            exclude_session_id: ID de session à exclure (pour édition)
            
        Returns:
            Liste des sessions en conflit
        """
        try:
            session_db = get_session()
            query = session_db.query(Session).filter(
                Session.instructor_id == instructor_id,
                Session.status != SessionStatus.CANCELLED,
                Session.start_datetime < end_dt,
                Session.end_datetime > start_dt
            )
            
            if exclude_session_id:
                query = query.filter(Session.id != exclude_session_id)
            
            return query.all()
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des conflits moniteur : {e}")
            return []
    
    @staticmethod
    def check_vehicle_conflict(vehicle_id: int, start_dt: datetime, end_dt: datetime,
                               exclude_session_id: Optional[int] = None) -> List[Session]:
        """
        Vérifier les conflits d'horaire pour un véhicule
        
        Args:
            vehicle_id: ID du véhicule
            start_dt: Date/heure de début
            end_dt: Date/heure de fin
            exclude_session_id: ID de session à exclure (pour édition)
            
        Returns:
            Liste des sessions en conflit
        """
        try:
            session_db = get_session()
            query = session_db.query(Session).filter(
                Session.vehicle_id == vehicle_id,
                Session.status != SessionStatus.CANCELLED,
                Session.start_datetime < end_dt,
                Session.end_datetime > start_dt
            )
            
            if exclude_session_id:
                query = query.filter(Session.id != exclude_session_id)
            
            return query.all()
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des conflits véhicule : {e}")
            return []
    
    @staticmethod
    def check_student_conflict(student_id: int, start_dt: datetime, end_dt: datetime,
                               exclude_session_id: Optional[int] = None) -> List[Session]:
        """
        Vérifier les conflits d'horaire pour un élève
        
        Args:
            student_id: ID de l'élève
            start_dt: Date/heure de début
            end_dt: Date/heure de fin
            exclude_session_id: ID de session à exclure (pour édition)
            
        Returns:
            Liste des sessions en conflit
        """
        try:
            session_db = get_session()
            query = session_db.query(Session).filter(
                Session.student_id == student_id,
                Session.status != SessionStatus.CANCELLED,
                Session.start_datetime < end_dt,
                Session.end_datetime > start_dt
            )
            
            if exclude_session_id:
                query = query.filter(Session.id != exclude_session_id)
            
            return query.all()
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des conflits élève : {e}")
            return []
    
    @staticmethod
    def create_session(session_data: dict) -> Optional[Session]:
        """
        Créer une nouvelle session
        
        Args:
            session_data: Dictionnaire avec les données de la session
            
        Returns:
            Session créée ou None si erreur
        """
        try:
            session_db = get_session()
            
            # Créer la session
            new_session = Session(
                student_id=session_data['student_id'],
                instructor_id=session_data.get('instructor_id'),
                vehicle_id=session_data.get('vehicle_id'),
                session_type=session_data['session_type'],
                start_datetime=session_data['start_datetime'],
                end_datetime=session_data['end_datetime'],
                status=session_data.get('status', SessionStatus.SCHEDULED),
                notes=session_data.get('notes')
            )
            
            session_db.add(new_session)
            session_db.commit()
            session_db.refresh(new_session)
            
            logger.info(f"Session créée : ID {new_session.id}")
            return new_session
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la session : {e}")
            session_db.rollback()
            return None
    
    @staticmethod
    def update_session(session_id: int, session_data: dict) -> bool:
        """
        Mettre à jour une session
        
        Args:
            session_id: ID de la session
            session_data: Dictionnaire avec les nouvelles données
            
        Returns:
            True si succès, False sinon
        """
        try:
            session_db = get_session()
            session_obj = session_db.query(Session).filter(Session.id == session_id).first()
            
            if not session_obj:
                logger.error(f"Session {session_id} introuvable")
                return False
            
            # Mettre à jour les attributs
            for key, value in session_data.items():
                if hasattr(session_obj, key):
                    setattr(session_obj, key, value)
            
            session_db.commit()
            logger.info(f"Session {session_id} mise à jour")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la session : {e}")
            session_db.rollback()
            return False
    
    @staticmethod
    def delete_session(session_id: int) -> bool:
        """
        Supprimer une session
        
        Args:
            session_id: ID de la session
            
        Returns:
            True si succès, False sinon
        """
        try:
            session_db = get_session()
            session_obj = session_db.query(Session).filter(Session.id == session_id).first()
            
            if not session_obj:
                logger.error(f"Session {session_id} introuvable")
                return False
            
            session_db.delete(session_obj)
            session_db.commit()
            logger.info(f"Session {session_id} supprimée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la session : {e}")
            session_db.rollback()
            return False
    
    @staticmethod
    def export_to_csv(sessions: Optional[List[Session]] = None,
                     filename: Optional[str] = None) -> tuple[bool, str]:
        """
        Exporter les sessions vers un fichier CSV
        
        Args:
            sessions: Liste de sessions (optionnel, toutes si None)
            filename: Nom du fichier (optionnel)
        
        Returns:
            Tuple (success, filepath/message)
        """
        try:
            if sessions is None:
                sessions = SessionController.get_all_sessions()
            
            if not sessions:
                return False, "Aucune session à exporter"
            
            # Préparer les données avec infos complètes
            data = []
            for session_obj in sessions:
                session_dict = {
                    'id': session_obj.id,
                    'student_id': session_obj.student_id,
                    'student_name': session_obj.student.full_name if session_obj.student else '',
                    'student_cin': session_obj.student.cin if session_obj.student else '',
                    'instructor_id': session_obj.instructor_id,
                    'instructor_name': session_obj.instructor.full_name if session_obj.instructor else '',
                    'vehicle_id': session_obj.vehicle_id,
                    'vehicle_plate': session_obj.vehicle.plate_number if session_obj.vehicle else '',
                    'session_type': session_obj.session_type,
                    'start_datetime': session_obj.start_datetime.isoformat() if session_obj.start_datetime else '',
                    'end_datetime': session_obj.end_datetime.isoformat() if session_obj.end_datetime else '',
                    'duration_hours': session_obj.duration_hours,
                    'status': session_obj.status.value if session_obj.status else '',
                    'performance_rating': session_obj.performance_rating,
                    'notes': session_obj.notes or '',
                    'created_at': session_obj.created_at.isoformat() if session_obj.created_at else ''
                }
                data.append(session_dict)
            
            # Exporter avec ExportManager
            export_mgr = get_export_manager()
            filepath = export_mgr.export_to_csv(data, 'sessions', filename)
            
            logger.info(f"{len(sessions)} sessions exportées vers {filepath}")
            return True, filepath
            
        except Exception as e:
            error_msg = f"Erreur lors de l'export : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
