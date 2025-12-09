"""
Contrôleur pour la gestion des moniteurs
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime

from sqlalchemy import or_, func
from src.models import Instructor, Session, SessionStatus, get_session
from src.utils import get_logger, get_export_manager

logger = get_logger()


class InstructorController:
    """Contrôleur pour gérer les opérations sur les moniteurs"""
    
    @staticmethod
    def get_all_instructors(available_only: bool = False) -> List[Instructor]:
        """
        Récupérer tous les moniteurs
        
        Args:
            available_only: Filtrer uniquement les moniteurs disponibles
        
        Returns:
            Liste des moniteurs
        """
        try:
            session = get_session()
            query = session.query(Instructor)
            
            if available_only:
                query = query.filter(Instructor.is_available == True)
            
            instructors = query.order_by(Instructor.full_name).all()
            return instructors
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des moniteurs : {e}")
            return []
    
    @staticmethod
    def get_instructor_by_id(instructor_id: int) -> Optional[Instructor]:
        """
        Récupérer un moniteur par son ID
        
        Args:
            instructor_id: ID du moniteur
        
        Returns:
            Moniteur ou None
        """
        try:
            session = get_session()
            return session.query(Instructor).filter(Instructor.id == instructor_id).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du moniteur {instructor_id} : {e}")
            return None
    
    @staticmethod
    def get_instructor_by_cin(cin: str) -> Optional[Instructor]:
        """
        Récupérer un moniteur par son CIN
        
        Args:
            cin: Numéro CIN
        
        Returns:
            Moniteur ou None
        """
        try:
            session = get_session()
            return session.query(Instructor).filter(Instructor.cin == cin).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du moniteur CIN {cin} : {e}")
            return None
    
    @staticmethod
    def get_instructor_by_license(license_number: str) -> Optional[Instructor]:
        """
        Récupérer un moniteur par son numéro de permis
        
        Args:
            license_number: Numéro de permis
        
        Returns:
            Moniteur ou None
        """
        try:
            session = get_session()
            return session.query(Instructor).filter(Instructor.license_number == license_number).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du moniteur (permis {license_number}) : {e}")
            return None
    
    @staticmethod
    def search_instructors(query: str) -> List[Instructor]:
        """
        Rechercher des moniteurs par nom, CIN, téléphone ou email
        
        Args:
            query: Terme de recherche
        
        Returns:
            Liste des moniteurs correspondants
        """
        try:
            session = get_session()
            search_term = f"%{query}%"
            
            instructors = session.query(Instructor).filter(
                or_(
                    Instructor.full_name.like(search_term),
                    Instructor.cin.like(search_term),
                    Instructor.phone.like(search_term),
                    Instructor.email.like(search_term),
                    Instructor.license_number.like(search_term)
                )
            ).order_by(Instructor.full_name).all()
            
            return instructors
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de moniteurs : {e}")
            return []
    
    @staticmethod
    def create_instructor(full_name: str, cin: str, phone: str, 
                         license_number: str, **kwargs) -> tuple[bool, str, Optional[Instructor]]:
        """
        Créer un nouveau moniteur
        
        Args:
            full_name: Nom complet
            cin: Numéro CIN
            phone: Téléphone
            license_number: Numéro de permis
            **kwargs: Autres paramètres optionnels
        
        Returns:
            Tuple (success, message, instructor)
        """
        try:
            session = get_session()
            
            # Vérifier que le CIN n'existe pas déjà
            existing = session.query(Instructor).filter(Instructor.cin == cin).first()
            if existing:
                return False, "Un moniteur avec ce CIN existe déjà", None
            
            # Vérifier que le numéro de permis n'existe pas déjà
            existing_license = session.query(Instructor).filter(Instructor.license_number == license_number).first()
            if existing_license:
                return False, "Un moniteur avec ce numéro de permis existe déjà", None
            
            # Créer le moniteur
            instructor = Instructor(
                full_name=full_name,
                cin=cin,
                phone=phone,
                license_number=license_number,
                **kwargs
            )
            
            session.add(instructor)
            session.commit()
            session.refresh(instructor)
            
            logger.info(f"Moniteur créé : {full_name} (CIN: {cin})")
            return True, "Moniteur créé avec succès", instructor
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la création du moniteur : {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def update_instructor(instructor_id: int, **kwargs) -> tuple[bool, str]:
        """
        Mettre à jour un moniteur
        
        Args:
            instructor_id: ID du moniteur
            **kwargs: Champs à mettre à jour
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            instructor = session.query(Instructor).filter(Instructor.id == instructor_id).first()
            
            if not instructor:
                return False, "Moniteur introuvable"
            
            # Vérifier l'unicité du CIN si modifié
            if 'cin' in kwargs and kwargs['cin'] != instructor.cin:
                existing = session.query(Instructor).filter(
                    Instructor.cin == kwargs['cin'],
                    Instructor.id != instructor_id
                ).first()
                if existing:
                    return False, "Un moniteur avec ce CIN existe déjà"
            
            # Vérifier l'unicité du permis si modifié
            if 'license_number' in kwargs and kwargs['license_number'] != instructor.license_number:
                existing_license = session.query(Instructor).filter(
                    Instructor.license_number == kwargs['license_number'],
                    Instructor.id != instructor_id
                ).first()
                if existing_license:
                    return False, "Un moniteur avec ce numéro de permis existe déjà"
            
            # Mettre à jour les champs
            for key, value in kwargs.items():
                if hasattr(instructor, key):
                    setattr(instructor, key, value)
            
            session.commit()
            logger.info(f"Moniteur {instructor_id} mis à jour")
            return True, "Moniteur mis à jour avec succès"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la mise à jour du moniteur : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def delete_instructor(instructor_id: int) -> tuple[bool, str]:
        """
        Supprimer un moniteur
        
        Args:
            instructor_id: ID du moniteur
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            instructor = session.query(Instructor).filter(Instructor.id == instructor_id).first()
            
            if not instructor:
                return False, "Moniteur introuvable"
            
            # Vérifier s'il y a des sessions liées
            sessions_count = session.query(Session).filter(Session.instructor_id == instructor_id).count()
            if sessions_count > 0:
                return False, f"Impossible de supprimer : {sessions_count} session(s) liée(s) à ce moniteur"
            
            session.delete(instructor)
            session.commit()
            
            logger.info(f"Moniteur {instructor_id} supprimé")
            return True, "Moniteur supprimé avec succès"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la suppression du moniteur : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def set_availability(instructor_id: int, is_available: bool) -> tuple[bool, str]:
        """
        Définir la disponibilité d'un moniteur
        
        Args:
            instructor_id: ID du moniteur
            is_available: Disponible ou non
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            instructor = session.query(Instructor).filter(Instructor.id == instructor_id).first()
            
            if not instructor:
                return False, "Moniteur introuvable"
            
            instructor.is_available = is_available
            session.commit()
            
            status = "disponible" if is_available else "indisponible"
            logger.info(f"Moniteur {instructor_id} marqué comme {status}")
            return True, f"Moniteur marqué comme {status}"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def get_instructor_statistics(instructor_id: int) -> Dict[str, Any]:
        """
        Obtenir les statistiques d'un moniteur
        
        Args:
            instructor_id: ID du moniteur
        
        Returns:
            Dictionnaire de statistiques
        """
        try:
            session = get_session()
            instructor = session.query(Instructor).filter(Instructor.id == instructor_id).first()
            
            if not instructor:
                return {}
            
            # Compter les sessions
            total_sessions = session.query(Session).filter(
                Session.instructor_id == instructor_id
            ).count()
            
            completed_sessions = session.query(Session).filter(
                Session.instructor_id == instructor_id,
                Session.status == SessionStatus.COMPLETED
            ).count()
            
            cancelled_sessions = session.query(Session).filter(
                Session.instructor_id == instructor_id,
                Session.status == SessionStatus.CANCELLED
            ).count()
            
            # Calculer les heures totales
            from sqlalchemy import func
            from datetime import timedelta
            
            sessions_with_duration = session.query(Session).filter(
                Session.instructor_id == instructor_id,
                Session.status == SessionStatus.COMPLETED
            ).all()
            
            total_hours = sum([
                (s.end_datetime - s.start_datetime).total_seconds() / 3600 
                for s in sessions_with_duration
                if s.start_datetime and s.end_datetime
            ])
            
            # Compter les élèves uniques
            unique_students = session.query(Session.student_id).filter(
                Session.instructor_id == instructor_id
            ).distinct().count()
            
            return {
                'instructor_id': instructor_id,
                'full_name': instructor.full_name,
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'cancelled_sessions': cancelled_sessions,
                'pending_sessions': total_sessions - completed_sessions - cancelled_sessions,
                'total_hours': round(total_hours, 2),
                'unique_students': unique_students,
                'hourly_rate': instructor.hourly_rate,
                'monthly_salary': instructor.monthly_salary,
                'success_rate': instructor.success_rate,
                'is_available': instructor.is_available
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques du moniteur : {e}")
            return {}
    
    @staticmethod
    def get_instructors_by_license_type(license_type: str, available_only: bool = False) -> List[Instructor]:
        """
        Obtenir les moniteurs pouvant enseigner un type de permis
        
        Args:
            license_type: Type de permis (A, B, C, D)
            available_only: Uniquement les moniteurs disponibles
        
        Returns:
            Liste des moniteurs
        """
        try:
            session = get_session()
            query = session.query(Instructor).filter(
                Instructor.license_types.like(f"%{license_type.upper()}%")
            )
            
            if available_only:
                query = query.filter(Instructor.is_available == True)
            
            return query.order_by(Instructor.full_name).all()
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des moniteurs (permis {license_type}) : {e}")
            return []
    
    @staticmethod
    def export_to_csv(instructors: Optional[List[Instructor]] = None, 
                     filename: Optional[str] = None) -> tuple[bool, str]:
        """
        Exporter les moniteurs vers un fichier CSV
        
        Args:
            instructors: Liste de moniteurs (optionnel, tous si None)
            filename: Nom du fichier (optionnel)
        
        Returns:
            Tuple (success, filepath/message)
        """
        try:
            if instructors is None:
                instructors = InstructorController.get_all_instructors()
            
            if not instructors:
                return False, "Aucun moniteur à exporter"
            
            # Préparer les données
            data = [instructor.to_dict() for instructor in instructors]
            
            # Exporter avec ExportManager
            export_mgr = get_export_manager()
            filepath = export_mgr.export_to_csv(data, 'instructors', filename)
            
            logger.info(f"{len(instructors)} moniteurs exportés vers {filepath}")
            return True, filepath
            
        except Exception as e:
            error_msg = f"Erreur lors de l'export : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
