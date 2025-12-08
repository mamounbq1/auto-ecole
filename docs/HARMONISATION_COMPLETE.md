# 🎨 Harmonisation Complète de l'Application

Ce document décrit l'harmonisation complète de l'application **Auto-École Manager** avec les informations du centre configurables.

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Modules harmonisés](#modules-harmonisés)
4. [Utilisation](#utilisation)
5. [Tests](#tests)

---

## 🎯 Vue d'ensemble

### Objectif

Créer une application **100% brandée** où les informations du centre (nom, adresse, contact, logo, etc.) apparaissent automatiquement dans **tous** les modules, documents et exports.

### Principe

**"Configure une fois, affiche partout"**

1. L'utilisateur configure les infos du centre dans **⚙️ Paramètres**
2. Les informations sont sauvegardées dans `config.json`
3. Le `ConfigManager` (singleton) fournit un accès centralisé
4. Tous les modules utilisent le `ConfigManager` pour afficher les infos
5. Résultat : **cohérence visuelle totale** et **professionnalisme**

---

## 🏗️ Architecture

### 1. ConfigManager (Singleton)

**Fichier** : `src/utils/config_manager.py`

**Rôle** : Gestionnaire centralisé de configuration

```python
from src.utils.config_manager import get_config_manager

config = get_config_manager()
center = config.get_center_info()  # Toutes les infos
name = config.get_center_name()    # Juste le nom
logo = config.get_logo_path()      # Chemin du logo
```

**Méthodes principales** :
- `get_center_info()` - Dict complet des infos du centre
- `get_center_name()` - Nom du centre
- `get_center_address()` - Adresse formatée
- `get_center_contact()` - Ligne de contact
- `get_center_legal_info()` - Infos légales (SIRET, TVA, etc.)
- `get_logo_path()` - Chemin du logo
- `format_center_header()` - En-tête formaté pour documents
- `format_center_footer()` - Pied de page formaté

### 2. Common Widgets

**Fichier** : `src/views/widgets/common_widgets.py`

**Rôle** : Widgets réutilisables pour l'interface

```python
from src.views.widgets.common_widgets import (
    create_center_header_widget,
    create_info_card,
    create_stat_card
)

# En-tête du centre (mode compact ou complet)
header = create_center_header_widget(compact=True)
layout.addWidget(header)
```

**Composants disponibles** :
- `create_center_header_widget(compact=False)` - En-tête avec gradient violet
- `create_info_card(title, content, color)` - Carte d'information
- `create_stat_card(title, value, icon, color, subtitle)` - Carte statistique

### 3. PDF Generator

**Fichier** : `src/utils/pdf_generator.py`

**Rôle** : Génération de documents PDF professionnels

**Méthodes harmonisées** :
- `_create_center_header(story, doc_title)` - En-tête PDF avec logo + infos
- `_create_center_footer(canvas, doc)` - Pied de page PDF
- `generate_receipt()` - Reçu de paiement
- `generate_contract()` - Contrat d'inscription
- `generate_summons()` - Convocation d'examen

**Tous les PDFs incluent automatiquement** :
- Logo du centre (si disponible)
- Nom en grand (bold, uppercase)
- Adresse complète
- Contact (téléphone, email, site web)
- Infos légales (agrément, SIRET, TVA)
- Pied de page avec numéro de page

### 4. Export Manager

**Fichier** : `src/utils/export.py`

**Rôle** : Exports de données (CSV, etc.)

**Harmonisation** :
- Tous les exports CSV incluent un en-tête avec les infos du centre
- Format :
  ```
  # Auto-École Excellence
  # 123 Avenue Mohammed V
  # Tél: +212 5XX-XXXXXX | Email: contact@...
  # Exporté le 08/12/2024 à 15:30
  #
  [données CSV...]
  ```

---

## ✅ Modules Harmonisés

### Interface Utilisateur

| Module | En-tête Centre | Status |
|--------|---------------|---------|
| **Dashboard Principal** | ✅ Oui (compact) | ✅ Terminé |
| **Paiements Dashboard** | ✅ Oui (compact) | ✅ Terminé |
| **Moniteurs Dashboard** | ✅ Oui (compact) | ✅ Terminé |
| **Véhicules Dashboard** | ✅ Oui (compact) | ✅ Terminé |
| **Examens Dashboard** | ✅ Oui (compact) | ✅ Terminé |
| **Rapports** | ✅ Oui (complet) | ✅ Terminé |
| **Paramètres** | ⚙️ Config | ✅ Terminé |

### Documents PDF

| Document | En-tête | Pied de page | Status |
|----------|---------|--------------|---------|
| **Reçu de paiement** | ✅ Oui | ✅ Oui | ✅ Terminé |
| **Contrat d'inscription** | ✅ Oui | ✅ Oui | ✅ Terminé |
| **Convocation d'examen** | ✅ Oui | ✅ Oui | ✅ Terminé |

### Exports de Données

| Export | En-tête Centre | Status |
|--------|---------------|---------|
| **CSV Élèves** | ✅ Oui | ✅ Terminé |
| **CSV Paiements** | ✅ Oui | ✅ Terminé |
| **CSV Sessions** | ✅ Oui | ✅ Terminé |
| **CSV Moniteurs** | ✅ Oui | ✅ Terminé |
| **CSV Véhicules** | ✅ Oui | ✅ Terminé |
| **CSV Examens** | ✅ Oui | ✅ Terminé |

---

## 💻 Utilisation

### Configuration Initiale

1. **Lancer l'application**
   ```bash
   python start_safe.py
   ```

2. **Accéder aux Paramètres**
   - Cliquer sur **⚙️ Paramètres** dans le menu latéral

3. **Remplir les informations**
   - **Onglet "🏢 Informations du Centre"** :
     - Nom, adresse, ville, code postal
     - Téléphone, email, site web
     - SIRET/ICE, TVA, agrément
     - Logo (PNG/JPG/SVG)
   
4. **Sauvegarder**
   - Cliquer sur **💾 Sauvegarder Tout**
   - Message de confirmation attendu

5. **Vérifier**
   - Les infos apparaissent immédiatement dans tous les modules !

### Vérification Visuelle

**Dashboards** :
- Aller dans chaque module (Paiements, Moniteurs, Véhicules, Examens, Rapports)
- Vérifier l'en-tête du centre en haut de chaque dashboard
- Design : gradient violet, nom en gras, contact

**PDFs** :
1. Aller dans **💰 Paiements** → Cliquer sur un paiement → **Générer reçu PDF**
2. Ouvrir le PDF → Vérifier en-tête + pied de page
3. Même chose pour contrats et convocations

**Exports CSV** :
1. Aller dans n'importe quel module
2. Cliquer sur **📤 Exporter CSV**
3. Ouvrir le fichier CSV avec Excel/LibreOffice
4. Vérifier les 4 premières lignes (en-tête commenté avec #)

---

## 🧪 Tests

### Plan de Tests Complet

#### Phase 1 : Configuration (5 min)

**Actions** :
1. Aller dans **⚙️ Paramètres**
2. Remplir tous les champs de "Informations du Centre"
3. Uploader un logo (PNG recommandé)
4. Cliquer sur **💾 Sauvegarder Tout**

**Résultat attendu** :
- ✅ Message "Configuration sauvegardée avec succès!"
- ✅ Le logo apparaît dans l'aperçu

---

#### Phase 2 : Dashboards (10 min)

**Modules à tester** :
1. 📊 Dashboard Principal
2. 💰 Paiements
3. 👨‍🏫 Moniteurs
4. 🚗 Véhicules
5. 📝 Examens
6. 📊 Rapports

**Pour chaque module** :
- [ ] En-tête du centre visible en haut
- [ ] Nom du centre correct (uppercase)
- [ ] Contact affiché (téléphone | email)
- [ ] Design : gradient violet
- [ ] Texte blanc sur fond gradient

---

#### Phase 3 : Documents PDF (15 min)

**Test 1 : Reçu de Paiement**

1. Aller dans **💰 Paiements**
2. Sélectionner un paiement existant
3. Cliquer sur **Générer reçu PDF** (ou créer un paiement)
4. Ouvrir le PDF généré

**Vérifications** :
- [ ] Logo du centre en haut (si configuré)
- [ ] Nom du centre en grand (bold, uppercase)
- [ ] Adresse complète affichée
- [ ] Contact (tél, email, site web)
- [ ] Infos légales (agrément, SIRET, TVA)
- [ ] Ligne de séparation bleue
- [ ] Pied de page avec contact + numéro de page
- [ ] Titre "REÇU DE PAIEMENT" visible

**Test 2 : Contrat d'Inscription**

1. Aller dans **👥 Élèves**
2. Sélectionner un élève
3. Générer un contrat PDF

**Vérifications** :
- [ ] Même en-tête que le reçu
- [ ] Nom du centre dans le corps du contrat
- [ ] Format professionnel

**Test 3 : Convocation d'Examen**

1. Aller dans **📝 Examens**
2. Sélectionner un examen
3. Générer une convocation PDF

**Vérifications** :
- [ ] Même en-tête que les autres documents
- [ ] Cohérence visuelle totale

---

#### Phase 4 : Exports CSV (10 min)

**Modules à tester** :
- Élèves, Paiements, Sessions, Moniteurs, Véhicules, Examens

**Pour chaque module** :

1. Cliquer sur **📤 Exporter CSV**
2. Ouvrir le fichier CSV avec Excel/LibreOffice/Notepad

**Vérifications** :
- [ ] Ligne 1: `# [Nom du centre]`
- [ ] Ligne 2: `# [Adresse]` (si configurée)
- [ ] Ligne 3: `# Tél: ... | Email: ...`
- [ ] Ligne 4: `# Exporté le [date] à [heure]`
- [ ] Ligne 5: `#` (séparateur)
- [ ] Ligne 6: En-têtes des colonnes
- [ ] Ligne 7+: Données

**Note** : Les lignes commentées (#) sont ignorées par Excel lors de l'import

---

#### Phase 5 : Persistance (5 min)

**Test de Persistance**

1. Modifier les infos du centre dans **⚙️ Paramètres**
2. Sauvegarder
3. Aller dans **📊 Dashboard** → Vérifier changement
4. Aller dans **📊 Rapports** → Vérifier changement
5. **Fermer complètement l'application**
6. **Relancer** : `python start_safe.py`
7. Vérifier que les changements sont conservés

**Résultat attendu** :
- ✅ Les modifications persistent après redémarrage
- ✅ Fichier `config.json` mis à jour correctement

---

#### Phase 6 : Edge Cases (5 min)

**Test 1 : Infos Manquantes**

1. Aller dans **⚙️ Paramètres**
2. Laisser certains champs vides (ex: email, site web)
3. Sauvegarder
4. Vérifier que l'application ne crash pas
5. Vérifier que seules les infos renseignées apparaissent

**Test 2 : Logo Invalide**

1. Essayer d'uploader un fichier non-image
2. Vérifier message d'erreur ou rejet

**Test 3 : Suppression du Logo**

1. Uploader un logo
2. Cliquer sur **🗑️ Supprimer**
3. Sauvegarder
4. Vérifier que le logo n'apparaît plus dans les PDFs

---

### Grille de Tests Rapide

| Zone | Vérification | Status | Notes |
|------|--------------|--------|-------|
| **Paramètres** | Config sauvegardée | ⏳ | |
| **Dashboard** | En-tête visible | ⏳ | |
| **Paiements** | En-tête visible | ⏳ | |
| **Moniteurs** | En-tête visible | ⏳ | |
| **Véhicules** | En-tête visible | ⏳ | |
| **Examens** | En-tête visible | ⏳ | |
| **Rapports** | En-tête visible | ⏳ | |
| **PDF Reçu** | En-tête + pied de page | ⏳ | |
| **PDF Contrat** | En-tête + pied de page | ⏳ | |
| **PDF Convocation** | En-tête + pied de page | ⏳ | |
| **CSV Élèves** | En-tête commenté | ⏳ | |
| **CSV Paiements** | En-tête commenté | ⏳ | |
| **CSV Moniteurs** | En-tête commenté | ⏳ | |
| **Persistance** | Après redémarrage | ⏳ | |

---

## 🎨 Design System

### Couleurs Principales

- **Gradient Violet** : `#667eea` → `#764ba2`
- **Bleu Primaire** : `#3498db`
- **Vert Succès** : `#27ae60`
- **Orange Avertissement** : `#f39c12`
- **Rouge Erreur** : `#e74c3c`

### Typographie

- **Titres** : Segoe UI / Helvetica, Bold, 18-24px
- **Sous-titres** : Segoe UI / Helvetica, 14-16px
- **Corps** : Segoe UI / Helvetica, 11-13px
- **Notes** : Segoe UI / Helvetica, 9-10px

### Espacement

- **Marges** : 20px
- **Espacement** : 15-20px entre éléments
- **Padding** : 15px dans les cards
- **Border-radius** : 8-12px

---

## 📊 Statistiques d'Harmonisation

### Code

- **Fichiers modifiés** : 8
- **Fichiers créés** : 2
- **Lignes ajoutées** : ~600
- **Modules harmonisés** : 6 dashboards + 3 PDFs + 6 exports CSV = **15 modules**

### Couverture

- **Dashboards** : 100% (6/6)
- **PDFs** : 100% (3/3)
- **Exports CSV** : 100% (6/6)
- **Configuration** : 100% (1/1)

### Impact

- **Une seule configuration** → **15 endroits différents**
- **Ratio d'efficacité** : 1:15
- **Temps de configuration** : **5 minutes**
- **Temps gagné** : **Des heures** de maintenance

---

## 🚀 Prochaines Améliorations

### Court terme
- [ ] Emails automatiques avec signature du centre
- [ ] Factures avec en-tête/pied de page
- [ ] Attestations de formation

### Moyen terme
- [ ] Templates de documents personnalisables
- [ ] Multi-langues dans les documents
- [ ] QR Code avec infos du centre

### Long terme
- [ ] Thèmes personnalisables (couleurs du centre)
- [ ] Modèles de documents multiples
- [ ] Intégration réseau social (logo/infos automatiques)

---

## 📞 Support

### Problèmes Courants

**Les infos ne s'affichent pas ?**
1. Vérifiez la sauvegarde dans Paramètres
2. Rechargez le module (bouton 🔄)
3. Redémarrez l'application
4. Vérifiez `config.json` (syntaxe JSON valide)

**Le logo ne s'affiche pas ?**
1. Format supporté : PNG, JPG, JPEG, SVG
2. Taille max : 500 KB recommandé
3. Chemin correct dans config.json
4. Fichier existe dans `src/resources/`

**Les PDFs sont vides ?**
1. Vérifiez les données source (élèves, paiements, etc.)
2. Regardez les logs pour erreurs
3. Testez avec données de test

### Logs

```bash
# Logs de l'application
tail -f logs/autoecole.log

# Rechercher erreurs
grep -i error logs/autoecole.log
```

---

## ✅ Checklist de Déploiement

Avant de déployer en production :

- [ ] Configurer toutes les infos du centre dans Paramètres
- [ ] Uploader un logo professionnel (PNG transparent)
- [ ] Tester génération de 1 reçu PDF
- [ ] Tester génération de 1 contrat PDF
- [ ] Tester génération de 1 convocation PDF
- [ ] Tester 1 export CSV
- [ ] Vérifier tous les dashboards
- [ ] Faire un backup de `config.json`
- [ ] Former les utilisateurs

---

**Dernière mise à jour** : 08/12/2024  
**Version** : 2.0.0  
**Status** : ✅ Harmonisation 100% terminée
