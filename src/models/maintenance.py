"""
Modèle de gestion de l'historique de maintenance des véhicules
Phase 1 - Critical Improvements
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import Base


class MaintenanceType(str, Enum):
    """Types de maintenance"""
    VIDANGE = "vidange"
    REVISION = "révision"
    CONTROLE_TECHNIQUE = "contrôle technique"
    REPARATION = "réparation"
    CHANGEMENT_PNEUS = "changement pneus"
    CHANGEMENT_PLAQUETTES = "changement plaquettes"
    REPARATION_CARROSSERIE = "réparation carrosserie"
    REPARATION_MECANIQUE = "réparation mécanique"
    REPARATION_ELECTRIQUE = "réparation électrique"
    AUTRE = "autre"


class MaintenanceStatus(str, Enum):
    """Statuts de maintenance"""
    PLANIFIEE = "planifiée"
    EN_COURS = "en cours"
    TERMINEE = "terminée"
    ANNULEE = "annulée"


class VehicleMaintenance(Base):
    """
    Modèle pour l'historique de maintenance des véhicules
    
    Cette table permet de :
    - Suivre toutes les interventions de maintenance
    - Calculer les coûts totaux de maintenance
    - Générer des alertes préventives
    - Produire des rapports de maintenance
    """
    
    __tablename__ = 'vehicle_maintenances'
    
    # Clé primaire
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Lien avec véhicule
    vehicle_id = Column(Integer, ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False)
    vehicle = relationship('Vehicle', back_populates='maintenances')
    
    # Informations de maintenance
    maintenance_type = Column(SQLEnum(MaintenanceType), nullable=False)
    status = Column(SQLEnum(MaintenanceStatus), default=MaintenanceStatus.PLANIFIEE, nullable=False)
    
    # Dates
    scheduled_date = Column(DateTime, nullable=False)  # Date prévue
    start_date = Column(DateTime, nullable=True)  # Date de début réelle
    completion_date = Column(DateTime, nullable=True)  # Date de fin réelle
    
    # Kilométrage
    mileage_at_maintenance = Column(Integer, nullable=True)  # Kilométrage au moment de la maintenance
    
    # Fournisseur
    provider_name = Column(String(200), nullable=True)  # Garage, concessionnaire, etc.
    provider_contact = Column(String(100), nullable=True)  # Téléphone/email
    
    # Coûts
    labor_cost = Column(Float, default=0.0, nullable=False)  # Coût main d'œuvre
    parts_cost = Column(Float, default=0.0, nullable=False)  # Coût pièces
    other_cost = Column(Float, default=0.0, nullable=False)  # Autres frais
    total_cost = Column(Float, default=0.0, nullable=False)  # Coût total
    
    # Détails
    description = Column(Text, nullable=True)  # Description de l'intervention
    parts_replaced = Column(Text, nullable=True)  # Liste des pièces remplacées
    technician_name = Column(String(200), nullable=True)  # Nom du technicien
    
    # Notes et observations
    notes = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)  # Recommandations pour l'avenir
    
    # Documents
    invoice_number = Column(String(100), nullable=True)  # Numéro de facture
    invoice_path = Column(String(500), nullable=True)  # Chemin vers la facture scannée
    
    # Prochaine maintenance
    next_maintenance_date = Column(DateTime, nullable=True)  # Date de la prochaine intervention
    next_maintenance_mileage = Column(Integer, nullable=True)  # Kilométrage de la prochaine intervention
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    created_by = Column(String(200), nullable=True)  # Utilisateur ayant créé l'enregistrement
    
    def __repr__(self):
        return (
            f"<VehicleMaintenance(id={self.id}, vehicle_id={self.vehicle_id}, "
            f"type={self.maintenance_type.value}, status={self.status.value}, "
            f"scheduled_date={self.scheduled_date}, total_cost={self.total_cost} DH)>"
        )
    
    def calculate_total_cost(self):
        """Calculer le coût total de la maintenance"""
        self.total_cost = self.labor_cost + self.parts_cost + self.other_cost
        return self.total_cost
    
    def start_maintenance(self, start_date=None):
        """Démarrer la maintenance"""
        self.status = MaintenanceStatus.EN_COURS
        self.start_date = start_date or datetime.now()
    
    def complete_maintenance(self, completion_date=None):
        """Terminer la maintenance"""
        self.status = MaintenanceStatus.TERMINEE
        self.completion_date = completion_date or datetime.now()
    
    def cancel_maintenance(self):
        """Annuler la maintenance"""
        self.status = MaintenanceStatus.ANNULEE
    
    def is_overdue(self):
        """Vérifier si la maintenance est en retard"""
        if self.status in [MaintenanceStatus.TERMINEE, MaintenanceStatus.ANNULEE]:
            return False
        return datetime.now() > self.scheduled_date
    
    def days_until_scheduled(self):
        """Nombre de jours jusqu'à la date prévue"""
        if self.status in [MaintenanceStatus.TERMINEE, MaintenanceStatus.ANNULEE]:
            return None
        delta = self.scheduled_date - datetime.now()
        return delta.days
    
    def duration_hours(self):
        """Durée de la maintenance en heures"""
        if self.start_date and self.completion_date:
            delta = self.completion_date - self.start_date
            return round(delta.total_seconds() / 3600, 1)
        return None
    
    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'vehicle_plate': self.vehicle.plate_number if self.vehicle else None,
            'maintenance_type': self.maintenance_type.value,
            'status': self.status.value,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'mileage_at_maintenance': self.mileage_at_maintenance,
            'provider_name': self.provider_name,
            'provider_contact': self.provider_contact,
            'labor_cost': self.labor_cost,
            'parts_cost': self.parts_cost,
            'other_cost': self.other_cost,
            'total_cost': self.total_cost,
            'description': self.description,
            'parts_replaced': self.parts_replaced,
            'technician_name': self.technician_name,
            'notes': self.notes,
            'recommendations': self.recommendations,
            'invoice_number': self.invoice_number,
            'next_maintenance_date': self.next_maintenance_date.isoformat() if self.next_maintenance_date else None,
            'next_maintenance_mileage': self.next_maintenance_mileage,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_overdue': self.is_overdue(),
            'days_until_scheduled': self.days_until_scheduled(),
            'duration_hours': self.duration_hours()
        }
