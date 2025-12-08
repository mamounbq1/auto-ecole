"""
Gestionnaire de logs pour l'application
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logger(name: str = "autoecole", 
                 log_dir: str = "logs",
                 log_level: int = logging.INFO) -> logging.Logger:
    """
    Configurer le logger de l'application
    
    Args:
        name: Nom du logger
        log_dir: Répertoire des logs
        log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configuré
    """
    # Créer le répertoire des logs
    os.makedirs(log_dir, exist_ok=True)
    
    # Nom du fichier de log avec la date du jour
    log_filename = f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    log_filepath = os.path.join(log_dir, log_filename)
    
    # Créer le logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Éviter les handlers dupliqués
    if logger.handlers:
        return logger
    
    # Format des logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour le fichier
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler pour la console (optionnel, pour debug)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Seulement warnings et errors en console
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = "autoecole") -> logging.Logger:
    """
    Obtenir un logger existant
    
    Args:
        name: Nom du logger
    
    Returns:
        Logger
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger


# Logger principal de l'application
app_logger = setup_logger()
