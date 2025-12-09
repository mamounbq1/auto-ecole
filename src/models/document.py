"""
Modèle pour la gestion des documents
Phase 3 - Gestion Documentaire
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, BigInteger, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import Base
import os


class DocumentType(str, Enum):
    """Types de documents"""
    # Documents d'identité
    CIN = "cin"
    PASSPORT = "passeport"
    RESIDENCE_PERMIT = "titre_sejour"
    
    # Documents de permis
    DRIVER_LICENSE = "permis_conduire"
    LICENSE_APPLICATION = "demande_permis"
    
    # Documents contractuels
    REGISTRATION_CONTRACT = "contrat_inscription"
    TRAINING_CERTIFICATE = "attestation_formation"
    COMPLETION_CERTIFICATE = "certificat_fin_formation"
    
    # Documents financiers
    PAYMENT_RECEIPT = "recu_paiement"
    INVOICE = "facture"
    
    # Documents examens
    EXAM_SUMMONS = "convocation_examen"
    EXAM_RESULT = "resultat_examen"
    
    # Documents véhicules
    VEHICLE_REGISTRATION = "carte_grise"
    VEHICLE_INSURANCE = "assurance_vehicule"
    MAINTENANCE_INVOICE = "facture_maintenance"
    TECHNICAL_INSPECTION = "controle_technique"
    
    # Photos
    PHOTO_IDENTITY = "photo_identite"
    PHOTO_SIGNATURE = "photo_signature"
    
    # Autres
    MEDICAL_CERTIFICATE = "certificat_medical"
    OTHER = "autre"


class DocumentStatus(str, Enum):
    """Statuts de documents"""
    ACTIVE = "actif"
    EXPIRED = "expire"
    PENDING_VALIDATION = "en_attente_validation"
    VALIDATED = "valide"
    REJECTED = "rejete"
    ARCHIVED = "archive"


class Document(Base):
    """
    Modèle pour la gestion des documents
    
    Permet de stocker et gérer tous les documents liés à l'auto-école :
    - Documents élèves (CIN, photos, certificats)
    - Documents contractuels (contrats, attestations)
    - Documents financiers (reçus, factures)
    - Documents véhicules (carte grise, assurance)
    - Documents examens (convocations, résultats)
    """
    
    __tablename__ = 'documents'
    
    # Clé primaire
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Type et catégorie
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.ACTIVE, nullable=False)
    
    # Entité liée (peut être un student, instructor, vehicle, etc.)
    entity_type = Column(String(50), nullable=True)  # student, instructor, vehicle, payment, exam
    entity_id = Column(Integer, nullable=True)
    
    # Informations du document
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Stockage du fichier
    file_path = Column(String(1000), nullable=False)  # Chemin relatif ou absolu
    file_name = Column(String(500), nullable=False)  # Nom original du fichier
    file_size = Column(BigInteger, nullable=True)  # Taille en bytes
    mime_type = Column(String(100), nullable=True)  # ex: application/pdf, image/jpeg
    
    # Métadonnées
    reference_number = Column(String(200), nullable=True)  # Numéro de référence (ex: numéro CIN)
    issue_date = Column(DateTime, nullable=True)  # Date d'émission
    expiry_date = Column(DateTime, nullable=True)  # Date d'expiration
    
    # Validation
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_by = Column(String(200), nullable=True)  # Utilisateur ayant vérifié
    verified_at = Column(DateTime, nullable=True)
    
    # Tags et recherche
    tags = Column(Text, nullable=True)  # Tags séparés par virgules
    notes = Column(Text, nullable=True)
    
    # Génération automatique
    is_generated = Column(Boolean, default=False, nullable=False)  # Document généré automatiquement
    template_used = Column(String(200), nullable=True)  # Template utilisé pour la génération
    
    # Métadonnées système
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    created_by = Column(String(200), nullable=True)
    
    # Relations optionnelles (à activer selon les besoins)
    # student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=True)
    # student = relationship('Student', back_populates='documents')
    
    def __repr__(self):
        return (
            f"<Document(id={self.id}, type={self.document_type.value}, "
            f"title={self.title}, entity={self.entity_type}:{self.entity_id})>"
        )
    
    def mark_as_verified(self, verified_by: str = None):
        """Marquer le document comme vérifié"""
        self.is_verified = True
        self.verified_by = verified_by
        self.verified_at = datetime.now()
        self.status = DocumentStatus.VALIDATED
    
    def mark_as_expired(self):
        """Marquer le document comme expiré"""
        self.status = DocumentStatus.EXPIRED
    
    def is_expiring_soon(self, days: int = 30) -> bool:
        """Vérifier si le document expire bientôt"""
        if not self.expiry_date:
            return False
        days_until_expiry = (self.expiry_date - datetime.now()).days
        return 0 < days_until_expiry <= days
    
    def is_expired(self) -> bool:
        """Vérifier si le document est expiré"""
        if not self.expiry_date:
            return False
        return datetime.now() > self.expiry_date
    
    def get_file_extension(self) -> str:
        """Obtenir l'extension du fichier"""
        return os.path.splitext(self.file_name)[1].lower()
    
    def get_file_size_mb(self) -> float:
        """Obtenir la taille du fichier en MB"""
        if not self.file_size:
            return 0.0
        return round(self.file_size / (1024 * 1024), 2)
    
    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'document_type': self.document_type.value,
            'status': self.status.value,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'title': self.title,
            'description': self.description,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_size_mb': self.get_file_size_mb(),
            'mime_type': self.mime_type,
            'file_extension': self.get_file_extension(),
            'reference_number': self.reference_number,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'is_verified': self.is_verified,
            'verified_by': self.verified_by,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'tags': self.tags,
            'notes': self.notes,
            'is_generated': self.is_generated,
            'template_used': self.template_used,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'is_expired': self.is_expired(),
            'is_expiring_soon': self.is_expiring_soon()
        }
