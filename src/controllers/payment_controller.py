"""
Contrôleur pour la gestion des paiements
"""

from typing import List, Optional, Dict, Any
from datetime import date
from decimal import Decimal

from src.models import Payment, PaymentMethod, Student, get_session
from src.utils import get_logger, get_export_manager

logger = get_logger()

# Constantes de validation
MIN_AMOUNT = 0.01
MAX_AMOUNT = 100000.00


class PaymentController:
    """Contrôleur pour gérer les opérations sur les paiements"""
    
    @staticmethod
    def create_payment(student_id: int, amount: float, payment_method: PaymentMethod,
                      description: str = "", validated_by: str = "") -> tuple[bool, str, Optional[Payment]]:
        """
        Créer un nouveau paiement avec validation stricte
        
        Args:
            student_id: ID de l'élève
            amount: Montant du paiement
            payment_method: Méthode de paiement
            description: Description
            validated_by: Validé par (nom du caissier)
        
        Returns:
            Tuple (success, message, payment)
        """
        session = get_session()
        try:
            # VALIDATION 1: Montant
            if amount <= 0:
                return False, "Le montant doit être positif", None
            if amount > MAX_AMOUNT:
                return False, f"Le montant ne peut pas dépasser {MAX_AMOUNT:,.2f} DH", None
            
            # Arrondir à 2 décimales
            amount = round(float(amount), 2)
            
            # VALIDATION 2: Élève existe
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
            
            # Mettre à jour le solde de l'élève (dans la même transaction)
            student.add_payment(amount)
            
            # Commit de la transaction complète
            session.commit()
            
            # Rafraîchir les objets après commit
            session.refresh(payment)
            session.refresh(student)
            
            logger.info(f"Paiement créé : {amount} DH pour {student.full_name} (nouveau solde: {student.balance})")
            return True, "Paiement enregistré avec succès", payment
            
        except Exception as e:
            session.rollback()
            # Rafraîchir l'élève pour annuler les modifications en mémoire
            try:
                session.refresh(session.query(Student).filter(Student.id == student_id).first())
            except:
                pass
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
        Calculer le chiffre d'affaires mensuel (EXCLUT les paiements annulés)
        
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
                extract('month', Payment.payment_date) == month,
                Payment.is_cancelled == False  # IMPORTANT: Exclure annulés
            ).all()
            
            total = sum(float(p.amount) for p in payments)
            return round(total, 2)
        except Exception as e:
            logger.error(f"Erreur lors du calcul du CA mensuel : {e}")
            return 0.0
    
    @staticmethod
    def generate_receipt_pdf(payment_id: int) -> tuple[bool, str]:
        """
        Générer un reçu PDF professionnel pour un paiement
        
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
                'description': payment.description or 'Paiement formation',
                'validated_by': payment.validated_by or 'Administration',
            }
            
            # Générer le PDF professionnel avec ReportLab
            from src.utils.pdf_generator import get_pdf_generator
            pdf_gen = get_pdf_generator()
            return pdf_gen.generate_professional_receipt(receipt_data)
            
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
        Mettre à jour un paiement avec synchronisation du solde
        
        Args:
            payment_id: ID du paiement
            **kwargs: Champs à mettre à jour
        
        Returns:
            Tuple (success, message)
        """
        session = get_session()
        try:
            payment = session.query(Payment).filter(Payment.id == payment_id).first()
            
            if not payment:
                return False, "Paiement introuvable"
            
            # Vérifier si le paiement est annulé
            if payment.is_cancelled:
                return False, "Impossible de modifier un paiement annulé"
            
            # TRAITEMENT SPÉCIAL POUR LE MONTANT (pour éviter double ajustement)
            new_amount = kwargs.pop('amount', None)
            
            if new_amount is not None:
                # Validation du nouveau montant
                if new_amount <= 0:
                    return False, "Le montant doit être positif"
                if new_amount > MAX_AMOUNT:
                    return False, f"Le montant ne peut pas dépasser {MAX_AMOUNT:,.2f} DH"
                
                # Arrondir
                new_amount = round(float(new_amount), 2)
                
                # Calculer la différence
                old_amount = float(payment.amount)
                difference = new_amount - old_amount
                
                # Synchroniser le solde de l'élève SI différence non nulle
                if difference != 0 and payment.student:
                    payment.student.add_payment(difference)
                    logger.info(f"Solde élève {payment.student.id} ajusté de {difference:+.2f} DH")
                
                # Appliquer le nouveau montant
                payment.amount = Decimal(str(new_amount))
            
            # Mettre à jour les autres champs
            for key, value in kwargs.items():
                if hasattr(payment, key):
                    setattr(payment, key, value)
            
            session.commit()
            
            # Rafraîchir les objets
            session.refresh(payment)
            if payment.student:
                session.refresh(payment.student)
            
            logger.info(f"Paiement {payment_id} mis à jour avec succès")
            return True, "Paiement mis à jour avec succès"
            
        except Exception as e:
            session.rollback()
            # Rafraîchir pour annuler les modifications
            try:
                session.refresh(payment)
                if payment.student:
                    session.refresh(payment.student)
            except:
                pass
            error_msg = f"Erreur lors de la mise à jour du paiement : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def cancel_payment(payment_id: int, reason: str = "") -> tuple[bool, str]:
        """
        Annuler un paiement (utilise correctement is_cancelled)
        
        Args:
            payment_id: ID du paiement
            reason: Raison de l'annulation (OBLIGATOIRE)
        
        Returns:
            Tuple (success, message)
        """
        session = get_session()
        try:
            payment = session.query(Payment).filter(Payment.id == payment_id).first()
            
            if not payment:
                return False, "Paiement introuvable"
            
            # Vérifier si déjà annulé
            if payment.is_cancelled:
                return False, "Ce paiement est déjà annulé"
            
            # Exiger une raison
            if not reason or reason.strip() == "":
                return False, "Une raison d'annulation est obligatoire"
            
            old_amount = float(payment.amount)
            
            # Utiliser la méthode cancel() du modèle (correctement!)
            payment.cancel(reason)
            
            # Synchroniser le solde de l'élève (retirer le paiement)
            if payment.student:
                payment.student.add_payment(-old_amount)
                logger.info(f"Solde élève {payment.student.id} ajusté de {-old_amount:.2f} DH")
            
            session.commit()
            
            # Rafraîchir
            session.refresh(payment)
            if payment.student:
                session.refresh(payment.student)
            
            logger.warning(f"Paiement {payment_id} annulé par raison: {reason}")
            return True, "Paiement annulé avec succès"
            
        except Exception as e:
            session.rollback()
            # Rafraîchir pour annuler les modifications
            try:
                session.refresh(payment)
                if payment.student:
                    session.refresh(payment.student)
            except:
                pass
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
        Obtenir les statistiques de paiements (EXCLUT les paiements annulés)
        
        Args:
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
        
        Returns:
            Dictionnaire de statistiques
        """
        try:
            session = get_session()
            query = session.query(Payment).filter(Payment.is_cancelled == False)  # IMPORTANT
            
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
                    'by_method': {},
                    'validated_count': 0,
                    'pending_count': 0,
                    'cancelled_count': 0
                }
            
            total = len(payments)
            total_amount = sum(float(p.amount) for p in payments)
            average_amount = total_amount / total if total > 0 else 0.0
            
            # Statistiques par méthode de paiement
            by_method = {}
            for method in PaymentMethod:
                method_payments = [p for p in payments if p.payment_method == method]
                if method_payments:
                    by_method[method.value] = {
                        'count': len(method_payments),
                        'amount': round(sum(float(p.amount) for p in method_payments), 2)
                    }
            
            # Compter aussi les annulés (pour info)
            all_payments_query = session.query(Payment)
            if start_date:
                all_payments_query = all_payments_query.filter(Payment.payment_date >= start_date)
            if end_date:
                all_payments_query = all_payments_query.filter(Payment.payment_date <= end_date)
            cancelled_count = all_payments_query.filter(Payment.is_cancelled == True).count()
            
            return {
                'total_payments': total,
                'total_amount': round(total_amount, 2),
                'average_amount': round(average_amount, 2),
                'by_method': by_method,
                'validated_count': len([p for p in payments if p.is_validated]),
                'pending_count': len([p for p in payments if not p.is_validated and not p.is_cancelled]),
                'cancelled_count': cancelled_count
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
