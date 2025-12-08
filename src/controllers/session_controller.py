"""
Contrôleur pour la gestion des sessions de conduite
"""

from typing import List, Optional
from datetime import datetime, date, timedelta

from src.models import Session, SessionStatus, get_session
from src.utils import get_logger

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
