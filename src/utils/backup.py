"""
Gestionnaire de sauvegarde et restauration de la base de données
"""

import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from .logger import get_logger
from .config_manager import get_config_manager

logger = get_logger()


class BackupManager:
    """Gestionnaire de sauvegarde de la base de données"""
    
    def __init__(self, db_path: str = None, backup_dir: str = None):
        """
        Initialiser le gestionnaire de sauvegarde
        
        Args:
            db_path: Chemin vers la base de données (None = défaut data/autoecole.db)
            backup_dir: Répertoire des sauvegardes (None = utilise config)
        """
        config = get_config_manager()
        self.db_path = db_path or "data/autoecole.db"
        self.backup_dir = backup_dir or config.get_backup_path()
        
        # Créer le répertoire de sauvegarde s'il n'existe pas
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, backup_name: Optional[str] = None, compress: bool = True) -> tuple[bool, str]:
        """
        Créer une sauvegarde de la base de données
        
        Args:
            backup_name: Nom personnalisé pour la sauvegarde (optionnel)
            compress: Compresser en ZIP
        
        Returns:
            Tuple (success, filepath_or_error_message)
        """
        try:
            # Vérifier que la base de données existe
            if not os.path.exists(self.db_path):
                error_msg = f"Base de données introuvable : {self.db_path}"
                logger.error(error_msg)
                return False, error_msg
            
            # Générer le nom de la sauvegarde
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if backup_name:
                # Nettoyer le nom personnalisé
                backup_name = "".join(c for c in backup_name if c.isalnum() or c in (' ', '-', '_')).strip()
                base_name = f"{backup_name}_{timestamp}"
            else:
                base_name = f"autoecole_backup_{timestamp}"
            
            # Chemins de sauvegarde
            if compress:
                backup_filename = f"{base_name}.zip"
                backup_filepath = os.path.join(self.backup_dir, backup_filename)
                
                # Créer une archive ZIP
                with zipfile.ZipFile(backup_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(self.db_path, os.path.basename(self.db_path))
                
                logger.info(f"Sauvegarde compressée créée : {backup_filepath}")
            else:
                backup_filename = f"{base_name}.db"
                backup_filepath = os.path.join(self.backup_dir, backup_filename)
                
                # Copier la base de données
                shutil.copy2(self.db_path, backup_filepath)
                
                logger.info(f"Sauvegarde créée : {backup_filepath}")
            
            return True, backup_filepath
            
        except Exception as e:
            error_msg = f"Erreur lors de la création de la sauvegarde : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def restore_backup(self, backup_path: str, create_backup_before: bool = True) -> tuple[bool, str]:
        """
        Restaurer une sauvegarde
        
        Args:
            backup_path: Chemin vers le fichier de sauvegarde
            create_backup_before: Créer une sauvegarde de sécurité avant la restauration
        
        Returns:
            Tuple (success, message)
        """
        try:
            # Vérifier que le fichier de sauvegarde existe
            if not os.path.exists(backup_path):
                error_msg = f"Fichier de sauvegarde introuvable : {backup_path}"
                logger.error(error_msg)
                return False, error_msg
            
            # Créer une sauvegarde de sécurité de la base actuelle
            if create_backup_before and os.path.exists(self.db_path):
                success, result = self.create_backup(backup_name="before_restore")
                if not success:
                    logger.warning(f"Impossible de créer la sauvegarde de sécurité : {result}")
            
            # Déterminer si c'est un fichier ZIP ou DB direct
            if backup_path.endswith('.zip'):
                # Extraire du ZIP
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    # Trouver le fichier .db dans l'archive
                    db_files = [f for f in zipf.namelist() if f.endswith('.db')]
                    if not db_files:
                        error_msg = "Aucune base de données trouvée dans l'archive ZIP"
                        logger.error(error_msg)
                        return False, error_msg
                    
                    # Extraire dans un fichier temporaire
                    temp_path = f"{self.db_path}.temp"
                    with zipf.open(db_files[0]) as source, open(temp_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    
                    # Remplacer la base actuelle
                    if os.path.exists(self.db_path):
                        os.remove(self.db_path)
                    shutil.move(temp_path, self.db_path)
            else:
                # Copie directe
                if os.path.exists(self.db_path):
                    os.remove(self.db_path)
                shutil.copy2(backup_path, self.db_path)
            
            logger.info(f"Base de données restaurée depuis : {backup_path}")
            return True, "Restauration réussie"
            
        except Exception as e:
            error_msg = f"Erreur lors de la restauration : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def list_backups(self) -> List[dict]:
        """
        Lister les sauvegardes disponibles
        
        Returns:
            Liste de dictionnaires avec les informations des sauvegardes
        """
        backups = []
        
        try:
            if not os.path.exists(self.backup_dir):
                return backups
            
            for filename in os.listdir(self.backup_dir):
                if filename.endswith(('.db', '.zip')):
                    filepath = os.path.join(self.backup_dir, filename)
                    file_stat = os.stat(filepath)
                    
                    backups.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': file_stat.st_size,
                        'size_mb': round(file_stat.st_size / (1024 * 1024), 2),
                        'created': datetime.fromtimestamp(file_stat.st_ctime),
                        'modified': datetime.fromtimestamp(file_stat.st_mtime),
                    })
            
            # Trier par date de modification (plus récent en premier)
            backups.sort(key=lambda x: x['modified'], reverse=True)
            
        except Exception as e:
            logger.error(f"Erreur lors du listage des sauvegardes : {e}")
        
        return backups
    
    def delete_backup(self, backup_path: str) -> tuple[bool, str]:
        """
        Supprimer une sauvegarde
        
        Args:
            backup_path: Chemin vers le fichier de sauvegarde
        
        Returns:
            Tuple (success, message)
        """
        try:
            if not os.path.exists(backup_path):
                return False, "Fichier introuvable"
            
            os.remove(backup_path)
            logger.info(f"Sauvegarde supprimée : {backup_path}")
            return True, "Sauvegarde supprimée"
            
        except Exception as e:
            error_msg = f"Erreur lors de la suppression : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Nettoyer les anciennes sauvegardes
        
        Args:
            keep_count: Nombre de sauvegardes à conserver
        
        Returns:
            Nombre de sauvegardes supprimées
        """
        backups = self.list_backups()
        deleted_count = 0
        
        # Garder seulement les N plus récentes
        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                success, _ = self.delete_backup(backup['filepath'])
                if success:
                    deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"{deleted_count} anciennes sauvegardes supprimées")
        
        return deleted_count


# Fonctions globales
_default_backup_manager = None


def get_backup_manager() -> BackupManager:
    """Obtenir l'instance du gestionnaire de sauvegarde"""
    global _default_backup_manager
    if _default_backup_manager is None:
        _default_backup_manager = BackupManager()
    return _default_backup_manager


def create_backup(backup_name: Optional[str] = None, compress: bool = True) -> tuple[bool, str]:
    """Créer une sauvegarde"""
    return get_backup_manager().create_backup(backup_name, compress)


def restore_backup(backup_path: str, create_backup_before: bool = True) -> tuple[bool, str]:
    """Restaurer une sauvegarde"""
    return get_backup_manager().restore_backup(backup_path, create_backup_before)


def list_backups() -> List[dict]:
    """Lister les sauvegardes"""
    return get_backup_manager().list_backups()
