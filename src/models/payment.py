"""
Modèle Payment - Gestion des paiements
"""

import enum
from datetime import datetime, date
from typing import Optional

from sqlalchemy import Column, Integer, String, Enum, Date, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from .base import Base, BaseModel


class PaymentMethod(enum.Enum):
    """Méthodes de paiement disponibles"""
    CASH = "especes"
    CARD = "carte_bancaire"
    CHECK = "cheque"
    TRANSFER = "virement"
    MOBILE_MONEY = "mobile_money"


class Payment(Base, BaseModel):
    """Modèle paiement pour la gestion des transactions financières"""
    
    __tablename__ = "payments"
    
    # Relation avec l'élève
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Informations du paiement
    amount = Column(Float, nullable=False)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.CASH, nullable=False)
    payment_date = Column(Date, default=date.today, nullable=False, index=True)
    
    # Référence et traçabilité
    receipt_number = Column(String(50), unique=True, nullable=True, index=True)
    reference_number = Column(String(100), nullable=True)  # Numéro de chèque, transaction, etc.
    
    # Description
    description = Column(String(255), nullable=True)
    category = Column(String(50), default="inscription", nullable=True)  # inscription, conduite, examen, etc.
    
    # Validation et status
    is_validated = Column(Boolean, default=True, nullable=False)
    validated_by = Column(String(100), nullable=True)  # Nom du caissier
    validated_at = Column(Date, nullable=True)
    
    # Annulation
    is_cancelled = Column(Boolean, default=False, nullable=False)
    cancellation_reason = Column(String(255), nullable=True)
    cancelled_at = Column(Date, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Relations ORM
    student = relationship("Student", back_populates="payments")
    
    def __init__(self, student_id: int, amount: float,
                 payment_method: PaymentMethod = PaymentMethod.CASH, **kwargs):
        """
        Initialiser un paiement
        
        Args:
            student_id: ID de l'élève
            amount: Montant du paiement
            payment_method: Méthode de paiement
        """
        self.student_id = student_id
        self.amount = amount
        self.payment_method = payment_method
        
        # Appliquer les autres attributs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def generate_receipt_number(self) -> str:
        """
        Générer un numéro de reçu unique
        
        Returns:
            Numéro de reçu formaté
        """
        # Format: REC-YYYYMMDD-XXXXX
        payment_date = self.payment_date if self.payment_date else date.today()
        date_str = payment_date.strftime('%Y%m%d')
        if self.id:
            return f"REC-{date_str}-{self.id:05d}"
        # Use timestamp for draft to ensure uniqueness
        import time
        timestamp = int(time.time() * 1000)  # milliseconds
        return f"REC-{date_str}-DRAFT-{timestamp}"
    
    def validate(self, validated_by: str) -> None:
        """
        Valider le paiement
        
        Args:
            validated_by: Nom de la personne qui valide
        """
        self.is_validated = True
        self.validated_by = validated_by
        self.validated_at = date.today()
        
        # Générer le numéro de reçu si pas déjà fait
        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()
    
    def cancel(self, reason: str) -> None:
        """
        Annuler le paiement
        
        Args:
            reason: Raison de l'annulation
        """
        self.is_cancelled = True
        self.cancellation_reason = reason
        self.cancelled_at = date.today()
    
    @property
    def is_active(self) -> bool:
        """Vérifier si le paiement est actif (non annulé)"""
        return not self.is_cancelled
    
    @property
    def status(self) -> str:
        """Obtenir le statut du paiement"""
        if self.is_cancelled:
            return "annule"
        elif self.is_validated:
            return "valide"
        else:
            return "en_attente"
    
    def __repr__(self) -> str:
        return (f"<Payment(id={self.id}, student_id={self.student_id}, "
                f"amount={self.amount}, method='{self.payment_method.value}', "
                f"date='{self.payment_date}')>")
    
    def to_dict(self) -> dict:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'amount': self.amount,
            'payment_method': self.payment_method.value,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'receipt_number': self.receipt_number,
            'reference_number': self.reference_number,
            'description': self.description,
            'category': self.category,
            'is_validated': self.is_validated,
            'validated_by': self.validated_by,
            'validated_at': self.validated_at.isoformat() if self.validated_at else None,
            'is_cancelled': self.is_cancelled,
            'cancellation_reason': self.cancellation_reason,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'is_active': self.is_active,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
