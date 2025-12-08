"""Contrôleur pour la gestion des examens"""
from typing import List
from src.models import Exam, get_session
from src.utils import get_logger

logger = get_logger()

class ExamController:
    @staticmethod
    def get_upcoming_exams() -> List[Exam]:
        try:
            session = get_session()
            from datetime import date
            return session.query(Exam).filter(Exam.scheduled_date >= date.today()).order_by(Exam.scheduled_date).all()
        except Exception as e:
            logger.error(f"Erreur : {e}")
            return []
    
    @staticmethod
    def get_all_exams() -> List[Exam]:
        """Obtenir tous les examens"""
        try:
            session = get_session()
            return session.query(Exam).order_by(Exam.scheduled_date.desc()).all()
        except Exception as e:
            logger.error(f"Erreur : {e}")
            return []
