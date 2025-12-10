"""
Modèle Document - Pour gestion des documents des élèves
Utilisé uniquement dans le module Élèves
"""

import enum
from datetime import datetime, date
from typing import Optional

from sqlalchemy import Column, Integer, String, Enum, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from .base import Base, BaseModel


class DocumentType(enum.Enum):
    """Types de documents"""
    CIN = "cin"
    PASSPORT = "passport"
    BIRTH_CERTIFICATE = "birth_certificate"
    MEDICAL_CERTIFICATE = "medical_certificate"
    PHOTO = "photo"
    RESIDENCE_CERTIFICATE = "residence_certificate"
    LICENSE_COPY = "license_copy"
    SIGNATURE = "signature"
    CONTRACT = "contract"
    PAYMENT_PROOF = "payment_proof"
    OTHER = "other"


class DocumentStatus(enum.Enum):
    """Statuts de documents"""
    VALID = "valid"
    EXPIRED = "expired"
    PENDING = "pending"
    REJECTED = "rejected"


class Document(Base, BaseModel):
    """Modèle pour la gestion des documents des élèves"""
    
    __tablename__ = "documents"
    
    # Relation avec l'élève
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Informations du document
    title = Column(String(255), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    
    # Fichier
    file_path = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)  # En octets
    mime_type = Column(String(100), nullable=True)
    
    # Dates
    upload_date = Column(DateTime, default=datetime.now, nullable=False)
    expiry_date = Column(Date, nullable=True)
    verification_date = Column(DateTime, nullable=True)
    
    # Métadonnées
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    is_required = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_by = Column(String(100), nullable=True)
    
    # Relations ORM
    student = relationship("Student", back_populates="documents")
    
    def __init__(self, student_id: int, title: str, document_type: DocumentType, **kwargs):
        """
        Initialiser un document
        
        Args:
            student_id: ID de l'élève
            title: Titre du document
            document_type: Type de document
        """
        self.student_id = student_id
        self.title = title
        self.document_type = document_type
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def is_expired(self) -> bool:
        """Vérifier si le document est expiré"""
        if self.expiry_date:
            return self.expiry_date < date.today()
        return False
    
    @property
    def days_until_expiry(self) -> Optional[int]:
        """Nombre de jours jusqu'à expiration"""
        if self.expiry_date:
            delta = self.expiry_date - date.today()
            return delta.days
        return None
    
    @property
    def file_size_mb(self) -> Optional[float]:
        """Taille du fichier en MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None
    
    def mark_verified(self, verified_by: str) -> None:
        """Marquer le document comme vérifié"""
        self.is_verified = True
        self.verified_by = verified_by
        self.verification_date = datetime.now()
        self.status = DocumentStatus.VALID
    
    def __repr__(self) -> str:
        return (f"<Document(id={self.id}, student_id={self.student_id}, "
                f"type='{self.document_type.value}', title='{self.title}')>")
    
    def to_dict(self) -> dict:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'title': self.title,
            'document_type': self.document_type.value,
            'status': self.status.value,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_size_mb': self.file_size_mb,
            'mime_type': self.mime_type,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'description': self.description,
            'notes': self.notes,
            'is_required': self.is_required,
            'is_verified': self.is_verified,
            'verified_by': self.verified_by,
            'is_expired': self.is_expired,
            'days_until_expiry': self.days_until_expiry,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
