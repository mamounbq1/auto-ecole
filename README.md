# 🚗 Application de Gestion Auto-École

## 📋 Description

Application complète de gestion pour auto-école permettant de digitaliser et automatiser la gestion des élèves, moniteurs, véhicules, planning, paiements et examens.

## ✨ Fonctionnalités Principales

### 🎯 MVP (Version 1.0)

- **Gestion des élèves** : CRUD complet, historique, import/export CSV
- **Gestion des moniteurs** : Fiches moniteurs, disponibilités
- **Gestion des véhicules** : Immatriculation, maintenance, disponibilité
- **Planning intelligent** : Calendrier interactif, affectation automatique
- **Paiements & Facturation** : Suivi des paiements, génération de reçus PDF
- **Examens** : Gestion sessions d'examen, convocations
- **Authentification & Rôles** : Admin, Caissier, Moniteur, Réceptionniste
- **Rapports & Statistiques** : Dashboard, CA, KPIs
- **Sauvegarde/Restauration** : Backup automatique de la base de données

## 🛠️ Stack Technique

- **Frontend** : PySide6 (Qt for Python)
- **Backend** : Python 3.9+
- **Base de données** : SQLite avec SQLAlchemy ORM
- **Sécurité** : bcrypt pour les mots de passe
- **Génération PDF** : ReportLab
- **Export Excel** : openpyxl, pandas
- **Internationalisation** : gettext (FR/AR)

## 📦 Installation

### Prérequis

```bash
Python 3.9 ou supérieur
```

### Dépendances

```bash
pip install -r requirements.txt
```

### Configuration initiale

```bash
python src/init_db.py
```

Compte admin par défaut :
- **Username** : admin
- **Password** : Admin123!

⚠️ **Important** : Changez le mot de passe lors de la première connexion !

## 🚀 Lancement

```bash
python src/main.py
```

Ou utilisez l'exécutable packagé :
```bash
# Windows
AutoEcole.exe

# macOS
./AutoEcole.app
```

## 👥 Rôles et Permissions

| Rôle | Permissions |
|------|-------------|
| **Admin** | Accès complet, gestion utilisateurs, sauvegarde |
| **Caissier** | Paiements, reçus, consultation élèves |
| **Moniteur** | Planning, présences, fiches élèves |
| **Réceptionniste** | Inscriptions, rendez-vous, convocations |

## 📊 Structure du Projet

```
webapp/
├── src/
│   ├── models/          # Modèles de données SQLAlchemy
│   ├── views/           # Interfaces utilisateur PySide6
│   ├── controllers/     # Logique métier
│   ├── utils/           # Utilitaires (PDF, export, backup)
│   └── resources/       # Ressources (icônes, traductions)
├── data/               # Base de données SQLite
├── exports/            # Exports CSV/PDF
├── backups/            # Sauvegardes automatiques
├── logs/               # Fichiers de logs
├── tests/              # Tests unitaires et fonctionnels
└── docs/               # Documentation
```

## 🔧 Configuration

Le fichier `config.json` permet de personnaliser :

- Langue de l'interface (FR/AR)
- Dossiers d'export et de sauvegarde
- Paramètres de sécurité
- Fréquence des sauvegardes automatiques

## 📖 Guide d'Utilisation

### Inscription d'un élève

1. Menu **Élèves** → **Nouvel Élève**
2. Remplir les informations (CIN, nom, téléphone...)
3. **Enregistrer**
4. Imprimer le contrat et la première facture

### Création d'une session de conduite

1. Ouvrir le **Planning**
2. Cliquer sur un créneau horaire
3. Sélectionner : Élève, Moniteur, Véhicule
4. **Valider**

### Enregistrement d'un paiement

1. Ouvrir la fiche **Élève**
2. Onglet **Paiements** → **Nouveau Paiement**
3. Saisir montant et mode de paiement
4. **Générer le reçu PDF**

### Sauvegarde de la base

1. Menu **Paramètres** → **Sauvegarde**
2. Choisir l'emplacement
3. Confirmation

## 🔒 Sécurité

- Mots de passe hashés avec bcrypt (salt)
- Permissions basées sur les rôles (RBAC)
- Logs des actions critiques
- Sauvegarde chiffrée optionnelle

## 📈 Rapports Disponibles

- Chiffre d'affaires mensuel/annuel
- Nombre d'élèves actifs
- Sessions par moniteur
- Taux de réussite aux examens
- État de trésorerie

## 🌍 Internationalisation

L'application supporte le français et l'arabe. Changez la langue dans **Paramètres** → **Langue**.

## 🧪 Tests

```bash
# Tests unitaires
pytest tests/unit/

# Tests fonctionnels
pytest tests/functional/

# Tous les tests avec couverture
pytest --cov=src tests/
```

## 📦 Packaging (Distribution)

### Windows

```bash
pyinstaller --windowed --onefile --name "AutoEcole" src/main.py
```

### macOS

```bash
python -m briefcase package
```

## 🐛 Dépannage

### La base de données ne se crée pas
```bash
python src/init_db.py --force
```

### Problème de permissions
Vérifiez que l'utilisateur a les droits en écriture sur le dossier `data/`.

### Erreur au démarrage
Consultez les logs dans `logs/autoecole.log`.

## 📝 Changelog

### Version 1.0.0 (MVP) - 2024-12
- ✅ Gestion complète élèves, moniteurs, véhicules
- ✅ Planning avec calendrier interactif
- ✅ Module paiements et facturation
- ✅ Authentification et rôles
- ✅ Sauvegarde/restauration
- ✅ Export CSV/PDF

## 🗺️ Roadmap (Versions Futures)

- [ ] Version 2.0 : Application mobile (iOS/Android)
- [ ] Intégration SMS automatiques (Twilio)
- [ ] Paiement en ligne (Stripe/PayPal)
- [ ] Mode multi-agences (serveur central)
- [ ] API REST pour intégrations tierces

## 🤝 Contribution

Ce projet est développé pour un usage interne. Pour toute suggestion ou bug, contactez l'équipe technique.

## 📄 Licence

Propriétaire - Usage réservé à [Nom Auto-École]

## 👨‍💻 Développement

### Prérequis de développement

```bash
pip install -r requirements-dev.txt
```

### Standards de code

- PEP 8 pour Python
- Type hints obligatoires
- Docstrings pour toutes les fonctions publiques
- Tests unitaires pour la logique métier

## 📞 Support

Pour toute assistance technique :
- Email : support@autoecole.local
- Téléphone : +212 XXX XXX XXX

---

**Développé avec ❤️ pour digitaliser les auto-écoles**
