# 🔐 Guide du Système de Licence

## Vue d'ensemble

L'Auto-École Manager utilise un système de licence basé sur le Hardware ID pour protéger l'application. Chaque licence est liée à un ordinateur spécifique.

---

## 🔑 Pour les Utilisateurs

### Première Installation

1. **Lancez l'application:**
   ```bash
   python src/main_gui.py
   ```

2. **La fenêtre d'activation apparaît** (si aucune licence n'est installée)

3. **Copiez votre Hardware ID:**
   - Cliquez sur "📋 Copier l'Identifiant"
   - L'identifiant est copié dans le presse-papiers

4. **Obtenez de l'aide (optionnel):**
   - Cliquez sur "❓ Comment obtenir une licence ?"
   - Lisez les instructions dans la popup

5. **Contactez le support:**
   - Email: e.belqasim@gmail.com
   - Téléphone: +212 637-636146
   - Fournissez votre Hardware ID

6. **Recevez votre clé de licence:**
   - Le support vous enverra une clé unique par email
   - Format: `XXXXX-XXXXX-XXXXX-XXXXX-XXXXX`

7. **Activez la licence:**
   - Copiez la clé reçue
   - Collez-la dans le champ "Clé de licence"
   - Cliquez sur "✅ Activer la Licence"

8. **Confirmation:**
   - Si la clé est valide → Application démarre
   - Si la clé est invalide → Message d'erreur

### Utilisations Suivantes

- L'application vérifie automatiquement la licence au démarrage
- Si la licence est valide → Accès direct à l'application
- Si la licence est expirée → Message d'avertissement avec nombre de jours restants
- Si la licence n'est plus valide → Fenêtre d'activation réaffichée

---

## 👨‍💼 Pour les Administrateurs / Support

### Générer une Licence

#### Méthode 1: Script interactif

```bash
python generate_license.py
```

Le script vous demandera:
- Nom de l'auto-école
- Durée de validité (en jours)

#### Méthode 2: Script avec paramètres

```bash
python generate_license.py "Nom Auto-École" 365
```

Paramètres:
- Premier argument: Nom de l'entreprise
- Deuxième argument: Durée en jours (ex: 365 pour 1 an)

#### Méthode 3: En Python

```python
from src.utils.license_manager import get_license_manager

# Créer le gestionnaire
license_manager = get_license_manager()

# Obtenir le Hardware ID du client
hardware_id = "XXXXXXXXXXXX"  # Fourni par le client

# Générer la licence
license_key = license_manager.generate_license_key(
    company_name="Auto-École Test",
    duration_days=365,
    hardware_id=hardware_id
)

print(f"Clé de licence: {license_key}")
```

### Vérifier une Licence Existante

```bash
python -c "
from src.utils.license_manager import get_license_manager

lm = get_license_manager()

if lm.is_licensed():
    info = lm.get_license_info()
    print(f'✅ Licence valide')
    print(f'   Entreprise: {info[\"company\"]}')
    print(f'   Expire le: {info[\"expiration_date\"]}')
    print(f'   Jours restants: {info[\"days_remaining\"]}')
else:
    print('❌ Aucune licence valide')
"
```

---

## 🔧 Détails Techniques

### Hardware ID

Le Hardware ID est généré à partir de:
- Nom de la machine (`platform.node()`)
- Système d'exploitation (`platform.system()`)
- Version du système (`platform.release()`)
- Architecture (`platform.machine()`)
- UUID de la machine (méthode spécifique à l'OS):
  - **Windows**: `wmic` ou PowerShell
  - **Linux**: `/etc/machine-id` ou `/var/lib/dbus/machine-id`
  - **macOS**: `ioreg IOPlatformUUID`
- Fallback: Adresse MAC (`uuid.getnode()`)

Le résultat est un hash SHA-256 tronqué à 16 caractères.

### Format de la Clé de Licence

La clé contient (chiffré):
- Nom de l'entreprise
- Hardware ID autorisé
- Date d'émission
- Date d'expiration
- Signature de validation

Exemple: `AE2024-X5K9P-7M3N2-Q8W4R-F6H1J`

### Stockage

- Fichier: `config/license.dat`
- Chiffrement: Fernet (cryptography)
- Clé de chiffrement: Basée sur un salt secret

### Validation

La licence est validée à chaque démarrage:
1. Vérification de l'existence du fichier
2. Déchiffrement des données
3. Validation du Hardware ID
4. Vérification de la date d'expiration
5. Contrôle d'intégrité (signature)

---

## 🛠️ Résolution de Problèmes

### Erreur: "wmic n'est pas reconnu"

**Solution**: Le système utilise maintenant plusieurs méthodes de fallback:
- PowerShell sur Windows moderne
- machine-id sur Linux
- Adresse MAC en dernier recours

Cette erreur est normale et gérée automatiquement.

### Licence invalide après changement de matériel

**Cause**: La licence est liée au matériel
**Solution**: Générer une nouvelle licence avec le nouveau Hardware ID

### Transférer une licence

1. Contactez le support
2. Fournissez l'ancien et le nouveau Hardware ID
3. Le support génère une nouvelle clé
4. Activez avec la nouvelle clé

### Licence expirée

1. Contactez le support pour renouvellement
2. Une nouvelle clé avec une nouvelle date d'expiration sera générée

---

## 📊 Durées de Licence Recommandées

| Type | Durée | Usage |
|------|-------|-------|
| Test | 30 jours | Période d'essai |
| Standard | 365 jours | 1 an |
| Prolongée | 730 jours | 2 ans |
| Lifetime | 3650 jours | 10 ans (pseudo-permanent) |

---

## 🔒 Sécurité

### Protection Implémentée

✅ **Hardware Binding**: Licence liée à un ordinateur spécifique  
✅ **Chiffrement**: Données chiffrées avec Fernet  
✅ **Expiration**: Contrôle de la date de validité  
✅ **Signature**: Vérification d'intégrité  
✅ **Multi-plateforme**: Windows, Linux, macOS  

### Recommandations

- **Ne partagez jamais votre clé de licence**
- **Conservez votre clé en lieu sûr**
- **Sauvegardez `config/license.dat` avec vos backups**
- **Contactez le support pour tout problème**

---

## 📝 Exemples d'Utilisation

### Exemple 1: Générer une licence de test (30 jours)

```bash
python generate_license.py "Auto-École Test" 30
```

### Exemple 2: Générer une licence annuelle

```bash
python generate_license.py "Auto-École Marrakech" 365
```

### Exemple 3: Générer une licence avec activation automatique

```bash
python generate_license.py "Mon Auto-École" 365
# Répondez 'o' quand demandé si vous voulez activer
```

---

## 📞 Support

Pour toute question concernant les licences:

- 📧 **Email**: e.belqasim@gmail.com
- 📱 **Téléphone**: +212 637-636146
- 🌐 **Site Web**: https://auto-ecole-manager.com

---

**Auto-École Manager - Système de Licence v1.0**
