"""
Gestionnaire d'authentification et d'autorisation
"""

from typing import Optional, Callable
from functools import wraps
from datetime import datetime

from src.models import User, UserRole, get_session
from .logger import get_logger

logger = get_logger()


class AuthManager:
    """Gestionnaire d'authentification singleton"""
    
    _instance = None
    _current_user: Optional[User] = None
    _session = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthManager, cls).__new__(cls)
        return cls._instance
    
    def login(self, username: str, password: str, max_attempts: int = 5) -> tuple[bool, str, Optional[User]]:
        """
        Authentifier un utilisateur
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe
            max_attempts: Nombre maximum de tentatives
        
        Returns:
            Tuple (success, message, user)
        """
        try:
            session = get_session()
            
            # Rechercher l'utilisateur
            user = session.query(User).filter(User.username == username).first()
            
            if not user:
                logger.warning(f"Tentative de connexion échouée : utilisateur '{username}' inexistant")
                return False, "Nom d'utilisateur ou mot de passe incorrect", None
            
            # Vérifier si le compte est verrouillé
            if user.is_locked:
                logger.warning(f"Tentative de connexion sur compte verrouillé : {username}")
                return False, "Compte verrouillé. Contactez l'administrateur.", None
            
            # Vérifier si le compte est actif
            if not user.is_active:
                logger.warning(f"Tentative de connexion sur compte inactif : {username}")
                return False, "Compte désactivé. Contactez l'administrateur.", None
            
            # Vérifier le mot de passe
            if not user.check_password(password):
                user.record_login_attempt(success=False, max_attempts=max_attempts)
                session.commit()
                
                remaining = max_attempts - user.failed_login_attempts
                if user.is_locked:
                    logger.warning(f"Compte verrouillé après trop de tentatives : {username}")
                    return False, "Compte verrouillé après trop de tentatives.", None
                else:
                    logger.warning(f"Mot de passe incorrect pour : {username} ({remaining} tentatives restantes)")
                    return False, f"Mot de passe incorrect ({remaining} tentatives restantes)", None
            
            # Authentification réussie
            user.record_login_attempt(success=True)
            session.commit()
            
            self._current_user = user
            self._session = session
            
            logger.info(f"Connexion réussie : {username} (rôle: {user.role.value})")
            return True, "Connexion réussie", user
            
        except Exception as e:
            logger.error(f"Erreur lors de la connexion : {e}")
            return False, f"Erreur lors de la connexion : {str(e)}", None
    
    def bypass_login(self, preferred_roles: Optional[list[UserRole]] = None) -> tuple[bool, str, Optional[User]]:
        """Forcer une connexion sans vérifier le mot de passe (mode temporaire)."""
        try:
            session = get_session()
            search_roles = preferred_roles or [
                UserRole.ADMIN,
                UserRole.CASHIER,
                UserRole.INSTRUCTOR,
                UserRole.RECEPTIONIST,
            ]

            user: Optional[User] = None

            for role in search_roles:
                user = (
                    session.query(User)
                    .filter(
                        User.role == role,
                        User.is_active.is_(True),
                        User.is_locked.is_(False),
                    )
                    .order_by(User.id.asc())
                    .first()
                )
                if user:
                    break

            if not user:
                user = (
                    session.query(User)
                    .filter(
                        User.is_active.is_(True),
                        User.is_locked.is_(False),
                    )
                    .order_by(User.id.asc())
                    .first()
                )

            if not user:
                logger.error("Bypass login impossible : aucun utilisateur actif disponible")
                session.close()
                return False, "Aucun utilisateur actif disponible pour la connexion automatique.", None

            user.record_login_attempt(success=True)
            session.commit()

            if self._session:
                self._session.close()

            self._current_user = user
            self._session = session

            logger.warning(
                "Mode bypass activé : connexion automatique pour l'utilisateur '%s' (rôle: %s)",
                user.username,
                user.role.value,
            )
            return True, "Connexion bypass réussie", user

        except Exception as e:
            logger.error(f"Erreur lors du bypass de connexion : {e}")
            return False, f"Erreur lors du bypass de connexion : {str(e)}", None

    def logout(self) -> None:
        """Déconnecter l'utilisateur actuel"""
        if self._current_user:
            logger.info(f"Déconnexion : {self._current_user.username}")
        
        self._current_user = None
        if self._session:
            self._session.close()
            self._session = None
    
    def get_current_user(self) -> Optional[User]:
        """
        Obtenir l'utilisateur actuellement connecté
        
        Returns:
            Utilisateur ou None
        """
        return self._current_user
    
    def is_authenticated(self) -> bool:
        """
        Vérifier si un utilisateur est authentifié
        
        Returns:
            True si authentifié
        """
        return self._current_user is not None
    
    def has_role(self, role: UserRole = None, role_name: str = None) -> bool:
        """
        Vérifier si l'utilisateur a un rôle spécifique
        
        Args:
            role: Rôle legacy à vérifier
            role_name: Nom du nouveau rôle à vérifier
        
        Returns:
            True si l'utilisateur a ce rôle
        """
        if not self.is_authenticated():
            return False
        
        # Nouveau système : vérifier par nom de rôle
        if role_name:
            if hasattr(self._current_user, 'roles') and self._current_user.roles:
                return any(r.name == role_name and r.is_active for r in self._current_user.roles)
            return False
        
        # Ancien système : vérifier via hiérarchie
        if role:
            return self._current_user.has_permission(required_role=role)
        
        return False
    
    def has_permission(self, permission_key: str) -> bool:
        """
        Vérifier si l'utilisateur a une permission spécifique
        
        Args:
            permission_key: Clé de la permission à vérifier
        
        Returns:
            True si l'utilisateur a cette permission
        """
        if not self.is_authenticated():
            return False
        
        return self._current_user.has_permission(permission_key=permission_key)
    
    def require_auth(self, func: Callable) -> Callable:
        """
        Décorateur pour exiger l'authentification
        
        Args:
            func: Fonction à décorer
        
        Returns:
            Fonction décorée
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.is_authenticated():
                raise PermissionError("Authentification requise")
            return func(*args, **kwargs)
        return wrapper
    
    def require_role(self, role: UserRole) -> Callable:
        """
        Décorateur pour exiger un rôle spécifique
        
        Args:
            role: Rôle minimal requis
        
        Returns:
            Décorateur de fonction
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.is_authenticated():
                    raise PermissionError("Authentification requise")
                if not self.has_role(role):
                    raise PermissionError(f"Rôle {role.value} requis")
                return func(*args, **kwargs)
            return wrapper
        return decorator


# Instance globale du gestionnaire d'authentification
_auth_manager = AuthManager()


# Fonctions globales pour faciliter l'utilisation
def login(username: str, password: str, max_attempts: int = 5) -> tuple[bool, str, Optional[User]]:
    """Connexion globale"""
    return _auth_manager.login(username, password, max_attempts)


def bypass_login(preferred_roles: Optional[list[UserRole]] = None) -> tuple[bool, str, Optional[User]]:
    """Connexion forcée sans mot de passe (usage temporaire)."""
    return _auth_manager.bypass_login(preferred_roles)


def logout() -> None:
    """Déconnexion globale"""
    _auth_manager.logout()


def get_current_user() -> Optional[User]:
    """Obtenir l'utilisateur connecté"""
    return _auth_manager.get_current_user()


def is_authenticated() -> bool:
    """Vérifier l'authentification"""
    return _auth_manager.is_authenticated()


def has_role(role: UserRole = None, role_name: str = None) -> bool:
    """Vérifier le rôle"""
    return _auth_manager.has_role(role, role_name)


def has_permission(permission_key: str) -> bool:
    """Vérifier une permission"""
    return _auth_manager.has_permission(permission_key)


def require_auth(func: Callable) -> Callable:
    """Décorateur d'authentification"""
    return _auth_manager.require_auth(func)


def require_role(role: UserRole) -> Callable:
    """Décorateur de rôle"""
    return _auth_manager.require_role(role)
