"""
Modèle Student - Gestion des élèves
"""

import enum
from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Enum, Date, Float, Text
from sqlalchemy.orm import relationship

from .base import Base, BaseModel


class StudentStatus(enum.Enum):
    """Statuts possibles pour un élève"""
    ACTIVE = "actif"
    PENDING = "en_attente"
    SUSPENDED = "suspendu"
    GRADUATED = "diplome"
    ABANDONED = "abandonne"


class Student(Base, BaseModel):
    """Modèle élève pour la gestion des inscrits"""
    
    __tablename__ = "students"
    
    # Informations personnelles
    full_name = Column(String(100), nullable=False, index=True)
    cin = Column(String(20), unique=True, nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)
    
    # Informations inscription
    registration_date = Column(Date, default=date.today, nullable=False)
    status = Column(Enum(StudentStatus), default=StudentStatus.ACTIVE, nullable=False)
    
    # Informations permis
    license_type = Column(String(10), default="B", nullable=False)  # A, B, C, D
    theoretical_exam_passed = Column(Integer, default=0, nullable=False)  # Nombre de réussites
    practical_exam_passed = Column(Integer, default=0, nullable=False)
    theoretical_exam_attempts = Column(Integer, default=0, nullable=False)
    practical_exam_attempts = Column(Integer, default=0, nullable=False)
    
    # Informations financières
    total_paid = Column(Float, default=0.0, nullable=False)
    total_due = Column(Float, default=0.0, nullable=False)
    balance = Column(Float, default=0.0, nullable=False)  # Solde (négatif = dette)
    
    # Progression
    hours_completed = Column(Integer, default=0, nullable=False)  # Heures de conduite
    hours_planned = Column(Integer, default=20, nullable=False)  # Heures prévues au contrat
    
    # Informations contact d'urgence
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    
    # Notes et remarques
    notes = Column(Text, nullable=True)
    
    # Photo de profil (chemin)
    photo_path = Column(String(255), nullable=True)
    
    # Relations
    sessions = relationship("Session", back_populates="student", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="student", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="student", cascade="all, delete-orphan")
    
    def __init__(self, full_name: str, cin: str, date_of_birth: date, 
                 phone: str, **kwargs):
        """
        Initialiser un élève
        
        Args:
            full_name: Nom complet
            cin: Numéro CIN
            date_of_birth: Date de naissance
            phone: Téléphone
        """
        self.full_name = full_name
        self.cin = cin
        self.date_of_birth = date_of_birth
        self.phone = phone
        
        # Appliquer les autres attributs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def age(self) -> int:
        """Calculer l'âge de l'élève"""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def is_solvent(self) -> bool:
        """Vérifier si l'élève est à jour dans ses paiements"""
        # Balance = total_due - total_paid
        # Solvent if balance <= 0 (no debt or credit)
        return self.balance <= 0
    
    @property
    def completion_rate(self) -> float:
        """Calculer le taux de complétion des heures de conduite"""
        if self.hours_planned == 0:
            return 0.0
        return min(100.0, (self.hours_completed / self.hours_planned) * 100)
    
    def add_payment(self, amount: float) -> None:
        """
        Ajouter un paiement et mettre à jour le solde
        
        Args:
            amount: Montant du paiement
        
        Balance = total_due - total_paid
        - Balance > 0 : L'étudiant doit de l'argent (dette)
        - Balance < 0 : L'école doit de l'argent (crédit/trop-perçu)
        - Balance = 0 : À jour
        """
        self.total_paid += amount
        self.balance = self.total_due - self.total_paid
    
    def add_charge(self, amount: float) -> None:
        """
        Ajouter une charge (montant dû) et mettre à jour le solde
        
        Args:
            amount: Montant de la charge
        
        Balance = total_due - total_paid
        - Balance > 0 : L'étudiant doit de l'argent (dette)
        - Balance < 0 : L'école doit de l'argent (crédit/trop-perçu)
        - Balance = 0 : À jour
        """
        self.total_due += amount
        self.balance = self.total_due - self.total_paid
    
    def record_session(self, duration_hours: float = 1.0) -> None:
        """
        Enregistrer une session de conduite complétée
        
        Args:
            duration_hours: Durée de la session en heures
        """
        self.hours_completed += duration_hours
    
    def record_exam_attempt(self, exam_type: str, passed: bool) -> None:
        """
        Enregistrer une tentative d'examen
        
        Args:
            exam_type: Type d'examen ('theoretical' ou 'practical')
            passed: True si l'examen est réussi
        """
        if exam_type.lower() == 'theoretical':
            self.theoretical_exam_attempts += 1
            if passed:
                self.theoretical_exam_passed += 1
        elif exam_type.lower() == 'practical':
            self.practical_exam_attempts += 1
            if passed:
                self.practical_exam_passed += 1
                # Si l'examen pratique est réussi, passer au statut diplômé
                if passed:
                    self.status = StudentStatus.GRADUATED
    
    def __repr__(self) -> str:
        return f"<Student(id={self.id}, name='{self.full_name}', cin='{self.cin}', status='{self.status.value}')>"
    
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
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'status': self.status.value,
            'license_type': self.license_type,
            'theoretical_exam_passed': self.theoretical_exam_passed,
            'practical_exam_passed': self.practical_exam_passed,
            'theoretical_exam_attempts': self.theoretical_exam_attempts,
            'practical_exam_attempts': self.practical_exam_attempts,
            'total_paid': self.total_paid,
            'total_due': self.total_due,
            'balance': self.balance,
            'is_solvent': self.is_solvent,
            'hours_completed': self.hours_completed,
            'hours_planned': self.hours_planned,
            'completion_rate': self.completion_rate,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
