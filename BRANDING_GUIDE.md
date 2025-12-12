# 🎨 Guide de Branding - Auto-École Manager

## 📁 Assets disponibles

Le dossier `assets/` contient tous les éléments visuels de l'application :

### Icônes

1. **app_icon_new.png** (189 KB, 1024x1024)
   - Icône principale de l'application
   - Design professionnel avec voiture orange/ambre
   - Utilisée dans les fenêtres de l'application

2. **app_icon.ico** (61 KB, multi-résolution)
   - Format Windows natif
   - Contient 6 résolutions : 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
   - Utilisée pour l'exécutable et les raccourcis Windows
   - **Utilisation prioritaire pour Windows**

3. **app_icon.png** (1.7 KB)
   - Ancienne icône (conservée pour compatibilité)

### Bannières

4. **installer_banner.png** (185 KB, 1024x768)
   - Bannière complète pour l'installateur
   - Design professionnel avec texte "Auto-École Manager"
   - Gradient moderne blanc/bleu

5. **installer_banner.bmp** (151 KB, 164x314)
   - Version BMP pour Inno Setup
   - Redimensionnée pour l'assistant d'installation

6. **installer_icon.bmp** (9.1 KB, 55x55)
   - Petite icône pour Inno Setup
   - Utilisée dans l'assistant d'installation

## 🖼️ Utilisation dans le code

### Application principale
```python
# Dans main_gui.py
icon_ico = Path(__file__).parent.parent / "assets" / "app_icon.ico"
icon_png = Path(__file__).parent.parent / "assets" / "app_icon_new.png"

if icon_ico.exists():
    app.setWindowIcon(QIcon(str(icon_ico)))
elif icon_png.exists():
    app.setWindowIcon(QIcon(str(icon_png)))
```

### Fenêtres individuelles
Toutes les fenêtres (LoginWindow, MainWindow, LicenseActivationWindow) utilisent le même système :
- Priorité à `app_icon.ico` (format Windows)
- Fallback sur `app_icon_new.png`

### Logo dans l'en-tête
```python
# Dans login_window.py - Logo 80x80 dans le header
icon_new = Path(__file__).parent.parent.parent / "assets" / "app_icon_new.png"
if icon_new.exists():
    logo_label = QLabel()
    pixmap = QPixmap(str(icon_new))
    scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    logo_label.setPixmap(scaled_pixmap)
```

## 📦 Configuration de l'installateur

### PyInstaller (build_executable.py)
```python
'--icon=assets/app_icon.ico',  # Icône de l'exécutable
```

### Inno Setup (setup.iss)
```ini
SetupIconFile=assets\app_icon.ico
WizardImageFile=assets\installer_banner.bmp
WizardSmallImageFile=assets\installer_icon.bmp

[Icons]
; Tous les raccourcis utilisent app_icon.ico
IconFilename: "{app}\assets\app_icon.ico"
```

## 🎨 Identité visuelle

### Couleurs principales
- **Orange/Ambre** : Couleur principale de la voiture
- **Blanc à Bleu clair** : Gradient de fond
- **#2c3e50** : Texte principal
- **#7f8c8d** : Texte secondaire

### Typographie
- **Titres** : Segoe UI, 24pt, Bold
- **Sous-titres** : Segoe UI, 11pt, Normal
- **Corps** : Segoe UI, 10pt

### Style
- Design moderne et professionnel
- Icône simplifiée et reconnaissable
- Compatible avec thème clair et foncé Windows

## 📝 Notes importantes

1. **Priorité des formats** :
   - Windows : `.ico` (natif)
   - Multi-plateforme : `.png`

2. **Résolutions supportées** :
   - Icône : de 16x16 à 1024x1024
   - Bannière : 1024x768 (source), 164x314 (installateur)

3. **Taille totale** : ~612 KB pour tous les assets

4. **Génération** :
   - Images générées avec fal-ai/flux-2
   - Conversion BMP/ICO avec PIL/Pillow

## 🔄 Mise à jour des assets

Si vous souhaitez changer les images :

1. Remplacer `app_icon_new.png` (format carré, min 512x512)
2. Exécuter le script de conversion :
```bash
python3 -c "
from PIL import Image
# Créer .ico
icon = Image.open('assets/app_icon_new.png')
icon.save('assets/app_icon.ico', format='ICO', 
          sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
# Créer BMP pour installateur
icon_small = icon.resize((55, 55), Image.Resampling.LANCZOS)
icon_small.save('assets/installer_icon.bmp')
"
```

3. Pour la bannière :
   - Remplacer `installer_banner.png` (ratio 4:3)
   - Convertir en BMP 164x314 pour Inno Setup

## 📧 Contact

Pour toute question sur le branding :
- Email : e.belqasim@gmail.com
- Téléphone : +212 637-636146

---
© 2024-2025 Auto-École Manager
Version 1.0.0
