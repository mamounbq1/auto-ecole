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
    
    def has_role(self, role: UserRole) -> bool:
        """
        Vérifier si l'utilisateur a un rôle spécifique
        
        Args:
            role: Rôle à vérifier
        
        Returns:
            True si l'utilisateur a ce rôle ou un rôle supérieur
        """
        if not self.is_authenticated():
            return False
        
        return self._current_user.has_permission(role)
    
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


def logout() -> None:
    """Déconnexion globale"""
    _auth_manager.logout()


def get_current_user() -> Optional[User]:
    """Obtenir l'utilisateur connecté"""
    return _auth_manager.get_current_user()


def is_authenticated() -> bool:
    """Vérifier l'authentification"""
    return _auth_manager.is_authenticated()


def has_role(role: UserRole) -> bool:
    """Vérifier le rôle"""
    return _auth_manager.has_role(role)


def require_auth(func: Callable) -> Callable:
    """Décorateur d'authentification"""
    return _auth_manager.require_auth(func)


def require_role(role: UserRole) -> Callable:
    """Décorateur de rôle"""
    return _auth_manager.require_role(role)
