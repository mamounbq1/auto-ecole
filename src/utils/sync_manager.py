"""
Gestionnaire de synchronisation des données et statuts
Phase 4 - Synchronisation automatique
"""

from typing import List, Dict, Any
from datetime import datetime, date
from src.models import (
    Student, StudentStatus, Instructor, Vehicle, VehicleStatus,
    Session, SessionStatus, Exam, ExamResult, Payment,
    VehicleMaintenance, MaintenanceStatus, Document, DocumentStatus,
    get_session
)
from src.utils import get_logger

logger = get_logger()


class SyncManager:
    """Gestionnaire de synchronisation des statuts et données"""
    
    @staticmethod
    def sync_student_statuses() -> int:
        """
        Synchroniser les statuts des étudiants basés sur leur progression
        
        Returns:
            Nombre d'étudiants mis à jour
        """
        try:
            session = get_session()
            updated_count = 0
            
            students = session.query(Student).all()
            
            for student in students:
                old_status = student.status
                new_status = None
                
                # Vérifier les examens réussis
                passed_exams = [e for e in student.exams if e.result == ExamResult.PASSED]
                
                if len(passed_exams) >= 2:  # Code + Conduite réussis
                    new_status = StudentStatus.LICENSED
                elif student.hours_completed >= student.hours_planned:
                    new_status = StudentStatus.READY_FOR_EXAM
                elif student.hours_completed > 0:
                    new_status = StudentStatus.IN_TRAINING
                elif len(student.sessions) == 0:
                    new_status = StudentStatus.REGISTERED
                
                if new_status and new_status != old_status:
                    student.status = new_status
                    updated_count += 1
                    logger.info(f"Étudiant {student.full_name}: {old_status.value} → {new_status.value}")
            
            session.commit()
            logger.info(f"Synchronisation statuts étudiants: {updated_count} mis à jour")
            return updated_count
            
        except Exception as e:
            logger.error(f"Erreur sync statuts étudiants: {e}")
            session.rollback()
            return 0
    
    @staticmethod
    def sync_vehicle_statuses() -> int:
        """
        Synchroniser les statuts des véhicules basés sur leur maintenance
        
        Returns:
            Nombre de véhicules mis à jour
        """
        try:
            session = get_session()
            updated_count = 0
            
            vehicles = session.query(Vehicle).all()
            
            for vehicle in vehicles:
                old_status = vehicle.status
                new_status = None
                
                # Vérifier les maintenances en cours
                ongoing_maintenances = [
                    m for m in vehicle.maintenances 
                    if m.status in [MaintenanceStatus.PENDING, MaintenanceStatus.IN_PROGRESS]
                ]
                
                if ongoing_maintenances:
                    new_status = VehicleStatus.MAINTENANCE
                elif vehicle.status == VehicleStatus.MAINTENANCE:
                    # Si plus de maintenance en cours, remettre disponible
                    new_status = VehicleStatus.AVAILABLE
                
                if new_status and new_status != old_status:
                    vehicle.status = new_status
                    updated_count += 1
                    logger.info(f"Véhicule {vehicle.immatriculation}: {old_status.value} → {new_status.value}")
            
            session.commit()
            logger.info(f"Synchronisation statuts véhicules: {updated_count} mis à jour")
            return updated_count
            
        except Exception as e:
            logger.error(f"Erreur sync statuts véhicules: {e}")
            session.rollback()
            return 0
    
    @staticmethod
    def sync_session_statuses() -> int:
        """
        Synchroniser les statuts des séances basés sur leur date
        
        Returns:
            Nombre de séances mises à jour
        """
        try:
            session = get_session()
            updated_count = 0
            
            now = datetime.now()
            
            # Marquer les séances passées comme COMPLETED si elles sont toujours PLANNED
            sessions = session.query(Session).filter(
                Session.status == SessionStatus.SCHEDULED
            ).all()
            
            for sess in sessions:
                session_datetime = datetime.combine(sess.session_date, sess.start_time)
                
                if session_datetime < now:
                    sess.status = SessionStatus.COMPLETED
                    updated_count += 1
                    logger.info(f"Séance {sess.id} marquée COMPLETED (date passée)")
            
            session.commit()
            logger.info(f"Synchronisation statuts séances: {updated_count} mis à jour")
            return updated_count
            
        except Exception as e:
            logger.error(f"Erreur sync statuts séances: {e}")
            session.rollback()
            return 0
    
    @staticmethod
    def sync_document_statuses() -> int:
        """
        Synchroniser les statuts des documents basés sur leur date d'expiration
        
        Returns:
            Nombre de documents mis à jour
        """
        try:
            session = get_session()
            updated_count = 0
            
            today = date.today()
            
            # Documents expirés
            documents = session.query(Document).filter(
                Document.expiry_date < today,
                Document.status != DocumentStatus.EXPIRED
            ).all()
            
            for doc in documents:
                old_status = doc.status
                doc.status = DocumentStatus.EXPIRED
                updated_count += 1
                logger.info(f"Document {doc.title} marqué EXPIRED (expiré le {doc.expiry_date})")
            
            session.commit()
            logger.info(f"Synchronisation statuts documents: {updated_count} mis à jour")
            return updated_count
            
        except Exception as e:
            logger.error(f"Erreur sync statuts documents: {e}")
            session.rollback()
            return 0
    
    @staticmethod
    def sync_all() -> Dict[str, int]:
        """
        Synchroniser tous les statuts de l'application
        
        Returns:
            Dictionnaire avec le nombre de mises à jour par catégorie
        """
        logger.info("=== Début synchronisation globale ===")
        
        results = {
            'students': SyncManager.sync_student_statuses(),
            'vehicles': SyncManager.sync_vehicle_statuses(),
            'sessions': SyncManager.sync_session_statuses(),
            'documents': SyncManager.sync_document_statuses()
        }
        
        total = sum(results.values())
        logger.info(f"=== Fin synchronisation globale: {total} mises à jour ===")
        
        return results
    
    @staticmethod
    def get_sync_report(results: Dict[str, int]) -> str:
        """
        Générer un rapport textuel de synchronisation
        
        Args:
            results: Résultats de sync_all()
            
        Returns:
            Rapport formaté
        """
        total = sum(results.values())
        
        if total == 0:
            return "✅ Tous les statuts sont déjà synchronisés"
        
        lines = [f"🔄 Synchronisation effectuée: {total} mise(s) à jour"]
        
        if results['students'] > 0:
            lines.append(f"  • Étudiants: {results['students']}")
        
        if results['vehicles'] > 0:
            lines.append(f"  • Véhicules: {results['vehicles']}")
        
        if results['sessions'] > 0:
            lines.append(f"  • Séances: {results['sessions']}")
        
        if results['documents'] > 0:
            lines.append(f"  • Documents: {results['documents']}")
        
        return "\n".join(lines)
