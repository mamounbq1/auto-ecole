# 📖 Guide de Développement - Application Auto-École

## 🎯 État du Projet

### ✅ Fonctionnalités Implémentées (MVP v1.0)

#### 1. **Architecture & Base de Données**
- ✅ Structure du projet organisée (MVC pattern)
- ✅ Modèles de données complets avec SQLAlchemy
- ✅ Base de données SQLite avec migrations
- ✅ Relations ORM entre toutes les entités
- ✅ Script d'initialisation avec données de test

#### 2. **Système d'Authentification**
- ✅ Gestion des utilisateurs avec 4 rôles (Admin, Caissier, Moniteur, Réceptionniste)
- ✅ Hachage sécurisé des mots de passe (bcrypt)
- ✅ Système de permissions basé sur les rôles (RBAC)
- ✅ Verrouillage automatique après tentatives échouées
- ✅ Gestion des sessions

#### 3. **Gestion des Élèves**
- ✅ CRUD complet (Create, Read, Update, Delete)
- ✅ Recherche multi-critères (nom, CIN, téléphone, email)
- ✅ Filtrage par statut
- ✅ Suivi de la progression (heures complétées/planifiées)
- ✅ Gestion des soldes et paiements
- ✅ Export CSV
- ✅ Import CSV (avec validation)

#### 4. **Gestion des Moniteurs**
- ✅ Fiches moniteurs complètes
- ✅ Gestion des types de permis enseignables
- ✅ Disponibilités et statistiques
- ✅ Suivi des heures enseignées

#### 5. **Gestion des Véhicules**
- ✅ Parc automobile complet
- ✅ Suivi de maintenance
- ✅ Alertes assurance/contrôle technique
- ✅ Historique d'utilisation
- ✅ Gestion du kilométrage

#### 6. **Planning & Sessions**
- ✅ Modèle de session complet
- ✅ Affectation élève/moniteur/véhicule
- ✅ Gestion des statuts (planifié, confirmé, réalisé, annulé)
- ✅ Filtrage par date
- ✅ Sessions du jour et à venir
- ✅ Évaluation de performance

#### 7. **Paiements & Facturation**
- ✅ Enregistrement des paiements
- ✅ Multiples méthodes de paiement
- ✅ Génération automatique de numéros de reçu
- ✅ Export de reçus en HTML (imprimable)
- ✅ Suivi des dettes
- ✅ Validation par caissier

#### 8. **Examens**
- ✅ Gestion examens théoriques et pratiques
- ✅ Convocations
- ✅ Enregistrement des résultats
- ✅ Suivi des tentatives
- ✅ Statistiques de réussite

#### 9. **Utilitaires**
- ✅ Système de backup/restauration
- ✅ Export CSV universel
- ✅ Logging complet
- ✅ Configuration centralisée (config.json)

#### 10. **Tests & Qualité**
- ✅ Suite de tests fonctionnels complète
- ✅ 100% de réussite sur les tests critiques
- ✅ Validation de tous les modules

---

## 🚧 Prochaines Étapes (Roadmap)

### Phase 2 : Interface Graphique (PySide6)

#### 1. Interface de Connexion
```python
# À créer : src/views/login_window.py
class LoginWindow(QMainWindow):
    - Formulaire de connexion
    - Gestion des erreurs
    - Récupération de mot de passe
```

#### 2. Fenêtre Principale (MainWindow)
```python
# À créer : src/views/main_window.py
class MainWindow(QMainWindow):
    - Barre de menu
    - Barre latérale de navigation
    - Zone centrale (QStackedWidget)
    - Barre de statut
    - Dashboard avec statistiques
```

#### 3. Modules de Gestion

**Élèves** (`src/views/students/`)
- `student_list_widget.py` : Liste avec tableau et recherche
- `student_form_dialog.py` : Formulaire ajout/modification
- `student_detail_widget.py` : Fiche complète avec onglets
- `student_import_dialog.py` : Interface d'import CSV

**Moniteurs** (`src/views/instructors/`)
- `instructor_list_widget.py`
- `instructor_form_dialog.py`
- `instructor_stats_widget.py`

**Véhicules** (`src/views/vehicles/`)
- `vehicle_list_widget.py`
- `vehicle_form_dialog.py`
- `vehicle_maintenance_dialog.py`

**Planning** (`src/views/planning/`)
- `calendar_widget.py` : Vue calendrier (QCalendarWidget personnalisé)
- `session_form_dialog.py` : Création/modification session
- `session_list_widget.py` : Vue liste
- `drag_drop_session.py` : Glisser-déposer pour le planning

**Paiements** (`src/views/payments/`)
- `payment_form_dialog.py`
- `payment_history_widget.py`
- `receipt_preview_dialog.py`

**Examens** (`src/views/exams/`)
- `exam_schedule_widget.py`
- `exam_form_dialog.py`
- `summons_generator.py`

#### 4. Composants Réutilisables

**Widgets Communs** (`src/views/widgets/`)
```python
# search_bar.py
class SearchBar(QWidget):
    """Barre de recherche avec filtres"""

# data_table.py
class DataTable(QTableWidget):
    """Tableau avec tri, pagination, export"""

# stats_card.py
class StatsCard(QWidget):
    """Carte statistique pour le dashboard"""

# filter_panel.py
class FilterPanel(QWidget):
    """Panneau de filtres avancés"""
```

### Phase 3 : Fonctionnalités Avancées

#### 1. Rapports & Statistiques
```python
# src/controllers/report_controller.py
class ReportController:
    - Chiffre d'affaires mensuel/annuel
    - Taux de réussite aux examens
    - Performance des moniteurs
    - Utilisation des véhicules
    - Prévisions de trésorerie
    - Graphiques (matplotlib/plotly)
```

#### 2. Génération PDF Avancée
```python
# src/utils/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

class PDFGenerator:
    - Reçus de paiement professionnels
    - Contrats d'inscription
    - Convocations d'examen
    - Attestations de présence
    - Rapports mensuels
    - Factures détaillées
```

#### 3. Notifications & Rappels
```python
# src/utils/notifications.py
class NotificationManager:
    - Email (SMTP)
    - SMS (Twilio API)
    - Rappels automatiques :
      * Sessions à venir
      * Paiements en retard
      * Renouvellement assurance véhicules
      * Examens planifiés
```

#### 4. Internationalisation (i18n)
```python
# src/resources/translations/
- fr_FR.json : Français
- ar_MA.json : Arabe marocain
- en_US.json : Anglais

# Utilisation de gettext ou Qt Linguist
from PySide6.QtCore import QTranslator, QLocale
```

### Phase 4 : Optimisations & Qualité

#### 1. Performance
- ✅ Indexation de la base de données
- ⏳ Pagination des listes
- ⏳ Lazy loading des relations ORM
- ⏳ Cache pour les requêtes fréquentes
- ⏳ Optimisation des requêtes SQL

#### 2. Sécurité
- ✅ Mots de passe hashés (bcrypt)
- ⏳ Chiffrement de la base de données (SQLCipher)
- ⏳ Backup chiffré
- ⏳ Logs d'audit complets
- ⏳ Protection CSRF/XSS (si API web)

#### 3. Tests
- ✅ Tests unitaires des contrôleurs
- ⏳ Tests d'intégration
- ⏳ Tests de l'interface (pytest-qt)
- ⏳ Tests de performance
- ⏳ Couverture de code > 80%

#### 4. Documentation
- ✅ README complet
- ⏳ Documentation API (Sphinx)
- ⏳ Guide utilisateur PDF
- ⏳ Vidéos tutoriels
- ⏳ FAQ

### Phase 5 : Distribution

#### 1. Packaging
```bash
# Windows
pyinstaller --windowed --onefile \
  --name "AutoEcole" \
  --icon=resources/icon.ico \
  --add-data "config.json;." \
  --add-data "src/resources;resources" \
  src/main.py

# macOS
python -m briefcase create
python -m briefcase build
python -m briefcase package

# Linux
python -m briefcase create linux appimage
python -m briefcase package linux appimage
```

#### 2. Installeur
- ✅ Installeur Windows (NSIS/Inno Setup)
- ⏳ Package DMG macOS
- ⏳ Package DEB/RPM Linux
- ⏳ Script d'installation automatique

---

## 🛠️ Guide de Développement

### Installation Environnement de Dev

```bash
# 1. Cloner le dépôt
git clone <repo-url>
cd webapp

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Installer les dépendances de développement
pip install -r requirements-dev.txt

# 5. Initialiser la base de données
python src/init_db.py

# 6. Lancer les tests
python test_app.py

# 7. Lancer l'application
python src/main.py
```

### Structure des Fichiers

```
webapp/
├── src/
│   ├── models/          # Modèles de données (SQLAlchemy)
│   ├── views/           # Interface utilisateur (PySide6) - À créer
│   ├── controllers/     # Logique métier
│   ├── utils/           # Utilitaires (auth, backup, export, logs)
│   ├── resources/       # Ressources (icônes, traductions)
│   ├── init_db.py       # Initialisation base de données
│   └── main.py          # Point d'entrée
├── data/                # Base de données SQLite
├── exports/             # Exports CSV/PDF
├── backups/             # Sauvegardes
├── logs/                # Fichiers de logs
├── tests/               # Tests unitaires et fonctionnels
├── docs/                # Documentation
├── config.json          # Configuration
├── requirements.txt     # Dépendances Python
└── README.md            # Documentation principale
```

### Conventions de Code

#### Nommage
```python
# Classes : PascalCase
class StudentController:
    pass

# Fonctions/Méthodes : snake_case
def get_student_by_id(student_id: int):
    pass

# Constantes : UPPER_SNAKE_CASE
MAX_LOGIN_ATTEMPTS = 5

# Variables : snake_case
student_name = "Ahmed"
```

#### Type Hints
```python
from typing import List, Optional, Dict, Any

def search_students(query: str) -> List[Student]:
    """Type hints obligatoires"""
    pass

def get_student(student_id: int) -> Optional[Student]:
    """Retour optionnel si peut être None"""
    pass
```

#### Docstrings
```python
def create_payment(student_id: int, amount: float) -> tuple[bool, str, Optional[Payment]]:
    """
    Créer un nouveau paiement
    
    Args:
        student_id: ID de l'élève
        amount: Montant du paiement
    
    Returns:
        Tuple (success, message, payment)
    
    Raises:
        ValueError: Si le montant est négatif
    
    Example:
        >>> success, msg, payment = create_payment(1, 500.0)
        >>> print(payment.receipt_number)
        'REC-20241208-00001'
    """
    pass
```

### Git Workflow

```bash
# 1. Créer une branche pour une fonctionnalité
git checkout -b feature/student-ui

# 2. Développer et commiter régulièrement
git add .
git commit -m "feat(students): Add student list view"

# 3. Pousser la branche
git push origin feature/student-ui

# 4. Créer une Pull Request
# Via interface GitHub/GitLab

# 5. Après validation, merger dans main
git checkout main
git merge feature/student-ui
git push origin main
```

### Format des Commits

```
<type>(<scope>): <description>

[corps optionnel]

[footer optionnel]
```

**Types:**
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Formatage, pas de changement de code
- `refactor`: Refactoring
- `test`: Ajout de tests
- `chore`: Maintenance

**Exemples:**
```bash
feat(students): Add CSV import functionality
fix(auth): Correct password validation logic
docs(readme): Update installation instructions
refactor(models): Simplify Student model
test(payments): Add payment controller tests
```

---

## 🐛 Debugging & Troubleshooting

### Logs
```python
# Consulter les logs
tail -f logs/autoecole_20241208.log

# Augmenter le niveau de log
# Dans config.json
{
  "logging": {
    "level": "DEBUG"  # INFO, WARNING, ERROR, CRITICAL
  }
}
```

### Base de Données
```bash
# Ouvrir la base avec sqlite3
sqlite3 data/autoecole.db

# Commandes utiles
.tables                  # Lister les tables
.schema students         # Voir le schéma
SELECT * FROM students;  # Requête
.exit                    # Quitter
```

### Tests
```bash
# Lancer un test spécifique
pytest tests/test_students.py::test_create_student -v

# Avec couverture
pytest --cov=src --cov-report=html

# Voir le rapport
open htmlcov/index.html
```

---

## 📞 Support & Contact

- **Issues GitHub** : Pour signaler des bugs
- **Discussions** : Pour questions et suggestions
- **Email** : support@autoecole.local

---

## 📄 Licence

Propriétaire - Usage réservé à l'auto-école

---

**Dernière mise à jour** : 08/12/2024
**Version** : 1.0.0 (MVP)
