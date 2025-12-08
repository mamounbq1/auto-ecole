# 🚀 DÉMARRAGE RAPIDE - Auto-École Manager

## ⚡ INSTALLATION EN 2 ÉTAPES

### Étape 1 : Initialiser la base de données

**Double-cliquez sur** : `SIMPLE_SETUP.bat`

- Cela va créer la base de données automatiquement
- Des données de démonstration seront ajoutées
- Attendez que le message "INSTALLATION TERMINEE" s'affiche

### Étape 2 : Lancer l'application

**Double-cliquez sur** : `launch_app.bat`

- L'application va démarrer
- Connectez-vous avec :
  - **Username** : `admin`
  - **Password** : `Admin123!`

---

## 🎯 C'est tout !

Vous êtes maintenant prêt à utiliser l'application.

---

## 📋 Autres comptes disponibles

| Username         | Password       | Rôle           |
|------------------|----------------|----------------|
| `admin`          | `Admin123!`    | Administrateur |
| `caissier`       | `Caisse123!`   | Caissier       |
| `moniteur1`      | `Moniteur123!` | Moniteur       |
| `receptionniste` | `Reception123!`| Réceptionniste |

---

## ❓ Problèmes ?

### Python non trouvé
- Installez Python 3.8+ depuis [python.org](https://www.python.org/downloads/)
- Cochez "Add Python to PATH" pendant l'installation

### Base de données non créée
```bash
cd "C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main"
python src\init_db.py
```

### Erreur matplotlib
Ignorez l'erreur `RuntimeError: FigureCanvasQTAgg` dans la console - c'est un bug mineur qui n'empêche pas l'application de fonctionner.

---

## 📂 Fichiers créés

Après l'installation :
```
data\
└── autoecole.db   ← Base de données SQLite (~500 KB)
```

---

## 🔄 Recommencer l'installation

Si vous voulez recommencer :

1. Supprimez le fichier : `data\autoecole.db`
2. Double-cliquez sur : `SIMPLE_SETUP.bat`

---

## 📚 Documentation complète

- `INSTALLATION_WINDOWS.md` - Guide détaillé
- `DATABASE_FIX_COMPLETE.md` - Solutions aux problèmes
- `QUICK_FIX_GUIDE.md` - Dépannage rapide

---

🚗💨 **Bon démarrage !**
