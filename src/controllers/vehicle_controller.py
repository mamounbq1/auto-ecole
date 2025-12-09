"""
Contrôleur pour la gestion des véhicules
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import date, timedelta

from sqlalchemy import or_, and_
from src.models import Vehicle, VehicleStatus, Session, SessionStatus, get_session
from src.utils import get_logger, get_export_manager

logger = get_logger()


class VehicleController:
    """Contrôleur pour gérer les opérations sur les véhicules"""
    
    @staticmethod
    def get_all_vehicles(status: Optional[VehicleStatus] = None,
                        available_only: bool = False) -> List[Vehicle]:
        """
        Récupérer tous les véhicules
        
        Args:
            status: Filtrer par statut (optionnel)
            available_only: Filtrer uniquement les véhicules disponibles
        
        Returns:
            Liste des véhicules
        """
        try:
            session = get_session()
            query = session.query(Vehicle)
            
            if status:
                query = query.filter(Vehicle.status == status)
            if available_only:
                query = query.filter(Vehicle.is_available == True)
            
            vehicles = query.order_by(Vehicle.plate_number).all()
            return vehicles
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des véhicules : {e}")
            return []
    
    @staticmethod
    def get_vehicle_by_id(vehicle_id: int) -> Optional[Vehicle]:
        """
        Récupérer un véhicule par son ID
        
        Args:
            vehicle_id: ID du véhicule
        
        Returns:
            Véhicule ou None
        """
        try:
            session = get_session()
            return session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du véhicule {vehicle_id} : {e}")
            return None
    
    @staticmethod
    def get_vehicle_by_plate(plate_number: str) -> Optional[Vehicle]:
        """
        Récupérer un véhicule par son numéro de plaque
        
        Args:
            plate_number: Numéro de plaque
        
        Returns:
            Véhicule ou None
        """
        try:
            session = get_session()
            return session.query(Vehicle).filter(Vehicle.plate_number == plate_number).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du véhicule (plaque {plate_number}) : {e}")
            return None
    
    @staticmethod
    def get_vehicle_by_vin(vin: str) -> Optional[Vehicle]:
        """
        Récupérer un véhicule par son VIN
        
        Args:
            vin: Vehicle Identification Number
        
        Returns:
            Véhicule ou None
        """
        try:
            session = get_session()
            return session.query(Vehicle).filter(Vehicle.vin == vin).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du véhicule (VIN {vin}) : {e}")
            return None
    
    @staticmethod
    def search_vehicles(query: str) -> List[Vehicle]:
        """
        Rechercher des véhicules par plaque, marque, modèle
        
        Args:
            query: Terme de recherche
        
        Returns:
            Liste des véhicules correspondants
        """
        try:
            session = get_session()
            search_term = f"%{query}%"
            
            vehicles = session.query(Vehicle).filter(
                or_(
                    Vehicle.plate_number.like(search_term),
                    Vehicle.make.like(search_term),
                    Vehicle.model.like(search_term),
                    Vehicle.vin.like(search_term),
                    Vehicle.color.like(search_term)
                )
            ).order_by(Vehicle.plate_number).all()
            
            return vehicles
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de véhicules : {e}")
            return []
    
    @staticmethod
    def create_vehicle(plate_number: str, make: str, model: str,
                      **kwargs) -> tuple[bool, str, Optional[Vehicle]]:
        """
        Créer un nouveau véhicule
        
        Args:
            plate_number: Numéro de plaque
            make: Marque
            model: Modèle
            **kwargs: Autres paramètres optionnels
        
        Returns:
            Tuple (success, message, vehicle)
        """
        try:
            session = get_session()
            
            # Vérifier que la plaque n'existe pas déjà
            existing = session.query(Vehicle).filter(Vehicle.plate_number == plate_number).first()
            if existing:
                return False, "Un véhicule avec cette plaque existe déjà", None
            
            # Vérifier le VIN si fourni
            if 'vin' in kwargs and kwargs['vin']:
                existing_vin = session.query(Vehicle).filter(Vehicle.vin == kwargs['vin']).first()
                if existing_vin:
                    return False, "Un véhicule avec ce VIN existe déjà", None
            
            # Créer le véhicule
            vehicle = Vehicle(
                plate_number=plate_number,
                make=make,
                model=model,
                **kwargs
            )
            
            session.add(vehicle)
            session.commit()
            session.refresh(vehicle)
            
            logger.info(f"Véhicule créé : {plate_number} ({make} {model})")
            return True, "Véhicule créé avec succès", vehicle
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la création du véhicule : {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def update_vehicle(vehicle_id: int, **kwargs) -> tuple[bool, str]:
        """
        Mettre à jour un véhicule
        
        Args:
            vehicle_id: ID du véhicule
            **kwargs: Champs à mettre à jour
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
            
            if not vehicle:
                return False, "Véhicule introuvable"
            
            # Vérifier l'unicité de la plaque si modifiée
            if 'plate_number' in kwargs and kwargs['plate_number'] != vehicle.plate_number:
                existing = session.query(Vehicle).filter(
                    Vehicle.plate_number == kwargs['plate_number'],
                    Vehicle.id != vehicle_id
                ).first()
                if existing:
                    return False, "Un véhicule avec cette plaque existe déjà"
            
            # Vérifier l'unicité du VIN si modifié
            if 'vin' in kwargs and kwargs['vin'] and kwargs['vin'] != vehicle.vin:
                existing_vin = session.query(Vehicle).filter(
                    Vehicle.vin == kwargs['vin'],
                    Vehicle.id != vehicle_id
                ).first()
                if existing_vin:
                    return False, "Un véhicule avec ce VIN existe déjà"
            
            # Mettre à jour les champs
            for key, value in kwargs.items():
                if hasattr(vehicle, key):
                    setattr(vehicle, key, value)
            
            session.commit()
            logger.info(f"Véhicule {vehicle_id} mis à jour")
            return True, "Véhicule mis à jour avec succès"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la mise à jour du véhicule : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def delete_vehicle(vehicle_id: int) -> tuple[bool, str]:
        """
        Supprimer un véhicule
        
        Args:
            vehicle_id: ID du véhicule
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
            
            if not vehicle:
                return False, "Véhicule introuvable"
            
            # Vérifier s'il y a des sessions liées
            sessions_count = session.query(Session).filter(Session.vehicle_id == vehicle_id).count()
            if sessions_count > 0:
                return False, f"Impossible de supprimer : {sessions_count} session(s) liée(s) à ce véhicule"
            
            session.delete(vehicle)
            session.commit()
            
            logger.info(f"Véhicule {vehicle_id} supprimé")
            return True, "Véhicule supprimé avec succès"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la suppression du véhicule : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def set_status(vehicle_id: int, status: VehicleStatus) -> tuple[bool, str]:
        """
        Définir le statut d'un véhicule
        
        Args:
            vehicle_id: ID du véhicule
            status: Nouveau statut
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
            
            if not vehicle:
                return False, "Véhicule introuvable"
            
            vehicle.status = status
            vehicle.is_available = (status == VehicleStatus.AVAILABLE)
            session.commit()
            
            logger.info(f"Véhicule {vehicle_id} statut changé vers {status.value}")
            return True, f"Statut changé vers {status.value}"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def record_maintenance(vehicle_id: int, cost: float = 0.0, 
                          next_maintenance_date: Optional[date] = None,
                          notes: Optional[str] = None) -> tuple[bool, str]:
        """
        Enregistrer une maintenance
        
        Args:
            vehicle_id: ID du véhicule
            cost: Coût de la maintenance
            next_maintenance_date: Date de la prochaine maintenance
            notes: Notes sur la maintenance
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
            
            if not vehicle:
                return False, "Véhicule introuvable"
            
            vehicle.record_maintenance(cost, vehicle.current_mileage)
            
            if next_maintenance_date:
                vehicle.next_maintenance_date = next_maintenance_date
            
            if notes:
                current_notes = vehicle.notes or ""
                maintenance_note = f"\n[{date.today()}] Maintenance : {notes}"
                vehicle.notes = current_notes + maintenance_note
            
            session.commit()
            
            logger.info(f"Maintenance enregistrée pour le véhicule {vehicle_id}")
            return True, "Maintenance enregistrée avec succès"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def update_mileage(vehicle_id: int, new_mileage: int) -> tuple[bool, str]:
        """
        Mettre à jour le kilométrage
        
        Args:
            vehicle_id: ID du véhicule
            new_mileage: Nouveau kilométrage
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
            
            if not vehicle:
                return False, "Véhicule introuvable"
            
            if new_mileage < vehicle.current_mileage:
                return False, "Le nouveau kilométrage ne peut pas être inférieur à l'actuel"
            
            vehicle.current_mileage = new_mileage
            session.commit()
            
            logger.info(f"Kilométrage du véhicule {vehicle_id} mis à jour : {new_mileage} km")
            return True, f"Kilométrage mis à jour : {new_mileage} km"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def get_vehicles_needing_maintenance() -> List[Vehicle]:
        """
        Obtenir les véhicules nécessitant une maintenance
        
        Returns:
            Liste des véhicules
        """
        try:
            session = get_session()
            today = date.today()
            
            return session.query(Vehicle).filter(
                Vehicle.next_maintenance_date <= today
            ).order_by(Vehicle.next_maintenance_date).all()
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des véhicules à maintenir : {e}")
            return []
    
    @staticmethod
    def get_vehicles_with_expired_documents() -> Dict[str, List[Vehicle]]:
        """
        Obtenir les véhicules avec documents expirés
        
        Returns:
            Dictionnaire avec listes de véhicules par type de document
        """
        try:
            session = get_session()
            today = date.today()
            
            expired_insurance = session.query(Vehicle).filter(
                Vehicle.insurance_expiry_date <= today
            ).all()
            
            expired_inspection = session.query(Vehicle).filter(
                Vehicle.technical_inspection_date <= today
            ).all()
            
            return {
                'insurance': expired_insurance,
                'technical_inspection': expired_inspection
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des documents : {e}")
            return {'insurance': [], 'technical_inspection': []}
    
    @staticmethod
    def get_vehicle_statistics(vehicle_id: int) -> Dict[str, Any]:
        """
        Obtenir les statistiques d'un véhicule
        
        Args:
            vehicle_id: ID du véhicule
        
        Returns:
            Dictionnaire de statistiques
        """
        try:
            session = get_session()
            vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
            
            if not vehicle:
                return {}
            
            # Compter les sessions
            total_sessions = session.query(Session).filter(
                Session.vehicle_id == vehicle_id
            ).count()
            
            completed_sessions = session.query(Session).filter(
                Session.vehicle_id == vehicle_id,
                Session.status == SessionStatus.COMPLETED
            ).count()
            
            cancelled_sessions = session.query(Session).filter(
                Session.vehicle_id == vehicle_id,
                Session.status == SessionStatus.CANCELLED
            ).count()
            
            # Calculer les heures d'utilisation
            sessions_with_duration = session.query(Session).filter(
                Session.vehicle_id == vehicle_id,
                Session.status == SessionStatus.COMPLETED
            ).all()
            
            total_hours = sum([
                (s.end_datetime - s.start_datetime).total_seconds() / 3600 
                for s in sessions_with_duration
                if s.start_datetime and s.end_datetime
            ])
            
            return {
                'vehicle_id': vehicle_id,
                'plate_number': vehicle.plate_number,
                'full_name': vehicle.full_name,
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'cancelled_sessions': cancelled_sessions,
                'pending_sessions': total_sessions - completed_sessions - cancelled_sessions,
                'total_hours': round(total_hours, 2),
                'current_mileage': vehicle.current_mileage,
                'maintenance_cost': vehicle.maintenance_cost,
                'insurance_cost': vehicle.insurance_cost,
                'total_cost': vehicle.maintenance_cost + vehicle.insurance_cost,
                'needs_maintenance': vehicle.needs_maintenance,
                'insurance_expired': vehicle.insurance_expired,
                'technical_inspection_expired': vehicle.technical_inspection_expired,
                'is_available': vehicle.is_available,
                'status': vehicle.status.value
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques du véhicule : {e}")
            return {}
    
    @staticmethod
    def get_vehicles_by_license_type(license_type: str, available_only: bool = False) -> List[Vehicle]:
        """
        Obtenir les véhicules par type de permis
        
        Args:
            license_type: Type de permis (A, B, C, D)
            available_only: Uniquement les véhicules disponibles
        
        Returns:
            Liste des véhicules
        """
        try:
            session = get_session()
            query = session.query(Vehicle).filter(Vehicle.license_type == license_type.upper())
            
            if available_only:
                query = query.filter(Vehicle.is_available == True)
            
            return query.order_by(Vehicle.plate_number).all()
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des véhicules (permis {license_type}) : {e}")
            return []
    
    @staticmethod
    def export_to_csv(vehicles: Optional[List[Vehicle]] = None,
                     filename: Optional[str] = None) -> tuple[bool, str]:
        """
        Exporter les véhicules vers un fichier CSV
        
        Args:
            vehicles: Liste de véhicules (optionnel, tous si None)
            filename: Nom du fichier (optionnel)
        
        Returns:
            Tuple (success, filepath/message)
        """
        try:
            if vehicles is None:
                vehicles = VehicleController.get_all_vehicles()
            
            if not vehicles:
                return False, "Aucun véhicule à exporter"
            
            # Préparer les données
            data = [vehicle.to_dict() for vehicle in vehicles]
            
            # Exporter avec ExportManager
            export_mgr = get_export_manager()
            filepath = export_mgr.export_to_csv(data, 'vehicles', filename)
            
            logger.info(f"{len(vehicles)} véhicules exportés vers {filepath}")
            return True, filepath
            
        except Exception as e:
            error_msg = f"Erreur lors de l'export : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
