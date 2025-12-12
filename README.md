# 🚗 Auto-École Manager

Système de gestion complet pour auto-école avec interface moderne PySide6.

## 🚀 Démarrage Rapide

### Installation

```bash
# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données (première fois uniquement)
python scripts/setup_database.py

# Lancer l'application
python src/main_gui.py
```

## 🔐 Système de Licence

L'application nécessite une licence valide pour fonctionner.

### Générer une Licence

```bash
python generate_license.py "Nom Auto-École" 365
```

### Activation

1. Lancez l'application
2. Copiez votre Hardware ID
3. Contactez le support: **e.belqasim@gmail.com** / **+212 637-636146**
4. Recevez votre clé de licence
5. Activez dans l'application

## 👤 Connexion par Défaut

- **Username:** admin
- **Password:** Admin123!

⚠️ Changez le mot de passe après la première connexion!

## 📁 Structure du Projet

```
auto-ecole/
├── src/                    # Code source principal
│   ├── models/            # Modèles de données
│   ├── controllers/       # Logique métier
│   ├── views/             # Interface utilisateur
│   └── utils/             # Utilitaires
├── data/                  # Base de données
├── assets/                # Ressources (icônes, images)
├── migrations/            # Scripts de migration DB
├── scripts/               # Scripts utilitaires
└── generate_license.py    # Générateur de licences

```

## ✨ Fonctionnalités

- 📚 **Gestion des Élèves** - Dossiers complets avec suivi
- 📅 **Planning** - Gestion des cours et examens
- 💰 **Comptabilité** - Paiements et facturation
- 🚗 **Parc Véhicules** - Suivi de la flotte
- 👥 **RBAC** - Système de rôles et permissions
- 📊 **Statistiques** - Tableaux de bord analytiques
- 🔒 **Sécurité** - Chiffrement et licences

## 🛠️ Support

- **Email:** e.belqasim@gmail.com
- **Téléphone:** +212 637-636146

## 📄 Licence

Propriétaire - Auto-École Manager v1.0
