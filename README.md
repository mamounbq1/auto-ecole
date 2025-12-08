# 🚗 Auto-École Manager - Application de Gestion Complète

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)]()

Application complète de gestion pour auto-école avec interface graphique moderne (PySide6), permettant de digitaliser et automatiser la gestion des élèves, moniteurs, véhicules, planning, paiements et examens.

## 🎯 Installation rapide (Windows)

### Méthode 1 : Double-clic (Recommandé) ⭐

1. **Télécharger** le projet depuis GitHub
2. **Ouvrir** le dossier `auto-ecole-main`
3. **Double-cliquer** sur `SIMPLE_SETUP.bat` (initialisation)
4. **Double-cliquer** sur `AUTO_ECOLE.bat` (lancement)
5. **Se connecter** : `admin` / `Admin123!`

### Méthode 2 : Ligne de commande

```bash
cd "C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main"
python src\init_db.py
python src\main_gui.py
```

**📖 Guide complet** : Voir [`DEMARRAGE_RAPIDE.md`](DEMARRAGE_RAPIDE.md)

---

## ✨ Fonctionnalités Principales

### 7 Modules complets

1. **📊 Dashboard** - Statistiques en temps réel avec graphiques
   - Élèves actifs, CA mensuel, sessions du jour
   - Graphiques : évolution CA, répartition élèves, taux de réussite

2. **🎓 Élèves** - Gestion complète des apprenants
   - CRUD complet, historique, progression
   - Import/export CSV, filtres avancés

3. **💰 Paiements** - Suivi financier professionnel
   - Méthodes multiples (Espèces, Carte, Chèque, Virement)
   - Génération de reçus PDF, catégorisation

4. **📅 Planning** - Calendrier intelligent
   - Planification des sessions de conduite
   - Affectation moniteur + véhicule, vue calendrier

5. **👨‍🏫 Moniteurs** - Gestion des instructeurs
   - Types de permis, disponibilités, salaires
   - Statistiques de performance

6. **🚗 Véhicules** - Gestion de la flotte
   - Suivi kilométrage, maintenances planifiées
   - Coûts, assurances, contrôles techniques

7. **📝 Examens** - Gestion complète des examens
   - Planification théorique/pratique
   - Convocations PDF, résultats, statistiques

### Fonctionnalités transversales

- ✅ **Authentification** avec 4 rôles (Admin, Caissier, Moniteur, Réceptionniste)
- ✅ **Génération PDF** professionnelle (reçus, convocations, rapports)
- ✅ **Export CSV** pour tous les modules
- ✅ **Graphiques** avec matplotlib/seaborn
- ✅ **Sauvegarde/Restauration** de la base de données

---

## 🛠️ Stack Technique

| Composant | Technologie |
|-----------|-------------|
| **Interface** | PySide6 (Qt 6 for Python) |
| **Backend** | Python 3.8+ |
| **Base de données** | SQLite + SQLAlchemy ORM |
| **Graphiques** | Matplotlib, Seaborn |
| **PDF** | ReportLab |
| **Export** | CSV natif Python |

---

## 📦 Installation détaillée

### Prérequis

- **Python 3.8+** ([Télécharger](https://www.python.org/downloads/))
- **Windows 10/11** (testé et validé)

### Étape 1 : Cloner le projet

```bash
git clone https://github.com/mamounbq1/auto-ecole.git
cd auto-ecole
```

### Étape 2 : Installer les dépendances

```bash
pip install sqlalchemy PySide6 reportlab matplotlib seaborn
```

Ou avec requirements.txt :

```bash
pip install -r requirements.txt
```

### Étape 3 : Initialiser la base de données

**Windows** :
```bash
SIMPLE_SETUP.bat
```

**Ligne de commande** :
```bash
python src\init_db.py
```

### Étape 4 : Lancer l'application

**Windows** :
```bash
AUTO_ECOLE.bat
```

**Ligne de commande** :
```bash
python src\main_gui.py
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
