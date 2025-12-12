"""
Modèle User - Gestion des utilisateurs et authentification
"""

import enum
from datetime import datetime
from typing import Optional, Set, List, TYPE_CHECKING

import bcrypt
from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, Text
from sqlalchemy.orm import relationship

from .base import Base, BaseModel

if TYPE_CHECKING:
    from .role import Role


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
    
    # Rôle et permissions (LEGACY - conservé pour compatibilité)
    role = Column(Enum(UserRole), nullable=True, default=UserRole.RECEPTIONIST)
    
    # Nouveau système multi-rôles (many-to-many avec Role)
    # La relation est définie ici, la table user_roles est créée dans role.py
    
    # Mot de passe en clair (visible par admin UNIQUEMENT - optionnel)
    password_plain = Column(Text, nullable=True)
    
    # Status et sécurité
    is_active = Column(Boolean, default=True, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    last_login = Column(DateTime, nullable=True)
    last_password_change = Column(DateTime, nullable=True)
    
    # Notes
    notes = Column(String(500), nullable=True)
    
    def __init__(self, username: str, password: str, full_name: str, 
                 role: UserRole = None, **kwargs):
        """
        Initialiser un utilisateur
        
        Args:
            username: Nom d'utilisateur unique
            password: Mot de passe en clair (sera hashé)
            full_name: Nom complet
            role: Rôle legacy (optionnel, pour compatibilité)
        """
        self.username = username
        self.full_name = full_name
        if role:
            self.role = role
        self.set_password(password)
        
        # Appliquer les autres attributs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_password(self, password: str, store_plain: bool = True) -> None:
        """
        Hasher et définir le mot de passe
        
        Args:
            password: Mot de passe en clair
            store_plain: Stocker le mot de passe en clair (pour admin)
        """
        # Générer un salt et hasher le mot de passe
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        self.last_password_change = datetime.now()
        
        # Stocker le mot de passe en clair (visible par admin uniquement)
        if store_plain:
            self.password_plain = password
    
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
    
    def has_permission(self, permission_key: str = None, required_role: UserRole = None) -> bool:
        """
        Vérifier si l'utilisateur a les permissions requises
        
        Args:
            permission_key: Clé de permission à vérifier (nouveau système)
            required_role: Rôle minimal requis (ancien système, compatibilité)
        
        Returns:
            True si l'utilisateur a les permissions
        """
        # Nouveau système multi-rôles
        if permission_key:
            # Vérifier dans tous les rôles assignés
            if hasattr(self, 'roles') and self.roles:
                for role in self.roles:
                    if role.has_permission(permission_key):
                        return True
            # Fallback: admin legacy a toutes les permissions
            if self.role == UserRole.ADMIN:
                return True
            return False
        
        # Ancien système (hiérarchie)
        if required_role:
            role_hierarchy = {
                UserRole.ADMIN: 4,
                UserRole.CASHIER: 3,
                UserRole.INSTRUCTOR: 2,
                UserRole.RECEPTIONIST: 1
            }
            return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)
        
        return False
    
    def get_all_permissions(self) -> Set[str]:
        """
        Obtenir toutes les permissions de l'utilisateur (combinées de tous ses rôles)
        
        Returns:
            Set des clés de permissions
        """
        permissions = set()
        
        # Permissions des rôles assignés
        if hasattr(self, 'roles') and self.roles:
            for role in self.roles:
                permissions.update(role.get_permission_keys())
        
        # Si admin legacy, ajouter toutes les permissions
        if self.role == UserRole.ADMIN:
            # Import PermissionType ici pour éviter import circulaire
            try:
                from .role import PermissionType
                permissions.update([p.value for p in PermissionType])
            except ImportError:
                pass
        
        return permissions
    
    def get_role_names(self) -> List[str]:
        """
        Obtenir les noms d'affichage de tous les rôles
        
        Returns:
            Liste des noms de rôles
        """
        role_names = []
        
        # Rôles du nouveau système
        if hasattr(self, 'roles') and self.roles:
            role_names.extend([r.display_name for r in self.roles if r.is_active])
        
        # Rôle legacy
        if self.role and not role_names:
            role_names.append(self.role.value.title())
        
        return role_names
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"
    
    def to_dict(self, include_password: bool = False, include_roles: bool = True) -> dict:
        """
        Convertir en dictionnaire
        
        Args:
            include_password: Inclure le mot de passe en clair (admin seulement)
            include_roles: Inclure les rôles assignés
        
        Returns:
            Dictionnaire
        """
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role.value if self.role else None,  # Legacy
            'is_active': self.is_active,
            'is_locked': self.is_locked,
            'failed_login_attempts': self.failed_login_attempts,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_password_change': self.last_password_change.isoformat() if self.last_password_change else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        # Inclure le mot de passe en clair (admin seulement)
        if include_password:
            data['password_plain'] = self.password_plain
        
        # Inclure les rôles
        if include_roles:
            data['role_names'] = self.get_role_names()
            if hasattr(self, 'roles') and self.roles:
                data['roles'] = [r.to_dict() for r in self.roles if r.is_active]
        
        return data


# La relation many-to-many sera configurée après import de role.py dans __init__.py
# Pour éviter les imports circulaires, on ne définit pas la relation ici
# Elle sera ajoutée dynamiquement via: User.roles = relationship("Role", secondary="user_roles", back_populates="users")
