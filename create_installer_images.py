#!/usr/bin/env python3
"""
Script pour créer les images de l'installeur Inno Setup
- Banner: 497x314 pixels (grande image en haut)
- Small Icon: 55x58 pixels (petite icône)
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_banner():
    """Créer l'image banner pour l'installeur (497x314)"""
    
    # Créer l'image
    width, height = 497, 314
    img = Image.new('RGB', (width, height), color='#f5f6fa')
    draw = ImageDraw.Draw(img)
    
    # Fond dégradé
    for y in range(height):
        # Dégradé du bleu clair au blanc
        r = int(245 + (255 - 245) * (y / height))
        g = int(246 + (255 - 246) * (y / height))
        b = int(250 + (255 - 250) * (y / height))
        color = (r, g, b)
        draw.line([(0, y), (width, y)], fill=color)
    
    # Rectangle décoratif en haut
    draw.rectangle([0, 0, width, 60], fill='#2c3e50')
    
    # Rectangle décoratif à gauche
    draw.rectangle([0, 0, 150, height], fill='#3498db', outline=None)
    
    # Cercle pour simuler l'icône de voiture (gauche)
    circle_x, circle_y = 75, 157
    circle_radius = 50
    draw.ellipse(
        [circle_x - circle_radius, circle_y - circle_radius,
         circle_x + circle_radius, circle_y + circle_radius],
        fill='#e67e22', outline='#ffffff', width=4
    )
    
    # Dessiner une voiture simplifiée dans le cercle
    # Carrosserie
    car_points = [
        (circle_x - 25, circle_y + 10),
        (circle_x - 25, circle_y),
        (circle_x - 15, circle_y - 10),
        (circle_x + 15, circle_y - 10),
        (circle_x + 25, circle_y),
        (circle_x + 25, circle_y + 10),
    ]
    draw.polygon(car_points, fill='#ffffff')
    
    # Roues
    draw.ellipse([circle_x - 20, circle_y + 5, circle_x - 10, circle_y + 15], fill='#2c3e50')
    draw.ellipse([circle_x + 10, circle_y + 5, circle_x + 20, circle_y + 15], fill='#2c3e50')
    
    # Fenêtres
    draw.rectangle([circle_x - 12, circle_y - 8, circle_x - 2, circle_y - 1], fill='#3498db')
    draw.rectangle([circle_x + 2, circle_y - 8, circle_x + 12, circle_y - 1], fill='#3498db')
    
    try:
        # Essayer de charger une police système
        try:
            font_title = ImageFont.truetype("arial.ttf", 42)
            font_subtitle = ImageFont.truetype("arial.ttf", 20)
            font_small = ImageFont.truetype("arial.ttf", 14)
        except:
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
                font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            except:
                # Fallback: police par défaut
                font_title = ImageFont.load_default()
                font_subtitle = ImageFont.load_default()
                font_small = ImageFont.load_default()
        
        # Titre principal
        title_text = "Auto-École Manager"
        draw.text((180, 80), title_text, fill='#2c3e50', font=font_title)
        
        # Sous-titre
        subtitle_text = "Système de Gestion Professionnel"
        draw.text((180, 140), subtitle_text, fill='#7f8c8d', font=font_subtitle)
        
        # Version
        version_text = "Version 1.0.0"
        draw.text((180, 180), version_text, fill='#95a5a6', font=font_small)
        
        # Ligne de séparation
        draw.line([(180, 210), (480, 210)], fill='#bdc3c7', width=2)
        
        # Caractéristiques
        features = [
            "✓ Gestion des élèves",
            "✓ Planning et séances",
            "✓ Comptabilité complète",
            "✓ Parc automobile"
        ]
        
        y_pos = 230
        for feature in features:
            draw.text((180, y_pos), feature, fill='#2c3e50', font=font_small)
            y_pos += 20
        
    except Exception as e:
        print(f"Note: Police par défaut utilisée - {e}")
        # Utiliser du texte simple sans police spéciale
        draw.text((180, 100), "Auto-Ecole Manager", fill='#2c3e50')
        draw.text((180, 140), "Version 1.0.0", fill='#7f8c8d')
    
    # Sauvegarder
    img.save('installer_banner.bmp')
    print("✓ Banner créé: installer_banner.bmp (497x314)")
    return img

def create_small_icon():
    """Créer la petite icône pour l'installeur (55x58)"""
    
    # Créer l'image
    width, height = 55, 58
    img = Image.new('RGB', (width, height), color='#3498db')
    draw = ImageDraw.Draw(img)
    
    # Fond dégradé bleu
    for y in range(height):
        ratio = y / height
        r = int(52 + (41 - 52) * ratio)
        g = int(152 + (128 - 152) * ratio)
        b = int(219 + (185 - 219) * ratio)
        color = (r, g, b)
        draw.line([(0, y), (width, y)], fill=color)
    
    # Cercle central pour l'icône
    center_x, center_y = width // 2, height // 2
    circle_radius = 22
    draw.ellipse(
        [center_x - circle_radius, center_y - circle_radius,
         center_x + circle_radius, center_y + circle_radius],
        fill='#e67e22', outline='#ffffff', width=2
    )
    
    # Dessiner une voiture simplifiée
    # Carrosserie
    car_points = [
        (center_x - 12, center_y + 5),
        (center_x - 12, center_y - 2),
        (center_x - 7, center_y - 7),
        (center_x + 7, center_y - 7),
        (center_x + 12, center_y - 2),
        (center_x + 12, center_y + 5),
    ]
    draw.polygon(car_points, fill='#ffffff')
    
    # Roues
    draw.ellipse([center_x - 10, center_y + 2, center_x - 5, center_y + 7], fill='#2c3e50')
    draw.ellipse([center_x + 5, center_y + 2, center_x + 10, center_y + 7], fill='#2c3e50')
    
    # Fenêtres
    draw.rectangle([center_x - 6, center_y - 6, center_x - 1, center_y - 1], fill='#3498db')
    draw.rectangle([center_x + 1, center_y - 6, center_x + 6, center_y - 1], fill='#3498db')
    
    # Sauvegarder
    img.save('installer_icon.bmp')
    print("✓ Icône créée: installer_icon.bmp (55x58)")
    return img

def create_preview():
    """Créer une prévisualisation des deux images côte à côte"""
    
    # Charger les images
    try:
        banner = Image.open('installer_banner.bmp')
        icon = Image.open('installer_icon.bmp')
        
        # Créer une image de prévisualisation
        preview_width = 600
        preview_height = 400
        preview = Image.new('RGB', (preview_width, preview_height), color='#ecf0f1')
        
        # Coller le banner
        preview.paste(banner, (50, 20))
        
        # Coller l'icône agrandie
        icon_large = icon.resize((110, 116), Image.Resampling.LANCZOS)
        preview.paste(icon_large, (245, 340))
        
        # Ajouter des labels
        draw = ImageDraw.Draw(preview)
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 345), "Banner: 497x314", fill='#2c3e50', font=font)
        draw.text((370, 395), "Icon: 55x58", fill='#2c3e50', font=font)
        
        preview.save('installer_images_preview.png')
        print("✓ Prévisualisation créée: installer_images_preview.png")
        
    except Exception as e:
        print(f"Note: Impossible de créer la prévisualisation - {e}")

def main():
    """Fonction principale"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     🎨 CRÉATION DES IMAGES INSTALLEUR                     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    try:
        # Vérifier que PIL est installé
        from PIL import Image
        print("✓ PIL/Pillow est installé")
    except ImportError:
        print("❌ PIL/Pillow n'est pas installé!")
        print("   Installez-le avec: pip install pillow")
        return 1
    
    print()
    print("Création des images...")
    print()
    
    # Créer les images
    create_banner()
    create_small_icon()
    create_preview()
    
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║              ✅ IMAGES CRÉÉES AVEC SUCCÈS!                 ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print("📁 Fichiers créés:")
    print("   • installer_banner.bmp  (497x314 - Banner installeur)")
    print("   • installer_icon.bmp    (55x58 - Petite icône)")
    print("   • installer_images_preview.png (Prévisualisation)")
    print()
    print("🎯 Ces images sont prêtes pour Inno Setup!")
    print("   Le fichier setup.iss les utilisera automatiquement.")
    print()
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
