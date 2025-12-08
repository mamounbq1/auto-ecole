"""
Modèle Instructor - Gestion des moniteurs
"""

from datetime import date
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Date, Boolean, Text
from sqlalchemy.orm import relationship

from .base import Base, BaseModel


class Instructor(Base, BaseModel):
    """Modèle moniteur pour la gestion des instructeurs"""
    
    __tablename__ = "instructors"
    
    # Informations personnelles
    full_name = Column(String(100), nullable=False, index=True)
    cin = Column(String(20), unique=True, nullable=False, index=True)
    date_of_birth = Column(Date, nullable=True)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)
    
    # Informations professionnelles
    license_number = Column(String(50), nullable=False, unique=True)  # Numéro de permis
    license_types = Column(String(50), default="B", nullable=False)  # Ex: "A,B,C"
    hire_date = Column(Date, default=date.today, nullable=False)
    
    # Disponibilité
    is_available = Column(Boolean, default=True, nullable=False)
    max_students_per_day = Column(Integer, default=8, nullable=False)
    
    # Statistiques
    total_hours_taught = Column(Integer, default=0, nullable=False)
    total_students_taught = Column(Integer, default=0, nullable=False)
    success_rate = Column(Integer, default=0, nullable=False)  # Pourcentage de réussite
    
    # Salaire et paiements
    hourly_rate = Column(Integer, default=0, nullable=False)  # Taux horaire
    monthly_salary = Column(Integer, default=0, nullable=False)  # Salaire mensuel fixe
    
    # Informations contact d'urgence
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    
    # Notes et remarques
    notes = Column(Text, nullable=True)
    
    # Photo de profil (chemin)
    photo_path = Column(String(255), nullable=True)
    
    # Relations
    sessions = relationship("Session", back_populates="instructor")
    
    def __init__(self, full_name: str, cin: str, phone: str, 
                 license_number: str, **kwargs):
        """
        Initialiser un moniteur
        
        Args:
            full_name: Nom complet
            cin: Numéro CIN
            phone: Téléphone
            license_number: Numéro de permis
        """
        self.full_name = full_name
        self.cin = cin
        self.phone = phone
        self.license_number = license_number
        
        # Appliquer les autres attributs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def age(self) -> Optional[int]:
        """Calculer l'âge du moniteur"""
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def license_types_list(self) -> List[str]:
        """Obtenir la liste des types de permis"""
        if not self.license_types:
            return []
        return [lt.strip() for lt in self.license_types.split(',')]
    
    def can_teach_license_type(self, license_type: str) -> bool:
        """
        Vérifier si le moniteur peut enseigner un type de permis
        
        Args:
            license_type: Type de permis à vérifier
        
        Returns:
            True si le moniteur peut enseigner ce type
        """
        return license_type.upper() in [lt.upper() for lt in self.license_types_list]
    
    def record_session(self, duration_hours: float = 1.0) -> None:
        """
        Enregistrer une session d'enseignement
        
        Args:
            duration_hours: Durée de la session en heures
        """
        self.total_hours_taught += duration_hours
    
    def update_success_rate(self, passed_students: int, total_students: int) -> None:
        """
        Mettre à jour le taux de réussite
        
        Args:
            passed_students: Nombre d'élèves ayant réussi
            total_students: Nombre total d'élèves
        """
        if total_students > 0:
            self.success_rate = int((passed_students / total_students) * 100)
        else:
            self.success_rate = 0
    
    def __repr__(self) -> str:
        return f"<Instructor(id={self.id}, name='{self.full_name}', license='{self.license_number}')>"
    
    def to_dict(self) -> dict:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'cin': self.cin,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'age': self.age,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'license_number': self.license_number,
            'license_types': self.license_types,
            'license_types_list': self.license_types_list,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'is_available': self.is_available,
            'max_students_per_day': self.max_students_per_day,
            'total_hours_taught': self.total_hours_taught,
            'total_students_taught': self.total_students_taught,
            'success_rate': self.success_rate,
            'hourly_rate': self.hourly_rate,
            'monthly_salary': self.monthly_salary,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
