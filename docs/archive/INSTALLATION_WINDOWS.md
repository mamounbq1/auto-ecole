# 🚗 Installation Auto-École Manager - Windows

## 🚨 PROBLÈME RÉSOLU : "unable to open database file"

Le problème vient du fait que le dossier `data/` et la base de données n'existent pas sur votre machine Windows.

---

## ✅ SOLUTION RAPIDE (Recommandée)

### Option 1 : Double-clic sur les fichiers .bat

1. **Ouvrez l'Explorateur Windows**
2. **Naviguez vers** : `C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main`
3. **Double-cliquez sur** : `setup_database.bat`
   - Cela va créer le dossier `data/`
   - Initialiser la base de données
   - Créer des données de démonstration
4. **Ensuite, double-cliquez sur** : `launch_app.bat`
   - Cela lance l'application automatiquement

---

## 📋 Option 2 : Ligne de commande

### Étape 1 : Ouvrir le Terminal

1. Appuyez sur `Windows + R`
2. Tapez `cmd` et appuyez sur Entrée
3. Naviguez vers le projet :

```bash
cd "C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main"
```

### Étape 2 : Initialiser la base de données

```bash
setup_database.bat
```

**Ce script va :**
- ✅ Créer le dossier `data/`
- ✅ Créer la base de données SQLite
- ✅ Créer toutes les tables
- ✅ Insérer des données de démonstration :
  - 4 utilisateurs (admin, caissier, moniteur, réceptionniste)
  - 5 élèves
  - 3 moniteurs
  - 3 véhicules
  - Des sessions, paiements, et examens

### Étape 3 : Lancer l'application

```bash
python src\main_gui.py
```

**Ou utilisez le lanceur automatique :**

```bash
launch_app.bat
```

---

## 🔐 Comptes de connexion

Après l'initialisation, vous pouvez vous connecter avec :

| Rôle          | Username         | Mot de passe     |
|---------------|------------------|------------------|
| **Admin**     | `admin`          | `Admin123!`      |
| Caissier      | `caissier`       | `Caisse123!`     |
| Moniteur      | `moniteur1`      | `Moniteur123!`   |
| Réception     | `receptionniste` | `Reception123!`  |

---

## 📂 Structure créée

Après l'installation, vous aurez :

```
C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main\
├── data/                    ← NOUVEAU dossier créé
│   └── autoecole.db         ← Base de données SQLite
├── src/
│   ├── main_gui.py
│   ├── init_db.py
│   └── ...
├── setup_database.bat       ← Script d'installation
└── launch_app.bat           ← Lanceur d'application
```

---

## ❓ Dépannage

### Problème : "Python n'est pas reconnu"

**Solution :**
```bash
python --version
```

Si cette commande ne fonctionne pas :
1. Vérifiez que Python est installé (Python 3.8+)
2. Ajoutez Python au PATH Windows
3. Ou utilisez `py` au lieu de `python`

### Problème : "Module 'sqlalchemy' not found"

**Solution :**
```bash
python -m pip install sqlalchemy PySide6 reportlab
```

### Problème : "Permission denied"

**Solution :**
- Exécutez le terminal en tant qu'administrateur
- Ou déplacez le projet dans un dossier sans restriction

### Problème : La base existe déjà et je veux recommencer

**Solution :**
```bash
cd "C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main"
del data\autoecole.db
python src\init_db.py
```

---

## 🎯 Après l'installation

### 1. Vérifier que tout fonctionne

```bash
cd "C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main"
python check_imports.py
```

Vous devriez voir :
```
✓ All core models imported successfully
✓ All controllers imported successfully
✓ Database session created successfully
✓ All critical imports working!
✓ Backend is fully functional!
```

### 2. Lancer l'application

```bash
launch_app.bat
```

Ou :

```bash
python src\main_gui.py
```

### 3. Se connecter

- **Username :** `admin`
- **Password :** `Admin123!`

---

## 📊 Données de démonstration incluses

L'initialisation crée automatiquement :

- **5 élèves** avec différents statuts (actif, diplômé, en attente)
- **3 moniteurs** avec spécialités différentes
- **3 véhicules** (Dacia Logan, Renault Clio, Peugeot 208)
- **Paiements** pour tester le module financier
- **Sessions de conduite** complétées et à venir
- **Examens** théoriques et pratiques (réussis, échoués, à venir)

Cela vous permet de tester immédiatement toutes les fonctionnalités !

---

## ✅ Checklist d'installation

- [ ] Naviguer vers `C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main`
- [ ] Exécuter `setup_database.bat`
- [ ] Vérifier que `data\autoecole.db` existe
- [ ] Lancer `launch_app.bat` ou `python src\main_gui.py`
- [ ] Se connecter avec `admin / Admin123!`
- [ ] Accéder au Dashboard et voir les statistiques

---

## 🚀 Prochaines étapes

Une fois l'application lancée, vous pouvez :

1. **Explorer le Dashboard** - Voir les statistiques en temps réel avec graphiques
2. **Gérer les Élèves** - Ajouter, modifier, suivre la progression
3. **Gérer les Paiements** - Enregistrer les transactions financières
4. **Planifier les Sessions** - Organiser les cours de conduite
5. **Gérer les Moniteurs** - Suivre les disponibilités et salaires
6. **Gérer les Véhicules** - Maintenance et statuts de la flotte
7. **Gérer les Examens** - Planifier et enregistrer les résultats

---

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifiez les logs dans la console
2. Consultez `QUICK_FIX_GUIDE.md` pour les erreurs communes
3. Exécutez `python check_imports.py` pour diagnostiquer
4. Vérifiez que vous avez bien exécuté `setup_database.bat`

---

## 🎉 C'est tout !

Vous êtes maintenant prêt à utiliser l'application Auto-École Manager !

**Commande rapide pour tout faire :**

```bash
cd "C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main" && setup_database.bat && launch_app.bat
```

Bon courage ! 🚗💨
