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
    
    @staticmethod
    def get_payment_by_id(payment_id: int) -> Optional[Payment]:
        """Récupérer un paiement par son ID"""
        try:
            session = get_session()
            return session.query(Payment).filter(Payment.id == payment_id).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du paiement {payment_id} : {e}")
            return None
    
    @staticmethod
    def get_payment_by_receipt(receipt_number: str) -> Optional[Payment]:
        """Récupérer un paiement par son numéro de reçu"""
        try:
            session = get_session()
            return session.query(Payment).filter(Payment.receipt_number == receipt_number).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du paiement (reçu {receipt_number}) : {e}")
            return None
    
    @staticmethod
    def update_payment(payment_id: int, **kwargs) -> tuple[bool, str]:
        """
        Mettre à jour un paiement
        
        Args:
            payment_id: ID du paiement
            **kwargs: Champs à mettre à jour
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            payment = session.query(Payment).filter(Payment.id == payment_id).first()
            
            if not payment:
                return False, "Paiement introuvable"
            
            # Si le montant change, mettre à jour le solde de l'élève
            if 'amount' in kwargs and kwargs['amount'] != payment.amount:
                old_amount = payment.amount
                new_amount = kwargs['amount']
                difference = new_amount - old_amount
                
                if payment.student:
                    payment.student.add_payment(difference)
            
            # Mettre à jour les autres champs
            for key, value in kwargs.items():
                if hasattr(payment, key):
                    setattr(payment, key, value)
            
            session.commit()
            logger.info(f"Paiement {payment_id} mis à jour")
            return True, "Paiement mis à jour avec succès"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la mise à jour du paiement : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def cancel_payment(payment_id: int, reason: str = "") -> tuple[bool, str]:
        """
        Annuler un paiement
        
        Args:
            payment_id: ID du paiement
            reason: Raison de l'annulation
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            payment = session.query(Payment).filter(Payment.id == payment_id).first()
            
            if not payment:
                return False, "Paiement introuvable"
            
            # Mettre à jour le solde de l'élève (retirer le paiement)
            if payment.student:
                payment.student.add_payment(-payment.amount)
            
            # Ajouter une note d'annulation
            cancellation_note = f"Annulé le {date.today().strftime('%d/%m/%Y')}"
            if reason:
                cancellation_note += f" - Raison: {reason}"
            
            current_description = payment.description or ""
            payment.description = f"{current_description}\n{cancellation_note}"
            payment.is_validated = False
            
            session.commit()
            logger.info(f"Paiement {payment_id} annulé")
            return True, "Paiement annulé avec succès"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de l'annulation du paiement : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def validate_payment(payment_id: int, validated_by: str) -> tuple[bool, str]:
        """
        Valider un paiement
        
        Args:
            payment_id: ID du paiement
            validated_by: Nom du validateur
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            payment = session.query(Payment).filter(Payment.id == payment_id).first()
            
            if not payment:
                return False, "Paiement introuvable"
            
            payment.validate(validated_by)
            session.commit()
            
            logger.info(f"Paiement {payment_id} validé par {validated_by}")
            return True, "Paiement validé avec succès"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la validation du paiement : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def search_payments(query: str) -> List[Payment]:
        """
        Rechercher des paiements par numéro de reçu ou nom d'élève
        
        Args:
            query: Terme de recherche
        
        Returns:
            Liste des paiements correspondants
        """
        try:
            from sqlalchemy import or_
            session = get_session()
            search_term = f"%{query}%"
            
            payments = session.query(Payment).join(Student).filter(
                or_(
                    Payment.receipt_number.like(search_term),
                    Payment.description.like(search_term),
                    Student.full_name.like(search_term),
                    Student.cin.like(search_term)
                )
            ).order_by(Payment.payment_date.desc()).all()
            
            return payments
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de paiements : {e}")
            return []
    
    @staticmethod
    def get_payments_by_date_range(start_date: date, end_date: date) -> List[Payment]:
        """
        Récupérer les paiements dans une plage de dates
        
        Args:
            start_date: Date de début
            end_date: Date de fin
        
        Returns:
            Liste des paiements
        """
        try:
            session = get_session()
            return session.query(Payment).filter(
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            ).order_by(Payment.payment_date.desc()).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des paiements : {e}")
            return []
    
    @staticmethod
    def get_payments_by_method(payment_method: PaymentMethod) -> List[Payment]:
        """
        Récupérer les paiements par méthode
        
        Args:
            payment_method: Méthode de paiement
        
        Returns:
            Liste des paiements
        """
        try:
            session = get_session()
            return session.query(Payment).filter(
                Payment.payment_method == payment_method
            ).order_by(Payment.payment_date.desc()).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des paiements : {e}")
            return []
    
    @staticmethod
    def get_payment_statistics(start_date: Optional[date] = None,
                               end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Obtenir les statistiques de paiements
        
        Args:
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
        
        Returns:
            Dictionnaire de statistiques
        """
        try:
            session = get_session()
            query = session.query(Payment)
            
            if start_date:
                query = query.filter(Payment.payment_date >= start_date)
            if end_date:
                query = query.filter(Payment.payment_date <= end_date)
            
            payments = query.all()
            
            if not payments:
                return {
                    'total_payments': 0,
                    'total_amount': 0.0,
                    'average_amount': 0.0,
                    'by_method': {}
                }
            
            total = len(payments)
            total_amount = sum(p.amount for p in payments)
            average_amount = total_amount / total if total > 0 else 0.0
            
            # Statistiques par méthode de paiement
            by_method = {}
            for method in PaymentMethod:
                method_payments = [p for p in payments if p.payment_method == method]
                if method_payments:
                    by_method[method.value] = {
                        'count': len(method_payments),
                        'amount': sum(p.amount for p in method_payments)
                    }
            
            return {
                'total_payments': total,
                'total_amount': round(total_amount, 2),
                'average_amount': round(average_amount, 2),
                'by_method': by_method,
                'validated_count': len([p for p in payments if p.is_validated]),
                'pending_count': len([p for p in payments if not p.is_validated])
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques : {e}")
            return {}
    
    @staticmethod
    def export_to_csv(payments: Optional[List[Payment]] = None,
                     filename: Optional[str] = None) -> tuple[bool, str]:
        """
        Exporter les paiements vers un fichier CSV
        
        Args:
            payments: Liste de paiements (optionnel, tous si None)
            filename: Nom du fichier (optionnel)
        
        Returns:
            Tuple (success, filepath/message)
        """
        try:
            if payments is None:
                payments = PaymentController.get_all_payments()
            
            if not payments:
                return False, "Aucun paiement à exporter"
            
            # Préparer les données avec infos élève
            data = []
            for payment in payments:
                payment_dict = payment.to_dict()
                if payment.student:
                    payment_dict['student_name'] = payment.student.full_name
                    payment_dict['student_cin'] = payment.student.cin
                else:
                    payment_dict['student_name'] = ''
                    payment_dict['student_cin'] = ''
                data.append(payment_dict)
            
            # Exporter avec ExportManager
            export_mgr = get_export_manager()
            filepath = export_mgr.export_to_csv(data, 'payments', filename)
            
            logger.info(f"{len(payments)} paiements exportés vers {filepath}")
            return True, filepath
            
        except Exception as e:
            error_msg = f"Erreur lors de l'export : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
