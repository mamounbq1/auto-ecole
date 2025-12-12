"""
Contrôleur pour la gestion des utilisateurs/staff
"""

from typing import List, Optional, Dict, Tuple
from datetime import datetime

from src.models import (
    get_session, User, UserRole,
    Role, Permission
)
from ..utils.logger import get_logger

logger = get_logger()


class UserController:
    """Contrôleur pour les opérations CRUD sur les utilisateurs"""
    
    @staticmethod
    def get_all_users(include_inactive: bool = False) -> List[User]:
        """
        Récupérer tous les utilisateurs
        
        Args:
            include_inactive: Inclure les utilisateurs inactifs
        
        Returns:
            Liste des utilisateurs
        """
        try:
            from sqlalchemy.orm import joinedload
            session = get_session()
            query = session.query(User).options(joinedload(User.roles))
            
            if not include_inactive:
                query = query.filter(User.is_active == True)
            
            users = query.order_by(User.full_name).all()
            
            # Force load deferred columns before closing session
            for user in users:
                try:
                    _ = user.password_plain  # Force load deferred column
                    _ = user.roles  # Force load relationship
                except Exception:
                    pass
            
            session.expunge_all()  # Detach all objects so they can be used after session close
            session.close()
            return users
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des utilisateurs : {e}")
            return []
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Récupérer un utilisateur par son ID
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Utilisateur ou None
        """
        try:
            from sqlalchemy.orm import joinedload
            session = get_session()
            user = session.query(User).options(joinedload(User.roles)).filter(User.id == user_id).first()
            
            if user:
                # Force load deferred columns before closing session
                try:
                    _ = user.password_plain
                    _ = user.roles
                except Exception:
                    pass
                session.expunge(user)  # Detach object so it can be used after session close
            
            session.close()
            return user
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur {user_id} : {e}")
            return None
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """
        Récupérer un utilisateur par son nom d'utilisateur
        
        Args:
            username: Nom d'utilisateur
        
        Returns:
            Utilisateur ou None
        """
        try:
            session = get_session()
            user = session.query(User).filter(User.username == username).first()
            session.close()
            return user
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur '{username}' : {e}")
            return None
    
    @staticmethod
    def create_user(username: str, password: str, full_name: str,
                   email: Optional[str] = None, phone: Optional[str] = None,
                   role_ids: Optional[List[int]] = None,
                   notes: Optional[str] = None) -> Tuple[bool, str, Optional[User]]:
        """
        Créer un nouvel utilisateur
        
        Args:
            username: Nom d'utilisateur unique
            password: Mot de passe
            full_name: Nom complet
            email: Email (optionnel)
            phone: Téléphone (optionnel)
            role_ids: Liste des IDs de rôles
            notes: Notes (optionnel)
        
        Returns:
            Tuple (success, message, user)
        """
        try:
            session = get_session()
            
            # Vérifier si le nom d'utilisateur existe déjà
            existing_user = session.query(User).filter(User.username == username).first()
            if existing_user:
                session.close()
                return False, f"Le nom d'utilisateur '{username}' existe déjà", None
            
            # Vérifier si l'email existe déjà (si fourni)
            if email:
                existing_email = session.query(User).filter(User.email == email).first()
                if existing_email:
                    session.close()
                    return False, f"L'email '{email}' est déjà utilisé", None
            
            # Créer l'utilisateur
            user = User(
                username=username,
                password=password,
                full_name=full_name,
                email=email,
                phone=phone,
                notes=notes,
                is_active=True,
                is_locked=False
            )
            
            # Assigner les rôles
            if role_ids:
                roles = session.query(Role).filter(Role.id.in_(role_ids)).all()
                user.roles = roles
            
            session.add(user)
            session.commit()
            
            user_id = user.id
            session.close()
            
            logger.info(f"✓ Utilisateur créé : {username} (ID: {user_id})")
            return True, f"Utilisateur '{username}' créé avec succès", user
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'utilisateur : {e}")
            return False, f"Erreur : {str(e)}", None
    
    @staticmethod
    def update_user(user_id: int, 
                   username: Optional[str] = None,
                   full_name: Optional[str] = None,
                   email: Optional[str] = None,
                   phone: Optional[str] = None,
                   role_ids: Optional[List[int]] = None,
                   is_active: Optional[bool] = None,
                   notes: Optional[str] = None) -> Tuple[bool, str]:
        """
        Mettre à jour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            username: Nouveau nom d'utilisateur
            full_name: Nouveau nom complet
            email: Nouvel email
            phone: Nouveau téléphone
            role_ids: Nouveaux IDs de rôles
            is_active: Nouveau statut actif
            notes: Nouvelles notes
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                session.close()
                return False, f"Utilisateur ID {user_id} introuvable"
            
            # Vérifier l'unicité du username
            if username and username != user.username:
                existing_user = session.query(User).filter(User.username == username).first()
                if existing_user:
                    session.close()
                    return False, f"Le nom d'utilisateur '{username}' existe déjà"
                user.username = username
            
            # Vérifier l'unicité de l'email
            if email and email != user.email:
                existing_email = session.query(User).filter(User.email == email).first()
                if existing_email:
                    session.close()
                    return False, f"L'email '{email}' est déjà utilisé"
                user.email = email
            
            # Mettre à jour les autres champs
            if full_name is not None:
                user.full_name = full_name
            if phone is not None:
                user.phone = phone
            if is_active is not None:
                user.is_active = is_active
            if notes is not None:
                user.notes = notes
            
            # Mettre à jour les rôles
            if role_ids is not None:
                roles = session.query(Role).filter(Role.id.in_(role_ids)).all()
                user.roles = roles
            
            session.commit()
            session.close()
            
            logger.info(f"✓ Utilisateur mis à jour : {user.username} (ID: {user_id})")
            return True, f"Utilisateur mis à jour avec succès"
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'utilisateur : {e}")
            return False, f"Erreur : {str(e)}"
    
    @staticmethod
    def change_password(user_id: int, new_password: str, 
                       changed_by_admin: bool = False) -> Tuple[bool, str]:
        """
        Changer le mot de passe d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            new_password: Nouveau mot de passe
            changed_by_admin: Changé par un administrateur
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                session.close()
                return False, f"Utilisateur ID {user_id} introuvable"
            
            # Changer le mot de passe (stocke en clair si changé par admin)
            user.set_password(new_password, store_plain=changed_by_admin)
            
            session.commit()
            session.close()
            
            logger.info(f"✓ Mot de passe changé pour : {user.username} (par admin: {changed_by_admin})")
            return True, "Mot de passe changé avec succès"
            
        except Exception as e:
            logger.error(f"Erreur lors du changement de mot de passe : {e}")
            return False, f"Erreur : {str(e)}"
    
    @staticmethod
    def delete_user(user_id: int) -> Tuple[bool, str]:
        """
        Supprimer un utilisateur (soft delete - désactiver)
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                session.close()
                return False, f"Utilisateur ID {user_id} introuvable"
            
            # Désactiver l'utilisateur au lieu de le supprimer
            user.is_active = False
            
            session.commit()
            session.close()
            
            logger.info(f"✓ Utilisateur désactivé : {user.username} (ID: {user_id})")
            return True, f"Utilisateur '{user.username}' désactivé avec succès"
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'utilisateur : {e}")
            return False, f"Erreur : {str(e)}"
    
    @staticmethod
    def unlock_user(user_id: int) -> Tuple[bool, str]:
        """
        Déverrouiller un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                session.close()
                return False, f"Utilisateur ID {user_id} introuvable"
            
            user.unlock()
            
            session.commit()
            session.close()
            
            logger.info(f"✓ Utilisateur déverrouillé : {user.username}")
            return True, f"Utilisateur '{user.username}' déverrouillé avec succès"
            
        except Exception as e:
            logger.error(f"Erreur lors du déverrouillage de l'utilisateur : {e}")
            return False, f"Erreur : {str(e)}"
    
    @staticmethod
    def get_all_roles() -> List[Role]:
        """
        Récupérer tous les rôles disponibles
        
        Returns:
            Liste des rôles
        """
        try:
            session = get_session()
            roles = session.query(Role).filter(Role.is_active == True).order_by(Role.display_name).all()
            session.close()
            return roles
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des rôles : {e}")
            return []
    
    @staticmethod
    def get_user_statistics() -> Dict[str, int]:
        """
        Obtenir des statistiques sur les utilisateurs
        
        Returns:
            Dictionnaire de statistiques
        """
        try:
            session = get_session()
            
            total = session.query(User).count()
            active = session.query(User).filter(User.is_active == True).count()
            locked = session.query(User).filter(User.is_locked == True).count()
            
            session.close()
            
            return {
                'total': total,
                'active': active,
                'inactive': total - active,
                'locked': locked
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques : {e}")
            return {'total': 0, 'active': 0, 'inactive': 0, 'locked': 0}
