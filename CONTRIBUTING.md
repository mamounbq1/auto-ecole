# 🤝 Guide de Contribution

Merci de votre intérêt pour contribuer à l'application Auto-École Manager !

## 🌟 Comment Contribuer

### 1. Fork & Clone

```bash
# Fork le projet sur GitHub
# Puis cloner votre fork
git clone https://github.com/votre-username/autoecole.git
cd autoecole

# Ajouter le repo original comme remote
git remote add upstream https://github.com/original/autoecole.git
```

### 2. Créer une Branche

```bash
# Toujours créer une nouvelle branche pour vos modifications
git checkout -b feature/ma-nouvelle-fonctionnalite

# Ou pour un bugfix
git checkout -b fix/correction-bug-paiement
```

### 3. Développer

```bash
# Installer les dépendances de dev
pip install -r requirements-dev.txt

# Développer votre fonctionnalité
# ...

# Tester
python test_app.py
pytest tests/

# Formater le code
black src/
isort src/

# Vérifier la qualité
flake8 src/
mypy src/
```

### 4. Commiter

Utilisez le format de commit conventionnel :

```
<type>(<scope>): <description courte>

[Corps optionnel avec détails]

[Footer optionnel]
```

**Types de commits :**
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Formatage (pas de changement de logique)
- `refactor`: Refactoring
- `perf`: Amélioration de performance
- `test`: Ajout/modification de tests
- `chore`: Maintenance, configuration

**Exemples :**
```bash
git commit -m "feat(students): Add bulk import from Excel"
git commit -m "fix(payments): Correct receipt number generation"
git commit -m "docs(readme): Update installation instructions"
```

### 5. Push & Pull Request

```bash
# Pousser votre branche
git push origin feature/ma-nouvelle-fonctionnalite

# Créer une Pull Request sur GitHub
# Inclure :
# - Description claire de ce qui est fait
# - Captures d'écran si UI
# - Tests ajoutés/modifiés
# - Issues liées (#123)
```

## 📋 Checklist Avant PR

- [ ] Code formaté (black, isort)
- [ ] Pas d'erreurs de linting (flake8)
- [ ] Type hints ajoutés (mypy)
- [ ] Tests ajoutés/mis à jour
- [ ] Tous les tests passent
- [ ] Documentation mise à jour
- [ ] Commit messages suivent le format
- [ ] Pas de conflits avec main

## 🧪 Tests

### Exécuter les Tests

```bash
# Tous les tests
pytest

# Tests spécifiques
pytest tests/test_students.py

# Avec couverture
pytest --cov=src --cov-report=html

# Tests rapides (sans slow)
pytest -m "not slow"
```

### Écrire des Tests

```python
# tests/test_mon_module.py
import pytest
from src.controllers import StudentController

def test_create_student():
    """Test de création d'un élève"""
    data = {
        'full_name': 'Test Student',
        'cin': 'TEST123',
        'date_of_birth': date(2000, 1, 1),
        'phone': '+212 600-000000'
    }
    
    success, msg, student = StudentController.create_student(data)
    
    assert success
    assert student is not None
    assert student.full_name == 'Test Student'

def test_duplicate_cin():
    """Test de détection de CIN en double"""
    # ...
```

## 🎨 Standards de Code

### Style Python

Suivre PEP 8 et nos conventions :

```python
# Classes : PascalCase
class StudentController:
    pass

# Fonctions : snake_case
def get_student_by_id(student_id: int):
    pass

# Constantes : UPPER_SNAKE_CASE
MAX_ATTEMPTS = 5

# Privé : préfixe underscore
def _internal_helper():
    pass
```

### Type Hints

Obligatoires pour toutes les fonctions publiques :

```python
from typing import List, Optional, Dict, Any

def search_students(
    query: str, 
    limit: int = 10
) -> List[Student]:
    """
    Rechercher des élèves
    
    Args:
        query: Terme de recherche
        limit: Nombre maximum de résultats
    
    Returns:
        Liste des élèves trouvés
    """
    pass
```

### Docstrings

Format Google Style :

```python
def create_payment(
    student_id: int,
    amount: float,
    method: PaymentMethod
) -> tuple[bool, str, Optional[Payment]]:
    """
    Créer un nouveau paiement pour un élève.
    
    Cette fonction enregistre un paiement, génère un numéro de reçu
    unique et met à jour le solde de l'élève automatiquement.
    
    Args:
        student_id: Identifiant unique de l'élève
        amount: Montant du paiement en dirhams (doit être > 0)
        method: Méthode de paiement utilisée
    
    Returns:
        Un tuple contenant:
            - success (bool): True si le paiement est créé
            - message (str): Message de succès ou d'erreur
            - payment (Payment | None): L'objet Payment créé
    
    Raises:
        ValueError: Si le montant est négatif ou nul
        StudentNotFoundError: Si l'élève n'existe pas
    
    Example:
        >>> success, msg, payment = create_payment(
        ...     student_id=1,
        ...     amount=1500.0,
        ...     method=PaymentMethod.CASH
        ... )
        >>> if success:
        ...     print(f"Reçu: {payment.receipt_number}")
        Reçu: REC-20241208-00042
    
    Note:
        Le paiement est automatiquement validé et un reçu PDF
        peut être généré avec `generate_receipt_pdf()`.
    """
    pass
```

## 🐛 Signaler un Bug

### Template d'Issue

```markdown
## Description du Bug
Brève description du problème

## Étapes pour Reproduire
1. Aller sur '...'
2. Cliquer sur '...'
3. Voir l'erreur

## Comportement Attendu
Ce qui devrait se passer

## Comportement Actuel
Ce qui se passe réellement

## Screenshots
Si applicable

## Environnement
- OS: [e.g. Windows 11]
- Python: [e.g. 3.10.5]
- Version App: [e.g. 1.0.0]

## Logs
```
Copier les logs pertinents de logs/autoecole_*.log
```

## Informations Additionnelles
Contexte supplémentaire
```

## 💡 Proposer une Fonctionnalité

### Template de Feature Request

```markdown
## Problème à Résoudre
Quel besoin cette fonctionnalité comble-t-elle ?

## Solution Proposée
Description claire de la fonctionnalité souhaitée

## Alternatives Considérées
Autres façons d'atteindre le même objectif

## Bénéfices
- Qui en bénéficie ?
- Impact sur les utilisateurs
- Impact sur le code

## Complexité Estimée
- [ ] Simple (quelques heures)
- [ ] Moyenne (quelques jours)
- [ ] Complexe (une semaine ou plus)

## Maquettes / Exemples
Screenshots, wireframes, exemples de code...
```

## 🏗️ Architecture & Design

### Ajout d'un Nouveau Module

1. **Créer le modèle** (`src/models/mon_module.py`)
2. **Créer le contrôleur** (`src/controllers/mon_module_controller.py`)
3. **Ajouter les tests** (`tests/test_mon_module.py`)
4. **Documenter** (`docs/MON_MODULE.md`)
5. **Mettre à jour** les imports dans `__init__.py`

### Modèle de Base

```python
# src/models/mon_entite.py
from sqlalchemy import Column, Integer, String
from .base import Base, BaseModel

class MonEntite(Base, BaseModel):
    __tablename__ = "mon_entite"
    
    name = Column(String(100), nullable=False)
    # ...
    
    def __init__(self, name: str, **kwargs):
        self.name = name
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
        }
```

### Contrôleur de Base

```python
# src/controllers/mon_entite_controller.py
from typing import List, Optional
from src.models import MonEntite, get_session
from src.utils import get_logger

logger = get_logger()

class MonEntiteController:
    
    @staticmethod
    def get_all() -> List[MonEntite]:
        try:
            session = get_session()
            return session.query(MonEntite).all()
        except Exception as e:
            logger.error(f"Erreur: {e}")
            return []
    
    @staticmethod
    def create(data: dict) -> tuple[bool, str, Optional[MonEntite]]:
        try:
            session = get_session()
            entity = MonEntite(**data)
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return True, "Créé avec succès", entity
        except Exception as e:
            session.rollback()
            return False, str(e), None
```

## 🔒 Sécurité

### Ne JAMAIS Commiter

- ❌ Mots de passe en clair
- ❌ Clés API
- ❌ Tokens d'authentification
- ❌ Données personnelles réelles
- ❌ Base de données de production

### Utiliser

- ✅ Variables d'environnement (`.env`)
- ✅ Fichiers de configuration locaux (`.local`)
- ✅ Données de test anonymisées
- ✅ Secrets chiffrés

## 📞 Questions ?

- 💬 **Discussions GitHub** : Pour questions générales
- 🐛 **Issues** : Pour bugs et features
- 📧 **Email** : dev@autoecole.local
- 📚 **Docs** : `docs/DEVELOPMENT_GUIDE.md`

## 🎖️ Reconnaissance

Tous les contributeurs seront mentionnés dans :
- `CONTRIBUTORS.md`
- Release notes
- Section About de l'application

Merci de contribuer ! 🙏
