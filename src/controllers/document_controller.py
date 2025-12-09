"""
Contrôleur pour la gestion des documents
Phase 3 - Gestion Documentaire
"""

from typing import List, Optional, Dict, Any, BinaryIO
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_
import os
import shutil
import csv
from pathlib import Path

from src.models import Document, DocumentType, DocumentStatus, get_session
from src.utils import get_logger
from src.utils.pdf_generator import PDFGenerator
from src.utils.config_manager import ConfigManager

logger = get_logger()


class DocumentController:
    """Contrôleur pour gérer les documents"""
    
    # Répertoire de stockage des documents
    STORAGE_DIR = "storage/documents"
    
    # Tailles maximales (en bytes)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
    
    # Extensions autorisées
    ALLOWED_EXTENSIONS = {
        'pdf': ['application/pdf'],
        'jpg': ['image/jpeg', 'image/jpg'],
        'jpeg': ['image/jpeg', 'image/jpg'],
        'png': ['image/png'],
        'doc': ['application/msword'],
        'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        'xls': ['application/vnd.ms-excel'],
        'xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
    }
    
    @staticmethod
    def _ensure_storage_dir():
        """Créer le répertoire de stockage s'il n'existe pas"""
        Path(DocumentController.STORAGE_DIR).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def _get_entity_storage_path(entity_type: str, entity_id: int, document_type: DocumentType) -> str:
        """Obtenir le chemin de stockage pour une entité"""
        return os.path.join(
            DocumentController.STORAGE_DIR,
            entity_type,
            str(entity_id),
            document_type.value
        )
    
    @staticmethod
    def _validate_file(file_path: str, max_size: int = None) -> tuple[bool, str]:
        """Valider un fichier (existence, taille, extension)"""
        if not os.path.exists(file_path):
            return False, "Fichier introuvable"
        
        # Vérifier la taille
        file_size = os.path.getsize(file_path)
        max_allowed = max_size or DocumentController.MAX_FILE_SIZE
        
        if file_size > max_allowed:
            return False, f"Fichier trop volumineux (max {max_allowed / (1024*1024):.1f} MB)"
        
        # Vérifier l'extension
        ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        if ext not in DocumentController.ALLOWED_EXTENSIONS:
            return False, f"Extension '{ext}' non autorisée"
        
        return True, "OK"
    
    # ========== CRUD Operations ==========
    
    @staticmethod
    def upload_document(
        file_path: str,
        document_type: DocumentType,
        title: str,
        entity_type: str = None,
        entity_id: int = None,
        description: str = None,
        reference_number: str = None,
        issue_date: datetime = None,
        expiry_date: datetime = None,
        tags: str = None,
        created_by: str = None
    ) -> Optional[Document]:
        """
        Uploader un document
        
        Args:
            file_path: Chemin du fichier source
            document_type: Type de document
            title: Titre du document
            entity_type: Type d'entité (student, instructor, vehicle, etc.)
            entity_id: ID de l'entité
            ... autres métadonnées
            
        Returns:
            Document créé ou None si erreur
        """
        try:
            # Convertir document_type en enum si c'est une string
            if isinstance(document_type, str):
                try:
                    document_type = DocumentType(document_type)
                except ValueError:
                    logger.error(f"Type de document invalide : {document_type}")
                    return None
            
            # Valider le fichier
            is_valid, message = DocumentController._validate_file(file_path)
            if not is_valid:
                logger.error(f"Validation fichier échouée : {message}")
                return None
            
            # Créer le répertoire de destination
            DocumentController._ensure_storage_dir()
            
            if entity_type and entity_id:
                dest_dir = DocumentController._get_entity_storage_path(entity_type, entity_id, document_type)
            else:
                dest_dir = os.path.join(DocumentController.STORAGE_DIR, "general", document_type.value)
            
            Path(dest_dir).mkdir(parents=True, exist_ok=True)
            
            # Générer un nom de fichier unique
            file_name = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_name = f"{timestamp}_{file_name}"
            dest_path = os.path.join(dest_dir, unique_name)
            
            # Copier le fichier
            shutil.copy2(file_path, dest_path)
            
            # Obtenir les métadonnées du fichier
            file_size = os.path.getsize(dest_path)
            
            # Déterminer le MIME type
            ext = os.path.splitext(file_name)[1].lower().lstrip('.')
            mime_type = DocumentController.ALLOWED_EXTENSIONS.get(ext, ['application/octet-stream'])[0]
            
            # Créer l'entrée en base de données
            session = get_session()
            
            document = Document(
                document_type=document_type,
                status=DocumentStatus.ACTIVE,
                entity_type=entity_type,
                entity_id=entity_id,
                title=title,
                description=description,
                file_path=dest_path,
                file_name=file_name,
                file_size=file_size,
                mime_type=mime_type,
                reference_number=reference_number,
                issue_date=issue_date,
                expiry_date=expiry_date,
                tags=tags,
                created_by=created_by
            )
            
            session.add(document)
            session.commit()
            session.refresh(document)
            
            logger.info(f"Document uploadé : ID {document.id}, type {document_type.value}")
            return document
            
        except Exception as e:
            logger.error(f"Erreur lors de l'upload du document : {e}")
            if 'session' in locals():
                session.rollback()
            return None
    
    @staticmethod
    def get_document_by_id(document_id: int) -> Optional[Document]:
        """Obtenir un document par ID"""
        try:
            session = get_session()
            return session.query(Document).filter(Document.id == document_id).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du document {document_id} : {e}")
            return None
    
    @staticmethod
    def get_documents_by_entity(entity_type: str, entity_id: int) -> List[Document]:
        """Obtenir tous les documents d'une entité"""
        try:
            session = get_session()
            return session.query(Document).filter(
                and_(
                    Document.entity_type == entity_type,
                    Document.entity_id == entity_id
                )
            ).order_by(Document.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des documents : {e}")
            return []
    
    @staticmethod
    def get_documents_by_type(
        document_type: DocumentType,
        entity_type: str = None
    ) -> List[Document]:
        """Obtenir tous les documents d'un type"""
        try:
            session = get_session()
            query = session.query(Document).filter(Document.document_type == document_type)
            
            if entity_type:
                query = query.filter(Document.entity_type == entity_type)
            
            return query.order_by(Document.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des documents : {e}")
            return []
    
    @staticmethod
    def search_documents(
        title: str = None,
        document_type: DocumentType = None,
        entity_type: str = None,
        entity_id: int = None,
        status: DocumentStatus = None,
        tags: str = None,
        start_date: date = None,
        end_date: date = None
    ) -> List[Document]:
        """Rechercher des documents avec critères multiples"""
        try:
            session = get_session()
            query = session.query(Document)
            
            if title:
                query = query.filter(Document.title.ilike(f'%{title}%'))
            
            if document_type:
                query = query.filter(Document.document_type == document_type)
            
            if entity_type:
                query = query.filter(Document.entity_type == entity_type)
            
            if entity_id:
                query = query.filter(Document.entity_id == entity_id)
            
            if status:
                query = query.filter(Document.status == status)
            
            if tags:
                query = query.filter(Document.tags.ilike(f'%{tags}%'))
            
            if start_date:
                query = query.filter(Document.created_at >= datetime.combine(start_date, datetime.min.time()))
            
            if end_date:
                query = query.filter(Document.created_at <= datetime.combine(end_date, datetime.max.time()))
            
            return query.order_by(Document.created_at.desc()).all()
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de documents : {e}")
            return []
    
    @staticmethod
    def delete_document(document_id: int, delete_file: bool = True) -> bool:
        """
        Supprimer un document
        
        Args:
            document_id: ID du document
            delete_file: Si True, supprime aussi le fichier physique
        """
        try:
            session = get_session()
            document = session.query(Document).filter(Document.id == document_id).first()
            
            if not document:
                return False
            
            # Supprimer le fichier physique si demandé
            if delete_file and os.path.exists(document.file_path):
                os.remove(document.file_path)
                logger.info(f"Fichier supprimé : {document.file_path}")
            
            # Supprimer l'entrée en base
            session.delete(document)
            session.commit()
            
            logger.info(f"Document {document_id} supprimé")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du document : {e}")
            if 'session' in locals():
                session.rollback()
            return False
    
    # ========== Validation ==========
    
    @staticmethod
    def verify_document(document_id: int, verified_by: str = None) -> bool:
        """Marquer un document comme vérifié"""
        try:
            session = get_session()
            document = session.query(Document).filter(Document.id == document_id).first()
            
            if not document:
                return False
            
            document.mark_as_verified(verified_by)
            session.commit()
            
            logger.info(f"Document {document_id} vérifié par {verified_by}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du document : {e}")
            if 'session' in locals():
                session.rollback()
            return False
    
    # ========== Documents expirés ==========
    
    @staticmethod
    def get_expiring_documents(days: int = 30) -> List[Document]:
        """Obtenir les documents qui expirent bientôt"""
        try:
            session = get_session()
            cutoff_date = datetime.now() + timedelta(days=days)
            
            documents = session.query(Document).filter(
                and_(
                    Document.expiry_date.isnot(None),
                    Document.expiry_date <= cutoff_date,
                    Document.expiry_date > datetime.now(),
                    Document.status == DocumentStatus.ACTIVE
                )
            ).order_by(Document.expiry_date).all()
            
            return documents
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des documents expirant : {e}")
            return []
    
    @staticmethod
    def get_expired_documents() -> List[Document]:
        """Obtenir les documents expirés"""
        try:
            session = get_session()
            
            documents = session.query(Document).filter(
                and_(
                    Document.expiry_date.isnot(None),
                    Document.expiry_date < datetime.now(),
                    Document.status != DocumentStatus.EXPIRED
                )
            ).order_by(Document.expiry_date.desc()).all()
            
            return documents
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des documents expirés : {e}")
            return []
    
    @staticmethod
    def mark_expired_documents() -> int:
        """Marquer automatiquement les documents expirés"""
        try:
            expired_docs = DocumentController.get_expired_documents()
            count = 0
            
            session = get_session()
            for doc in expired_docs:
                doc.mark_as_expired()
                count += 1
            
            session.commit()
            logger.info(f"{count} documents marqués comme expirés")
            return count
            
        except Exception as e:
            logger.error(f"Erreur lors du marquage des documents expirés : {e}")
            if 'session' in locals():
                session.rollback()
            return 0
    
    # ========== Statistiques ==========
    
    @staticmethod
    def get_document_statistics() -> Dict[str, Any]:
        """Obtenir les statistiques des documents"""
        try:
            session = get_session()
            documents = session.query(Document).all()
            
            if not documents:
                return {
                    'total': 0,
                    'by_type': {},
                    'by_status': {},
                    'total_size_mb': 0.0
                }
            
            stats = {
                'total': len(documents),
                'by_type': {},
                'by_status': {},
                'by_entity_type': {},
                'verified': len([d for d in documents if d.is_verified]),
                'expiring_soon': len([d for d in documents if d.is_expiring_soon()]),
                'expired': len([d for d in documents if d.is_expired()]),
                'total_size_mb': round(sum(d.file_size or 0 for d in documents) / (1024 * 1024), 2)
            }
            
            # Par type
            for doc_type in DocumentType:
                count = len([d for d in documents if d.document_type == doc_type])
                if count > 0:
                    stats['by_type'][doc_type.value] = count
            
            # Par statut
            for status in DocumentStatus:
                count = len([d for d in documents if d.status == status])
                if count > 0:
                    stats['by_status'][status.value] = count
            
            # Par type d'entité
            entity_types = set(d.entity_type for d in documents if d.entity_type)
            for entity_type in entity_types:
                count = len([d for d in documents if d.entity_type == entity_type])
                stats['by_entity_type'][entity_type] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques : {e}")
            return {}
    
    @staticmethod
    def export_to_csv(documents: Optional[List[Document]] = None, filename: Optional[str] = None) -> tuple[bool, str]:
        """
        Exporter les documents vers un fichier CSV
        
        Args:
            documents: Liste des documents à exporter (None = tous)
            filename: Nom du fichier CSV (None = généré automatiquement)
        
        Returns:
            tuple[bool, str]: (succès, message ou chemin du fichier)
        """
        try:
            session = get_session()
            
            # Si aucun document fourni, récupérer tous les documents
            if documents is None:
                documents = session.query(Document).order_by(Document.created_at.desc()).all()
            
            if not documents:
                return False, "Aucun document à exporter"
            
            # Générer le nom de fichier si non fourni
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"documents_export_{timestamp}.csv"
            
            # Assurer l'extension .csv
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            # Créer le répertoire d'export si nécessaire
            export_dir = "exports"
            Path(export_dir).mkdir(parents=True, exist_ok=True)
            filepath = os.path.join(export_dir, filename)
            
            # Écrire le fichier CSV
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = [
                    'ID', 'Titre', 'Type', 'Statut', 'Entité Type', 'Entité ID',
                    'Numéro', 'Date Emission', 'Date Expiration', 'Autorité',
                    'Fichier', 'Taille (Ko)', 'Vérifié', 'Vérifié Par', 'Date Vérification',
                    'Notes', 'Créé Le', 'Créé Par', 'Modifié Le'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for doc in documents:
                    writer.writerow({
                        'ID': doc.id,
                        'Titre': doc.title,
                        'Type': doc.document_type.value if doc.document_type else '',
                        'Statut': doc.status.value if doc.status else '',
                        'Entité Type': doc.entity_type or '',
                        'Entité ID': doc.entity_id or '',
                        'Numéro': doc.document_number or '',
                        'Date Emission': doc.issue_date.strftime("%Y-%m-%d") if doc.issue_date else '',
                        'Date Expiration': doc.expiry_date.strftime("%Y-%m-%d") if doc.expiry_date else '',
                        'Autorité': doc.issuing_authority or '',
                        'Fichier': doc.file_name or '',
                        'Taille (Ko)': round((doc.file_size or 0) / 1024, 2),
                        'Vérifié': 'Oui' if doc.is_verified else 'Non',
                        'Vérifié Par': doc.verified_by or '',
                        'Date Vérification': doc.verified_at.strftime("%Y-%m-%d %H:%M") if doc.verified_at else '',
                        'Notes': doc.notes or '',
                        'Créé Le': doc.created_at.strftime("%Y-%m-%d %H:%M") if doc.created_at else '',
                        'Créé Par': doc.created_by or '',
                        'Modifié Le': doc.updated_at.strftime("%Y-%m-%d %H:%M") if doc.updated_at else ''
                    })
            
            logger.info(f"{len(documents)} documents exportés vers {filepath}")
            return True, filepath
            
        except Exception as e:
            error_msg = f"Erreur lors de l'export CSV : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
