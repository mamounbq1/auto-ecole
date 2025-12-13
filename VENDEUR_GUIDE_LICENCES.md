# 🔐 GUIDE VENDEUR : Gestion des Licences

> ⚠️ **CONFIDENTIEL** : Ce fichier est réservé au vendeur uniquement.  
> **NE JAMAIS** inclure ce fichier ni `generate_license.py` dans la distribution client !

---

## 📋 Vue d'Ensemble

L'application **Auto-École Manager** utilise un système de licences pour protéger votre logiciel :

- ✅ **Chaque installation** nécessite une licence unique
- ✅ **Licence liée au matériel** (Hardware ID)
- ✅ **Durée configurable** (jours, mois, années)
- ✅ **Génération côté vendeur uniquement**

---

## 🛠️ Génération d'une Licence

### Étape 1 : Le Client Vous Contact

Le client vous envoie son **Hardware ID** affiché dans l'application :

```
Exemple de Hardware ID :
ABC123-DEF456-789012
```

**Où le client trouve son Hardware ID :**
- Fenêtre de connexion → Bouton "Activer Licence"
- Fenêtre d'activation → Hardware ID affiché en bas

### Étape 2 : Générer la Licence

Ouvrez un terminal dans le dossier du projet :

```bash
cd "C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main"
python generate_license.py
```

**Exemple d'utilisation :**

```
=== Générateur de Licence Auto-École Manager ===

Entrez le Hardware ID du client : ABC123-DEF456-789012
Nom du client (optionnel) : Auto-École Rabat
Durée en jours (30, 365, etc.) : 365

✅ Licence générée avec succès !

📄 Fichier : license_ABC123-DEF456-789012.key
📧 Clé de licence : 

eyJoYXJkd2FyZV9pZCI6ICJBQK...xxxLONGUE_CLÉ_CHIFFRÉE...xxxfQ==

📋 À envoyer au client :
-----------------------------------
Clé de licence valide 365 jours :
eyJoYXJkd2FyZV9pZCI6ICJBQK...xxxLONGUE_CLÉ_CHIFFRÉE...xxxfQ==
-----------------------------------
```

### Étape 3 : Envoyer la Licence au Client

**Par Email :**
```
Bonjour,

Voici votre clé de licence Auto-École Manager :

eyJoYXJkd2FyZV9pZCI6ICJBQK...xxxLONGUE_CLÉ_CHIFFRÉE...xxxfQ==

Validité : 365 jours

Instructions d'activation :
1. Ouvrez l'application
2. Cliquez sur "Activer Licence"
3. Collez la clé ci-dessus
4. Cliquez sur "Activer"

Cordialement,
[Votre nom]
```

**Par WhatsApp/SMS :**
```
🔑 Licence Auto-École Manager
Valide 365 jours

eyJoYXJkd2FyZV9pZCI6ICJBQK...xxxLONGUE_CLÉ_CHIFFRÉE...xxxfQ==

Instructions : Ouvrir app → Activer Licence → Coller clé → Activer
```

---

## 💰 Tarification Suggérée

| Durée | Prix Suggéré (MAD) | Notes |
|-------|-------------------|-------|
| 1 mois (30j) | 500 DH | Test/Démo |
| 3 mois (90j) | 1 200 DH | Court terme |
| 6 mois (180j) | 2 000 DH | Populaire |
| 1 an (365j) | 3 500 DH | Meilleur rapport |
| 2 ans (730j) | 6 000 DH | Entreprise |
| Perpétuelle (36500j = 100 ans) | 10 000 DH | Licence "illimitée" |

---

## 🔒 Sécurité

### ✅ CE QUI EST SÛR

1. **`generate_license.py` n'est PAS dans l'exe**
   - Le client ne peut pas générer ses propres licences
   - Seul vous (vendeur) pouvez générer des licences

2. **Hardware ID unique**
   - Basé sur : UUID machine + Processeur + Carte réseau
   - Change si le client change de PC
   - → Le client doit vous recontacter pour un nouveau PC

3. **Licence chiffrée**
   - Clé cryptographique dans `src/utils/license_manager.py`
   - Impossible à décrypter sans la clé (Fernet)

### 🚨 FICHIERS À NE JAMAIS PARTAGER

- ❌ `generate_license.py` (racine du projet)
- ❌ `src/utils/license_manager.py` (contient la clé de chiffrement)
- ❌ `*.key` (fichiers de licence générés)
- ❌ Ce fichier (`VENDEUR_GUIDE_LICENCES.md`)

### ✅ FICHIERS SAFE À PARTAGER

- ✅ `AutoEcoleManager.exe` (l'exécutable)
- ✅ `AutoEcoleManager_Setup_v1.0.0.exe` (l'installateur)
- ✅ Dossier `assets/` (images, icônes)
- ✅ `README.md` (si vous en créez un pour les clients)

---

## 🛡️ Scénarios Courants

### Scénario 1 : Nouveau Client

1. Client télécharge l'installateur
2. Client installe l'application
3. Client lance l'app → Fenêtre d'activation
4. Client vous envoie son Hardware ID
5. Vous générez la licence
6. Vous lui envoyez la clé
7. Client active → Connexion possible

### Scénario 2 : Licence Expirée

1. Client ouvre l'app après expiration
2. Message : "Licence expirée"
3. Client vous recontacte
4. Vous générez une nouvelle licence (même Hardware ID)
5. Client active la nouvelle licence

### Scénario 3 : Changement de PC

1. Client installe sur nouveau PC
2. **Nouveau Hardware ID** (différent)
3. Client vous envoie le nouveau ID
4. Vous générez une nouvelle licence avec le nouveau ID
5. **Option** : Facturer frais de transfert (ex: 500 DH)

### Scénario 4 : Renouvellement

1. Client souhaite renouveler avant expiration
2. Vous générez une nouvelle licence avec durée additionnelle
3. Client active → Les jours s'additionnent

---

## 📊 Suivi des Licences

### Tableur de Suivi (Excel/Google Sheets)

| Date | Client | Hardware ID | Durée | Expiration | Montant | Statut |
|------|--------|-------------|-------|------------|---------|--------|
| 2025-01-15 | Auto-École Rabat | ABC123-... | 365j | 2026-01-15 | 3500 DH | ✅ Actif |
| 2025-01-20 | École Conduite Casa | XYZ789-... | 180j | 2025-07-19 | 2000 DH | ✅ Actif |
| 2024-10-01 | Permis Plus | DEF456-... | 90j | 2025-01-01 | 1200 DH | ⚠️ Expiré |

### Fichier à Créer : `licences_vendues.txt`

```
# Licences Auto-École Manager
# Format : DATE | CLIENT | HARDWARE_ID | DURÉE | MONTANT

2025-01-15 | Auto-École Rabat | ABC123-DEF456-789012 | 365j | 3500 DH
2025-01-20 | École Conduite Casa | XYZ789-ABC123-456789 | 180j | 2000 DH
```

---

## 🚀 Distribution

### Fichiers à Donner au Client

**Option 1 : Exécutable Seul**
```
📁 AutoEcole_v1.0.0/
  ├── AutoEcoleManager.exe
  └── README_CLIENT.txt (instructions)
```

**Option 2 : Installateur Professionnel (Recommandé)**
```
📁 AutoEcole_v1.0.0/
  ├── AutoEcoleManager_Setup_v1.0.0.exe
  └── README_CLIENT.txt
```

### README_CLIENT.txt (Exemple)

```
AUTO-ÉCOLE MANAGER v1.0.0
=========================

Installation :
1. Double-cliquer sur AutoEcoleManager_Setup_v1.0.0.exe
2. Suivre l'assistant d'installation
3. Lancer l'application depuis le menu Démarrer

Activation :
1. Au premier lancement, notez votre Hardware ID
2. Contactez votre fournisseur avec ce Hardware ID
3. Vous recevrez une clé de licence par email
4. Cliquez sur "Activer Licence" et collez la clé

Support :
Email : votre.email@example.com
Téléphone : +212 XXX-XXXXXX
WhatsApp : +212 XXX-XXXXXX

---
© 2024-2025 Auto-École Manager
```

---

## 🔧 Maintenance

### Modifier la Clé de Chiffrement (Avancé)

Si vous soupçonnez une fuite de la clé :

1. Ouvrir `src/utils/license_manager.py`
2. Ligne ~30 : Générer nouvelle clé
   ```python
   # Ancienne clé
   # self.key = Fernet.generate_key()
   
   # Nouvelle clé (générer avec Python)
   # >>> from cryptography.fernet import Fernet
   # >>> Fernet.generate_key()
   # b'NOUVELLE_CLE_ICI...'
   
   self.key = b'VOTRE_NOUVELLE_CLE_GENEREE'
   ```
3. Recompiler l'exe
4. **⚠️ Toutes les anciennes licences deviennent invalides !**
5. Régénérer toutes les licences pour vos clients

### Version de l'Application

Pour changer la version (ex: v1.0.0 → v1.1.0) :

1. `src/config.py` → `APP_VERSION = "1.1.0"`
2. `build_executable.py` → Mettre à jour version dans VSVersionInfo
3. `setup.iss` (Inno Setup) → `AppVersion=1.1.0`
4. Recompiler tout

---

## ❓ FAQ Vendeur

**Q : Peut-on générer des licences illimitées ?**  
R : Oui, utilisez `36500` jours (100 ans) lors de la génération.

**Q : Un client peut-il utiliser une licence sur plusieurs PC ?**  
R : Non, une licence = un Hardware ID = un PC unique.

**Q : Que faire si un client perd sa clé de licence ?**  
R : Vous pouvez régénérer gratuitement avec le même Hardware ID.

**Q : Le client peut-il cracker le système de licence ?**  
R : Très difficile. La clé est chiffrée et le code est compilé. Un crack nécessiterait du reverse engineering avancé.

**Q : Combien de licences puis-je vendre ?**  
R : Illimité ! Chaque licence est unique et indépendante.

**Q : Y a-t-il un système de licence flottante (réseau) ?**  
R : Non, pour l'instant c'est une licence par poste. Vous pouvez facturer plus cher pour plusieurs postes.

---

## 📞 Support Technique

Si vous rencontrez des problèmes avec la génération de licences :

1. Vérifier que Python 3.8+ est installé
2. Vérifier que `cryptography` est installé : `pip install cryptography`
3. Vérifier que `generate_license.py` est bien dans le dossier projet

**Erreur courante :**
```
ModuleNotFoundError: No module named 'cryptography'
```
**Solution :**
```bash
pip install cryptography
```

---

## ✅ Checklist de Distribution

Avant de distribuer à un nouveau client :

- [ ] Exécutable/Installateur prêt
- [ ] README_CLIENT.txt créé
- [ ] Clé de licence générée
- [ ] Email d'activation préparé
- [ ] Prix convenu
- [ ] Paiement reçu ✅
- [ ] Licence envoyée au client
- [ ] Client confirmé l'activation
- [ ] Licence ajoutée au tableur de suivi

---

**Bonne vente ! 🎉**
