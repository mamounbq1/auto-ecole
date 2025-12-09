"""
Contrôleur pour la gestion de la maintenance des véhicules
Phase 1 - Critical Improvements
"""

from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_

from src.models import VehicleMaintenance, MaintenanceType, MaintenanceStatus, Vehicle, get_session
from src.utils import get_logger, get_export_manager

logger = get_logger()


class MaintenanceController:
    """Contrôleur pour gérer la maintenance des véhicules"""
    
    # ========== CRUD Operations ==========
    
    @staticmethod
    def create_maintenance(maintenance_data: dict) -> Optional[VehicleMaintenance]:
        """
        Créer une nouvelle maintenance
        
        Args:
            maintenance_data: Dictionnaire avec les données de la maintenance
            
        Returns:
            VehicleMaintenance créée ou None si erreur
        """
        try:
            session = get_session()
            
            # Créer la maintenance
            maintenance = VehicleMaintenance(
                vehicle_id=maintenance_data['vehicle_id'],
                maintenance_type=maintenance_data['maintenance_type'],
                status=maintenance_data.get('status', MaintenanceStatus.PLANIFIEE),
                scheduled_date=maintenance_data['scheduled_date'],
                start_date=maintenance_data.get('start_date'),
                completion_date=maintenance_data.get('completion_date'),
                mileage_at_maintenance=maintenance_data.get('mileage_at_maintenance'),
                provider_name=maintenance_data.get('provider_name'),
                provider_contact=maintenance_data.get('provider_contact'),
                labor_cost=maintenance_data.get('labor_cost', 0.0),
                parts_cost=maintenance_data.get('parts_cost', 0.0),
                other_cost=maintenance_data.get('other_cost', 0.0),
                description=maintenance_data.get('description'),
                parts_replaced=maintenance_data.get('parts_replaced'),
                technician_name=maintenance_data.get('technician_name'),
                notes=maintenance_data.get('notes'),
                recommendations=maintenance_data.get('recommendations'),
                invoice_number=maintenance_data.get('invoice_number'),
                invoice_path=maintenance_data.get('invoice_path'),
                next_maintenance_date=maintenance_data.get('next_maintenance_date'),
                next_maintenance_mileage=maintenance_data.get('next_maintenance_mileage'),
                created_by=maintenance_data.get('created_by')
            )
            
            # Calculer le coût total
            maintenance.calculate_total_cost()
            
            session.add(maintenance)
            session.commit()
            session.refresh(maintenance)
            
            logger.info(f"Maintenance créée : ID {maintenance.id} pour véhicule {maintenance.vehicle_id}")
            return maintenance
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la maintenance : {e}")
            session.rollback()
            return None
    
    @staticmethod
    def get_maintenance_by_id(maintenance_id: int) -> Optional[VehicleMaintenance]:
        """Obtenir une maintenance par ID"""
        try:
            session = get_session()
            return session.query(VehicleMaintenance).filter(
                VehicleMaintenance.id == maintenance_id
            ).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la maintenance {maintenance_id} : {e}")
            return None
    
    @staticmethod
    def get_all_maintenances() -> List[VehicleMaintenance]:
        """Obtenir toutes les maintenances"""
        try:
            session = get_session()
            return session.query(VehicleMaintenance).order_by(
                VehicleMaintenance.scheduled_date.desc()
            ).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des maintenances : {e}")
            return []
    
    @staticmethod
    def get_maintenances_by_vehicle(vehicle_id: int) -> List[VehicleMaintenance]:
        """Obtenir les maintenances d'un véhicule"""
        try:
            session = get_session()
            return session.query(VehicleMaintenance).filter(
                VehicleMaintenance.vehicle_id == vehicle_id
            ).order_by(VehicleMaintenance.scheduled_date.desc()).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des maintenances du véhicule {vehicle_id} : {e}")
            return []
    
    @staticmethod
    def update_maintenance(maintenance_id: int, maintenance_data: dict) -> bool:
        """
        Mettre à jour une maintenance
        
        Args:
            maintenance_id: ID de la maintenance
            maintenance_data: Dictionnaire avec les nouvelles données
            
        Returns:
            True si succès, False sinon
        """
        try:
            session = get_session()
            maintenance = session.query(VehicleMaintenance).filter(
                VehicleMaintenance.id == maintenance_id
            ).first()
            
            if not maintenance:
                logger.error(f"Maintenance {maintenance_id} introuvable")
                return False
            
            # Mettre à jour les attributs
            for key, value in maintenance_data.items():
                if hasattr(maintenance, key) and value is not None:
                    setattr(maintenance, key, value)
            
            # Recalculer le coût total si nécessaire
            if any(key in maintenance_data for key in ['labor_cost', 'parts_cost', 'other_cost']):
                maintenance.calculate_total_cost()
            
            session.commit()
            logger.info(f"Maintenance {maintenance_id} mise à jour")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la maintenance {maintenance_id} : {e}")
            session.rollback()
            return False
    
    @staticmethod
    def delete_maintenance(maintenance_id: int) -> bool:
        """
        Supprimer une maintenance
        
        Args:
            maintenance_id: ID de la maintenance
            
        Returns:
            True si succès, False sinon
        """
        try:
            session = get_session()
            maintenance = session.query(VehicleMaintenance).filter(
                VehicleMaintenance.id == maintenance_id
            ).first()
            
            if not maintenance:
                logger.error(f"Maintenance {maintenance_id} introuvable")
                return False
            
            session.delete(maintenance)
            session.commit()
            logger.info(f"Maintenance {maintenance_id} supprimée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la maintenance {maintenance_id} : {e}")
            session.rollback()
            return False
    
    # ========== Recherche et Filtres ==========
    
    @staticmethod
    def search_maintenances(
        vehicle_id: Optional[int] = None,
        maintenance_type: Optional[MaintenanceType] = None,
        status: Optional[MaintenanceStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        provider_name: Optional[str] = None,
        min_cost: Optional[float] = None,
        max_cost: Optional[float] = None
    ) -> List[VehicleMaintenance]:
        """
        Rechercher des maintenances avec critères multiples
        
        Args:
            vehicle_id: Filtrer par véhicule
            maintenance_type: Filtrer par type
            status: Filtrer par statut
            start_date: Date de début
            end_date: Date de fin
            provider_name: Nom du fournisseur
            min_cost: Coût minimum
            max_cost: Coût maximum
            
        Returns:
            Liste de maintenances correspondantes
        """
        try:
            session = get_session()
            query = session.query(VehicleMaintenance)
            
            # Filtres
            if vehicle_id:
                query = query.filter(VehicleMaintenance.vehicle_id == vehicle_id)
            
            if maintenance_type:
                query = query.filter(VehicleMaintenance.maintenance_type == maintenance_type)
            
            if status:
                query = query.filter(VehicleMaintenance.status == status)
            
            if start_date:
                query = query.filter(VehicleMaintenance.scheduled_date >= start_date)
            
            if end_date:
                query = query.filter(VehicleMaintenance.scheduled_date <= end_date)
            
            if provider_name:
                query = query.filter(VehicleMaintenance.provider_name.ilike(f'%{provider_name}%'))
            
            if min_cost is not None:
                query = query.filter(VehicleMaintenance.total_cost >= min_cost)
            
            if max_cost is not None:
                query = query.filter(VehicleMaintenance.total_cost <= max_cost)
            
            return query.order_by(VehicleMaintenance.scheduled_date.desc()).all()
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de maintenances : {e}")
            return []
    
    # ========== Gestion des statuts ==========
    
    @staticmethod
    def start_maintenance(maintenance_id: int) -> bool:
        """Démarrer une maintenance"""
        try:
            session = get_session()
            maintenance = session.query(VehicleMaintenance).filter(
                VehicleMaintenance.id == maintenance_id
            ).first()
            
            if not maintenance:
                return False
            
            maintenance.start_maintenance()
            session.commit()
            logger.info(f"Maintenance {maintenance_id} démarrée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage de la maintenance {maintenance_id} : {e}")
            session.rollback()
            return False
    
    @staticmethod
    def complete_maintenance(maintenance_id: int, completion_data: Optional[dict] = None) -> bool:
        """
        Terminer une maintenance
        
        Args:
            maintenance_id: ID de la maintenance
            completion_data: Données de complétion (kilométrage, notes, etc.)
        """
        try:
            session = get_session()
            maintenance = session.query(VehicleMaintenance).filter(
                VehicleMaintenance.id == maintenance_id
            ).first()
            
            if not maintenance:
                return False
            
            maintenance.complete_maintenance()
            
            if completion_data:
                for key, value in completion_data.items():
                    if hasattr(maintenance, key):
                        setattr(maintenance, key, value)
            
            session.commit()
            logger.info(f"Maintenance {maintenance_id} terminée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la complétion de la maintenance {maintenance_id} : {e}")
            session.rollback()
            return False
    
    @staticmethod
    def cancel_maintenance(maintenance_id: int) -> bool:
        """Annuler une maintenance"""
        try:
            session = get_session()
            maintenance = session.query(VehicleMaintenance).filter(
                VehicleMaintenance.id == maintenance_id
            ).first()
            
            if not maintenance:
                return False
            
            maintenance.cancel_maintenance()
            session.commit()
            logger.info(f"Maintenance {maintenance_id} annulée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'annulation de la maintenance {maintenance_id} : {e}")
            session.rollback()
            return False
    
    # ========== Alertes et Rappels ==========
    
    @staticmethod
    def get_upcoming_maintenances(days: int = 30) -> List[VehicleMaintenance]:
        """Obtenir les maintenances à venir dans les N prochains jours"""
        try:
            session = get_session()
            end_date = datetime.now() + timedelta(days=days)
            
            return session.query(VehicleMaintenance).filter(
                and_(
                    VehicleMaintenance.status == MaintenanceStatus.PLANIFIEE,
                    VehicleMaintenance.scheduled_date <= end_date,
                    VehicleMaintenance.scheduled_date >= datetime.now()
                )
            ).order_by(VehicleMaintenance.scheduled_date).all()
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des maintenances à venir : {e}")
            return []
    
    @staticmethod
    def get_overdue_maintenances() -> List[VehicleMaintenance]:
        """Obtenir les maintenances en retard"""
        try:
            session = get_session()
            
            return session.query(VehicleMaintenance).filter(
                and_(
                    VehicleMaintenance.status == MaintenanceStatus.PLANIFIEE,
                    VehicleMaintenance.scheduled_date < datetime.now()
                )
            ).order_by(VehicleMaintenance.scheduled_date).all()
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des maintenances en retard : {e}")
            return []
    
    @staticmethod
    def get_maintenance_alerts() -> Dict[str, List[VehicleMaintenance]]:
        """
        Obtenir toutes les alertes de maintenance
        
        Returns:
            Dictionnaire avec les maintenances urgentes, à venir et en retard
        """
        try:
            urgent = MaintenanceController.get_upcoming_maintenances(days=7)  # Dans les 7 prochains jours
            upcoming = MaintenanceController.get_upcoming_maintenances(days=30)  # Dans les 30 prochains jours
            overdue = MaintenanceController.get_overdue_maintenances()
            
            return {
                'urgent': urgent,  # À faire cette semaine
                'upcoming': upcoming,  # À faire ce mois
                'overdue': overdue  # En retard
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des alertes : {e}")
            return {'urgent': [], 'upcoming': [], 'overdue': []}
    
    # ========== Statistiques ==========
    
    @staticmethod
    def get_maintenance_statistics(vehicle_id: Optional[int] = None) -> dict:
        """
        Obtenir les statistiques de maintenance
        
        Args:
            vehicle_id: Filtrer par véhicule (optionnel)
        """
        try:
            session = get_session()
            query = session.query(VehicleMaintenance)
            
            if vehicle_id:
                query = query.filter(VehicleMaintenance.vehicle_id == vehicle_id)
            
            maintenances = query.all()
            
            if not maintenances:
                return {
                    'total_count': 0,
                    'total_cost': 0.0,
                    'average_cost': 0.0,
                    'by_type': {},
                    'by_status': {},
                    'overdue_count': 0
                }
            
            # Calculs
            total_count = len(maintenances)
            total_cost = sum(m.total_cost for m in maintenances)
            average_cost = total_cost / total_count if total_count > 0 else 0.0
            
            # Par type
            by_type = {}
            for m_type in MaintenanceType:
                count = len([m for m in maintenances if m.maintenance_type == m_type])
                cost = sum(m.total_cost for m in maintenances if m.maintenance_type == m_type)
                by_type[m_type.value] = {'count': count, 'total_cost': cost}
            
            # Par statut
            by_status = {}
            for status in MaintenanceStatus:
                count = len([m for m in maintenances if m.status == status])
                by_status[status.value] = count
            
            # En retard
            overdue_count = len([m for m in maintenances if m.is_overdue()])
            
            return {
                'total_count': total_count,
                'total_cost': total_cost,
                'average_cost': average_cost,
                'by_type': by_type,
                'by_status': by_status,
                'overdue_count': overdue_count
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques : {e}")
            return {}
    
    # ========== Export ==========
    
    @staticmethod
    def export_to_csv(maintenances: Optional[List[VehicleMaintenance]] = None,
                     filename: Optional[str] = None) -> tuple[bool, str]:
        """
        Exporter les maintenances vers un fichier CSV
        
        Args:
            maintenances: Liste de maintenances (optionnel, toutes si None)
            filename: Nom du fichier (optionnel)
        
        Returns:
            Tuple (success, filepath/message)
        """
        try:
            if maintenances is None:
                maintenances = MaintenanceController.get_all_maintenances()
            
            if not maintenances:
                return False, "Aucune maintenance à exporter"
            
            # Convertir en dictionnaires
            data = [m.to_dict() for m in maintenances]
            
            # Exporter avec ExportManager
            export_mgr = get_export_manager()
            filepath = export_mgr.export_to_csv(data, 'maintenances', filename)
            
            logger.info(f"{len(maintenances)} maintenances exportées vers {filepath}")
            return True, filepath
            
        except Exception as e:
            error_msg = f"Erreur lors de l'export : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
