# 📋 GUIDE DE TEST COMPLET - AUTO-ÉCOLE

**Date**: 2025-12-10  
**Version**: 1.0  
**Objectif**: Tester systématiquement tous les modules et fonctionnalités

---

## 📖 INSTRUCTIONS D'UTILISATION

### Comment utiliser ce guide:

1. **Suivre l'ordre** des modules (Dashboard → Élèves → Planning → etc.)
2. **Tester chaque élément** de la checklist
3. **Noter le résultat**:
   - ✅ **OK** = Fonctionne parfaitement
   - ⚠️ **ATTENTION** = Fonctionne mais avec petits problèmes
   - ❌ **ERREUR** = Ne fonctionne pas du tout
4. **Décrire les problèmes** dans la colonne "Notes"
5. **Prendre des captures d'écran** si nécessaire

---

## 🎯 CHECKLIST GLOBALE

### 0️⃣ DÉMARRAGE DE L'APPLICATION

| Test | Résultat | Notes |
|------|----------|-------|
| Lancement de l'app (python src\main_gui.py) | ⬜ | |
| Fenêtre de connexion s'affiche | ⬜ | |
| Login: admin / Admin123! | ⬜ | |
| Fenêtre principale s'ouvre | ⬜ | |
| Dashboard s'affiche par défaut | ⬜ | |
| Aucune erreur dans le terminal | ⬜ | |

**Notes générales démarrage**:
```
[Écrire ici les observations]
```

---

## 1️⃣ MODULE: LIENS RAPIDES (Header)

### Boutons du header (haut de page)

| Test | Résultat | Notes |
|------|----------|-------|
| 👤 **Nouvel Élève** - Clic sur le bouton | ⬜ | |
| → Dialog "Nouvel Élève" s'ouvre | ⬜ | |
| → Formulaire complet visible | ⬜ | |
| → Fermer sans sauvegarder fonctionne | ⬜ | |
| | | |
| 💳 **Nouveau Paiement** - Clic sur le bouton | ⬜ | |
| → Dialog "Nouveau Paiement" s'ouvre | ⬜ | |
| → Formulaire complet visible | ⬜ | |
| → Fermer sans sauvegarder fonctionne | ⬜ | |
| | | |
| 🚗 **Nouvelle Session** - Clic sur le bouton | ⬜ | |
| → Dialog "Nouvelle Session" s'ouvre | ⬜ | |
| → Formulaire complet visible | ⬜ | |
| → Fermer sans sauvegarder fonctionne | ⬜ | |
| | | |
| 📝 **Nouvel Examen** - Clic sur le bouton | ⬜ | |
| → Dialog "Nouvel Examen" s'ouvre | ⬜ | |
| → Formulaire complet visible | ⬜ | |
| → Fermer sans sauvegarder fonctionne | ⬜ | |
| | | |
| 👨‍🏫 **Nouveau Moniteur** - Clic sur le bouton | ⬜ | |
| → Dialog "Nouveau Moniteur" s'ouvre | ⬜ | |
| → Formulaire complet visible | ⬜ | |
| → Fermer sans sauvegarder fonctionne | ⬜ | |
| | | |
| 🔄 **Actualiser** - Bouton rafraîchir | ⬜ | |
| → Données se rechargent | ⬜ | |

**Problèmes identifiés (Liens rapides)**:
```
1. [Décrire problème 1]
2. [Décrire problème 2]
...
```

---

## 2️⃣ MODULE: DASHBOARD

### Navigation
| Test | Résultat | Notes |
|------|----------|-------|
| Cliquer sur "Dashboard" dans le menu | ⬜ | |
| Dashboard s'affiche | ⬜ | |

### Cartes statistiques (haut)
| Test | Résultat | Notes |
|------|----------|-------|
| **Carte 1**: Nombre d'élèves actifs affiché | ⬜ | |
| **Carte 2**: Chiffre d'affaires affiché (DH) | ⬜ | |
| **Carte 3**: Sessions aujourd'hui affiché | ⬜ | |
| **Carte 4**: Impayés affiché | ⬜ | |
| Les chiffres sont cohérents | ⬜ | |

### Alertes & Notifications (gauche)
| Test | Résultat | Notes |
|------|----------|-------|
| Section "Alertes & Notifications" visible | ⬜ | |
| 🔴 Alerte impayés (si applicable) | ⬜ | |
| 🟠 Alerte sessions planifiées | ⬜ | |
| 🟢 Alerte élèves actifs | ⬜ | |

### Activités Récentes (droite)
| Test | Résultat | Notes |
|------|----------|-------|
| Section "Activités Récentes" visible | ⬜ | |
| Liste des dernières activités affichée | ⬜ | |
| Icônes et dates correctes | ⬜ | |

**Problèmes identifiés (Dashboard)**:
```
1. [Décrire problème 1]
2. [Décrire problème 2]
...
```

---

## 3️⃣ MODULE: ÉLÈVES

### Navigation et affichage
| Test | Résultat | Notes |
|------|----------|-------|
| Cliquer sur "Élèves" dans le menu | ⬜ | |
| Module Élèves s'affiche | ⬜ | |
| Liste des élèves visible dans le tableau | ⬜ | |

### Barre de recherche et filtres
| Test | Résultat | Notes |
|------|----------|-------|
| Barre de recherche visible | ⬜ | |
| Saisir un nom → Résultats filtrés | ⬜ | |
| Filtre par statut (Actif/Inactif/Tous) | ⬜ | |
| Filtre par type de permis | ⬜ | |

### Boutons d'action (haut)
| Test | Résultat | Notes |
|------|----------|-------|
| **Nouvel Élève** - Bouton visible | ⬜ | |
| → Cliquer ouvre le dialog | ⬜ | |
| **Importer CSV** - Bouton visible | ⬜ | |
| → Cliquer ouvre le dialog d'import | ⬜ | |
| **Exporter CSV** - Bouton visible | ⬜ | |
| → Export génère un fichier CSV | ⬜ | |

### Tableau élèves
| Test | Résultat | Notes |
|------|----------|-------|
| Colonnes: Nom, CIN, Téléphone, Permis, Statut, Solde | ⬜ | |
| Données affichées correctement | ⬜ | |
| Tri par colonne fonctionne | ⬜ | |

### Actions sur un élève (boutons dans table)
| Test | Résultat | Notes |
|------|----------|-------|
| **👁️ Voir** - Bouton visible pour chaque élève | ⬜ | |
| → Cliquer ouvre la vue détaillée | ⬜ | |
| **✏️ Modifier** - Bouton visible | ⬜ | |
| → Cliquer ouvre le formulaire d'édition | ⬜ | |
| **🗑️ Supprimer** - Bouton visible | ⬜ | |
| → Confirmation avant suppression | ⬜ | |
| → Suppression fonctionne | ⬜ | |

### Vue détaillée d'un élève (Onglets)
| Test | Résultat | Notes |
|------|----------|-------|
| **Onglet Informations**: Données affichées | ⬜ | |
| **Onglet Paiements**: Liste des paiements | ⬜ | |
| → Ajouter un paiement fonctionne | ⬜ | |
| **Onglet Sessions**: Liste des sessions | ⬜ | |
| **Onglet Documents**: Liste des documents | ⬜ | |
| → Ajouter un document fonctionne | ⬜ | |
| → Voir un document fonctionne | ⬜ | |
| → Supprimer un document fonctionne | ⬜ | |
| **Onglet Examens**: Liste des examens | ⬜ | |
| **Onglet Progression**: Graphique/Stats | ⬜ | |

### Formulaire Nouvel Élève
| Test | Résultat | Notes |
|------|----------|-------|
| Tous les champs affichés | ⬜ | |
| Validation des champs obligatoires | ⬜ | |
| Sauvegarder un élève fonctionne | ⬜ | |
| Message de succès affiché | ⬜ | |
| Élève apparaît dans la liste | ⬜ | |

**Problèmes identifiés (Élèves)**:
```
1. [Décrire problème 1]
2. [Décrire problème 2]
...
```

---

## 4️⃣ MODULE: PLANNING

### Navigation et affichage
| Test | Résultat | Notes |
|------|----------|-------|
| Cliquer sur "Planning" dans le menu | ⬜ | |
| Module Planning s'affiche | ⬜ | |
| Calendrier ou liste visible | ⬜ | |

### Barre d'outils
| Test | Résultat | Notes |
|------|----------|-------|
| **Nouvelle Session** - Bouton visible | ⬜ | |
| → Cliquer ouvre le formulaire | ⬜ | |
| Filtres (par date, moniteur, élève) | ⬜ | |

### Affichage des sessions
| Test | Résultat | Notes |
|------|----------|-------|
| Liste/calendrier des sessions visible | ⬜ | |
| Informations complètes (date, heure, élève, moniteur) | ⬜ | |

### Formulaire Nouvelle Session
| Test | Résultat | Notes |
|------|----------|-------|
| Date et heure | ⬜ | |
| Sélection élève | ⬜ | |
| Sélection moniteur | ⬜ | |
| Sélection véhicule | ⬜ | |
| Type de session | ⬜ | |
| Durée | ⬜ | |
| Sauvegarder fonctionne | ⬜ | |
| Session apparaît dans la liste | ⬜ | |

### Actions sur session
| Test | Résultat | Notes |
|------|----------|-------|
| Modifier une session | ⬜ | |
| Supprimer une session | ⬜ | |
| Marquer comme complétée | ⬜ | |

**Problèmes identifiés (Planning)**:
```
1. [Décrire problème 1]
2. [Décrire problème 2]
...
```

---

## 5️⃣ MODULE: PAIEMENTS

### Navigation et affichage
| Test | Résultat | Notes |
|------|----------|-------|
| Cliquer sur "Paiements" dans le menu | ⬜ | |
| Module Paiements s'affiche | ⬜ | |
| Liste des paiements visible | ⬜ | |

### Barre d'outils
| Test | Résultat | Notes |
|------|----------|-------|
| **Nouveau Paiement** - Bouton | ⬜ | |
| Barre de recherche | ⬜ | |
| Filtres (date, méthode, statut) | ⬜ | |
| **Exporter CSV** | ⬜ | |

### Tableau paiements
| Test | Résultat | Notes |
|------|----------|-------|
| Colonnes: Date, Élève, Montant, Méthode, Statut | ⬜ | |
| Données correctes | ⬜ | |

### Formulaire Nouveau Paiement
| Test | Résultat | Notes |
|------|----------|-------|
| Sélection élève | ⬜ | |
| Montant | ⬜ | |
| Méthode de paiement (Espèces, Carte, etc.) | ⬜ | |
| Catégorie | ⬜ | |
| Description | ⬜ | |
| Sauvegarder fonctionne | ⬜ | |
| Générer reçu PDF | ⬜ | |
| Reçu s'ouvre automatiquement | ⬜ | |

### Actions sur paiement
| Test | Résultat | Notes |
|------|----------|-------|
| Voir détails | ⬜ | |
| Régénérer reçu | ⬜ | |
| Supprimer (si admin) | ⬜ | |

**Problèmes identifiés (Paiements)**:
```
1. [Décrire problème 1]
2. [Décrire problème 2]
...
```

---

## 6️⃣ MODULE: MONITEURS

### Navigation et affichage
| Test | Résultat | Notes |
|------|----------|-------|
| Cliquer sur "Moniteurs" dans le menu | ⬜ | |
| Module Moniteurs s'affiche | ⬜ | |
| Liste des moniteurs visible | ⬜ | |

### Barre d'outils
| Test | Résultat | Notes |
|------|----------|-------|
| **Nouveau Moniteur** - Bouton | ⬜ | |
| Barre de recherche | ⬜ | |
| Filtres (statut, permis) | ⬜ | |

### Tableau moniteurs
| Test | Résultat | Notes |
|------|----------|-------|
| Colonnes: Nom, CIN, Téléphone, Permis, Statut | ⬜ | |
| Données correctes | ⬜ | |

### Formulaire Nouveau Moniteur
| Test | Résultat | Notes |
|------|----------|-------|
| Nom complet | ⬜ | |
| CIN | ⬜ | |
| Téléphone | ⬜ | |
| Email | ⬜ | |
| Date d'embauche | ⬜ | |
| Types de permis enseignés | ⬜ | |
| Salaire | ⬜ | |
| Sauvegarder fonctionne | ⬜ | |

### Actions sur moniteur
| Test | Résultat | Notes |
|------|----------|-------|
| Voir détails | ⬜ | |
| Modifier | ⬜ | |
| Supprimer | ⬜ | |

**Problèmes identifiés (Moniteurs)**:
```
1. [Décrire problème 1]
2. [Décrire problème 2]
...
```

---

## 7️⃣ MODULE: VÉHICULES

### Navigation et affichage
| Test | Résultat | Notes |
|------|----------|-------|
| Cliquer sur "Véhicules" dans le menu | ⬜ | |
| Module Véhicules s'affiche | ⬜ | |
| Liste des véhicules visible | ⬜ | |

### Barre d'outils
| Test | Résultat | Notes |
|------|----------|-------|
| **Nouveau Véhicule** - Bouton | ⬜ | |
| Barre de recherche | ⬜ | |
| Filtres (statut, type) | ⬜ | |

### Tableau véhicules
| Test | Résultat | Notes |
|------|----------|-------|
| Colonnes: Marque, Modèle, Immatriculation, Statut | ⬜ | |
| Données correctes | ⬜ | |

### Formulaire Nouveau Véhicule
| Test | Résultat | Notes |
|------|----------|-------|
| Marque et modèle | ⬜ | |
| Immatriculation | ⬜ | |
| Année | ⬜ | |
| Type de permis | ⬜ | |
| Kilométrage | ⬜ | |
| Statut | ⬜ | |
| Sauvegarder fonctionne | ⬜ | |

### Actions sur véhicule
| Test | Résultat | Notes |
|------|----------|-------|
| Voir détails | ⬜ | |
| Modifier | ⬜ | |
| Ajouter maintenance | ⬜ | |
| Supprimer | ⬜ | |

**Problèmes identifiés (Véhicules)**:
```
1. [Décrire problème 1]
2. [Décrire problème 2]
...
```

---

## 8️⃣ MODULE: EXAMENS

### Navigation et affichage
| Test | Résultat | Notes |
|------|----------|-------|
| Cliquer sur "Examens" dans le menu | ⬜ | |
| Module Examens s'affiche | ⬜ | |
| Liste des examens visible | ⬜ | |

### Barre d'outils
| Test | Résultat | Notes |
|------|----------|-------|
| **Nouvel Examen** - Bouton | ⬜ | |
| Barre de recherche | ⬜ | |
| Filtres (type, résultat, date) | ⬜ | |

### Tableau examens
| Test | Résultat | Notes |
|------|----------|-------|
| Colonnes: Date, Élève, Type, Résultat, Note | ⬜ | |
| Données correctes | ⬜ | |
| Icône 🖨️ Imprimer Convocation | ⬜ | |

### Formulaire Nouvel Examen
| Test | Résultat | Notes |
|------|----------|-------|
| Sélection élève | ⬜ | |
| Type (Théorique/Pratique) | ⬜ | |
| Date et heure | ⬜ | |
| Centre d'examen | ⬜ | |
| Lieu | ⬜ | |
| Numéro de tentative | ⬜ | |
| Sauvegarder fonctionne | ⬜ | |

### Impression Convocation
| Test | Résultat | Notes |
|------|----------|-------|
| Cliquer sur 🖨️ (icône impression) | ⬜ | |
| PDF généré dans docs/export/ | ⬜ | |
| PDF s'ouvre automatiquement | ⬜ | |
| Contenu conforme (FR/AR, infos élève, examen) | ⬜ | |
| Mise en page correcte | ⬜ | |

### Actions sur examen
| Test | Résultat | Notes |
|------|----------|-------|
| Modifier | ⬜ | |
| Enregistrer résultat | ⬜ | |
| Supprimer | ⬜ | |

**Problèmes identifiés (Examens)**:
```
1. [Décrire problème 1]
2. [Décrire problème 2]
...
```

---

## 9️⃣ MODULE: RAPPORTS

### Navigation et affichage
| Test | Résultat | Notes |
|------|----------|-------|
| Cliquer sur "Rapports" dans le menu | ⬜ | |
| Module Rapports s'affiche | ⬜ | |

### Graphiques et statistiques
| Test | Résultat | Notes |
|------|----------|-------|
| Graphique revenus mensuels | ⬜ | |
| Graphique répartition élèves | ⬜ | |
| Graphique taux de réussite examens | ⬜ | |
| Statistiques financières | ⬜ | |

### Filtres et exports
| Test | Résultat | Notes |
|------|----------|-------|
| Filtrer par période (mois, année) | ⬜ | |
| Exporter rapport PDF | ⬜ | |
| Exporter rapport CSV | ⬜ | |

**Problèmes identifiés (Rapports)**:
```
1. [Décrire problème 1]
2. [Décrire problème 2]
...
```

---

## 🔟 MODULE: PARAMÈTRES

### Navigation et affichage
| Test | Résultat | Notes |
|------|----------|-------|
| Cliquer sur "Paramètres" dans le menu | ⬜ | |
| Module Paramètres s'affiche | ⬜ | |

### Onglet Centre
| Test | Résultat | Notes |
|------|----------|-------|
| Informations générales du centre | ⬜ | |
| Informations légales | ⬜ | |
| Logo du centre | ⬜ | |
| → Changer le logo fonctionne | ⬜ | |

### Onglet Général
| Test | Résultat | Notes |
|------|----------|-------|
| Paramètres application | ⬜ | |
| Horaires de travail | ⬜ | |
| Paramètres base de données | ⬜ | |

### Onglet Formats
| Test | Résultat | Notes |
|------|----------|-------|
| Format date | ⬜ | |
| Format heure | ⬜ | |
| Format monétaire | ⬜ | |
| Paramètres PDF | ⬜ | |
| Paramètres rapports | ⬜ | |

### Onglet Sauvegarde (Grid layout)
| Test | Résultat | Notes |
|------|----------|-------|
| 6 cards affichées en grille 3x2 | ⬜ | |
| **Card 1: Créer Sauvegarde** | ⬜ | |
| → Bouton "Exécuter" fonctionne | ⬜ | |
| → Sauvegarde créée dans backups/ | ⬜ | |
| **Card 2: Restaurer Sauvegarde** | ⬜ | |
| → Bouton "Exécuter" fonctionne | ⬜ | |
| **Card 3: Ouvrir Dossier** | ⬜ | |
| → Ouvre le dossier backups/ | ⬜ | |
| **Card 4: Exporter CSV** | ⬜ | |
| **Card 5: Optimiser Base** | ⬜ | |
| → Exécute VACUUM | ⬜ | |
| **Card 6: Synchroniser** | ⬜ | |
| **Section Danger: Réinitialiser** | ⬜ | |
| → Bouton rouge visible | ⬜ | |

### Sauvegarder les paramètres
| Test | Résultat | Notes |
|------|----------|-------|
| Modifier un paramètre | ⬜ | |
| Cliquer sur "Enregistrer" | ⬜ | |
| Message de succès | ⬜ | |
| Paramètre sauvegardé (redémarrer app) | ⬜ | |

**Problèmes identifiés (Paramètres)**:
```
1. [Décrire problème 1]
2. [Décrire problème 2]
...
```

---

## 🔐 GESTION UTILISATEURS & DÉCONNEXION

### Déconnexion
| Test | Résultat | Notes |
|------|----------|-------|
| Bouton "Déconnexion" visible | ⬜ | |
| Cliquer déconnecte l'utilisateur | ⬜ | |
| Retour à l'écran de connexion | ⬜ | |

**Problèmes identifiés (Déconnexion)**:
```
1. [Décrire problème 1]
...
```

---

## 📊 SYNTHÈSE DES TESTS

### Statistiques globales

| Module | Tests OK | Tests KO | Taux réussite |
|--------|----------|----------|---------------|
| Démarrage | __ / 6 | __ | __% |
| Liens rapides | __ / 16 | __ | __% |
| Dashboard | __ / 12 | __ | __% |
| Élèves | __ / 30 | __ | __% |
| Planning | __ / 15 | __ | __% |
| Paiements | __ / 16 | __ | __% |
| Moniteurs | __ / 13 | __ | __% |
| Véhicules | __ / 13 | __ | __% |
| Examens | __ / 19 | __ | __% |
| Rapports | __ / 8 | __ | __% |
| Paramètres | __ / 24 | __ | __% |
| Déconnexion | __ / 3 | __ | __% |
| **TOTAL** | __ / 175 | __ | __% |

---

## 🐛 LISTE DES PROBLÈMES IDENTIFIÉS

### Priorité HAUTE (Bloquants) 🔴

```
1. [Module] - [Description du problème]
   → Impact: [Décrire l'impact]
   → Reproduction: [Étapes pour reproduire]

2. ...
```

### Priorité MOYENNE (Gênants) 🟠

```
1. [Module] - [Description du problème]
   → Impact: [Décrire l'impact]
   
2. ...
```

### Priorité BASSE (Cosmétiques) 🟡

```
1. [Module] - [Description du problème]
   → Impact: [Décrire l'impact]
   
2. ...
```

---

## 📸 CAPTURES D'ÉCRAN

Joindre les captures d'écran numérotées:

```
capture_01_[description].png
capture_02_[description].png
...
```

---

## ✅ VALIDATION FINALE

- [ ] Tous les tests sont complétés
- [ ] Tous les problèmes sont documentés
- [ ] Captures d'écran jointes si nécessaire
- [ ] Prêt pour correction des bugs

**Date de fin des tests**: ___________  
**Testeur**: ___________

---

**FIN DU GUIDE DE TEST**
