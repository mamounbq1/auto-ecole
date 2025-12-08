"""Contrôleur pour la gestion des véhicules"""
from typing import List
from src.models import Vehicle, get_session
from src.utils import get_logger

logger = get_logger()

class VehicleController:
    @staticmethod
    def get_all_vehicles() -> List[Vehicle]:
        try:
            session = get_session()
            return session.query(Vehicle).order_by(Vehicle.plate_number).all()
        except Exception as e:
            logger.error(f"Erreur : {e}")
            return []
