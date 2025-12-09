"""
Contrôleur pour la recherche globale multi-entités
Phase 4 - Recherche avancée
"""

from typing import Dict, List, Any
from src.controllers import (
    StudentController, InstructorController, VehicleController,
    SessionController, PaymentController, ExamController,
    DocumentController, MaintenanceController, NotificationController
)
from src.utils import get_logger

logger = get_logger()


class SearchController:
    """Contrôleur pour effectuer des recherches globales"""
    
    @staticmethod
    def global_search(query: str) -> Dict[str, List[Any]]:
        """
        Recherche globale dans toutes les entités
        
        Args:
            query: Terme de recherche
            
        Returns:
            Dictionnaire avec les résultats par catégorie
        """
        if not query or len(query.strip()) < 2:
            return {}
        
        results = {}
        
        try:
            # Recherche dans les étudiants
            students = StudentController.search_students(query)
            if students:
                results['students'] = students
                logger.info(f"{len(students)} étudiant(s) trouvé(s)")
            
            # Recherche dans les moniteurs
            instructors = InstructorController.search_instructors(query)
            if instructors:
                results['instructors'] = instructors
                logger.info(f"{len(instructors)} moniteur(s) trouvé(s)")
            
            # Recherche dans les véhicules
            vehicles = VehicleController.search_vehicles(query)
            if vehicles:
                results['vehicles'] = vehicles
                logger.info(f"{len(vehicles)} véhicule(s) trouvé(s)")
            
            # Recherche dans les examens
            exams = ExamController.search_exams(query)
            if exams:
                results['exams'] = exams
                logger.info(f"{len(exams)} examen(s) trouvé(s)")
            
            # Recherche dans les paiements
            payments = PaymentController.search_payments(query)
            if payments:
                results['payments'] = payments
                logger.info(f"{len(payments)} paiement(s) trouvé(s)")
            
            # Recherche dans les documents
            documents = DocumentController.search_documents(query)
            if documents:
                results['documents'] = documents
                logger.info(f"{len(documents)} document(s) trouvé(s)")
            
            # Recherche dans les maintenances
            maintenances = MaintenanceController.search_maintenances(query)
            if maintenances:
                results['maintenances'] = maintenances
                logger.info(f"{len(maintenances)} maintenance(s) trouvée(s)")
            
            # Recherche dans les notifications
            notifications = NotificationController.search_notifications(query)
            if notifications:
                results['notifications'] = notifications
                logger.info(f"{len(notifications)} notification(s) trouvée(s)")
            
            total = sum(len(v) for v in results.values())
            logger.info(f"Recherche globale '{query}' : {total} résultat(s) total")
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche globale : {e}")
            return {}
    
    @staticmethod
    def get_search_summary(results: Dict[str, List[Any]]) -> str:
        """
        Obtenir un résumé textuel des résultats de recherche
        
        Args:
            results: Résultats de la recherche globale
            
        Returns:
            Chaîne de résumé formatée
        """
        if not results:
            return "Aucun résultat trouvé"
        
        summary_parts = []
        
        if 'students' in results:
            summary_parts.append(f"{len(results['students'])} étudiant(s)")
        
        if 'instructors' in results:
            summary_parts.append(f"{len(results['instructors'])} moniteur(s)")
        
        if 'vehicles' in results:
            summary_parts.append(f"{len(results['vehicles'])} véhicule(s)")
        
        if 'exams' in results:
            summary_parts.append(f"{len(results['exams'])} examen(s)")
        
        if 'payments' in results:
            summary_parts.append(f"{len(results['payments'])} paiement(s)")
        
        if 'documents' in results:
            summary_parts.append(f"{len(results['documents'])} document(s)")
        
        if 'maintenances' in results:
            summary_parts.append(f"{len(results['maintenances'])} maintenance(s)")
        
        if 'notifications' in results:
            summary_parts.append(f"{len(results['notifications'])} notification(s)")
        
        return " | ".join(summary_parts)
