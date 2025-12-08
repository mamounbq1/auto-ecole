"""
Modèle Session - Gestion des séances de conduite
"""

import enum
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship

from .base import Base, BaseModel


class SessionType(enum.Enum):
    """Types de sessions"""
    PRACTICAL_DRIVING = "conduite_pratique"
    THEORETICAL_CLASS = "cours_theorique"
    CODE_EXAM = "examen_code"
    PRACTICAL_EXAM = "examen_pratique"
    SIMULATION = "simulation"
    ROAD_SESSION = "creneau_route"
    CITY_SESSION = "creneau_ville"
    HIGHWAY_SESSION = "creneau_autoroute"


class SessionStatus(enum.Enum):
    """Statuts possibles pour une session"""
    SCHEDULED = "prevu"
    CONFIRMED = "confirme"
    IN_PROGRESS = "en_cours"
    COMPLETED = "realise"
    CANCELLED = "annule"
    NO_SHOW = "absent"


class Session(Base, BaseModel):
    """Modèle session pour la gestion des créneaux de conduite"""
    
    __tablename__ = "sessions"
    
    # Relations avec d'autres entités
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    instructor_id = Column(Integer, ForeignKey('instructors.id', ondelete='SET NULL'), nullable=True, index=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Informations de la session
    session_type = Column(Enum(SessionType), default=SessionType.PRACTICAL_DRIVING, nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.SCHEDULED, nullable=False)
    
    # Horaires
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60, nullable=False)
    
    # Lieu de départ/arrivée
    pickup_location = Column(String(255), nullable=True)
    dropoff_location = Column(String(255), nullable=True)
    
    # Détails de la session
    distance_km = Column(Float, default=0.0, nullable=False)
    fuel_consumed = Column(Float, default=0.0, nullable=False)
    
    # Évaluation et remarques
    performance_score = Column(Integer, nullable=True)  # Note sur 10 ou 20
    instructor_notes = Column(Text, nullable=True)
    student_feedback = Column(Text, nullable=True)
    
    # Compétences travaillées (JSON ou texte)
    skills_practiced = Column(Text, nullable=True)  # Ex: "stationnement,créneaux,ronds-points"
    
    # Facturation
    price = Column(Float, default=0.0, nullable=False)
    is_paid = Column(Integer, default=0, nullable=False)  # Booléen (0 ou 1)
    
    # Notes administratives
    cancellation_reason = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relations ORM
    student = relationship("Student", back_populates="sessions")
    instructor = relationship("Instructor", back_populates="sessions")
    vehicle = relationship("Vehicle", back_populates="sessions")
    
    def __init__(self, student_id: int, start_datetime: datetime,
                 duration_minutes: int = 60, **kwargs):
        """
        Initialiser une session
        
        Args:
            student_id: ID de l'élève
            start_datetime: Date et heure de début
            duration_minutes: Durée en minutes
        """
        self.student_id = student_id
        self.start_datetime = start_datetime
        self.duration_minutes = duration_minutes
        self.end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        
        # Appliquer les autres attributs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def duration_hours(self) -> float:
        """Durée de la session en heures"""
        return self.duration_minutes / 60.0
    
    @property
    def is_past(self) -> bool:
        """Vérifier si la session est passée"""
        return self.end_datetime < datetime.now()
    
    @property
    def is_upcoming(self) -> bool:
        """Vérifier si la session est à venir"""
        return self.start_datetime > datetime.now()
    
    @property
    def is_today(self) -> bool:
        """Vérifier si la session est aujourd'hui"""
        today = datetime.now().date()
        return self.start_datetime.date() == today
    
    @property
    def can_be_cancelled(self) -> bool:
        """Vérifier si la session peut être annulée"""
        return self.status in [SessionStatus.SCHEDULED, SessionStatus.CONFIRMED] and self.is_upcoming
    
    @property
    def can_be_completed(self) -> bool:
        """Vérifier si la session peut être marquée comme complétée"""
        return self.status in [SessionStatus.SCHEDULED, SessionStatus.CONFIRMED, SessionStatus.IN_PROGRESS]
    
    def mark_as_completed(self, performance_score: Optional[int] = None,
                         instructor_notes: Optional[str] = None) -> None:
        """
        Marquer la session comme complétée
        
        Args:
            performance_score: Note de performance
            instructor_notes: Remarques du moniteur
        """
        self.status = SessionStatus.COMPLETED
        if performance_score is not None:
            self.performance_score = performance_score
        if instructor_notes is not None:
            self.instructor_notes = instructor_notes
    
    def mark_as_cancelled(self, reason: Optional[str] = None) -> None:
        """
        Marquer la session comme annulée
        
        Args:
            reason: Raison de l'annulation
        """
        self.status = SessionStatus.CANCELLED
        if reason:
            self.cancellation_reason = reason
    
    def mark_as_no_show(self) -> None:
        """Marquer l'élève comme absent"""
        self.status = SessionStatus.NO_SHOW
    
    def update_end_datetime(self) -> None:
        """Mettre à jour l'heure de fin en fonction de la durée"""
        self.end_datetime = self.start_datetime + timedelta(minutes=self.duration_minutes)
    
    def __repr__(self) -> str:
        return (f"<Session(id={self.id}, student_id={self.student_id}, "
                f"type='{self.session_type.value}', status='{self.status.value}', "
                f"start='{self.start_datetime}')>")
    
    def to_dict(self) -> dict:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'instructor_id': self.instructor_id,
            'vehicle_id': self.vehicle_id,
            'session_type': self.session_type.value,
            'status': self.status.value,
            'start_datetime': self.start_datetime.isoformat() if self.start_datetime else None,
            'end_datetime': self.end_datetime.isoformat() if self.end_datetime else None,
            'duration_minutes': self.duration_minutes,
            'duration_hours': self.duration_hours,
            'pickup_location': self.pickup_location,
            'dropoff_location': self.dropoff_location,
            'distance_km': self.distance_km,
            'fuel_consumed': self.fuel_consumed,
            'performance_score': self.performance_score,
            'instructor_notes': self.instructor_notes,
            'student_feedback': self.student_feedback,
            'skills_practiced': self.skills_practiced,
            'price': self.price,
            'is_paid': self.is_paid,
            'cancellation_reason': self.cancellation_reason,
            'notes': self.notes,
            'is_past': self.is_past,
            'is_upcoming': self.is_upcoming,
            'is_today': self.is_today,
            'can_be_cancelled': self.can_be_cancelled,
            'can_be_completed': self.can_be_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
