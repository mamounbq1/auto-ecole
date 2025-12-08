"""
Modèle Exam - Gestion des examens
"""

import enum
from datetime import datetime, date
from typing import Optional

from sqlalchemy import Column, Integer, String, Enum, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from .base import Base, BaseModel


class ExamType(enum.Enum):
    """Types d'examens"""
    THEORETICAL = "theorique"
    PRACTICAL = "pratique"


class ExamResult(enum.Enum):
    """Résultats possibles pour un examen"""
    PASSED = "reussi"
    FAILED = "echoue"
    ABSENT = "absent"
    PENDING = "en_attente"


class Exam(Base, BaseModel):
    """Modèle examen pour la gestion des sessions d'examen"""
    
    __tablename__ = "exams"
    
    # Relation avec l'élève
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Type et résultat
    exam_type = Column(Enum(ExamType), nullable=False)
    result = Column(Enum(ExamResult), default=ExamResult.PENDING, nullable=False)
    
    # Dates
    scheduled_date = Column(Date, nullable=False, index=True)
    scheduled_time = Column(String(10), nullable=True)  # Format HH:MM
    completion_date = Column(Date, nullable=True)
    
    # Lieu
    location = Column(String(255), nullable=True)
    exam_center = Column(String(100), nullable=True)
    
    # Pour examen théorique
    theory_score = Column(Integer, nullable=True)  # Score sur 40 ou autre
    theory_max_score = Column(Integer, default=40, nullable=True)
    theory_passing_score = Column(Integer, default=35, nullable=True)
    
    # Pour examen pratique
    practical_score = Column(Integer, nullable=True)  # Score ou évaluation
    examiner_name = Column(String(100), nullable=True)
    vehicle_plate = Column(String(20), nullable=True)
    
    # Informations complémentaires
    attempt_number = Column(Integer, default=1, nullable=False)  # Numéro de tentative
    is_official = Column(Boolean, default=True, nullable=False)  # Officiel ou test blanc
    
    # Convocation
    summons_number = Column(String(50), nullable=True)  # Numéro de convocation
    summons_generated = Column(Boolean, default=False, nullable=False)
    summons_sent = Column(Boolean, default=False, nullable=False)
    
    # Coût
    registration_fee = Column(Integer, default=0, nullable=False)
    is_paid = Column(Boolean, default=False, nullable=False)
    
    # Notes et remarques
    examiner_notes = Column(Text, nullable=True)
    errors_made = Column(Text, nullable=True)  # Erreurs commises
    notes = Column(Text, nullable=True)
    
    # Relations ORM
    student = relationship("Student", back_populates="exams")
    
    def __init__(self, student_id: int, exam_type: ExamType,
                 scheduled_date: date, **kwargs):
        """
        Initialiser un examen
        
        Args:
            student_id: ID de l'élève
            exam_type: Type d'examen
            scheduled_date: Date prévue de l'examen
        """
        self.student_id = student_id
        self.exam_type = exam_type
        self.scheduled_date = scheduled_date
        
        # Appliquer les autres attributs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def is_past(self) -> bool:
        """Vérifier si l'examen est passé"""
        return self.scheduled_date < date.today()
    
    @property
    def is_upcoming(self) -> bool:
        """Vérifier si l'examen est à venir"""
        return self.scheduled_date > date.today()
    
    @property
    def is_today(self) -> bool:
        """Vérifier si l'examen est aujourd'hui"""
        return self.scheduled_date == date.today()
    
    @property
    def theory_percentage(self) -> Optional[float]:
        """Calculer le pourcentage pour l'examen théorique"""
        if self.theory_score is not None and self.theory_max_score:
            return (self.theory_score / self.theory_max_score) * 100
        return None
    
    @property
    def has_passed(self) -> bool:
        """Vérifier si l'examen est réussi"""
        return self.result == ExamResult.PASSED
    
    def record_result(self, result: ExamResult, score: Optional[int] = None,
                     examiner_notes: Optional[str] = None) -> None:
        """
        Enregistrer le résultat de l'examen
        
        Args:
            result: Résultat de l'examen
            score: Score obtenu
            examiner_notes: Remarques de l'examinateur
        """
        self.result = result
        self.completion_date = date.today()
        
        if score is not None:
            if self.exam_type == ExamType.THEORETICAL:
                self.theory_score = score
            else:
                self.practical_score = score
        
        if examiner_notes:
            self.examiner_notes = examiner_notes
    
    def generate_summons_number(self) -> str:
        """
        Générer un numéro de convocation
        
        Returns:
            Numéro de convocation formaté
        """
        # Format: CONV-TYPE-YYYYMMDD-XXXXX
        type_prefix = "TH" if self.exam_type == ExamType.THEORETICAL else "PR"
        date_str = self.scheduled_date.strftime('%Y%m%d')
        if self.id:
            return f"CONV-{type_prefix}-{date_str}-{self.id:05d}"
        return f"CONV-{type_prefix}-{date_str}-DRAFT"
    
    def mark_summons_generated(self) -> None:
        """Marquer la convocation comme générée"""
        self.summons_generated = True
        if not self.summons_number:
            self.summons_number = self.generate_summons_number()
    
    def mark_summons_sent(self) -> None:
        """Marquer la convocation comme envoyée"""
        self.summons_sent = True
        if not self.summons_generated:
            self.mark_summons_generated()
    
    def __repr__(self) -> str:
        return (f"<Exam(id={self.id}, student_id={self.student_id}, "
                f"type='{self.exam_type.value}', result='{self.result.value}', "
                f"date='{self.scheduled_date}')>")
    
    def to_dict(self) -> dict:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'exam_type': self.exam_type.value,
            'result': self.result.value,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'scheduled_time': self.scheduled_time,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'location': self.location,
            'exam_center': self.exam_center,
            'theory_score': self.theory_score,
            'theory_max_score': self.theory_max_score,
            'theory_passing_score': self.theory_passing_score,
            'theory_percentage': self.theory_percentage,
            'practical_score': self.practical_score,
            'examiner_name': self.examiner_name,
            'vehicle_plate': self.vehicle_plate,
            'attempt_number': self.attempt_number,
            'is_official': self.is_official,
            'summons_number': self.summons_number,
            'summons_generated': self.summons_generated,
            'summons_sent': self.summons_sent,
            'registration_fee': self.registration_fee,
            'is_paid': self.is_paid,
            'examiner_notes': self.examiner_notes,
            'errors_made': self.errors_made,
            'notes': self.notes,
            'is_past': self.is_past,
            'is_upcoming': self.is_upcoming,
            'is_today': self.is_today,
            'has_passed': self.has_passed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
