"""
Contrôleur pour la gestion des élèves
"""

from typing import List, Optional, Dict, Any
from datetime import date

from sqlalchemy import or_
from src.models import Student, StudentStatus, get_session
from src.utils import get_logger, export_to_csv, import_from_csv

logger = get_logger()


class StudentController:
    """Contrôleur pour gérer les opérations sur les élèves"""
    
    @staticmethod
    def get_all_students(status: Optional[StudentStatus] = None) -> List[Student]:
        """
        Récupérer tous les élèves
        
        Args:
            status: Filtrer par statut (optionnel)
        
        Returns:
            Liste des élèves
        """
        try:
            session = get_session()
            query = session.query(Student)
            
            if status:
                query = query.filter(Student.status == status)
            
            students = query.order_by(Student.registration_date.desc()).all()
            return students
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des élèves : {e}")
            return []
    
    @staticmethod
    def get_student_by_id(student_id: int) -> Optional[Student]:
        """
        Récupérer un élève par son ID
        
        Args:
            student_id: ID de l'élève
        
        Returns:
            Élève ou None
        """
        try:
            session = get_session()
            return session.query(Student).filter(Student.id == student_id).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'élève {student_id} : {e}")
            return None
    
    @staticmethod
    def get_student_by_cin(cin: str) -> Optional[Student]:
        """
        Récupérer un élève par son CIN
        
        Args:
            cin: Numéro CIN
        
        Returns:
            Élève ou None
        """
        try:
            session = get_session()
            return session.query(Student).filter(Student.cin == cin).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'élève CIN {cin} : {e}")
            return None
    
    @staticmethod
    def search_students(query: str) -> List[Student]:
        """
        Rechercher des élèves par nom, CIN ou téléphone
        
        Args:
            query: Terme de recherche
        
        Returns:
            Liste des élèves correspondants
        """
        try:
            session = get_session()
            search_term = f"%{query}%"
            
            students = session.query(Student).filter(
                or_(
                    Student.full_name.like(search_term),
                    Student.cin.like(search_term),
                    Student.phone.like(search_term),
                    Student.email.like(search_term)
                )
            ).order_by(Student.full_name).all()
            
            return students
        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'élèves : {e}")
            return []
    
    @staticmethod
    def create_student(student_data: Dict[str, Any]) -> tuple[bool, str, Optional[Student]]:
        """
        Créer un nouvel élève
        
        Args:
            student_data: Données de l'élève
        
        Returns:
            Tuple (success, message, student)
        """
        try:
            session = get_session()
            
            # Vérifier si le CIN existe déjà
            existing = session.query(Student).filter(Student.cin == student_data['cin']).first()
            if existing:
                return False, "Un élève avec ce CIN existe déjà", None
            
            # Créer l'élève
            student = Student(**student_data)
            session.add(student)
            session.commit()
            session.refresh(student)
            
            logger.info(f"Élève créé : {student.full_name} (ID: {student.id})")
            return True, "Élève créé avec succès", student
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la création de l'élève : {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def update_student(student_id: int, student_data: Dict[str, Any]) -> tuple[bool, str, Optional[Student]]:
        """
        Mettre à jour un élève
        
        Args:
            student_id: ID de l'élève
            student_data: Nouvelles données
        
        Returns:
            Tuple (success, message, student)
        """
        try:
            session = get_session()
            student = session.query(Student).filter(Student.id == student_id).first()
            
            if not student:
                return False, "Élève introuvable", None
            
            # Sauvegarder les anciennes valeurs financières
            old_total_due = student.total_due
            old_total_paid = student.total_paid
            
            # Mettre à jour les attributs
            for key, value in student_data.items():
                if hasattr(student, key) and key != 'id':
                    setattr(student, key, value)
            
            # CRITIQUE : Recalculer le balance si total_due ou total_paid ont changé
            if 'total_due' in student_data or old_total_due != student.total_due:
                # Balance = total_paid - total_due
                # Positive = CRÉDIT (trop-perçu), Negative = DETTE, Zero = À jour
                from decimal import Decimal
                paid = Decimal(str(float(student.total_paid) if student.total_paid else 0.0))
                due = Decimal(str(float(student.total_due) if student.total_due else 0.0))
                student.balance = paid - due
                logger.info(f"Balance recalculé pour {student.full_name}: {student.balance} DH (Dû: {student.total_due}, Payé: {student.total_paid})")
            
            session.commit()
            session.refresh(student)
            
            logger.info(f"Élève mis à jour : {student.full_name} (ID: {student.id})")
            return True, "Élève mis à jour avec succès", student
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la mise à jour de l'élève : {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def delete_student(student_id: int) -> tuple[bool, str]:
        """
        Supprimer un élève
        
        Args:
            student_id: ID de l'élève
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            student = session.query(Student).filter(Student.id == student_id).first()
            
            if not student:
                return False, "Élève introuvable"
            
            student_name = student.full_name
            session.delete(student)
            session.commit()
            
            logger.info(f"Élève supprimé : {student_name} (ID: {student_id})")
            return True, "Élève supprimé avec succès"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la suppression de l'élève : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def get_active_students() -> List[Student]:
        """Obtenir tous les élèves actifs"""
        try:
            session = get_session()
            students = session.query(Student).filter(Student.status == StudentStatus.ACTIVE).all()
            return students
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des élèves actifs : {e}")
            return []
    
    @staticmethod
    def get_active_students_count() -> int:
        """Obtenir le nombre d'élèves actifs"""
        try:
            session = get_session()
            return session.query(Student).filter(Student.status == StudentStatus.ACTIVE).count()
        except Exception as e:
            logger.error(f"Erreur lors du comptage des élèves actifs : {e}")
            return 0
    
    @staticmethod
    def get_students_with_debt() -> List[Student]:
        """Obtenir les élèves ayant des dettes
        
        Balance = total_due - total_paid
        Balance > 0 = L'étudiant doit de l'argent (dette)
        """
        try:
            session = get_session()
            return session.query(Student).filter(Student.balance < 0).order_by(Student.balance).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des élèves endettés : {e}")
            return []
    
    @staticmethod
    def export_students_to_csv(students: List[Student], filename: str = "students") -> tuple[bool, str]:
        """
        Exporter les élèves vers un fichier CSV
        
        Args:
            students: Liste des élèves
            filename: Nom du fichier
        
        Returns:
            Tuple (success, filepath_or_error)
        """
        try:
            data = [student.to_dict() for student in students]
            return export_to_csv(data, filename)
        except Exception as e:
            error_msg = f"Erreur lors de l'export : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def import_students_from_csv(filepath: str) -> tuple[bool, int, str]:
        """
        Importer des élèves depuis un fichier CSV
        
        Args:
            filepath: Chemin vers le fichier CSV
        
        Returns:
            Tuple (success, count, message)
        """
        try:
            required_fields = ['full_name', 'cin', 'date_of_birth', 'phone']
            success, data, message = import_from_csv(filepath, required_fields)
            
            if not success:
                return False, 0, message
            
            session = get_session()
            imported_count = 0
            errors = []
            
            for row in data:
                try:
                    # Vérifier si le CIN existe déjà
                    if session.query(Student).filter(Student.cin == row['cin']).first():
                        errors.append(f"CIN {row['cin']} existe déjà")
                        continue
                    
                    # Convertir la date de naissance
                    if isinstance(row['date_of_birth'], str):
                        row['date_of_birth'] = date.fromisoformat(row['date_of_birth'])
                    
                    # Créer l'élève
                    student = Student(**row)
                    session.add(student)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Erreur ligne {imported_count + 1} : {str(e)}")
            
            session.commit()
            
            result_message = f"{imported_count} élèves importés"
            if errors:
                result_message += f" ({len(errors)} erreurs)"
            
            logger.info(result_message)
            return True, imported_count, result_message
            
        except Exception as e:
            error_msg = f"Erreur lors de l'import : {str(e)}"
            logger.error(error_msg)
            return False, 0, error_msg
