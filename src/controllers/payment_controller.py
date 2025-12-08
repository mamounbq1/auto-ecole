"""
Contrôleur pour la gestion des paiements
"""

from typing import List, Optional, Dict, Any
from datetime import date

from src.models import Payment, PaymentMethod, Student, get_session
from src.utils import get_logger, get_export_manager

logger = get_logger()


class PaymentController:
    """Contrôleur pour gérer les opérations sur les paiements"""
    
    @staticmethod
    def create_payment(student_id: int, amount: float, payment_method: PaymentMethod,
                      description: str = "", validated_by: str = "") -> tuple[bool, str, Optional[Payment]]:
        """
        Créer un nouveau paiement
        
        Args:
            student_id: ID de l'élève
            amount: Montant du paiement
            payment_method: Méthode de paiement
            description: Description
            validated_by: Validé par (nom du caissier)
        
        Returns:
            Tuple (success, message, payment)
        """
        try:
            session = get_session()
            
            # Vérifier que l'élève existe
            student = session.query(Student).filter(Student.id == student_id).first()
            if not student:
                return False, "Élève introuvable", None
            
            # Créer le paiement
            payment = Payment(
                student_id=student_id,
                amount=amount,
                payment_method=payment_method,
                description=description
            )
            
            # Valider le paiement
            if validated_by:
                payment.validate(validated_by)
            
            session.add(payment)
            
            # Mettre à jour le solde de l'élève
            student.add_payment(amount)
            
            session.commit()
            session.refresh(payment)
            
            logger.info(f"Paiement créé : {amount} DH pour {student.full_name}")
            return True, "Paiement enregistré avec succès", payment
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la création du paiement : {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def get_payments_by_student(student_id: int) -> List[Payment]:
        """Obtenir les paiements d'un élève"""
        try:
            session = get_session()
            return session.query(Payment).filter(Payment.student_id == student_id).order_by(Payment.payment_date.desc()).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des paiements : {e}")
            return []
    
    @staticmethod
    def get_monthly_revenue(year: int, month: int) -> float:
        """
        Calculer le chiffre d'affaires mensuel
        
        Args:
            year: Année
            month: Mois (1-12)
        
        Returns:
            Montant total des paiements du mois
        """
        try:
            from datetime import datetime
            from sqlalchemy import extract
            
            session = get_session()
            payments = session.query(Payment).filter(
                extract('year', Payment.payment_date) == year,
                extract('month', Payment.payment_date) == month
            ).all()
            
            total = sum(p.amount for p in payments)
            return total
        except Exception as e:
            logger.error(f"Erreur lors du calcul du CA mensuel : {e}")
            return 0.0
    
    @staticmethod
    def generate_receipt_pdf(payment_id: int) -> tuple[bool, str]:
        """
        Générer un reçu PDF pour un paiement
        
        Args:
            payment_id: ID du paiement
        
        Returns:
            Tuple (success, filepath_or_error)
        """
        try:
            session = get_session()
            payment = session.query(Payment).filter(Payment.id == payment_id).first()
            
            if not payment:
                return False, "Paiement introuvable"
            
            student = payment.student
            
            # Préparer les données du reçu
            receipt_data = {
                'receipt_number': payment.receipt_number,
                'date': payment.payment_date.strftime('%d/%m/%Y'),
                'student_name': student.full_name,
                'student_cin': student.cin,
                'student_phone': student.phone,
                'amount': payment.amount,
                'payment_method': payment.payment_method.value,
                'description': payment.description or '',
                'validated_by': payment.validated_by or '',
            }
            
            # Générer le HTML du reçu
            export_manager = get_export_manager()
            receipt_html = export_manager.generate_receipt_html(receipt_data)
            
            # Exporter vers HTML/PDF
            filename = f"recu_{payment.receipt_number}"
            return export_manager.export_to_pdf(receipt_html, filename, "Reçu de Paiement")
            
        except Exception as e:
            error_msg = f"Erreur lors de la génération du reçu : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def get_all_payments() -> List[Payment]:
        """Obtenir tous les paiements"""
        try:
            session = get_session()
            payments = session.query(Payment).order_by(Payment.payment_date.desc()).all()
            return payments
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des paiements : {e}")
            return []
