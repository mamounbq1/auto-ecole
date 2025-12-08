# 🚀 Guide de Démarrage Rapide - Auto-École Manager

## ⚡ Installation Express (5 minutes)

### Prérequis
- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation

```bash
# 1. Télécharger le projet
cd /path/to/webapp

# 2. Installer les dépendances
pip install SQLAlchemy bcrypt

# 3. Initialiser la base de données
python src/init_db.py

# 4. Lancer l'application
python src/main.py
```

---

## 👤 Première Connexion

L'application est livrée avec 4 comptes de démonstration :

| Rôle | Utilisateur | Mot de passe | Permissions |
|------|-------------|--------------|-------------|
| **Admin** | `admin` | `Admin123!` | Accès complet |
| **Caissier** | `caissier` | `Caisse123!` | Paiements, reçus |
| **Moniteur** | `moniteur1` | `Moniteur123!` | Planning, présences |
| **Réception** | `receptionniste` | `Reception123!` | Inscriptions, RDV |

⚠️ **Important** : Changez ces mots de passe lors de la première utilisation !

---

## 📚 Workflows Courants

### 1️⃣ Inscrire un Nouvel Élève

**Via l'interface console :**
```
1. Connexion avec compte Admin ou Réceptionniste
2. Menu Principal → Gestion des Élèves
3. Ajouter un élève (option future)
4. Remplir les informations :
   - Nom complet
   - CIN
   - Date de naissance
   - Téléphone
   - Adresse
5. Définir le montant total du forfait
6. Enregistrer
```

**Via Python (pour tests) :**
```python
from src.controllers import StudentController
from datetime import date

success, msg, student = StudentController.create_student({
    'full_name': 'Karim Alami',
    'cin': 'AA123456',
    'date_of_birth': date(2002, 5, 15),
    'phone': '+212 600-123456',
    'email': 'karim@email.com',
    'address': 'Casablanca',
    'license_type': 'B',
    'hours_planned': 20,
    'total_due': 5000
})

if success:
    print(f"✅ Élève créé : {student.full_name}")
```

---

### 2️⃣ Enregistrer un Paiement

```
1. Menu Principal → Gestion des Paiements
2. Enregistrer un paiement
3. Saisir :
   - ID de l'élève
   - Montant
   - Méthode (Espèces/Carte/Chèque)
   - Description (optionnel)
4. Générer le reçu PDF
5. Imprimer et remettre à l'élève
```

**Via Python :**
```python
from src.controllers import PaymentController
from src.models import PaymentMethod
from src.utils import login

# Connexion
login("caissier", "Caisse123!")

# Créer paiement
success, msg, payment = PaymentController.create_payment(
    student_id=1,
    amount=1500,
    payment_method=PaymentMethod.CASH,
    description="2ème versement",
    validated_by="Mohamed Alami"
)

if success:
    print(f"✅ Paiement enregistré : {payment.receipt_number}")
    
    # Générer reçu
    success, filepath = PaymentController.generate_receipt_pdf(payment.id)
    print(f"📄 Reçu : {filepath}")
```

---

### 3️⃣ Planifier une Session de Conduite

```python
from src.models import Session, SessionType, get_session
from datetime import datetime, timedelta

# Créer une session
session_db = get_session()

tomorrow_10am = datetime.now() + timedelta(days=1)
tomorrow_10am = tomorrow_10am.replace(hour=10, minute=0, second=0)

new_session = Session(
    student_id=1,
    instructor_id=1,
    vehicle_id=1,
    start_datetime=tomorrow_10am,
    duration_minutes=60,
    session_type=SessionType.PRACTICAL_DRIVING
)

session_db.add(new_session)
session_db.commit()

print(f"✅ Session planifiée : {new_session.start_datetime}")
```

---

### 4️⃣ Consulter le Planning du Jour

```
1. Menu Principal → Planning des Sessions
2. Voir les sessions du jour avec :
   - Heure
   - Élève
   - Moniteur
   - Statut
```

**Via Python :**
```python
from src.controllers import SessionController

today_sessions = SessionController.get_today_sessions()

for session in today_sessions:
    print(f"{session.start_datetime.strftime('%H:%M')} - "
          f"{session.student.full_name} avec "
          f"{session.instructor.full_name}")
```

---

### 5️⃣ Exporter les Données

**Export CSV des élèves :**
```
1. Menu Principal → Gestion des Élèves
2. Exporter en CSV
3. Fichier créé dans : exports/students_YYYYMMDD_HHMMSS.csv
```

**Via Python :**
```python
from src.controllers import StudentController

students = StudentController.get_all_students()
success, filepath = StudentController.export_students_to_csv(students)

print(f"✅ Export : {filepath}")
```

---

### 6️⃣ Créer une Sauvegarde

```
1. Menu Principal → Sauvegardes
2. Créer une nouvelle sauvegarde
3. Nommer la sauvegarde (optionnel)
4. Fichier créé dans : backups/
```

**Via Python :**
```python
from src.utils import create_backup

success, filepath = create_backup("sauvegarde_quotidienne")
print(f"✅ Sauvegarde : {filepath}")
```

**Restauration :**
```python
from src.utils import restore_backup

success, msg = restore_backup("backups/sauvegarde_20241208.zip")
print(msg)
```

---

## 📊 Statistiques & Rapports

### Dashboard Rapide
```python
from src.controllers import StudentController, SessionController

# Élèves actifs
active = StudentController.get_active_students_count()
print(f"Élèves actifs : {active}")

# Sessions du jour
today = SessionController.get_today_sessions()
print(f"Sessions aujourd'hui : {len(today)}")

# Élèves avec dette
debt_students = StudentController.get_students_with_debt()
total_debt = sum(abs(s.balance) for s in debt_students)
print(f"Dette totale : {total_debt} DH")
```

---

## 🔍 Recherche & Filtres

### Rechercher un Élève
```python
from src.controllers import StudentController

# Par nom/CIN/téléphone
results = StudentController.search_students("Sara")

for student in results:
    print(f"{student.full_name} - {student.cin} - {student.phone}")
```

### Filtrer par Statut
```python
from src.models import StudentStatus

# Élèves actifs seulement
active_students = StudentController.get_all_students(
    status=StudentStatus.ACTIVE
)

# Élèves diplômés
graduated = StudentController.get_all_students(
    status=StudentStatus.GRADUATED
)
```

---

## 🐛 Résolution de Problèmes

### La base de données ne se crée pas
```bash
# Supprimer l'ancienne base
rm data/autoecole.db

# Réinitialiser
python src/init_db.py
```

### Erreur "Module not found"
```bash
# Réinstaller les dépendances
pip install -r requirements.txt
```

### Mot de passe oublié (Admin)
```python
from src.models import User, get_session

session = get_session()
admin = session.query(User).filter(User.username == 'admin').first()
admin.set_password('NouveauMotDePasse123!')
session.commit()
print("✅ Mot de passe réinitialisé")
```

### Débloquer un compte verrouillé
```python
from src.models import User, get_session

session = get_session()
user = session.query(User).filter(User.username == 'username').first()
user.unlock()
session.commit()
print("✅ Compte débloqué")
```

---

## 📁 Fichiers Importants

| Fichier | Description |
|---------|-------------|
| `data/autoecole.db` | Base de données principale |
| `config.json` | Configuration de l'application |
| `logs/autoecole_*.log` | Fichiers de logs quotidiens |
| `exports/*.csv` | Exports de données |
| `backups/*.zip` | Sauvegardes compressées |

---

## 🔒 Sécurité

### Bonnes Pratiques

1. **Mots de passe forts**
   - Minimum 8 caractères
   - Majuscules + minuscules + chiffres + caractères spéciaux

2. **Sauvegardes régulières**
   - Quotidienne recommandée
   - Stocker hors site (clé USB, cloud)

3. **Logs d'audit**
   - Consulter régulièrement `logs/`
   - Vérifier les activités suspectes

4. **Permissions**
   - Donner le minimum de droits nécessaires
   - Utiliser des comptes séparés par rôle

---

## 🎓 Cas d'Usage Complets

### Cycle de Vie d'un Élève

```python
# 1. Inscription
student = create_student(...)

# 2. Paiement initial
payment = create_payment(student.id, 2000, ...)

# 3. Planifier sessions
for i in range(20):
    create_session(student.id, ...)

# 4. Enregistrer examens
create_exam(student.id, ExamType.THEORETICAL, ...)

# 5. Diplômé
student.status = StudentStatus.GRADUATED
```

---

## 📞 Support

- **Logs** : Consulter `logs/autoecole_*.log`
- **Tests** : Exécuter `python test_app.py`
- **Documentation** : Lire `README.md` et `docs/DEVELOPMENT_GUIDE.md`

---

## ✨ Tips & Astuces

### Raccourcis
```python
# Importer rapidement
from src.utils import *
from src.controllers import *
from src.models import *

# Session rapide
session = get_session()

# Logger
logger = get_logger()
logger.info("Mon message")
```

### Mode Debug
```python
# Activer le mode verbose SQL
from src.models import get_engine
engine = get_engine(echo=True)  # Affiche toutes les requêtes SQL
```

### Console Interactive
```bash
python
>>> from src.utils import login
>>> login("admin", "Admin123!")
>>> from src.controllers import *
# Explorer interactivement
```

---

**Prêt à démarrer ! 🚗💨**
