"""
Validateurs communs pour l'application
Phase 4 - Validations complètes
"""

import re
from datetime import datetime, date
from typing import Optional, Tuple


class ValidationResult:
    """Résultat d'une validation"""
    
    def __init__(self, is_valid: bool, error_message: str = ""):
        self.is_valid = is_valid
        self.error_message = error_message
    
    def __bool__(self):
        return self.is_valid
    
    def __str__(self):
        return self.error_message if not self.is_valid else "Validation réussie"


class CommonValidators:
    """Validateurs communs réutilisables"""
    
    @staticmethod
    def validate_required(value: any, field_name: str = "Ce champ") -> ValidationResult:
        """Valider qu'un champ n'est pas vide"""
        if value is None or (isinstance(value, str) and not value.strip()):
            return ValidationResult(False, f"{field_name} est obligatoire")
        return ValidationResult(True)
    
    @staticmethod
    def validate_email(email: str) -> ValidationResult:
        """Valider un email"""
        if not email:
            return ValidationResult(False, "L'email est obligatoire")
        
        # Pattern regex pour email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return ValidationResult(False, "Format d'email invalide")
        
        return ValidationResult(True)
    
    @staticmethod
    def validate_phone(phone: str) -> ValidationResult:
        """Valider un numéro de téléphone marocain"""
        if not phone:
            return ValidationResult(False, "Le téléphone est obligatoire")
        
        # Nettoyer le numéro
        cleaned = re.sub(r'[\s\-\.]', '', phone)
        
        # Formats acceptés: 0612345678, +212612345678, 00212612345678
        patterns = [
            r'^0[5-7]\d{8}$',  # 0612345678
            r'^\+212[5-7]\d{8}$',  # +212612345678
            r'^00212[5-7]\d{8}$'  # 00212612345678
        ]
        
        for pattern in patterns:
            if re.match(pattern, cleaned):
                return ValidationResult(True)
        
        return ValidationResult(False, "Format de téléphone invalide (ex: 0612345678)")
    
    @staticmethod
    def validate_cin(cin: str) -> ValidationResult:
        """Valider une CIN marocaine"""
        if not cin:
            return ValidationResult(False, "La CIN est obligatoire")
        
        # CIN: 1-2 lettres + 6-7 chiffres (ex: AB123456)
        cleaned = cin.upper().strip()
        
        patterns = [
            r'^[A-Z]{1,2}\d{6,7}$',  # Format standard
            r'^\d{6,7}$'  # Ancien format (uniquement chiffres)
        ]
        
        for pattern in patterns:
            if re.match(pattern, cleaned):
                return ValidationResult(True)
        
        return ValidationResult(False, "Format de CIN invalide (ex: AB123456)")
    
    @staticmethod
    def validate_license_number(license_num: str) -> ValidationResult:
        """Valider un numéro de permis"""
        if not license_num:
            return ValidationResult(False, "Le numéro de permis est obligatoire")
        
        # Permis: généralement alphanumérique
        cleaned = license_num.strip()
        
        if len(cleaned) < 5:
            return ValidationResult(False, "Numéro de permis trop court (min 5 caractères)")
        
        if len(cleaned) > 20:
            return ValidationResult(False, "Numéro de permis trop long (max 20 caractères)")
        
        return ValidationResult(True)
    
    @staticmethod
    def validate_immatriculation(immat: str) -> ValidationResult:
        """Valider une immatriculation de véhicule"""
        if not immat:
            return ValidationResult(False, "L'immatriculation est obligatoire")
        
        # Formats marocains:
        # Ancien: 12345-أ-67 ou 12345-A-67
        # Nouveau: 12345-أ-67 ou A-12345-B
        cleaned = immat.upper().strip()
        
        if len(cleaned) < 5:
            return ValidationResult(False, "Immatriculation trop courte")
        
        if len(cleaned) > 20:
            return ValidationResult(False, "Immatriculation trop longue")
        
        return ValidationResult(True)
    
    @staticmethod
    def validate_positive_number(value: float, field_name: str = "Ce montant") -> ValidationResult:
        """Valider un nombre positif"""
        try:
            num = float(value)
            if num < 0:
                return ValidationResult(False, f"{field_name} doit être positif")
            return ValidationResult(True)
        except (ValueError, TypeError):
            return ValidationResult(False, f"{field_name} doit être un nombre valide")
    
    @staticmethod
    def validate_positive_integer(value: int, field_name: str = "Cette valeur") -> ValidationResult:
        """Valider un entier positif"""
        try:
            num = int(value)
            if num < 0:
                return ValidationResult(False, f"{field_name} doit être positif")
            return ValidationResult(True)
        except (ValueError, TypeError):
            return ValidationResult(False, f"{field_name} doit être un entier valide")
    
    @staticmethod
    def validate_date_not_future(date_value: date, field_name: str = "Cette date") -> ValidationResult:
        """Valider qu'une date n'est pas dans le futur"""
        if not date_value:
            return ValidationResult(False, f"{field_name} est obligatoire")
        
        if date_value > date.today():
            return ValidationResult(False, f"{field_name} ne peut pas être dans le futur")
        
        return ValidationResult(True)
    
    @staticmethod
    def validate_date_not_past(date_value: date, field_name: str = "Cette date") -> ValidationResult:
        """Valider qu'une date n'est pas dans le passé"""
        if not date_value:
            return ValidationResult(False, f"{field_name} est obligatoire")
        
        if date_value < date.today():
            return ValidationResult(False, f"{field_name} ne peut pas être dans le passé")
        
        return ValidationResult(True)
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date) -> ValidationResult:
        """Valider qu'une plage de dates est cohérente"""
        if not start_date or not end_date:
            return ValidationResult(False, "Les deux dates sont obligatoires")
        
        if start_date > end_date:
            return ValidationResult(False, "La date de début doit être avant la date de fin")
        
        return ValidationResult(True)
    
    @staticmethod
    def validate_min_age(birth_date: date, min_age: int = 18) -> ValidationResult:
        """Valider l'âge minimum"""
        if not birth_date:
            return ValidationResult(False, "La date de naissance est obligatoire")
        
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        if age < min_age:
            return ValidationResult(False, f"Âge minimum requis: {min_age} ans")
        
        return ValidationResult(True)
    
    @staticmethod
    def validate_string_length(value: str, min_len: int = None, max_len: int = None, 
                              field_name: str = "Ce champ") -> ValidationResult:
        """Valider la longueur d'une chaîne"""
        if not value:
            return ValidationResult(False, f"{field_name} est obligatoire")
        
        length = len(value.strip())
        
        if min_len and length < min_len:
            return ValidationResult(False, f"{field_name} doit contenir au moins {min_len} caractères")
        
        if max_len and length > max_len:
            return ValidationResult(False, f"{field_name} ne peut pas dépasser {max_len} caractères")
        
        return ValidationResult(True)
