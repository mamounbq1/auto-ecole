"""
Widgets communs réutilisables dans toute l'application
"""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from src.utils.config_manager import get_config_manager


def create_center_header_widget(compact=False):
    """
    Crée un widget d'en-tête avec les informations du centre
    
    Args:
        compact: Si True, affiche une version compacte (sans adresse)
    
    Returns:
        QFrame avec l'en-tête du centre
    """
    config = get_config_manager()
    center = config.get_center_info()
    
    header = QFrame()
    header.setStyleSheet("""
        QFrame {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667eea, stop:1 #764ba2);
            border-radius: 10px;
            padding: 15px;
        }
        QLabel {
            color: white;
            background: transparent;
        }
    """)
    
    layout = QVBoxLayout(header)
    layout.setSpacing(5)
    layout.setContentsMargins(15, 10, 15, 10)
    
    # Nom du centre (toujours affiché)
    name_label = QLabel(center.get('name', 'Auto-École Manager').upper())
    name_label.setStyleSheet("font-size: 18px; font-weight: bold;")
    layout.addWidget(name_label)
    
    if not compact:
        # Adresse
        if center.get('address') or center.get('city'):
            address_parts = []
            if center.get('address'):
                address_parts.append(center['address'])
            
            city_parts = []
            if center.get('postal_code'):
                city_parts.append(center['postal_code'])
            if center.get('city'):
                city_parts.append(center['city'])
            if city_parts:
                address_parts.append(' '.join(city_parts))
            
            if address_parts:
                address_label = QLabel(' - '.join(address_parts))
                address_label.setStyleSheet("font-size: 11px; color: rgba(255, 255, 255, 0.85);")
                layout.addWidget(address_label)
    
    # Contact (toujours affiché)
    contact_parts = []
    if center.get('phone'):
        contact_parts.append(f"📞 {center['phone']}")
    if center.get('email'):
        contact_parts.append(f"📧 {center['email']}")
    if center.get('website'):
        contact_parts.append(f"🌐 {center['website']}")
    
    if contact_parts:
        contact_label = QLabel(' | '.join(contact_parts))
        contact_label.setStyleSheet("font-size: 10px; color: rgba(255, 255, 255, 0.8);")
        layout.addWidget(contact_label)
    
    return header


def create_info_card(title, content, color="#3498db"):
    """
    Crée une carte d'information colorée
    
    Args:
        title: Titre de la carte
        content: Contenu (peut être du HTML)
        color: Couleur principale
    
    Returns:
        QFrame avec la carte stylisée
    """
    card = QFrame()
    card.setStyleSheet(f"""
        QFrame {{
            background: white;
            border-left: 4px solid {color};
            border-radius: 8px;
            padding: 15px;
        }}
        QFrame:hover {{
            background: #f8f9fa;
        }}
    """)
    
    layout = QVBoxLayout(card)
    layout.setSpacing(8)
    
    # Titre
    title_label = QLabel(title)
    title_label.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {color};")
    layout.addWidget(title_label)
    
    # Contenu
    content_label = QLabel(content)
    content_label.setStyleSheet("color: #555; font-size: 12px;")
    content_label.setWordWrap(True)
    layout.addWidget(content_label)
    
    return card


def create_stat_card(title, value, icon="📊", color="#3498db", subtitle=""):
    """
    Crée une carte statistique moderne
    
    Args:
        title: Titre de la stat
        value: Valeur à afficher
        icon: Emoji/icône
        color: Couleur du thème
        subtitle: Sous-titre optionnel
    
    Returns:
        QFrame avec la carte stylisée
    """
    card = QFrame()
    card.setStyleSheet(f"""
        QFrame {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {color}, stop:1 {_darken_color(color, 20)});
            border-radius: 12px;
            padding: 20px;
            min-height: 120px;
        }}
        QLabel {{
            color: white;
            background: transparent;
        }}
    """)
    
    layout = QVBoxLayout(card)
    layout.setSpacing(5)
    
    # Icône + Titre
    header_layout = QVBoxLayout()
    icon_label = QLabel(icon)
    icon_label.setStyleSheet("font-size: 32px;")
    icon_label.setAlignment(Qt.AlignLeft)
    header_layout.addWidget(icon_label)
    
    title_label = QLabel(title)
    title_label.setStyleSheet("font-size: 11px; opacity: 0.9;")
    title_label.setWordWrap(True)
    header_layout.addWidget(title_label)
    
    layout.addLayout(header_layout)
    layout.addStretch()
    
    # Valeur
    value_label = QLabel(str(value))
    value_label.setStyleSheet("font-size: 32px; font-weight: bold;")
    layout.addWidget(value_label)
    
    # Sous-titre optionnel
    if subtitle:
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("font-size: 10px; opacity: 0.8;")
        layout.addWidget(subtitle_label)
    
    return card


def _darken_color(hex_color, percent):
    """
    Assombrit une couleur hexadécimale
    
    Args:
        hex_color: Couleur en hex (#RRGGBB)
        percent: Pourcentage d'assombrissement (0-100)
    
    Returns:
        Couleur assombrie en hex
    """
    # Enlever le #
    hex_color = hex_color.lstrip('#')
    
    # Convertir en RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # Assombrir
    factor = 1 - (percent / 100)
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    
    # Reconvertir en hex
    return f"#{r:02x}{g:02x}{b:02x}"
