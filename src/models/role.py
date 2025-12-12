"""
Modèles Role et Permission - Système RBAC multi-rôles
"""

import enum
from datetime import datetime
from typing import List, Set

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, Text
from sqlalchemy.orm import relationship

from .base import Base, BaseModel


class PermissionType(enum.Enum):
    """Types de permissions dans le système"""
    # Gestion des élèves
    VIEW_STUDENTS = "view_students"
    CREATE_STUDENTS = "create_students"
    EDIT_STUDENTS = "edit_students"
    DELETE_STUDENTS = "delete_students"
    
    # Gestion des moniteurs
    VIEW_INSTRUCTORS = "view_instructors"
    CREATE_INSTRUCTORS = "create_instructors"
    EDIT_INSTRUCTORS = "edit_instructors"
    DELETE_INSTRUCTORS = "delete_instructors"
    
    # Gestion des véhicules
    VIEW_VEHICLES = "view_vehicles"
    CREATE_VEHICLES = "create_vehicles"
    EDIT_VEHICLES = "edit_vehicles"
    DELETE_VEHICLES = "delete_vehicles"
    
    # Gestion des séances
    VIEW_SESSIONS = "view_sessions"
    CREATE_SESSIONS = "create_sessions"
    EDIT_SESSIONS = "edit_sessions"
    DELETE_SESSIONS = "delete_sessions"
    
    # Gestion des paiements
    VIEW_PAYMENTS = "view_payments"
    CREATE_PAYMENTS = "create_payments"
    EDIT_PAYMENTS = "edit_payments"
    DELETE_PAYMENTS = "delete_payments"
    
    # Gestion des examens
    VIEW_EXAMS = "view_exams"
    CREATE_EXAMS = "create_exams"
    EDIT_EXAMS = "edit_exams"
    DELETE_EXAMS = "delete_exams"
    
    # Gestion des documents
    VIEW_DOCUMENTS = "view_documents"
    CREATE_DOCUMENTS = "create_documents"
    EDIT_DOCUMENTS = "edit_documents"
    DELETE_DOCUMENTS = "delete_documents"
    
    # Rapports et statistiques
    VIEW_REPORTS = "view_reports"
    VIEW_STATISTICS = "view_statistics"
    VIEW_FINANCIAL_REPORTS = "view_financial_reports"
    
    # Administration système
    VIEW_SETTINGS = "view_settings"
    EDIT_SETTINGS = "edit_settings"
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    MANAGE_BACKUPS = "manage_backups"
    VIEW_LOGS = "view_logs"


# Table d'association many-to-many entre Role et Permission
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
)


# Table d'association many-to-many entre User et Role
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)


class Permission(Base, BaseModel):
    """Modèle Permission - Permissions individuelles du système"""
    
    __tablename__ = "permissions"
    
    # Clé unique de la permission (utilisée dans le code)
    key = Column(String(100), unique=True, nullable=False, index=True)
    
    # Nom d'affichage
    name = Column(String(100), nullable=False)
    
    # Description de la permission
    description = Column(Text, nullable=True)
    
    # Catégorie (pour grouper les permissions dans l'UI)
    category = Column(String(50), nullable=True)
    
    # Actif/Inactif
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relations
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    
    def __repr__(self) -> str:
        return f"<Permission(key='{self.key}', name='{self.name}')>"
    
    def to_dict(self) -> dict:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'key': self.key,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Role(Base, BaseModel):
    """Modèle Role - Rôles du système avec permissions"""
    
    __tablename__ = "roles"
    
    # Nom du rôle (unique)
    name = Column(String(50), unique=True, nullable=False, index=True)
    
    # Nom d'affichage
    display_name = Column(String(100), nullable=False)
    
    # Description du rôle
    description = Column(Text, nullable=True)
    
    # Actif/Inactif
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Rôle système (ne peut pas être supprimé)
    is_system = Column(Boolean, default=False, nullable=False)
    
    # Relations
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("User", secondary=user_roles, back_populates="roles")
    
    def __repr__(self) -> str:
        return f"<Role(name='{self.name}', display_name='{self.display_name}')>"
    
    def has_permission(self, permission_key: str) -> bool:
        """
        Vérifier si ce rôle a une permission spécifique
        
        Args:
            permission_key: Clé de la permission
        
        Returns:
            True si le rôle a cette permission
        """
        return any(p.key == permission_key and p.is_active for p in self.permissions)
    
    def get_permission_keys(self) -> Set[str]:
        """
        Obtenir toutes les clés de permissions de ce rôle
        
        Returns:
            Set des clés de permissions
        """
        return {p.key for p in self.permissions if p.is_active}
    
    def to_dict(self, include_permissions: bool = False) -> dict:
        """
        Convertir en dictionnaire
        
        Args:
            include_permissions: Inclure les permissions
        
        Returns:
            Dictionnaire
        """
        data = {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'is_active': self.is_active,
            'is_system': self.is_system,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_permissions:
            data['permissions'] = [p.to_dict() for p in self.permissions]
        
        return data
