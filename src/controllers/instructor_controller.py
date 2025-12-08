"""Contrôleur pour la gestion des moniteurs"""
from typing import List
from src.models import Instructor, get_session
from src.utils import get_logger

logger = get_logger()

class InstructorController:
    @staticmethod
    def get_all_instructors() -> List[Instructor]:
        try:
            session = get_session()
            return session.query(Instructor).order_by(Instructor.full_name).all()
        except Exception as e:
            logger.error(f"Erreur : {e}")
            return []
