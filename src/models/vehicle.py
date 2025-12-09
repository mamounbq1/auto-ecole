"""
Modèle Vehicle - Gestion des véhicules
"""

import enum
from datetime import date
from typing import Optional

from sqlalchemy import Column, Integer, String, Enum, Date, Boolean, Text
from sqlalchemy.orm import relationship

from .base import Base, BaseModel


class VehicleStatus(enum.Enum):
    """Statuts possibles pour un véhicule"""
    AVAILABLE = "disponible"
    IN_SERVICE = "en_service"
    MAINTENANCE = "en_maintenance"
    OUT_OF_SERVICE = "hors_service"


class Vehicle(Base, BaseModel):
    """Modèle véhicule pour la gestion du parc automobile"""
    
    __tablename__ = "vehicles"
    
    # Informations du véhicule
    plate_number = Column(String(20), unique=True, nullable=False, index=True)
    make = Column(String(50), nullable=False)  # Marque
    model = Column(String(50), nullable=False)  # Modèle
    year = Column(Integer, nullable=True)  # Année
    color = Column(String(30), nullable=True)
    
    # Type de permis
    license_type = Column(String(10), default="B", nullable=False)  # A, B, C, D
    
    # Status et disponibilité
    status = Column(Enum(VehicleStatus), default=VehicleStatus.AVAILABLE, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    
    # Informations techniques
    vin = Column(String(17), nullable=True, unique=True)  # Vehicle Identification Number
    fuel_type = Column(String(20), default="Essence", nullable=True)  # Essence, Diesel, Électrique
    transmission = Column(String(20), default="Manuelle", nullable=True)  # Manuelle, Automatique
    
    # Dates importantes
    purchase_date = Column(Date, nullable=True)
    registration_date = Column(Date, nullable=True)
    last_maintenance_date = Column(Date, nullable=True)
    next_maintenance_date = Column(Date, nullable=True)
    insurance_expiry_date = Column(Date, nullable=True)
    technical_inspection_date = Column(Date, nullable=True)
    
    # Kilométrage
    current_mileage = Column(Integer, default=0, nullable=False)
    last_oil_change_mileage = Column(Integer, default=0, nullable=False)
    
    # Statistiques d'utilisation
    total_hours_used = Column(Integer, default=0, nullable=False)
    total_sessions = Column(Integer, default=0, nullable=False)
    
    # Coûts
    purchase_price = Column(Integer, default=0, nullable=False)
    maintenance_cost = Column(Integer, default=0, nullable=False)
    insurance_cost = Column(Integer, default=0, nullable=False)
    
    # Notes et remarques
    notes = Column(Text, nullable=True)
    
    # Relations
    sessions = relationship("Session", back_populates="vehicle")
    maintenances = relationship("VehicleMaintenance", back_populates="vehicle", cascade="all, delete-orphan")
    
    def __init__(self, plate_number: str, make: str, model: str, **kwargs):
        """
        Initialiser un véhicule
        
        Args:
            plate_number: Numéro de plaque d'immatriculation
            make: Marque du véhicule
            model: Modèle du véhicule
        """
        self.plate_number = plate_number
        self.make = make
        self.model = model
        
        # Appliquer les autres attributs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def full_name(self) -> str:
        """Nom complet du véhicule"""
        parts = [self.make, self.model]
        if self.year:
            parts.append(str(self.year))
        return " ".join(parts)
    
    @property
    def age_years(self) -> Optional[int]:
        """Âge du véhicule en années"""
        if not self.year:
            return None
        return date.today().year - self.year
    
    @property
    def needs_maintenance(self) -> bool:
        """Vérifier si le véhicule a besoin d'une maintenance"""
        if not self.next_maintenance_date:
            return False
        return date.today() >= self.next_maintenance_date
    
    @property
    def insurance_expired(self) -> bool:
        """Vérifier si l'assurance est expirée"""
        if not self.insurance_expiry_date:
            return False
        return date.today() >= self.insurance_expiry_date
    
    @property
    def technical_inspection_expired(self) -> bool:
        """Vérifier si le contrôle technique est expiré"""
        if not self.technical_inspection_date:
            return False
        return date.today() >= self.technical_inspection_date
    
    def record_session(self, duration_hours: float = 1.0, mileage_km: int = 0) -> None:
        """
        Enregistrer une session d'utilisation
        
        Args:
            duration_hours: Durée de la session en heures
            mileage_km: Kilométrage parcouru
        """
        self.total_hours_used += duration_hours
        self.total_sessions += 1
        self.current_mileage += mileage_km
    
    def record_maintenance(self, cost: float = 0.0, mileage: Optional[int] = None) -> None:
        """
        Enregistrer une maintenance
        
        Args:
            cost: Coût de la maintenance
            mileage: Kilométrage actuel (optionnel)
        """
        self.last_maintenance_date = date.today()
        self.maintenance_cost += cost
        if mileage is not None:
            self.current_mileage = mileage
    
    def set_available(self, available: bool) -> None:
        """
        Définir la disponibilité du véhicule
        
        Args:
            available: True si disponible
        """
        self.is_available = available
        if available:
            self.status = VehicleStatus.AVAILABLE
        else:
            self.status = VehicleStatus.IN_SERVICE
    
    def __repr__(self) -> str:
        return f"<Vehicle(id={self.id}, plate='{self.plate_number}', model='{self.full_name}', status='{self.status.value}')>"
    
    def to_dict(self) -> dict:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'plate_number': self.plate_number,
            'make': self.make,
            'model': self.model,
            'full_name': self.full_name,
            'year': self.year,
            'age_years': self.age_years,
            'color': self.color,
            'license_type': self.license_type,
            'status': self.status.value,
            'is_available': self.is_available,
            'vin': self.vin,
            'fuel_type': self.fuel_type,
            'transmission': self.transmission,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'last_maintenance_date': self.last_maintenance_date.isoformat() if self.last_maintenance_date else None,
            'next_maintenance_date': self.next_maintenance_date.isoformat() if self.next_maintenance_date else None,
            'insurance_expiry_date': self.insurance_expiry_date.isoformat() if self.insurance_expiry_date else None,
            'technical_inspection_date': self.technical_inspection_date.isoformat() if self.technical_inspection_date else None,
            'needs_maintenance': self.needs_maintenance,
            'insurance_expired': self.insurance_expired,
            'technical_inspection_expired': self.technical_inspection_expired,
            'current_mileage': self.current_mileage,
            'last_oil_change_mileage': self.last_oil_change_mileage,
            'total_hours_used': self.total_hours_used,
            'total_sessions': self.total_sessions,
            'purchase_price': self.purchase_price,
            'maintenance_cost': self.maintenance_cost,
            'insurance_cost': self.insurance_cost,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
