# 🚀 Guide de Démarrage Rapide

## ⚠️ IMPORTANT : Initialisation de la Base de Données

Avant de lancer l'application pour la première fois, vous **DEVEZ** initialiser la base de données.

### 📋 Étape 1 : Initialiser la Base de Données

Depuis le **répertoire racine** du projet (pas depuis `src/`) :

```bash
# Windows
python src/init_db.py

# Linux/Mac
python3 src/init_db.py
```

Cette commande va :
- ✅ Créer le dossier `data/`
- ✅ Créer la base de données `data/autoecole.db`
- ✅ Créer toutes les tables
- ✅ Insérer des données de démonstration

### 🎯 Étape 2 : Lancer l'Application

Deux méthodes possibles :

#### Méthode 1 : Depuis le répertoire racine (RECOMMANDÉ)

```bash
# Windows
python src/main_gui.py

# Linux/Mac
python3 src/main_gui.py
```

#### Méthode 2 : Depuis le dossier src/

```bash
cd src

# Windows
python main_gui.py

# Linux/Mac
python3 main_gui.py
```

**Note** : La nouvelle version gère automatiquement les chemins absolus, donc les deux méthodes fonctionnent !

### 🔑 Comptes de Connexion

Après l'initialisation, utilisez ces identifiants :

| Rôle           | Login          | Mot de passe      |
|----------------|----------------|-------------------|
| Administrateur | `admin`        | `Admin123!`       |
| Caissier       | `caissier`     | `Caisse123!`      |
| Moniteur       | `moniteur1`    | `Moniteur123!`    |
| Réceptionniste | `receptionniste` | `Reception123!` |

### ❌ Erreur "unable to open database file" ?

Si vous voyez cette erreur :

```
sqlite3.OperationalError: unable to open database file
```

**Cause** : La base de données n'a pas été initialisée ou est inaccessible.

**Solution** :

1. Assurez-vous d'avoir exécuté `python src/init_db.py` AVANT
2. Vérifiez que le fichier `data/autoecole.db` existe
3. Vérifiez les permissions du dossier `data/`

### 🔄 Réinitialiser la Base de Données

Pour repartir de zéro :

```bash
# Supprimer la base existante
rm data/autoecole.db  # Linux/Mac
del data\autoecole.db  # Windows

# Réinitialiser
python src/init_db.py
```

### 📦 Dépendances Requises

Assurez-vous d'avoir installé :

```bash
pip install -r requirements.txt
```

Principalement :
- PySide6 (interface graphique)
- SQLAlchemy (base de données)
- Other dependencies...

### 🎉 C'est Prêt !

Une fois la base initialisée, vous pouvez utiliser l'application normalement.

---

**Date** : 2025-12-09  
**Version** : 1.0.0  
**Support** : Voir README.md pour plus de détails
