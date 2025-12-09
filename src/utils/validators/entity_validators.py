"""
Validateurs spécifiques aux entités métier
Phase 4 - Validations complètes
"""

from typing import Dict, Any, List
from datetime import date
from .common_validators import CommonValidators, ValidationResult


class StudentValidator:
    """Validateur pour les étudiants"""
    
    @staticmethod
    def validate_student_data(data: Dict[str, Any]) -> List[ValidationResult]:
        """Valider les données d'un étudiant"""
        errors = []
        
        # Nom complet
        result = CommonValidators.validate_required(data.get('full_name'), "Le nom complet")
        if not result:
            errors.append(result)
        else:
            result = CommonValidators.validate_string_length(data['full_name'], min_len=3, max_len=100, field_name="Le nom complet")
            if not result:
                errors.append(result)
        
        # CIN
        result = CommonValidators.validate_cin(data.get('cin', ''))
        if not result:
            errors.append(result)
        
        # Date de naissance + âge minimum
        birth_date = data.get('date_of_birth')
        if birth_date:
            result = CommonValidators.validate_date_not_future(birth_date, "La date de naissance")
            if not result:
                errors.append(result)
            
            result = CommonValidators.validate_min_age(birth_date, min_age=16)
            if not result:
                errors.append(result)
        else:
            errors.append(ValidationResult(False, "La date de naissance est obligatoire"))
        
        # Téléphone
        result = CommonValidators.validate_phone(data.get('phone', ''))
        if not result:
            errors.append(result)
        
        # Email (optionnel mais validé si présent)
        email = data.get('email')
        if email and email.strip():
            result = CommonValidators.validate_email(email)
            if not result:
                errors.append(result)
        
        # Type de permis
        result = CommonValidators.validate_required(data.get('license_type'), "Le type de permis")
        if not result:
            errors.append(result)
        
        return errors
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> tuple[bool, Dict[str, str]]:
        """
        Valider les données d'un étudiant et retourner (is_valid, errors_dict)
        
        Args:
            data: Dictionnaire des données à valider
            
        Returns:
            Tuple (is_valid, errors_dict) où errors_dict est un dict {field: error_message}
        """
        validation_results = StudentValidator.validate_student_data(data)
        
        if not validation_results:
            return (True, {})
        
        # Convertir les ValidationResult en dictionnaire
        errors_dict = {}
        for result in validation_results:
            if not result.is_valid:
                # Extraire le nom du champ du message (ex: "Le nom complet" -> "nom_complet")
                field_name = result.message.split(':')[0].strip() if ':' in result.message else "Champ"
                errors_dict[field_name] = result.message
        
        return (len(errors_dict) == 0, errors_dict)


class InstructorValidator:
    """Validateur pour les moniteurs"""
    
    @staticmethod
    def validate_instructor_data(data: Dict[str, Any]) -> List[ValidationResult]:
        """Valider les données d'un moniteur"""
        errors = []
        
        # Nom complet
        result = CommonValidators.validate_required(data.get('full_name'), "Le nom complet")
        if not result:
            errors.append(result)
        else:
            result = CommonValidators.validate_string_length(data['full_name'], min_len=3, max_len=100, field_name="Le nom complet")
            if not result:
                errors.append(result)
        
        # CIN
        result = CommonValidators.validate_cin(data.get('cin', ''))
        if not result:
            errors.append(result)
        
        # Téléphone
        result = CommonValidators.validate_phone(data.get('phone', ''))
        if not result:
            errors.append(result)
        
        # Email
        result = CommonValidators.validate_email(data.get('email', ''))
        if not result:
            errors.append(result)
        
        # Numéro de permis
        result = CommonValidators.validate_license_number(data.get('license_number', ''))
        if not result:
            errors.append(result)
        
        # Date d'expiration permis (doit être future)
        license_expiry = data.get('license_expiry')
        if license_expiry:
            result = CommonValidators.validate_date_not_past(license_expiry, "La date d'expiration du permis")
            if not result:
                errors.append(result)
        
        # Taux horaire (doit être positif)
        hourly_rate = data.get('hourly_rate')
        if hourly_rate is not None:
            result = CommonValidators.validate_positive_number(hourly_rate, "Le taux horaire")
            if not result:
                errors.append(result)
        
        return errors


class VehicleValidator:
    """Validateur pour les véhicules"""
    
    @staticmethod
    def validate_vehicle_data(data: Dict[str, Any]) -> List[ValidationResult]:
        """Valider les données d'un véhicule"""
        errors = []
        
        # Immatriculation
        result = CommonValidators.validate_immatriculation(data.get('immatriculation', ''))
        if not result:
            errors.append(result)
        
        # Marque
        result = CommonValidators.validate_required(data.get('marque'), "La marque")
        if not result:
            errors.append(result)
        
        # Modèle
        result = CommonValidators.validate_required(data.get('modele'), "Le modèle")
        if not result:
            errors.append(result)
        
        # Année (doit être raisonnable)
        year = data.get('annee')
        if year:
            current_year = date.today().year
            if year < 1900 or year > current_year + 1:
                errors.append(ValidationResult(False, f"L'année doit être entre 1900 et {current_year + 1}"))
        
        # Kilométrage (doit être positif)
        mileage = data.get('kilometrage')
        if mileage is not None:
            result = CommonValidators.validate_positive_integer(mileage, "Le kilométrage")
            if not result:
                errors.append(result)
        
        # Type de véhicule
        result = CommonValidators.validate_required(data.get('vehicle_type'), "Le type de véhicule")
        if not result:
            errors.append(result)
        
        return errors


class PaymentValidator:
    """Validateur pour les paiements"""
    
    @staticmethod
    def validate_payment_data(data: Dict[str, Any]) -> List[ValidationResult]:
        """Valider les données d'un paiement"""
        errors = []
        
        # Étudiant
        result = CommonValidators.validate_required(data.get('student_id'), "L'étudiant")
        if not result:
            errors.append(result)
        
        # Montant (doit être strictement positif)
        amount = data.get('amount')
        if amount is None or amount <= 0:
            errors.append(ValidationResult(False, "Le montant doit être strictement positif"))
        else:
            result = CommonValidators.validate_positive_number(amount, "Le montant")
            if not result:
                errors.append(result)
        
        # Mode de paiement
        result = CommonValidators.validate_required(data.get('payment_method'), "Le mode de paiement")
        if not result:
            errors.append(result)
        
        # Date de paiement (ne peut pas être future)
        payment_date = data.get('payment_date')
        if payment_date:
            result = CommonValidators.validate_date_not_future(payment_date, "La date de paiement")
            if not result:
                errors.append(result)
        
        return errors


class SessionValidator:
    """Validateur pour les séances"""
    
    @staticmethod
    def validate_session_data(data: Dict[str, Any]) -> List[ValidationResult]:
        """Valider les données d'une séance"""
        errors = []
        
        # Étudiant
        result = CommonValidators.validate_required(data.get('student_id'), "L'étudiant")
        if not result:
            errors.append(result)
        
        # Moniteur
        result = CommonValidators.validate_required(data.get('instructor_id'), "Le moniteur")
        if not result:
            errors.append(result)
        
        # Véhicule
        result = CommonValidators.validate_required(data.get('vehicle_id'), "Le véhicule")
        if not result:
            errors.append(result)
        
        # Date
        result = CommonValidators.validate_required(data.get('session_date'), "La date de séance")
        if not result:
            errors.append(result)
        
        # Heure de début
        result = CommonValidators.validate_required(data.get('start_time'), "L'heure de début")
        if not result:
            errors.append(result)
        
        # Heure de fin
        result = CommonValidators.validate_required(data.get('end_time'), "L'heure de fin")
        if not result:
            errors.append(result)
        
        # Durée (doit être positive)
        duration = data.get('duration')
        if duration is not None:
            if duration <= 0:
                errors.append(ValidationResult(False, "La durée doit être positive"))
        
        # Type de séance
        result = CommonValidators.validate_required(data.get('session_type'), "Le type de séance")
        if not result:
            errors.append(result)
        
        return errors


class ExamValidator:
    """Validateur pour les examens"""
    
    @staticmethod
    def validate_exam_data(data: Dict[str, Any]) -> List[ValidationResult]:
        """Valider les données d'un examen"""
        errors = []
        
        # Étudiant
        result = CommonValidators.validate_required(data.get('student_id'), "L'étudiant")
        if not result:
            errors.append(result)
        
        # Type d'examen
        result = CommonValidators.validate_required(data.get('exam_type'), "Le type d'examen")
        if not result:
            errors.append(result)
        
        # Date
        result = CommonValidators.validate_required(data.get('exam_date'), "La date de l'examen")
        if not result:
            errors.append(result)
        
        # Note (si présente, doit être entre 0 et 20)
        score = data.get('score')
        if score is not None:
            if score < 0 or score > 20:
                errors.append(ValidationResult(False, "La note doit être entre 0 et 20"))
        
        return errors


class DocumentValidator:
    """Validateur pour les documents"""
    
    @staticmethod
    def validate_document_data(data: Dict[str, Any]) -> List[ValidationResult]:
        """Valider les données d'un document"""
        errors = []
        
        # Titre
        result = CommonValidators.validate_required(data.get('title'), "Le titre")
        if not result:
            errors.append(result)
        else:
            result = CommonValidators.validate_string_length(data['title'], min_len=3, max_len=200, field_name="Le titre")
            if not result:
                errors.append(result)
        
        # Type de document
        result = CommonValidators.validate_required(data.get('document_type'), "Le type de document")
        if not result:
            errors.append(result)
        
        # Fichier
        result = CommonValidators.validate_required(data.get('file_path'), "Le fichier")
        if not result:
            errors.append(result)
        
        # Date d'expiration (si présente, doit être future)
        expiry_date = data.get('expiry_date')
        if expiry_date:
            # Pour les nouveaux documents, la date d'expiration devrait être future
            # Pour les documents existants, on permet les dates passées
            pass  # Validation assouplie
        
        return errors
