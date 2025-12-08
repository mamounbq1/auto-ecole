# 🛠️ TEMPLATES POUR HARMONISATION - GUIDE D'IMPLÉMENTATION

> **Guide pratique** : Templates de code prêts à l'emploi pour harmoniser tous les contrôleurs.

---

## 📋 SOMMAIRE

1. [Template Contrôleur Standard](#template-contrôleur-standard)
2. [Template Validation](#template-validation)
3. [Template Export/Import](#template-exportimport)
4. [Template Recherche Avancée](#template-recherche-avancée)
5. [Template PDF Documents](#template-pdf-documents)
6. [Checklist d'implémentation](#checklist-dimplémentation)

---

## 1. Template Contrôleur Standard

### 🎯 Objectif
Standardiser TOUS les contrôleurs avec les mêmes méthodes de base.

### 📝 Template complet (ExamController modernisé)

```python
"""
Contrôleur pour la gestion des examens
Version harmonisée avec CRUD complet
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime

from sqlalchemy import or_, and_, extract
from src.models import Exam, ExamType, ExamResult, Student, get_session
from src.utils import get_logger, export_to_csv, import_from_csv
from src.utils.validators import DataValidator

logger = get_logger()


class ExamController:
    """Contrôleur harmonisé pour gérer les opérations sur les examens"""
    
    # ========== MÉTHODES CRUD DE BASE ==========
    
    @staticmethod
    def get_all_exams(filters: Optional[Dict[str, Any]] = None) -> List[Exam]:
        """
        Récupérer tous les examens avec filtres optionnels
        
        Args:
            filters: {
                'exam_type': ExamType,
                'result': ExamResult,
                'student_id': int,
                'date_start': date,
                'date_end': date,
                'is_official': bool
            }
        
        Returns:
            Liste des examens
        """
        try:
            session = get_session()
            query = session.query(Exam)
            
            # Appliquer les filtres
            if filters:
                if filters.get('exam_type'):
                    query = query.filter(Exam.exam_type == filters['exam_type'])
                if filters.get('result'):
                    query = query.filter(Exam.result == filters['result'])
                if filters.get('student_id'):
                    query = query.filter(Exam.student_id == filters['student_id'])
                if filters.get('date_start'):
                    query = query.filter(Exam.scheduled_date >= filters['date_start'])
                if filters.get('date_end'):
                    query = query.filter(Exam.scheduled_date <= filters['date_end'])
                if filters.get('is_official') is not None:
                    query = query.filter(Exam.is_official == filters['is_official'])
            
            exams = query.order_by(Exam.scheduled_date.desc()).all()
            logger.info(f"Récupération de {len(exams)} examens avec filtres : {filters}")
            return exams
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des examens : {e}")
            return []
    
    @staticmethod
    def get_exam_by_id(exam_id: int) -> Optional[Exam]:
        """
        Récupérer un examen par son ID
        
        Args:
            exam_id: ID de l'examen
        
        Returns:
            Examen ou None
        """
        try:
            session = get_session()
            exam = session.query(Exam).filter(Exam.id == exam_id).first()
            if not exam:
                logger.warning(f"Examen {exam_id} introuvable")
            return exam
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'examen {exam_id} : {e}")
            return None
    
    @staticmethod
    def search_exams(query: str) -> List[Exam]:
        """
        Rechercher des examens par élève, centre, ou examinateur
        
        Args:
            query: Terme de recherche
        
        Returns:
            Liste des examens correspondants
        """
        try:
            session = get_session()
            search_term = f"%{query}%"
            
            # Recherche dans plusieurs champs + jointure avec Student
            exams = session.query(Exam).join(Student).filter(
                or_(
                    Student.full_name.like(search_term),
                    Student.cin.like(search_term),
                    Exam.exam_center.like(search_term),
                    Exam.examiner_name.like(search_term),
                    Exam.location.like(search_term)
                )
            ).order_by(Exam.scheduled_date.desc()).all()
            
            logger.info(f"Recherche '{query}' : {len(exams)} résultats")
            return exams
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'examens : {e}")
            return []
    
    @staticmethod
    def create_exam(exam_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Exam]]:
        """
        Créer un nouvel examen
        
        Args:
            exam_data: Données de l'examen {
                'student_id': int,
                'exam_type': ExamType,
                'scheduled_date': date,
                'location': str,
                'exam_center': str,
                'examiner_name': str (optionnel),
                'is_official': bool,
                'registration_fee': float (optionnel)
            }
        
        Returns:
            Tuple (success, message, exam)
        """
        try:
            session = get_session()
            
            # Validation : vérifier que l'élève existe
            student = session.query(Student).filter(
                Student.id == exam_data['student_id']
            ).first()
            if not student:
                return False, "Élève introuvable", None
            
            # Validation : vérifier que la date n'est pas dans le passé
            if exam_data['scheduled_date'] < date.today():
                return False, "La date d'examen ne peut pas être dans le passé", None
            
            # Créer l'examen
            exam = Exam(**exam_data)
            
            # Générer automatiquement le numéro de convocation si officiel
            if exam_data.get('is_official', False):
                exam.summons_number = exam.generate_summons_number()
            
            session.add(exam)
            session.commit()
            session.refresh(exam)
            
            logger.info(f"Examen créé : ID {exam.id} pour {student.full_name}")
            return True, "Examen créé avec succès", exam
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la création de l'examen : {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def update_exam(exam_id: int, exam_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Exam]]:
        """
        Mettre à jour un examen
        
        Args:
            exam_id: ID de l'examen
            exam_data: Nouvelles données
        
        Returns:
            Tuple (success, message, exam)
        """
        try:
            session = get_session()
            exam = session.query(Exam).filter(Exam.id == exam_id).first()
            
            if not exam:
                return False, "Examen introuvable", None
            
            # Vérifier qu'on ne peut pas modifier un examen déjà complété
            if exam.completion_date and 'result' not in exam_data:
                return False, "Impossible de modifier un examen déjà terminé", None
            
            # Mettre à jour les attributs
            for key, value in exam_data.items():
                if hasattr(exam, key) and key != 'id':
                    setattr(exam, key, value)
            
            session.commit()
            session.refresh(exam)
            
            logger.info(f"Examen {exam_id} mis à jour")
            return True, "Examen mis à jour avec succès", exam
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la mise à jour de l'examen : {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def delete_exam(exam_id: int) -> Tuple[bool, str]:
        """
        Supprimer un examen
        
        Args:
            exam_id: ID de l'examen
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            exam = session.query(Exam).filter(Exam.id == exam_id).first()
            
            if not exam:
                return False, "Examen introuvable"
            
            # Vérifier qu'on ne peut pas supprimer un examen déjà passé
            if exam.completion_date:
                return False, "Impossible de supprimer un examen déjà passé"
            
            student_name = exam.student.full_name
            session.delete(exam)
            session.commit()
            
            logger.info(f"Examen supprimé : ID {exam_id} pour {student_name}")
            return True, "Examen supprimé avec succès"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de la suppression de l'examen : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    # ========== MÉTHODES MÉTIER SPÉCIFIQUES ==========
    
    @staticmethod
    def record_exam_result(exam_id: int, result: ExamResult, 
                          score: Optional[float] = None,
                          notes: Optional[str] = None) -> Tuple[bool, str]:
        """
        Enregistrer le résultat d'un examen
        
        Args:
            exam_id: ID de l'examen
            result: Résultat (PASSED, FAILED, ABSENT)
            score: Score obtenu (pour théorique)
            notes: Observations de l'examinateur
        
        Returns:
            Tuple (success, message)
        """
        try:
            session = get_session()
            exam = session.query(Exam).filter(Exam.id == exam_id).first()
            
            if not exam:
                return False, "Examen introuvable"
            
            # Enregistrer le résultat
            exam.record_result(result, score)
            
            if notes:
                exam.notes = notes
            
            session.commit()
            
            logger.info(f"Résultat enregistré pour examen {exam_id} : {result.value}")
            return True, "Résultat enregistré avec succès"
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lors de l'enregistrement du résultat : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def get_upcoming_exams(days: int = 7) -> List[Exam]:
        """
        Obtenir les examens à venir dans les N prochains jours
        
        Args:
            days: Nombre de jours à regarder (défaut 7)
        
        Returns:
            Liste des examens à venir
        """
        try:
            from datetime import timedelta
            session = get_session()
            today = date.today()
            future_date = today + timedelta(days=days)
            
            exams = session.query(Exam).filter(
                Exam.scheduled_date >= today,
                Exam.scheduled_date <= future_date,
                Exam.result == ExamResult.PENDING
            ).order_by(Exam.scheduled_date).all()
            
            logger.info(f"{len(exams)} examens à venir dans les {days} prochains jours")
            return exams
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des examens à venir : {e}")
            return []
    
    @staticmethod
    def get_failed_exams_for_retry(student_id: Optional[int] = None) -> List[Exam]:
        """
        Obtenir les examens échoués nécessitant une réinscription
        
        Args:
            student_id: Filtrer par élève (optionnel)
        
        Returns:
            Liste des examens échoués
        """
        try:
            session = get_session()
            query = session.query(Exam).filter(Exam.result == ExamResult.FAILED)
            
            if student_id:
                query = query.filter(Exam.student_id == student_id)
            
            exams = query.order_by(Exam.completion_date.desc()).all()
            return exams
            
        except Exception as e:
            logger.error(f"Erreur : {e}")
            return []
    
    # ========== MÉTHODES D'EXPORT/IMPORT ==========
    
    @staticmethod
    def export_exams_to_csv(exams: List[Exam], filename: str = "examens") -> Tuple[bool, str]:
        """
        Exporter les examens vers un fichier CSV
        
        Args:
            exams: Liste des examens
            filename: Nom du fichier
        
        Returns:
            Tuple (success, filepath_or_error)
        """
        try:
            # Transformer en dictionnaires avec informations élève
            data = []
            for exam in exams:
                exam_dict = {
                    'id': exam.id,
                    'eleve_nom': exam.student.full_name if exam.student else '',
                    'eleve_cin': exam.student.cin if exam.student else '',
                    'type_examen': exam.exam_type.value,
                    'resultat': exam.result.value,
                    'date_prevue': exam.scheduled_date.strftime('%Y-%m-%d'),
                    'date_passage': exam.completion_date.strftime('%Y-%m-%d') if exam.completion_date else '',
                    'lieu': exam.location or '',
                    'centre': exam.exam_center or '',
                    'examinateur': exam.examiner_name or '',
                    'note': exam.theory_score if exam.exam_type == ExamType.THEORETICAL else '',
                    'tentative': exam.attempt_number,
                    'officiel': 'Oui' if exam.is_official else 'Non',
                    'frais': exam.registration_fee or 0
                }
                data.append(exam_dict)
            
            return export_to_csv(data, filename)
            
        except Exception as e:
            error_msg = f"Erreur lors de l'export : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def generate_statistics(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Générer des statistiques sur les examens
        
        Args:
            filters: Filtres de période/type
        
        Returns:
            Dictionnaire de statistiques {
                'total': int,
                'reussis': int,
                'echoues': int,
                'absents': int,
                'en_attente': int,
                'taux_reussite': float,
                'moyenne_score_theorique': float
            }
        """
        try:
            session = get_session()
            exams = ExamController.get_all_exams(filters)
            
            stats = {
                'total': len(exams),
                'reussis': sum(1 for e in exams if e.result == ExamResult.PASSED),
                'echoues': sum(1 for e in exams if e.result == ExamResult.FAILED),
                'absents': sum(1 for e in exams if e.result == ExamResult.ABSENT),
                'en_attente': sum(1 for e in exams if e.result == ExamResult.PENDING),
            }
            
            # Taux de réussite (exclure absents et en attente)
            completed = stats['reussis'] + stats['echoues']
            stats['taux_reussite'] = (stats['reussis'] / completed * 100) if completed > 0 else 0
            
            # Moyenne des scores théoriques
            theory_scores = [e.theory_score for e in exams 
                           if e.exam_type == ExamType.THEORETICAL and e.theory_score]
            stats['moyenne_score_theorique'] = (
                sum(theory_scores) / len(theory_scores) if theory_scores else 0
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques : {e}")
            return {}
```

### 🎯 Utilisation du template

Pour harmoniser un autre contrôleur, copier la structure ci-dessus et adapter :
1. Remplacer `Exam` par le modèle cible (`Instructor`, `Vehicle`, etc.)
2. Adapter les champs de `filters` dans `get_all_*()`
3. Adapter les champs de recherche dans `search_*()`
4. Ajouter les validations métier dans `create_*()` et `update_*()`
5. Adapter les champs d'export dans `export_*_to_csv()`

---

## 2. Template Validation

### 📝 Créer le fichier `src/utils/validators.py`

```python
"""
Module de validation des données
Centralise toutes les règles de validation métier
"""

import re
from datetime import date, datetime
from typing import Tuple


class DataValidator:
    """Validateur de données avec règles métier"""
    
    # ========== VALIDATION IDENTITÉ ==========
    
    @staticmethod
    def validate_cin(cin: str) -> Tuple[bool, str]:
        """
        Valide le format du CIN marocain
        
        Format attendu : 1-2 lettres + 5-7 chiffres (ex: AB123456, A12345)
        
        Args:
            cin: Numéro CIN
        
        Returns:
            Tuple (is_valid, error_message)
        """
        if not cin or not isinstance(cin, str):
            return False, "CIN requis"
        
        cin_upper = cin.strip().upper()
        
        if not re.match(r'^[A-Z]{1,2}\d{5,7}$', cin_upper):
            return False, "Format CIN invalide (ex: AB123456 ou A12345)"
        
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Valide le format du téléphone marocain
        
        Formats acceptés :
        - 0612345678
        - +212612345678
        - 06 12 34 56 78
        - +212 6 12 34 56 78
        
        Args:
            phone: Numéro de téléphone
        
        Returns:
            Tuple (is_valid, error_message)
        """
        if not phone or not isinstance(phone, str):
            return False, "Téléphone requis"
        
        # Nettoyer (supprimer espaces, tirets, underscores)
        clean_phone = re.sub(r'[\s\-_/()]', '', phone)
        
        # Vérifier format marocain
        pattern = r'^(\+212|00212|0)[5-7]\d{8}$'
        if not re.match(pattern, clean_phone):
            return False, "Format téléphone invalide (ex: 0612345678 ou +212612345678)"
        
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Valide le format d'email
        
        Args:
            email: Adresse email
        
        Returns:
            Tuple (is_valid, error_message)
        """
        if not email or not isinstance(email, str):
            return False, "Email requis"
        
        # Pattern simple mais robuste
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email.strip()):
            return False, "Format email invalide (ex: exemple@domaine.com)"
        
        return True, ""
    
    # ========== VALIDATION DATES ==========
    
    @staticmethod
    def validate_date_of_birth(dob: date, min_age: int = 16, max_age: int = 100) -> Tuple[bool, str]:
        """
        Valide une date de naissance
        
        Args:
            dob: Date de naissance
            min_age: Âge minimum requis (défaut 16 ans)
            max_age: Âge maximum accepté (défaut 100 ans)
        
        Returns:
            Tuple (is_valid, error_message)
        """
        if not dob or not isinstance(dob, date):
            return False, "Date de naissance requise"
        
        if dob >= date.today():
            return False, "La date de naissance ne peut pas être dans le futur"
        
        age = (date.today() - dob).days // 365
        
        if age < min_age:
            return False, f"L'élève doit avoir au moins {min_age} ans"
        
        if age > max_age:
            return False, f"Date de naissance invalide (âge > {max_age} ans)"
        
        return True, ""
    
    @staticmethod
    def validate_future_date(target_date: date, allow_today: bool = True) -> Tuple[bool, str]:
        """
        Valide qu'une date est dans le futur
        
        Args:
            target_date: Date à valider
            allow_today: Autoriser la date du jour (défaut True)
        
        Returns:
            Tuple (is_valid, error_message)
        """
        if not target_date or not isinstance(target_date, date):
            return False, "Date requise"
        
        today = date.today()
        
        if allow_today:
            if target_date < today:
                return False, "La date ne peut pas être dans le passé"
        else:
            if target_date <= today:
                return False, "La date doit être dans le futur"
        
        return True, ""
    
    # ========== VALIDATION MONTANTS ==========
    
    @staticmethod
    def validate_amount(amount: float, min_value: float = 0, max_value: float = 100000) -> Tuple[bool, str]:
        """
        Valide un montant financier
        
        Args:
            amount: Montant à valider
            min_value: Valeur minimum (défaut 0)
            max_value: Valeur maximum (défaut 100000)
        
        Returns:
            Tuple (is_valid, error_message)
        """
        if amount is None:
            return False, "Montant requis"
        
        try:
            amount_float = float(amount)
        except (ValueError, TypeError):
            return False, "Le montant doit être un nombre"
        
        if amount_float < min_value:
            return False, f"Le montant doit être supérieur ou égal à {min_value}"
        
        if amount_float > max_value:
            return False, f"Le montant doit être inférieur ou égal à {max_value}"
        
        return True, ""
    
    # ========== VALIDATION VÉHICULES ==========
    
    @staticmethod
    def validate_plate_number(plate: str) -> Tuple[bool, str]:
        """
        Valide une plaque d'immatriculation marocaine
        
        Formats acceptés :
        - 12345-أ-16 (nouveau format)
        - 12345-A-16 (translittération)
        - A 12345 (ancien format)
        
        Args:
            plate: Numéro de plaque
        
        Returns:
            Tuple (is_valid, error_message)
        """
        if not plate or not isinstance(plate, str):
            return False, "Plaque d'immatriculation requise"
        
        plate_clean = plate.strip()
        
        # Format nouveau : 12345-A-16 ou 12345-أ-16
        pattern_new = r'^\d{4,5}[\-\s][A-Zأ-ي][\-\s]\d{1,2}$'
        # Format ancien : A 12345
        pattern_old = r'^[A-Z]\s?\d{4,6}$'
        
        if not (re.match(pattern_new, plate_clean, re.UNICODE) or re.match(pattern_old, plate_clean)):
            return False, "Format plaque invalide (ex: 12345-A-16 ou A 12345)"
        
        return True, ""
    
    @staticmethod
    def validate_vin(vin: str) -> Tuple[bool, str]:
        """
        Valide un numéro VIN (Vehicle Identification Number)
        
        Format : 17 caractères alphanumériques (sans I, O, Q)
        
        Args:
            vin: Numéro VIN
        
        Returns:
            Tuple (is_valid, error_message)
        """
        if not vin or not isinstance(vin, str):
            return False, "VIN requis"
        
        vin_upper = vin.strip().upper()
        
        # VIN = 17 caractères alphanumériques (exclure I, O, Q pour éviter confusion)
        if len(vin_upper) != 17:
            return False, "Le VIN doit contenir exactement 17 caractères"
        
        if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin_upper):
            return False, "Format VIN invalide (17 caractères sans I, O, Q)"
        
        return True, ""
    
    # ========== VALIDATION PERMIS ==========
    
    @staticmethod
    def validate_license_number(license_num: str) -> Tuple[bool, str]:
        """
        Valide un numéro de permis de conduire
        
        Args:
            license_num: Numéro de permis
        
        Returns:
            Tuple (is_valid, error_message)
        """
        if not license_num or not isinstance(license_num, str):
            return False, "Numéro de permis requis"
        
        clean_num = license_num.strip()
        
        if len(clean_num) < 5:
            return False, "Numéro de permis trop court (minimum 5 caractères)"
        
        if len(clean_num) > 20:
            return False, "Numéro de permis trop long (maximum 20 caractères)"
        
        return True, ""
    
    # ========== MÉTHODE UTILITAIRE ==========
    
    @staticmethod
    def validate_required_fields(data: dict, required_fields: list) -> Tuple[bool, str]:
        """
        Valide que tous les champs requis sont présents et non vides
        
        Args:
            data: Dictionnaire de données
            required_fields: Liste des champs requis
        
        Returns:
            Tuple (is_valid, error_message)
        """
        missing = []
        for field in required_fields:
            if field not in data or not data[field]:
                missing.append(field)
        
        if missing:
            return False, f"Champs requis manquants : {', '.join(missing)}"
        
        return True, ""


# ========== EXEMPLE D'UTILISATION DANS UN CONTRÔLEUR ==========

# Dans StudentController.create_student()
"""
# Valider les données avant création
validator = DataValidator()

# Valider CIN
is_valid, error = validator.validate_cin(student_data['cin'])
if not is_valid:
    return False, error, None

# Valider téléphone
is_valid, error = validator.validate_phone(student_data['phone'])
if not is_valid:
    return False, error, None

# Valider date de naissance
is_valid, error = validator.validate_date_of_birth(student_data['date_of_birth'])
if not is_valid:
    return False, error, None

# Valider email (si fourni)
if student_data.get('email'):
    is_valid, error = validator.validate_email(student_data['email'])
    if not is_valid:
        return False, error, None

# Si toutes les validations passent, créer l'élève
student = Student(**student_data)
session.add(student)
session.commit()
"""
```

---

## 3. Template Export/Import

### 📝 Ajout méthode export dans `export.py`

```python
# Ajouter dans ExportManager :

def export_to_csv_with_center_header(self, data: List[Dict], filename: str, 
                                      fieldnames: Optional[List[str]] = None) -> tuple[bool, str]:
    """
    Exporter des données en CSV avec en-tête du centre (VERSION COMPLÈTE)
    
    Args:
        data: Liste de dictionnaires
        filename: Nom du fichier
        fieldnames: Noms des colonnes (optionnel)
    
    Returns:
        Tuple (success, filepath_or_error)
    """
    from src.utils.config_manager import ConfigManager
    
    try:
        config = ConfigManager()
        center = config.get_center_info()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(self.export_dir, f"{filename}_{timestamp}.csv")
        
        if not data:
            return False, "Aucune donnée à exporter"
        
        # Déterminer les noms de colonnes
        if not fieldnames:
            fieldnames = list(data[0].keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            # EN-TÊTE DU CENTRE (4 premières lignes)
            csvfile.write(f"# {center['name']}\n")
            csvfile.write(f"# {center['full_address']}\n")
            csvfile.write(f"# Tél: {center['phone']} | Email: {center['email']}\n")
            csvfile.write(f"# Exporté le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}\n")
            csvfile.write("\n")  # Ligne vide
            
            # DONNÉES CSV
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"Export CSV réussi : {filepath}")
        return True, filepath
        
    except Exception as e:
        error_msg = f"Erreur lors de l'export CSV : {str(e)}"
        logger.error(error_msg)
        return False, error_msg
```

---

## 4. Template Recherche Avancée

### 📝 Exemple pour PaymentController

```python
@staticmethod
def search_payments(query: str, filters: Optional[Dict[str, Any]] = None) -> List[Payment]:
    """
    Recherche avancée de paiements
    
    Args:
        query: Terme de recherche (nom élève, CIN, numéro reçu)
        filters: {
            'date_start': date,
            'date_end': date,
            'payment_method': PaymentMethod,
            'amount_min': float,
            'amount_max': float,
            'is_validated': bool
        }
    
    Returns:
        Liste des paiements correspondants
    """
    try:
        session = get_session()
        
        # Requête de base avec jointure sur Student
        query_db = session.query(Payment).join(Student)
        
        # Recherche textuelle
        if query:
            search_term = f"%{query}%"
            query_db = query_db.filter(
                or_(
                    Student.full_name.like(search_term),
                    Student.cin.like(search_term),
                    Payment.receipt_number.like(search_term),
                    Payment.reference_number.like(search_term)
                )
            )
        
        # Appliquer les filtres
        if filters:
            if filters.get('date_start'):
                query_db = query_db.filter(Payment.payment_date >= filters['date_start'])
            if filters.get('date_end'):
                query_db = query_db.filter(Payment.payment_date <= filters['date_end'])
            if filters.get('payment_method'):
                query_db = query_db.filter(Payment.payment_method == filters['payment_method'])
            if filters.get('amount_min'):
                query_db = query_db.filter(Payment.amount >= filters['amount_min'])
            if filters.get('amount_max'):
                query_db = query_db.filter(Payment.amount <= filters['amount_max'])
            if filters.get('is_validated') is not None:
                query_db = query_db.filter(Payment.is_validated == filters['is_validated'])
        
        payments = query_db.order_by(Payment.payment_date.desc()).all()
        logger.info(f"Recherche paiements : {len(payments)} résultats")
        return payments
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de paiements : {e}")
        return []
```

---

## 5. Template PDF Documents

### 📝 Exemple : Attestation de formation

```python
# Ajouter dans PDFGenerator :

def generate_training_certificate(self, student_id: int) -> tuple[bool, str]:
    """
    Générer une attestation de formation
    
    Args:
        student_id: ID de l'élève
    
    Returns:
        Tuple (success, filepath_or_error)
    """
    try:
        from src.controllers.student_controller import StudentController
        from src.controllers.session_controller import SessionController
        
        # Récupérer l'élève
        student = StudentController.get_student_by_id(student_id)
        if not student:
            return False, "Élève introuvable"
        
        # Récupérer toutes les sessions de l'élève
        sessions = SessionController.get_all_sessions()
        student_sessions = [s for s in sessions if s.student_id == student_id and s.status == SessionStatus.COMPLETED]
        
        # Calculer les heures par type
        hours_by_type = {}
        for session in student_sessions:
            session_type = session.session_type.value
            duration_hours = session.duration_minutes / 60
            hours_by_type[session_type] = hours_by_type.get(session_type, 0) + duration_hours
        
        # Créer le PDF
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(self.output_dir, f"attestation_{student.cin}_{timestamp}.pdf")
        
        pdf = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        
        # En-tête du centre
        self._create_center_header(pdf, width, height)
        
        # Titre
        y = height - 200
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawCentredString(width / 2, y, "ATTESTATION DE FORMATION")
        
        # Corps du texte
        y -= 60
        pdf.setFont("Helvetica", 12)
        text_lines = [
            f"Je soussigné(e), représentant légal de {center['name']},",
            f"atteste que {student.full_name},",
            f"titulaire de la CIN n° {student.cin},",
            f"né(e) le {student.date_of_birth.strftime('%d/%m/%Y')},",
            "",
            "a suivi une formation de conduite automobile comprenant :",
        ]
        
        for line in text_lines:
            pdf.drawString(80, y, line)
            y -= 20
        
        # Détail des heures
        y -= 10
        pdf.setFont("Helvetica-Bold", 11)
        for session_type, hours in hours_by_type.items():
            pdf.drawString(100, y, f"• {session_type.replace('_', ' ').title()} : {hours:.1f} heures")
            y -= 18
        
        # Total
        y -= 10
        total_hours = sum(hours_by_type.values())
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, y, f"TOTAL : {total_hours:.1f} heures de formation")
        
        # Pied de page
        self._create_center_footer(pdf, width)
        
        pdf.save()
        logger.info(f"Attestation générée : {filepath}")
        return True, filepath
        
    except Exception as e:
        error_msg = f"Erreur lors de la génération de l'attestation : {str(e)}"
        logger.error(error_msg)
        return False, error_msg
```

---

## 6. Checklist d'implémentation

### ✅ Pour chaque contrôleur à harmoniser

#### Phase 1 : CRUD de base (obligatoire)
- [ ] `get_all()` avec support des filtres
- [ ] `get_by_id()`
- [ ] `search()` avec recherche multi-champs
- [ ] `create()` avec validation
- [ ] `update()` avec validation
- [ ] `delete()` avec vérifications

#### Phase 2 : Export/Import (recommandé)
- [ ] `export_to_csv()` avec en-tête centre
- [ ] `import_from_csv()` avec validation

#### Phase 3 : Méthodes métier (selon besoin)
- [ ] Méthodes spécifiques au domaine
- [ ] Génération de statistiques
- [ ] Méthodes de recherche avancée

#### Phase 4 : Tests (essentiel)
- [ ] Tester création avec données valides
- [ ] Tester création avec données invalides
- [ ] Tester recherche
- [ ] Tester export/import
- [ ] Tester suppression avec contraintes

---

## 🎯 Ordre d'implémentation recommandé

### 1. ExamController (3-4 heures)
**Priorité** : 🔴 CRITIQUE  
**Raison** : Actuellement 27 lignes, fonctionnalité clé manquante  
**Template** : Utiliser le template complet ci-dessus

### 2. InstructorController (2-3 heures)
**Priorité** : 🔴 CRITIQUE  
**Raison** : Actuellement 16 lignes, gestion RH bloquée  
**Template** : Adapter le template ExamController

### 3. VehicleController (2-3 heures)
**Priorité** : 🔴 CRITIQUE  
**Raison** : Actuellement 16 lignes, gestion flotte bloquée  
**Template** : Adapter le template ExamController

### 4. PaymentController (1-2 heures)
**Priorité** : 🟡 IMPORTANT  
**Raison** : Ajouter update/delete/cancel_payment  
**Template** : Template CRUD partiel

### 5. SessionController (1 heure)
**Priorité** : 🟢 AMÉLIORATION  
**Raison** : Ajouter export/import seulement  
**Template** : Template Export/Import uniquement

### 6. StudentController (30 min)
**Priorité** : 🟢 AMÉLIORATION  
**Raison** : Déjà complet, ajouter validation seulement  
**Template** : Template Validation uniquement

---

> **Temps total estimé** : 10-14 heures de développement pour harmonisation complète.  
> **Livrable** : 6 contrôleurs standardisés, maintenables et testés.

---

**Date** : 2025-12-08  
**Version** : 1.0
