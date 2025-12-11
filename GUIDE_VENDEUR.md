# 💼 Guide Rapide Vendeur - Système de Licence

## 🚀 Démarrage Rapide

### Quand un client achète l'application :

#### 📋 ÉTAPE 1 : Client installe l'app
```bash
# Le client lance l'application
python src/main_gui.py
```

**Résultat :** Une fenêtre s'affiche demandant la licence.

Le client voit son **Hardware ID** :
```
📟 Identifiant de cet Ordinateur
Hardware ID: A1B2C3D4E5F6G7H8
```

#### 📧 ÉTAPE 2 : Client vous contacte

Le client vous envoie :
- Nom de son auto-école
- Son Hardware ID (copié depuis l'app)

#### 🔑 ÉTAPE 3 : Vous générez la licence

```bash
cd /chemin/vers/auto-ecole
python tools/generate_license.py
```

**Questions posées :**
```
Nom de l'auto-école: Auto-École Al Mansour
Hardware ID du client: A1B2C3D4E5F6G7H8
Durée de validité en jours [365]: 365
```

**Vous recevez :**
```
🔑 CLÉ DE LICENCE :
gAAAAABlxxxxx-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx
```

#### 📨 ÉTAPE 4 : Vous envoyez la clé

**Email au client :**
```
Objet: Votre clé de licence - Auto-École Manager

Bonjour,

Votre licence a été générée avec succès !

🔑 Clé de licence :
gAAAAABlxxxxx-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx

📝 Instructions :
1. Ouvrez l'application Auto-École Manager
2. Copiez-collez la clé dans le champ prévu
3. Cliquez sur "Activer"

✅ Votre application sera immédiatement débloquée !

La licence est valide jusqu'au: [DATE]

Support: support@auto-ecole.com

Cordialement,
[Votre Nom]
```

#### ✅ ÉTAPE 5 : Client active

Le client :
1. Colle la clé dans l'application
2. Clique sur "Activer"
3. ✅ Application débloquée !

---

## 💰 Tarification Suggérée

### Option 1 : Abonnement Annuel
- **Prix** : 5000 DH / an
- **Durée** : 365 jours
- **Renouvellement** : Chaque année

### Option 2 : Abonnement Semestriel
- **Prix** : 3000 DH / 6 mois
- **Durée** : 180 jours
- **Renouvellement** : Tous les 6 mois

### Option 3 : Licence Permanente
- **Prix** : 15000 DH (une fois)
- **Durée** : 3650 jours (10 ans)
- **Renouvellement** : Non nécessaire

---

## 📊 Suivi des Licences (Excel)

Créez un fichier `licences_clients.xlsx` :

| Date | Auto-École | Hardware ID | Clé | Expiration | Prix | Statut | Contact |
|------|------------|-------------|-----|------------|------|--------|---------|
| 15/12/2024 | Al Mansour | A1B2C3D4... | gAAAAA... | 15/12/2025 | 5000 | ✅ Active | +212... |
| 16/12/2024 | Assalam | B2C3D4E5... | gAAAAB... | 16/06/2025 | 3000 | ✅ Active | +212... |

---

## 🔧 Commandes Utiles

### Générer une licence
```bash
python tools/generate_license.py
```

### Tester l'app (sans licence)
```bash
python src/main_gui.py
# → Affichera l'écran d'activation
```

### Initialiser la base (avec licence)
```bash
python src/init_db.py
# → Vérifie la licence avant de continuer
```

---

## ❓ Questions Fréquentes

### Q: Le client veut changer d'ordinateur ?

**R:** Deux options :

1. **Nouvelle licence** (recommandé)
   - Générer une nouvelle licence avec le nouveau Hardware ID
   - Facturer le transfert (ex: 1000 DH)

2. **Migration gratuite** (service client)
   - Client désinstalle l'app du vieux PC
   - Client supprime `config/license.dat`
   - Vous générez une licence avec le nouveau Hardware ID
   - Client installe sur le nouveau PC

### Q: La licence a expiré ?

**R:** Générer une nouvelle licence :
```bash
python tools/generate_license.py
```
Même Hardware ID, nouvelle durée → Nouvelle clé

### Q: Client dit "Clé invalide" ?

**R:** Causes possibles :
1. Clé mal copiée → Renvoyer par email
2. Hardware ID incorrect → Demander confirmation
3. Espace/caractère en trop → Copier-coller depuis txt brut

### Q: Combien de licences puis-je vendre ?

**R:** **Illimité !** Chaque licence est unique.

---

## 🎯 Avantages Commerciaux

### Pour Vous :
✅ **Revenus récurrents** : Renouvellements annuels  
✅ **Contrôle total** : Vous générez toutes les licences  
✅ **Anti-piratage** : 1 licence = 1 ordinateur  
✅ **Suivi client** : Base de données licences  

### Pour le Client :
✅ **Installation simple** : 5 minutes  
✅ **Activation immédiate** : Pas d'attente  
✅ **Pas de connexion web** : Fonctionne hors ligne  
✅ **Support technique** : Vous êtes disponible  

---

## 📞 Support Client

### Template Email Support

```
Objet: Support Technique - Licence Auto-École

Bonjour [Client],

Merci de votre message concernant votre licence.

Pour mieux vous aider, pouvez-vous me fournir :
1. Votre Hardware ID (visible dans l'application)
2. Le message d'erreur exact (capture d'écran si possible)
3. Votre auto-école et date d'activation

Je vous répondrai dans les 24h.

Cordialement,
[Votre Nom]
Support Technique
Email: support@auto-ecole.com
Tél: +212 XXX-XXXXXX
```

---

## 🔒 Sécurité - À NE JAMAIS PARTAGER

❌ **Ne JAMAIS donner :**
- Le script `tools/generate_license.py`
- Le fichier `src/utils/license_manager.py`
- Votre fichier de suivi des licences

✅ **Partager uniquement :**
- Les clés de licence générées
- L'application installable (sans le dossier tools/)

---

## 📦 Distribution de l'Application

### Créer un package pour le client

```bash
# 1. Copier les fichiers nécessaires (sans tools/)
cp -r src/ data/ config/ requirements.txt CLIENT_PACKAGE/

# 2. Supprimer le dossier tools (important!)
rm -rf CLIENT_PACKAGE/tools/

# 3. Créer un ZIP
zip -r AutoEcole_v1.0.zip CLIENT_PACKAGE/

# 4. Envoyer au client
```

⚠️ **Le client NE DOIT PAS avoir accès à `tools/generate_license.py`**

---

## 💡 Conseils Marketing

### 🎁 Offre de Lancement
```
🚀 OFFRE SPÉCIALE LANCEMENT !

✅ 1er mois GRATUIT
✅ Support technique inclus
✅ Mises à jour gratuites pendant 1 an
✅ Formation à distance offerte

À partir de 5000 DH/an seulement !

Contact: +212 XXX-XXXXXX
```

### 📈 Upselling
```
Pack Standard  : 5000 DH/an  → 1 PC
Pack Premium   : 8000 DH/an  → 2 PC + Support prioritaire
Pack Entreprise: 15000 DH/an → Licence permanente + Personnalisation
```

---

## ✅ Checklist Vente

Avant chaque vente, vérifiez :

- [ ] Client a testé la version démo
- [ ] Client a fourni son Hardware ID
- [ ] Licence générée avec les bons paramètres
- [ ] Clé envoyée par email sécurisé
- [ ] Client a activé avec succès
- [ ] Licence enregistrée dans votre fichier de suivi
- [ ] Facture envoyée au client
- [ ] Rappel expiration programmé (11 mois après)

---

## 🎉 Félicitations !

Vous avez maintenant un système de licence professionnel !

**Prochaines étapes :**
1. Testez le système vous-même
2. Créez vos premiers packages client
3. Configurez votre email de support
4. Préparez votre fichier de suivi Excel
5. Lancez votre campagne marketing !

**Bonne chance pour vos ventes ! 🚀💰**
