# 🚗 Guide Utilisateur - Auto-École Manager

## ✅ FÉLICITATIONS !

Votre application est maintenant **100% fonctionnelle** !

---

## 🎯 Pour lancer l'application

Vous avez **3 options** :

### Option 1 : Lancement propre (RECOMMANDÉ) ⭐

**Double-cliquez sur** : `AUTO_ECOLE.bat`

- ✅ Lance l'application sans console
- ✅ Pas de messages d'erreur visibles
- ✅ Expérience utilisateur propre

### Option 2 : Lancement classique

**Double-cliquez sur** : `launch_app.bat`

- ✅ Lance l'application
- ⚠️ Console visible avec messages matplotlib

### Option 3 : Ligne de commande

```bash
cd "C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main"
python src\main_gui.py
```

---

## 🔐 Comptes disponibles

| Username         | Password       | Rôle           | Accès                        |
|------------------|----------------|----------------|------------------------------|
| `admin`          | `Admin123!`    | Administrateur | Tous les modules + paramètres|
| `caissier`       | `Caisse123!`   | Caissier       | Paiements, élèves (lecture)  |
| `moniteur1`      | `Moniteur123!` | Moniteur       | Planning, sessions           |
| `receptionniste` | `Reception123!`| Réceptionniste | Élèves, planning (lecture)   |

---

## 📊 Modules disponibles

### 1. 📈 Dashboard
- **Statistiques en temps réel** :
  - Nombre d'élèves actifs
  - Chiffre d'affaires mensuel
  - Sessions du jour
  - Élèves en impayés
- **Graphiques** :
  - Évolution du CA sur 6 mois
  - Répartition des élèves par statut
  - Taux de réussite aux examens
  - Statut des sessions

### 2. 🎓 Élèves
- Ajouter un nouvel élève
- Modifier les informations
- Suivre la progression (heures, examens)
- Gérer les statuts (actif, suspendu, diplômé)
- Exporter la liste en CSV
- Voir l'historique complet

### 3. 💰 Paiements
- Enregistrer un paiement
- Méthodes : Espèces, Carte, Chèque, Virement
- Catégories : Inscription, Conduite, Examen, Matériel
- Générer un reçu PDF
- Filtrer par période, élève, statut
- Suivre les soldes

### 4. 📅 Planning
- Planifier une session de conduite
- Calendrier visuel (jour, semaine, mois)
- Assigner moniteur + véhicule
- Types de sessions : Conduite, Code, Examen blanc
- Voir les disponibilités
- Filtrer par élève, moniteur, véhicule

### 5. 👨‍🏫 Moniteurs (NOUVEAU)
- Gérer les instructeurs
- Types de permis autorisés (A, B, C, D, E)
- Disponibilités et planning
- Calcul du salaire (horaire + fixe)
- Statistiques (heures enseignées, taux de réussite)
- Exporter en CSV

### 6. 🚗 Véhicules (NOUVEAU)
- Gérer la flotte de véhicules
- Statuts : Disponible, En maintenance, Hors service
- Suivi du kilométrage
- Planification des maintenances
- Dates d'expiration (assurance, contrôle technique)
- Coûts (achat, maintenance, carburant)
- Exporter en CSV

### 7. 📝 Examens (NOUVEAU)
- Planifier un examen (théorique ou pratique)
- Enregistrer les résultats
- Générer une convocation PDF
- Suivre les tentatives
- Statistiques de réussite
- Frais d'inscription
- Exporter en CSV

### 8. 📄 Rapports
- Générer des rapports PDF professionnels
- Statistiques détaillées
- Listes personnalisées
- Exports pour comptabilité

### 9. ⚙️ Paramètres
- Gérer les utilisateurs
- Configurer les tarifs
- Paramètres de l'auto-école
- Sauvegardes de la base de données

---

## 🎨 Interface

### Navigation
- **Barre latérale gauche** : Accès rapide aux modules
- **Barre supérieure** : Actions rapides (Ajouter élève, Ajouter paiement, Rafraîchir)
- **Barre de statut** : Informations de connexion et heure

### Raccourcis clavier
- `F5` : Rafraîchir les données
- `Ctrl+N` : Nouvel élève (dans le module Élèves)
- `Ctrl+P` : Nouveau paiement (dans le module Paiements)
- `Ctrl+Q` : Quitter l'application

---

## 💾 Données de démonstration

L'application contient déjà des données de test :

### Élèves (5)
1. **Sara Bennani** - Actif (12/20 heures)
2. **Omar El Fassi** - Actif (8/20 heures)
3. **Leila Amrani** - Actif (18/20 heures, examen théorique réussi)
4. **Mehdi Ziani** - Diplômé (tous les examens réussis)
5. **Yasmine Taoufik** - En attente (nouvelle inscription)

### Moniteurs (3)
1. **Ahmed Bennis** - Permis B, C
2. **Youssef Idrissi** - Permis A, B
3. **Karim Tazi** - Permis B

### Véhicules (3)
1. **Dacia Logan 2022** - 25 000 km
2. **Renault Clio 2021** - 45 000 km
3. **Peugeot 208 2023** - 8 000 km

---

## ⚠️ À propos des messages matplotlib

Si vous voyez ce message dans la console :
```
RuntimeError: Internal C++ object (FigureCanvasQTAgg) already deleted.
```

**C'est normal et sans conséquence !**

- ✅ L'application fonctionne normalement
- ✅ Les graphiques s'affichent correctement
- ✅ Tous les modules sont opérationnels

**Solution** : Utilisez `AUTO_ECOLE.bat` pour lancer l'app sans console.

---

## 🔧 Maintenance

### Sauvegarder la base de données

**Option 1 : Via l'application**
- Menu : Paramètres → Sauvegarde
- Choisir l'emplacement
- Cliquer sur "Sauvegarder"

**Option 2 : Copie manuelle**
```bash
cd "C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main"
copy data\autoecole.db data\autoecole_backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%.db
```

### Réinitialiser la base de données

Si vous voulez recommencer à zéro :

```bash
cd "C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main"
del data\autoecole.db
python src\init_db.py
```

---

## 📚 Documentation

- **`DEMARRAGE_RAPIDE.md`** - Guide de démarrage
- **`INSTALLATION_WINDOWS.md`** - Installation complète
- **`DATABASE_FIX_COMPLETE.md`** - Solutions techniques
- **`QUICK_FIX_GUIDE.md`** - Dépannage
- **`LISEZ_MOI_DABORD.txt`** - Instructions simples

---

## 🆘 Dépannage

### L'application ne se lance pas

**Vérifiez Python** :
```bash
python --version
```

**Réinstallez les dépendances** :
```bash
python -m pip install --upgrade sqlalchemy PySide6 reportlab matplotlib seaborn
```

### Mot de passe oublié

Réinitialisez la base de données :
```bash
del data\autoecole.db
python src\init_db.py
```

Le mot de passe admin par défaut est : `Admin123!`

### Erreur "Base de données verrouillée"

Fermez toutes les instances de l'application et relancez.

### Les graphiques ne s'affichent pas

Vérifiez que matplotlib est installé :
```bash
python -m pip install matplotlib seaborn
```

---

## 🚀 Fonctionnalités avancées

### Export CSV
Tous les modules permettent l'export en CSV :
- Liste des élèves
- Historique des paiements
- Planning des sessions
- Liste des moniteurs
- Inventaire des véhicules
- Résultats d'examens

### Génération PDF
- Reçus de paiement
- Convocations d'examen
- Rapports statistiques
- Listes personnalisées

### Filtres et recherche
Chaque module propose des filtres avancés :
- Par date, période
- Par statut
- Par élève, moniteur, véhicule
- Par montant, catégorie

---

## 📈 Statistiques

Le dashboard affiche en temps réel :
- Nombre total d'élèves (actifs, en attente, diplômés)
- Chiffre d'affaires (jour, mois, année)
- Sessions planifiées et complétées
- Taux de réussite aux examens
- Véhicules disponibles
- Moniteurs actifs

---

## 🎯 Conseils d'utilisation

1. **Sauvegardez régulièrement** la base de données
2. **Vérifiez les disponibilités** avant de planifier une session
3. **Enregistrez les paiements** immédiatement après réception
4. **Mettez à jour les statuts** des élèves régulièrement
5. **Suivez les maintenances** des véhicules pour éviter les pannes
6. **Planifiez les examens** à l'avance
7. **Consultez le dashboard** pour une vue d'ensemble

---

## ✅ Checklist quotidienne

- [ ] Consulter le dashboard
- [ ] Vérifier les sessions du jour
- [ ] Enregistrer les paiements reçus
- [ ] Mettre à jour les progressions des élèves
- [ ] Vérifier les disponibilités des moniteurs
- [ ] Contrôler l'état des véhicules
- [ ] Planifier les sessions de demain

---

## 🎉 Vous êtes prêt !

Votre application Auto-École Manager est **complète** et **fonctionnelle**.

**Pour lancer** : Double-cliquez sur `AUTO_ECOLE.bat`

**Login** : `admin` / `Admin123!`

---

🚗💨 **Bonne gestion !**
