"""
Contrôleur pour la gestion des examens
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime, timedelta

from sqlalchemy import or_, and_, extract
from src.models import Exam, ExamType, ExamResult, Student, get_session
from src.utils import get_logger, get_export_manager

logger = get_logger()


class ExamController:
    """Contrôleur pour gérer les opérations sur les examens"""
    
    @staticmethod
    def get_all_exams(exam_type: Optional[ExamType] = None, 
                     result: Optional[ExamResult] = None) -> List[Exam]:
        """
        Récupérer tous les examens
        
        Args:
            exam_type: Filtrer par type d'examen (optionnel)
            result: Filtrer par résultat (optionnel)
        
        Returns:
            Liste des examens
        """
        try:
            session = get_session()
            query = session.query(Exam)
            
            if exam_type:
                query = query.filter(Exam.exam_type == exam_type)
            if result:
                query = query.filter(Exam.result == result)
            
            exams = query.order_by(Exam.scheduled_date.desc()).all()
            return exams
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des examens : {e}")
            return []
    
    @staticmethod
    def get_exam_by_id(exam_id: int) -> Optional[Exam]:
        """
        Récupérer un examen par son ID
        
        Args:
            exam_id: ID de l'examen
        
        Returns:
            Examen ou None
        """
        try:
            session = get_session()
            return session.query(Exam).filter(Exam.id == exam_id).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'examen {exam_id} : {e}")
            return None
    
    @staticmethod
    def get_upcoming_exams(days: int = 30) -> List[Exam]:
        """
        Récupérer les examens à venir
        
        Args:
            days: Nombre de jours à l'avance (défaut: 30)
        
        Returns:
            Liste des examens à venir
        """
        try:
            session = get_session()
            today = date.today()
            future_date = today + timedelta(days=days)
            
            return session.query(Exam).filter(
                Exam.scheduled_date >= today,
                Exam.scheduled_date <= future_date
            ).order_by(Exam.scheduled_date).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des examens à venir : {e}")
            return []
    
    @staticmethod
    def get_today_exams() -> List[Exam]:
        """Récupérer les examens du jour"""
        try:
            session = get_session()
            today = date.today()
            return session.query(Exam).filter(Exam.scheduled_date == today).order_by(Exam.scheduled_time).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des examens du jour : {e}")
            return []
    
    @staticmethod
    def get_past_exams(days: int = 90) -> List[Exam]:
        """
        Récupérer les examens passés
        
        Args:
            days: Nombre de jours en arrière (défaut: 90)
        
        Returns:
            Liste des examens passés
        """
        try:
            session = get_session()
            today = date.today()
            past_date = today - timedelta(days=days)
            
            return session.query(Exam).filter(
                Exam.scheduled_date < today,
                Exam.scheduled_date >= past_date
            ).order_by(Exam.scheduled_date.desc()).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des examens passés : {e}")
            return []
    
    @staticmethod
    def get_exams_by_student(student_id: int) -> List[Exam]:
        """Obtenir les examens d'un élève"""
        try:
            session = get_session()
            return session.query(Exam).filter(
                Exam.student_id == student_id
            ).order_by(Exam.scheduled_date.desc()).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des examens de l'élève : {e}")
            return []
    
    @staticmethod
    def search_exams(query: str) -> List[Exam]:
        """
        Rechercher des examens par convocation ou centre d'examen
        
        Args:
            query: Terme de recherche
        
        Returns:
            Liste des examens correspondants
        """
        try:
            session = get_session()
            search_term = f"%{query}%"
            
            exams = session.query(Exam).join(Student).filter(
                or_(
                    Exam.summons_number.like(search_term),
                    Exam.exam_center.like(search_term),
                    Exam.location.like(search_term),
                    Student.full_name.like(search_term),
                    Student.cin.like(search_term)
                )
            ).order_by(Exam.scheduled_date.desc()).all()
            
            return exams
        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'examens : {e}")
            return []
    
    @staticmethod
    def create_exam(student_id: int, exam_type: ExamType, scheduled_date: date,
                   **kwargs) -> tuple[bool, str, Optional[Exam]]:
        """
        Créer un nouvel examen
        
        Args:
            student_id: ID de l'élève
            exam_type: Type d'examen
            scheduled_date: Date prévue
            **kwargs: Autres paramètres optionnels
        
        Returns:
            Tuple (success, message, exam)
        """
        try:
            session = get_session()
            
            # Vérifier que l'élève existe
            student = session.query(Student).filter(Student.id == student_id).first()
            if not student:
                return False, "Élève introuvable", None
            
            # Calculer le numéro de tentative
            previous_exams = session.query(Exam).filter(
                Exam.student_id == student_id,
                Exam.exam_type == exam_type
            ).count()
            
            attempt_number = previous_exams + 1
            
            # Créer l'examen
            exam = Exam(
                student_id=student_id,
                exam_type=exam_type,
                scheduled_date=scheduled_date,
                attempt_number=attempt_number,
                **kwargs
            )
            
            # Générer le numéro de convocation
            session.add(exam)
            session.flush()  # Pour obtenir l'ID
            exam.summons_number = exam.generate_summons_number()
            
            session.commit()
            session.refresh(exam)
            
            logger.info(f"Examen créé : {exam_type.value} pour {student.full_name} le {scheduled_date}")
            return True, "Examen créé avec succès", exam
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la création de l'examen : {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def update_exam(exam_id: int, **kwargs) -> tuple[bool, str]:
        """
        Mettre à jour un examen
        
        Args:
            exam_id: ID de l'examen
            **kwargs: Champs à mettre à jour
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            exam = session.query(Exam).filter(Exam.id == exam_id).first()
            
            if not exam:
                return False, "Examen introuvable"
            
            # Mettre à jour les champs
            for key, value in kwargs.items():
                if hasattr(exam, key):
                    setattr(exam, key, value)
            
            session.commit()
            logger.info(f"Examen {exam_id} mis à jour")
            return True, "Examen mis à jour avec succès"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la mise à jour de l'examen : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def record_exam_result(exam_id: int, result: ExamResult, score: Optional[int] = None,
                          examiner_notes: Optional[str] = None, **kwargs) -> tuple[bool, str]:
        """
        Enregistrer le résultat d'un examen
        
        Args:
            exam_id: ID de l'examen
            result: Résultat de l'examen
            score: Score obtenu (optionnel)
            examiner_notes: Remarques de l'examinateur (optionnel)
            **kwargs: Autres champs à mettre à jour
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            exam = session.query(Exam).filter(Exam.id == exam_id).first()
            
            if not exam:
                return False, "Examen introuvable"
            
            # Enregistrer le résultat
            exam.record_result(result, score, examiner_notes)
            
            # Mettre à jour les autres champs
            for key, value in kwargs.items():
                if hasattr(exam, key):
                    setattr(exam, key, value)
            
            # Mettre à jour les statistiques de l'élève
            if exam.student:
                passed = result == ExamResult.PASSED
                exam.student.record_exam_attempt(
                    'theoretical' if exam.exam_type == ExamType.THEORETICAL else 'practical',
                    passed
                )
            
            session.commit()
            logger.info(f"Résultat de l'examen {exam_id} enregistré : {result.value}")
            return True, "Résultat enregistré avec succès"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de l'enregistrement du résultat : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def delete_exam(exam_id: int) -> tuple[bool, str]:
        """
        Supprimer un examen
        
        Args:
            exam_id: ID de l'examen
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            exam = session.query(Exam).filter(Exam.id == exam_id).first()
            
            if not exam:
                return False, "Examen introuvable"
            
            session.delete(exam)
            session.commit()
            
            logger.info(f"Examen {exam_id} supprimé")
            return True, "Examen supprimé avec succès"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la suppression de l'examen : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def generate_convocation(exam_id: int) -> tuple[bool, str]:
        """
        Générer une convocation d'examen
        
        Args:
            exam_id: ID de l'examen
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            exam = session.query(Exam).filter(Exam.id == exam_id).first()
            
            if not exam:
                return False, "Examen introuvable"
            
            exam.mark_summons_generated()
            session.commit()
            
            logger.info(f"Convocation générée pour l'examen {exam_id}")
            return True, f"Convocation {exam.summons_number} générée"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la génération de la convocation : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def mark_convocation_sent(exam_id: int) -> tuple[bool, str]:
        """
        Marquer une convocation comme envoyée
        
        Args:
            exam_id: ID de l'examen
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            exam = session.query(Exam).filter(Exam.id == exam_id).first()
            
            if not exam:
                return False, "Examen introuvable"
            
            exam.mark_summons_sent()
            session.commit()
            
            logger.info(f"Convocation {exam.summons_number} marquée comme envoyée")
            return True, "Convocation marquée comme envoyée"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def get_success_rate_statistics(exam_type: Optional[ExamType] = None,
                                    start_date: Optional[date] = None,
                                    end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Obtenir les statistiques de réussite
        
        Args:
            exam_type: Type d'examen (optionnel)
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
        
        Returns:
            Dictionnaire de statistiques
        """
        try:
            session = get_session()
            query = session.query(Exam).filter(Exam.result != ExamResult.PENDING)
            
            if exam_type:
                query = query.filter(Exam.exam_type == exam_type)
            if start_date:
                query = query.filter(Exam.scheduled_date >= start_date)
            if end_date:
                query = query.filter(Exam.scheduled_date <= end_date)
            
            exams = query.all()
            
            total = len(exams)
            if total == 0:
                return {
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'absent': 0,
                    'success_rate': 0.0
                }
            
            passed = len([e for e in exams if e.result == ExamResult.PASSED])
            failed = len([e for e in exams if e.result == ExamResult.FAILED])
            absent = len([e for e in exams if e.result == ExamResult.ABSENT])
            
            # Calculer le taux de réussite sur les présents
            present = passed + failed
            success_rate = (passed / present * 100) if present > 0 else 0.0
            
            return {
                'total': total,
                'passed': passed,
                'failed': failed,
                'absent': absent,
                'present': present,
                'success_rate': round(success_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques : {e}")
            return {}
    
    @staticmethod
    def export_to_csv(exams: Optional[List[Exam]] = None, filename: Optional[str] = None) -> tuple[bool, str]:
        """
        Exporter les examens vers un fichier CSV
        
        Args:
            exams: Liste d'examens (optionnel, tous si None)
            filename: Nom du fichier (optionnel)
        
        Returns:
            Tuple (success, filepath/message)
        """
        try:
            if exams is None:
                exams = ExamController.get_all_exams()
            
            if not exams:
                return False, "Aucun examen à exporter"
            
            # Préparer les données
            data = [exam.to_dict() for exam in exams]
            
            # Exporter avec ExportManager
            export_mgr = get_export_manager()
            filepath = export_mgr.export_to_csv(data, 'exams', filename)
            
            logger.info(f"{len(exams)} examens exportés vers {filepath}")
            return True, filepath
            
        except Exception as e:
            error_msg = f"Erreur lors de l'export : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
