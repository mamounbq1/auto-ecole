# 🔐 Système de Licence - Auto-École Manager

## 📋 Vue d'ensemble

Ce système de licence protège votre application Auto-École contre l'utilisation non autorisée. Chaque licence est liée de manière unique à un ordinateur spécifique.

---

## 🎯 Fonctionnalités

### ✅ Protection Complète
- **Hardware ID unique** : Chaque ordinateur a un identifiant unique
- **Chiffrement RSA** : Clés de licence cryptographiquement sécurisées
- **Validation stricte** : Impossible d'utiliser une licence sur un autre PC
- **Expiration automatique** : Contrôle de la date de validité

### 🔑 Workflow de Licence

```
1. CLIENT INSTALLE L'APP
   └─> Demande son Hardware ID
   
2. CLIENT CONTACTE LE SUPPORT
   └─> Fournit son Hardware ID
   
3. VOUS GÉNÉREZ LA LICENCE
   └─> Avec le script generate_license.py
   
4. CLIENT REÇOIT LA CLÉ
   └─> Active l'application
   
5. APPLICATION DÉBLOQUÉE
   └─> Peut créer des comptes et utiliser l'app
```

---

## 🛠️ Pour Vous (Vendeur)

### Générer une Licence

```bash
# Depuis le répertoire du projet
python tools/generate_license.py
```

**Informations requises :**
1. **Nom de l'auto-école** : Ex: "Auto-École Al Mansour"
2. **Hardware ID du client** : Fourni par le client (16 caractères)
3. **Durée de validité** : Ex: 365 jours (1 an)

**Exemple d'exécution :**
```
🔐 GÉNÉRATEUR DE LICENCES - AUTO-ÉCOLE
========================================

Nom de l'auto-école: Auto-École Al Mansour
Hardware ID du client: A1B2C3D4E5F6G7H8
Durée de validité en jours [365]: 365

✅ LICENCE GÉNÉRÉE AVEC SUCCÈS!
========================================

🔑 CLÉ DE LICENCE :
------------------------------------------------------------
gAAAAABlxxxxx-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx
------------------------------------------------------------

📧 Envoyez cette clé au client par email sécurisé
```

### Stockage des Licences

**Recommandation :** Conservez un fichier Excel/CSV avec :
- Nom de l'auto-école
- Hardware ID
- Clé de licence générée
- Date de génération
- Date d'expiration
- Contact du client

---

## 👤 Pour le Client

### 1. Premier Lancement

Au premier lancement, l'application affiche un écran d'activation :

```
🔐 Activation de Licence Requise
================================

📟 Identifiant de cet Ordinateur
Hardware ID: A1B2C3D4E5F6G7H8

[Copier l'Identifiant]

🔑 Activation de la Licence
Entrez votre clé de licence:
[_________________________]

[✅ Activer la Licence]
```

### 2. Obtenir une Licence

Le client doit :
1. **Copier son Hardware ID** (bouton "Copier")
2. **Contacter le support** : support@auto-ecole.com
3. **Fournir le Hardware ID**
4. **Recevoir la clé de licence** par email
5. **Entrer la clé** dans l'application
6. **Cliquer sur "Activer"**

### 3. Utilisation

Une fois activé :
- ✅ Accès complet à l'application
- ✅ Création de comptes utilisateurs
- ✅ Toutes les fonctionnalités débloquées
- ⏰ Licence valide jusqu'à la date d'expiration

---

## 🔒 Sécurité

### Protection Anti-Piratage

1. **Licence liée au Hardware ID**
   - Impossible de copier sur un autre ordinateur
   - UUID système + Nom machine + OS

2. **Chiffrement Fernet (AES-128)**
   - Clés de licence cryptées
   - Impossible de modifier une licence existante

3. **Validation à chaque lancement**
   - Vérification Hardware ID
   - Vérification date d'expiration
   - Blocage si licence invalide

4. **Fichier licence protégé**
   - Stocké dans `config/license.dat`
   - Format JSON chiffré
   - Impossible à éditer manuellement

---

## 📁 Structure des Fichiers

```
auto-ecole/
├── config/
│   └── license.dat              # Licence activée (créé après activation)
├── src/
│   ├── utils/
│   │   └── license_manager.py   # Gestionnaire de licences
│   └── views/
│       └── license_activation_window.py  # Interface d'activation
├── tools/
│   └── generate_license.py      # Script de génération (VENDEUR)
└── LICENSE_SYSTEM.md            # Ce fichier
```

---

## 🚨 Problèmes Courants

### ❌ "Cette licence n'est pas valide pour cet ordinateur"

**Cause :** Le Hardware ID ne correspond pas

**Solution :**
- Vérifier que la licence a été générée avec le bon Hardware ID
- Demander au client de confirmer son Hardware ID actuel
- Générer une nouvelle licence si nécessaire

### ❌ "Licence expirée"

**Cause :** La date de validité est dépassée

**Solution :**
- Générer une nouvelle licence avec une nouvelle durée
- Envoyer la nouvelle clé au client

### ❌ "Clé de licence invalide"

**Cause :** Clé mal copiée ou corrompue

**Solution :**
- Vérifier que la clé a été copiée entièrement
- Renvoyer la clé au client
- Utiliser un format texte brut (pas Word/PDF formaté)

---

## 💰 Modèle de Vente

### Options de Licence

1. **Licence Annuelle** (365 jours)
   - Prix : À définir
   - Renouvellement chaque année

2. **Licence Semestrielle** (180 jours)
   - Prix : À définir
   - Pour essai ou petits centres

3. **Licence à Vie** (3650 jours = 10 ans)
   - Prix premium
   - Pas de renouvellement

### Renouvellement

Pour renouveler une licence expirée :
1. Client contacte le support
2. Vous générez une nouvelle licence (même Hardware ID)
3. Client entre la nouvelle clé
4. Application à nouveau fonctionnelle

---

## 📧 Support Client

**Email de support recommandé :**
```
support@auto-ecole.com
```

**Template d'email pour les clients :**

```
Objet: Demande de licence - Auto-École [Nom]

Bonjour,

Je souhaite obtenir une licence pour l'application Auto-École Manager.

Nom de l'auto-école: [Nom]
Hardware ID: [Copié depuis l'application]
Contact: [Téléphone/Email]

Merci de me faire parvenir la clé de licence.

Cordialement,
[Nom]
```

---

## 🔧 Maintenance

### Désactiver une Licence (Admin)

Si un client demande de transférer sa licence sur un autre PC :

1. **Option 1 : Nouvelle licence**
   - Générer une nouvelle licence avec le nouveau Hardware ID
   - Facturer le transfert si souhaité

2. **Option 2 : Désactivation manuelle**
   - Demander au client de supprimer `config/license.dat`
   - Installer l'app sur le nouveau PC
   - Générer une licence avec le nouveau Hardware ID

---

## ⚠️ Important - Sécurité de Votre Clé

**GARDEZ SECRET :**
- Le script `generate_license.py`
- La clé de chiffrement dans `license_manager.py`

**Ne jamais :**
- Partager le script de génération
- Publier le code source du license_manager
- Donner accès au dossier `tools/`

---

## 📊 Suivi des Licences (Recommandé)

Créez un fichier Excel pour suivre vos licences :

| Auto-École | Hardware ID | Date Génération | Date Expiration | Clé | Statut | Contact |
|------------|-------------|-----------------|-----------------|-----|--------|---------|
| Al Mansour | A1B2C3D4... | 2024-12-15 | 2025-12-15 | gAAAAA... | Active | +212... |

---

## 🎉 Avantages du Système

✅ **Pour Vous (Vendeur) :**
- Contrôle total des installations
- Génération de revenus récurrents (renouvellements)
- Protection contre le piratage
- Suivi des clients

✅ **Pour le Client :**
- Installation simple
- Activation en quelques clics
- Aucune connexion internet requise après activation
- Support technique disponible

---

## 📝 Notes de Version

**v1.0 - Système de Licence Initial**
- Génération de licences par Hardware ID
- Chiffrement AES-128
- Interface d'activation graphique
- Blocage sans licence valide
- Expiration automatique
