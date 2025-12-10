"""
Contrôleur pour la gestion des documents des élèves
Utilisé uniquement dans le module Élèves
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import date

from src.models import Document, DocumentType, DocumentStatus, get_session
from src.utils import get_logger

logger = get_logger()


class DocumentController:
    """Contrôleur pour gérer les documents des élèves"""
    
    UPLOAD_DIR = Path("uploads/documents")
    
    @staticmethod
    def _ensure_upload_dir():
        """S'assurer que le dossier d'upload existe"""
        DocumentController.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def create_document(student_id: int, title: str, document_type: DocumentType,
                       file_path: Optional[str] = None, **kwargs) -> Optional[Document]:
        """
        Créer un nouveau document
        
        Args:
            student_id: ID de l'élève
            title: Titre du document
            document_type: Type de document
            file_path: Chemin du fichier (optionnel)
            **kwargs: Attributs supplémentaires
            
        Returns:
            Document créé ou None en cas d'erreur
        """
        session = get_session()
        try:
            document = Document(
                student_id=student_id,
                title=title,
                document_type=document_type,
                **kwargs
            )
            
            # Gérer le fichier si fourni
            if file_path and os.path.exists(file_path):
                DocumentController._ensure_upload_dir()
                
                # Copier le fichier
                file_name = os.path.basename(file_path)
                dest_path = DocumentController.UPLOAD_DIR / f"{student_id}_{file_name}"
                shutil.copy(file_path, dest_path)
                
                document.file_path = str(dest_path)
                document.file_name = file_name
                document.file_size = os.path.getsize(dest_path)
            
            session.add(document)
            session.commit()
            session.refresh(document)
            
            logger.info(f"Document créé: {document.title} pour élève {student_id}")
            return document
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erreur création document: {e}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def get_document(document_id: int) -> Optional[Document]:
        """Récupérer un document par son ID"""
        session = get_session()
        try:
            return session.query(Document).filter_by(id=document_id).first()
        finally:
            session.close()
    
    @staticmethod
    def get_documents_by_student(student_id: int) -> List[Document]:
        """Récupérer tous les documents d'un élève"""
        session = get_session()
        try:
            return session.query(Document).filter_by(student_id=student_id).order_by(Document.upload_date.desc()).all()
        finally:
            session.close()
    
    @staticmethod
    def get_documents_by_type(student_id: int, document_type: DocumentType) -> List[Document]:
        """Récupérer les documents d'un élève par type"""
        session = get_session()
        try:
            return session.query(Document).filter_by(
                student_id=student_id,
                document_type=document_type
            ).order_by(Document.upload_date.desc()).all()
        finally:
            session.close()
    
    @staticmethod
    def update_document(document_id: int, **kwargs) -> Optional[Document]:
        """Mettre à jour un document"""
        session = get_session()
        try:
            document = session.query(Document).filter_by(id=document_id).first()
            if document:
                for key, value in kwargs.items():
                    if hasattr(document, key):
                        setattr(document, key, value)
                
                session.commit()
                session.refresh(document)
                logger.info(f"Document mis à jour: {document_id}")
                return document
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"Erreur mise à jour document: {e}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def delete_document(document_id: int) -> bool:
        """Supprimer un document"""
        session = get_session()
        try:
            document = session.query(Document).filter_by(id=document_id).first()
            if document:
                # Supprimer le fichier physique
                if document.file_path and os.path.exists(document.file_path):
                    try:
                        os.remove(document.file_path)
                    except Exception as e:
                        logger.warning(f"Impossible de supprimer le fichier: {e}")
                
                session.delete(document)
                session.commit()
                logger.info(f"Document supprimé: {document_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Erreur suppression document: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def get_expired_documents(student_id: Optional[int] = None) -> List[Document]:
        """Récupérer les documents expirés"""
        session = get_session()
        try:
            query = session.query(Document).filter(
                Document.expiry_date < date.today()
            )
            
            if student_id:
                query = query.filter_by(student_id=student_id)
            
            return query.all()
        finally:
            session.close()
    
    @staticmethod
    def get_expiring_soon_documents(days: int = 30, student_id: Optional[int] = None) -> List[Document]:
        """Récupérer les documents qui expirent bientôt"""
        from datetime import timedelta
        session = get_session()
        try:
            expiry_limit = date.today() + timedelta(days=days)
            
            query = session.query(Document).filter(
                Document.expiry_date.isnot(None),
                Document.expiry_date >= date.today(),
                Document.expiry_date <= expiry_limit
            )
            
            if student_id:
                query = query.filter_by(student_id=student_id)
            
            return query.all()
        finally:
            session.close()
    
    @staticmethod
    def verify_document(document_id: int, verified_by: str) -> Optional[Document]:
        """Marquer un document comme vérifié"""
        session = get_session()
        try:
            document = session.query(Document).filter_by(id=document_id).first()
            if document:
                document.mark_verified(verified_by)
                session.commit()
                session.refresh(document)
                logger.info(f"Document vérifié: {document_id} par {verified_by}")
                return document
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"Erreur vérification document: {e}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def get_statistics(student_id: Optional[int] = None) -> dict:
        """Obtenir des statistiques sur les documents"""
        session = get_session()
        try:
            query = session.query(Document)
            if student_id:
                query = query.filter_by(student_id=student_id)
            
            documents = query.all()
            
            return {
                'total': len(documents),
                'verified': len([d for d in documents if d.is_verified]),
                'expired': len([d for d in documents if d.is_expired]),
                'pending': len([d for d in documents if d.status == DocumentStatus.PENDING]),
                'valid': len([d for d in documents if d.status == DocumentStatus.VALID]),
            }
        finally:
            session.close()
