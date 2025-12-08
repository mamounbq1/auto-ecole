"""
Modèle User - Gestion des utilisateurs et authentification
"""

import enum
from datetime import datetime
from typing import Optional

import bcrypt
from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship

from .base import Base, BaseModel


class UserRole(enum.Enum):
    """Rôles utilisateurs avec permissions"""
    ADMIN = "admin"  # Accès complet
    CASHIER = "cashier"  # Caissier - paiements, reçus
    INSTRUCTOR = "instructor"  # Moniteur - planning, présences
    RECEPTIONIST = "receptionist"  # Réceptionniste - inscriptions, RDV


class User(Base, BaseModel):
    """Modèle utilisateur pour l'authentification et RBAC"""
    
    __tablename__ = "users"
    
    # Informations de base
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    
    # Informations personnelles
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Rôle et permissions
    role = Column(Enum(UserRole), nullable=False, default=UserRole.RECEPTIONIST)
    
    # Status et sécurité
    is_active = Column(Boolean, default=True, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    last_login = Column(DateTime, nullable=True)
    last_password_change = Column(DateTime, nullable=True)
    
    # Notes
    notes = Column(String(500), nullable=True)
    
    def __init__(self, username: str, password: str, full_name: str, 
                 role: UserRole = UserRole.RECEPTIONIST, **kwargs):
        """
        Initialiser un utilisateur
        
        Args:
            username: Nom d'utilisateur unique
            password: Mot de passe en clair (sera hashé)
            full_name: Nom complet
            role: Rôle de l'utilisateur
        """
        self.username = username
        self.full_name = full_name
        self.role = role
        self.set_password(password)
        
        # Appliquer les autres attributs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_password(self, password: str) -> None:
        """
        Hasher et définir le mot de passe
        
        Args:
            password: Mot de passe en clair
        """
        # Générer un salt et hasher le mot de passe
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        self.last_password_change = datetime.now()
    
    def check_password(self, password: str) -> bool:
        """
        Vérifier le mot de passe
        
        Args:
            password: Mot de passe en clair à vérifier
        
        Returns:
            True si le mot de passe est correct
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    def record_login_attempt(self, success: bool, max_attempts: int = 5) -> None:
        """
        Enregistrer une tentative de connexion
        
        Args:
            success: True si la connexion a réussi
            max_attempts: Nombre maximum de tentatives avant verrouillage
        """
        if success:
            self.failed_login_attempts = 0
            self.last_login = datetime.now()
            self.is_locked = False
        else:
            self.failed_login_attempts += 1
            if self.failed_login_attempts >= max_attempts:
                self.is_locked = True
    
    def unlock(self) -> None:
        """Déverrouiller le compte utilisateur"""
        self.is_locked = False
        self.failed_login_attempts = 0
    
    def has_permission(self, required_role: UserRole) -> bool:
        """
        Vérifier si l'utilisateur a les permissions requises
        
        Args:
            required_role: Rôle minimal requis
        
        Returns:
            True si l'utilisateur a les permissions
        """
        # Hiérarchie des rôles
        role_hierarchy = {
            UserRole.ADMIN: 4,
            UserRole.CASHIER: 3,
            UserRole.INSTRUCTOR: 2,
            UserRole.RECEPTIONIST: 1
        }
        
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"
    
    def to_dict(self) -> dict:
        """Convertir en dictionnaire (sans le mot de passe)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role.value,
            'is_active': self.is_active,
            'is_locked': self.is_locked,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
