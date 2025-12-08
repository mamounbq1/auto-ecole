# 🏢 Configuration des Informations du Centre

Ce guide explique comment configurer les informations de votre auto-école qui apparaîtront dans tous les rapports.

## 📋 Table des Matières

1. [Configuration via l'interface](#configuration-via-linterface)
2. [Configuration manuelle](#configuration-manuelle)
3. [Champs disponibles](#champs-disponibles)
4. [Utilisation dans les rapports](#utilisation-dans-les-rapports)

---

## 🎯 Configuration via l'interface

**C'est la méthode recommandée** - simple et intuitive.

### Étapes :

1. **Lancez l'application**
   ```bash
   python start_safe.py
   ```

2. **Connectez-vous** avec vos identifiants

3. **Accédez aux Paramètres**
   - Cliquez sur **⚙️ Paramètres** dans le menu latéral

4. **Remplissez les informations**
   - Onglet **🏢 Informations du Centre** :
     - **Informations Principales** : nom, adresse, ville, code postal, téléphone, email, site web
     - **Informations Légales** : SIRET/ICE, TVA, numéro d'agrément, directeur
     - **Logo** : choisissez une image (PNG, JPG, SVG)

5. **Sauvegardez**
   - Cliquez sur **💾 Sauvegarder Tout** en haut à droite

6. **Vérifiez**
   - Allez dans **📊 Rapports**
   - Vous devriez voir votre en-tête personnalisé !

---

## 🔧 Configuration manuelle

Si vous préférez modifier directement le fichier de configuration :

### 1. Éditez `config.json`

Ajoutez la section `center` :

```json
{
  "center": {
    "name": "Auto-École Excellence",
    "address": "123 Avenue Mohammed V",
    "city": "Casablanca",
    "postal_code": "20000",
    "phone": "+212 5XX-XXXXXX",
    "email": "contact@autoecole-excellence.ma",
    "website": "www.autoecole-excellence.ma",
    "siret": "123456789",
    "tva_number": "MA123456789",
    "license_number": "AE-2024-001",
    "director_name": "Mohammed ALAMI"
  }
}
```

### 2. Fichier d'exemple

Un fichier `config.example.json` est fourni avec toutes les options disponibles.

---

## 📝 Champs disponibles

### Informations Principales

| Champ | Description | Exemple | Obligatoire |
|-------|-------------|---------|-------------|
| `name` | Nom de votre auto-école | "Auto-École Excellence" | ✅ Oui |
| `address` | Adresse complète | "123 Avenue Mohammed V" | ⭐ Recommandé |
| `city` | Ville | "Casablanca" | ⭐ Recommandé |
| `postal_code` | Code postal | "20000" | ❌ Non |
| `phone` | Numéro de téléphone | "+212 5XX-XXXXXX" | ⭐ Recommandé |
| `email` | Adresse email | "contact@..." | ⭐ Recommandé |
| `website` | Site web | "www.autoecole..." | ❌ Non |

### Informations Légales

| Champ | Description | Exemple | Obligatoire |
|-------|-------------|---------|-------------|
| `siret` | Numéro SIRET/ICE | "123456789" | ⭐ Recommandé |
| `tva_number` | Numéro de TVA | "MA123456789" | ❌ Non |
| `license_number` | Numéro d'agrément | "AE-2024-001" | ⭐ Recommandé |
| `director_name` | Nom du directeur | "Mohammed ALAMI" | ❌ Non |

### Logo

| Champ | Description | Formats supportés |
|-------|-------------|-------------------|
| `company_logo` | Chemin vers le logo | PNG, JPG, JPEG, SVG |

**Ajout du logo :**
- Via l'interface : **⚙️ Paramètres** → **🏢 Informations du Centre** → **🖼️ Logo du Centre** → **📁 Choisir un logo**
- Manuellement : placez votre logo dans `src/resources/` et mettez à jour `pdf.company_logo` dans `config.json`

---

## 📊 Utilisation dans les rapports

### Où apparaissent ces informations ?

Les informations du centre apparaissent automatiquement dans :

1. **📊 Module Rapports**
   - En-tête de chaque rapport
   - Affichage en grand avec design professionnel
   - Gradient violet élégant

2. **📄 Exports PDF** *(À venir)*
   - En-tête des factures
   - Pied de page des documents
   - Logo du centre

3. **📧 Emails** *(À venir)*
   - Signature automatique
   - En-tête des notifications

### Format d'affichage dans les rapports

```
┌─────────────────────────────────────────┐
│   AUTO-ÉCOLE EXCELLENCE                 │
│   123 Avenue Mohammed V                 │
│   20000 Casablanca                      │
│                                         │
│   📞 +212 5XX-XX   📧 contact@...       │
│   Agrément N° AE-2024-001 | SIRET: ...  │
│   📅 Rapport généré le 08/12/2024       │
└─────────────────────────────────────────┘
```

---

## 🔄 Mise à jour des informations

### Méthode 1 : Via l'interface

1. Allez dans **⚙️ Paramètres**
2. Modifiez les champs souhaités
3. Cliquez sur **💾 Sauvegarder Tout**
4. Les rapports seront automatiquement mis à jour

### Méthode 2 : Fichier de configuration

1. Éditez `config.json`
2. Modifiez la section `center`
3. Sauvegardez le fichier
4. Redémarrez l'application

---

## 💡 Conseils et bonnes pratiques

### ✅ À faire

- **Remplissez au minimum** : nom, téléphone, email
- **Vérifiez l'orthographe** : ces informations apparaîtront sur tous vos documents
- **Utilisez un logo professionnel** : format PNG avec fond transparent recommandé
- **Mettez à jour régulièrement** : surtout en cas de changement d'adresse ou de numéros

### ❌ À éviter

- Laisser des champs vides si vous les utilisez professionnellement
- Utiliser des images de logo trop grandes (max 500 Ko recommandé)
- Oublier de sauvegarder après modifications

---

## 🛠️ Dépannage

### Les informations n'apparaissent pas dans les rapports

1. **Vérifiez la sauvegarde**
   - Assurez-vous d'avoir cliqué sur **💾 Sauvegarder Tout**
   - Message de confirmation attendu : "✅ Configuration sauvegardée avec succès!"

2. **Rechargez le module Rapports**
   - Cliquez sur le bouton **🔄 Rafraîchir** dans le module Rapports

3. **Vérifiez config.json**
   - Ouvrez `config.json` avec un éditeur de texte
   - Vérifiez que la section `center` existe et contient vos données

4. **Redémarrez l'application**
   - Fermez complètement l'application
   - Relancez avec `python start_safe.py`

### Le logo ne s'affiche pas

1. **Vérifiez le format**
   - Formats supportés : PNG, JPG, JPEG, SVG
   - Taille recommandée : max 500 Ko

2. **Vérifiez le chemin**
   - Le logo doit être dans `src/resources/`
   - Le chemin dans config.json doit être correct

3. **Rechargez le logo**
   - Allez dans **⚙️ Paramètres**
   - **🖼️ Logo du Centre** → **🗑️ Supprimer**
   - Ensuite **📁 Choisir un logo** et sélectionnez à nouveau

---

## 📞 Support

Si vous rencontrez des problèmes :

1. Consultez la [Documentation principale](../README.md)
2. Vérifiez les [logs](../logs/) pour les erreurs
3. Contactez le support technique

---

## 🎯 Exemple complet

Voici un exemple de configuration complète pour une auto-école :

```json
{
  "center": {
    "name": "Auto-École Excellence",
    "address": "123 Avenue Mohammed V, Quartier Maarif",
    "city": "Casablanca",
    "postal_code": "20100",
    "phone": "+212 522-123456",
    "email": "contact@autoecole-excellence.ma",
    "website": "www.autoecole-excellence.ma",
    "siret": "123456789000123",
    "tva_number": "MA123456789",
    "license_number": "AE-CASA-2024-001",
    "director_name": "Mohammed ALAMI"
  },
  "pdf": {
    "company_logo": "src/resources/logo.png"
  }
}
```

**Résultat dans les rapports :**

```
╔════════════════════════════════════════════════════╗
║        AUTO-ÉCOLE EXCELLENCE                       ║
║   123 Avenue Mohammed V, Quartier Maarif           ║
║   20100 Casablanca                                 ║
║                                                    ║
║   📞 +212 522-123456 | 📧 contact@autoecole...    ║
║   🌐 www.autoecole-excellence.ma                   ║
║   Agrément N° AE-CASA-2024-001 | SIRET: 123...    ║
║   TVA: MA123456789                                 ║
║   📅 Rapport généré le 08/12/2024 à 15:30          ║
╚════════════════════════════════════════════════════╝
```

---

**Dernière mise à jour** : 08/12/2024  
**Version** : 1.0.0
