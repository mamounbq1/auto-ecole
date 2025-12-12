"""
Configuration de base pour SQLAlchemy
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool

# Base pour tous les modèles
Base = declarative_base()


class BaseModel:
    """Classe de base pour tous les modèles avec champs communs"""
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)


# Configuration de la base de données
_engine = None
_SessionLocal = None


def get_engine(database_path: Optional[str] = None, echo: bool = False):
    """
    Obtenir ou créer l'engine SQLAlchemy
    
    Args:
        database_path: Chemin vers la base de données SQLite (None = utiliser config)
        echo: Afficher les requêtes SQL (debug)
    
    Returns:
        Engine SQLAlchemy
    """
    global _engine
    
    if _engine is None:
        import os
        from pathlib import Path
        
        # Si aucun chemin fourni, utiliser la configuration par défaut
        if database_path is None:
            try:
                from src.config import DATABASE_PATH
                database_path = str(DATABASE_PATH)
            except ImportError:
                # Fallback si config.py n'existe pas
                current_file = Path(__file__).resolve()
                project_root = current_file.parent.parent.parent
                database_path = str(project_root / "data" / "autoecole.db")
        
        # Convertir en chemin absolu si c'est un chemin relatif
        if not os.path.isabs(database_path):
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent
            database_path = str(project_root / database_path)
        
        # Créer l'engine avec support multi-threading pour SQLite
        _engine = create_engine(
            f"sqlite:///{database_path}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=echo
        )
    
    return _engine


def get_session_factory(engine=None):
    """
    Obtenir la factory de session
    
    Args:
        engine: Engine SQLAlchemy (optionnel)
    
    Returns:
        Session factory
    """
    global _SessionLocal
    
    if _SessionLocal is None:
        if engine is None:
            engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return _SessionLocal


def get_session() -> Session:
    """
    Obtenir une session de base de données
    
    Returns:
        Session SQLAlchemy
    """
    SessionLocal = get_session_factory()
    return SessionLocal()


def init_db(database_path: Optional[str] = None, drop_all: bool = False):
    """
    Initialiser la base de données
    
    Args:
        database_path: Chemin vers la base de données (None = utiliser config)
        drop_all: Supprimer toutes les tables existantes
    """
    import os
    from pathlib import Path
    
    # Si aucun chemin fourni, utiliser la configuration par défaut
    if database_path is None:
        try:
            from src.config import DATABASE_PATH
            database_path = str(DATABASE_PATH)
        except ImportError:
            # Fallback
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent
            database_path = str(project_root / "data" / "autoecole.db")
    
    # Convertir en chemin absolu si c'est un chemin relatif
    if not os.path.isabs(database_path):
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent
        database_path = str(project_root / database_path)
    
    # Créer le dossier data s'il n'existe pas
    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    
    engine = get_engine(database_path)
    
    if drop_all:
        Base.metadata.drop_all(engine)
    
    # Créer toutes les tables
    Base.metadata.create_all(engine)
    
    print(f"✓ Base de données initialisée : {database_path}")


def close_db():
    """Fermer la connexion à la base de données"""
    global _engine, _SessionLocal
    
    if _engine:
        _engine.dispose()
        _engine = None
    
    _SessionLocal = None
