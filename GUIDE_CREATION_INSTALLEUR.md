## 📦 GUIDE COMPLET - CRÉATION DE L'INSTALLEUR PROFESSIONNEL

### 🎯 Vue d'ensemble

Ce guide vous explique comment créer un installeur professionnel (.exe) pour Auto-École Manager avec :
- ✅ Installation automatique
- ✅ Raccourcis bureau et menu démarrer
- ✅ Icône personnalisée
- ✅ Désinstallation propre
- ✅ Interface professionnelle

---

### 📋 PRÉREQUIS

#### 1. Installer Python (si pas déjà fait)
```bash
# Télécharger depuis: https://www.python.org/downloads/
# Version recommandée: Python 3.10 ou 3.11
```

#### 2. Installer PyInstaller
```bash
pip install pyinstaller
```

#### 3. Télécharger Inno Setup
```
🌐 Site: https://jrsoftware.org/isdl.php
📥 Téléchargez: innosetup-6.2.2.exe (ou version plus récente)
🔧 Installez avec les options par défaut
```

---

### 🔨 ÉTAPE 1: CRÉER L'EXÉCUTABLE

#### Option A: Avec le script automatique (Recommandé)

```bash
cd /chemin/vers/auto-ecole
python build_executable.py
```

Le script va:
1. Nettoyer les anciens builds
2. Créer le fichier de version
3. Compiler avec PyInstaller
4. Préparer la structure d'installation

#### Option B: Manuellement

```bash
# 1. Nettoyer
rmdir /s /q build dist
del *.spec

# 2. Compiler
pyinstaller --name=AutoEcoleManager ^
            --onefile ^
            --windowed ^
            --icon=assets/app_icon.png ^
            --add-data="assets;assets" ^
            --add-data="templates;templates" ^
            --add-data="src;src" ^
            --noconsole ^
            src/main_gui.py

# 3. L'exécutable sera dans: dist/AutoEcoleManager.exe
```

---

### 📦 ÉTAPE 2: CRÉER L'INSTALLEUR AVEC INNO SETUP

#### 1. Ouvrir Inno Setup Compiler

- Lancez: `Inno Setup Compiler`
- Ouvrez le fichier: `setup.iss`

#### 2. Vérifier la configuration

Le fichier `setup.iss` contient déjà tout:
- ✅ Informations de l'application
- ✅ Fichiers à inclure
- ✅ Raccourcis à créer
- ✅ Messages personnalisés

#### 3. Compiler l'installeur

Dans Inno Setup:
```
Build → Compile (ou F9)
```

Ou en ligne de commande:
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

#### 4. Résultat

L'installeur sera créé dans:
```
installer/AutoEcoleManager_Setup_v1.0.0.exe
```

---

### 🎨 PERSONNALISATION (Optionnel)

#### Créer des images pour l'installeur

**1. Banner (Image en haut de l'installeur)**

Créez une image `installer_banner.bmp`:
- Taille: 497 x 314 pixels
- Format: BMP 24-bit
- Contenu: Logo + texte "Auto-École Manager"

**2. Icône (Petite image en haut)**

Créez une image `installer_icon.bmp`:
- Taille: 55 x 58 pixels
- Format: BMP 24-bit
- Contenu: Icône voiture

Si vous n'avez pas ces images, l'installeur utilisera le style par défaut.

---

### ✅ ÉTAPE 3: TESTER L'INSTALLEUR

#### 1. Test sur machine de développement

```bash
# Lancer l'installeur
installer\AutoEcoleManager_Setup_v1.0.0.exe
```

Vérifiez:
- ☐ Installation sans erreur
- ☐ Raccourci sur le bureau créé
- ☐ Icône correcte
- ☐ Application dans le menu démarrer
- ☐ Application se lance correctement
- ☐ Désinstallation fonctionne

#### 2. Test sur machine vierge (Important!)

Testez sur un PC qui n'a jamais eu l'application:
- Windows 10 ou 11 fraîchement installé
- Ou utilisez une machine virtuelle (VirtualBox)

---

### 📤 ÉTAPE 4: DISTRIBUTION

#### Option 1: USB

```bash
# Copier l'installeur sur une clé USB
copy installer\AutoEcoleManager_Setup_v1.0.0.exe E:\
```

#### Option 2: Google Drive / Dropbox

```
1. Télécharger sur Google Drive
2. Créer un lien de partage
3. Envoyer le lien au client
```

#### Option 3: Site web

```html
<!-- Bouton de téléchargement -->
<a href="AutoEcoleManager_Setup_v1.0.0.exe" download>
  Télécharger Auto-École Manager
</a>
```

---

### 🔧 DÉPANNAGE

#### Problème: PyInstaller ne trouve pas les modules

**Solution:**
```bash
# Installer tous les modules requis
pip install -r requirements.txt

# Vérifier
pip list
```

#### Problème: Icône ne s'affiche pas

**Solution:**
```bash
# Convertir PNG en ICO
# Utilisez: https://convertio.co/fr/png-ico/
# Puis: --icon=assets/app_icon.ico
```

#### Problème: Antivirus bloque l'exécutable

**Solution:**
```bash
# Signer le .exe avec un certificat (optionnel mais recommandé)
# Ou ajouter une exception dans l'antivirus
```

#### Problème: "Erreur au lancement"

**Solution:**
```bash
# Tester sans --windowed pour voir les erreurs
pyinstaller --onefile --icon=assets/app_icon.png src/main_gui.py

# Lancer et vérifier les messages d'erreur
dist\main_gui.exe
```

---

### 📊 CHECKLIST COMPLÈTE

Avant de distribuer l'installeur:

**Développement:**
- ☐ Code testé et sans bugs
- ☐ Base de données initialisée
- ☐ Tous les modules fonctionnent
- ☐ Documentation à jour

**Exécutable:**
- ☐ Compilation sans erreur
- ☐ Application se lance
- ☐ Icône visible
- ☐ Toutes les fonctionnalités OK

**Installeur:**
- ☐ Installation réussie
- ☐ Raccourcis créés (bureau + menu)
- ☐ Icônes correctes
- ☐ Désinstallation propre
- ☐ Testé sur machine vierge

**Documentation:**
- ☐ LICENSE.txt présent
- ☐ INSTALL_INFO.txt clair
- ☐ AFTER_INSTALL.txt utile
- ☐ Contact support visible

---

### 💡 CONSEILS PRO

#### 1. Versioning

Changez la version dans `setup.iss`:
```iss
#define MyAppVersion "1.0.1"  ; Incrémentez à chaque mise à jour
```

#### 2. Réduire la taille

L'exécutable peut être gros (100-200 MB). Pour réduire:
```bash
# Utiliser UPX (compresseur)
pyinstaller ... --upx-dir="C:\upx"
```

#### 3. Updates automatiques

Ajoutez un système de vérification des mises à jour:
```python
# Dans l'application
def check_updates():
    url = "https://autoecole-manager.ma/version.txt"
    # Comparer avec la version actuelle
```

#### 4. Log des installations

Demandez aux clients de vous envoyer:
```
C:\Program Files\Auto-École Manager\install.log
```

---

### 📞 SUPPORT

Si vous rencontrez des problèmes:

**Email:** e.belqasim@gmail.com  
**Téléphone:** +212 637-636146

---

### 🎉 FÉLICITATIONS!

Vous avez maintenant un installeur professionnel prêt à distribuer!

**Fichier final:**
```
installer/AutoEcoleManager_Setup_v1.0.0.exe
```

**Taille:** ~150-200 MB  
**Système:** Windows 7/8/10/11  
**Installation:** 2-3 minutes  

---

© 2024-2025 Auto-École Manager
