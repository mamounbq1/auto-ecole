"""
Gestionnaire de configuration pour l'application
Permet de récupérer les informations du centre pour les rapports
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Gestionnaire de configuration centralisé"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Charge la configuration depuis config.json"""
        config_path = Path("config.json")
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                self._config = {}
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
            self._config = {}
    
    def reload(self):
        """Recharge la configuration depuis le fichier"""
        self._load_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration"""
        return self._config.get(key, default)
    
    def get_center_info(self) -> Dict[str, str]:
        """
        Récupère toutes les informations du centre
        
        Returns:
            Dict contenant toutes les informations du centre
        """
        center = self._config.get('center', {})
        
        # Valeurs par défaut si non configuré
        return {
            'name': center.get('name', 'Auto-École Manager'),
            'address': center.get('address', ''),
            'city': center.get('city', ''),
            'postal_code': center.get('postal_code', ''),
            'phone': center.get('phone', ''),
            'email': center.get('email', ''),
            'website': center.get('website', ''),
            'siret': center.get('siret', ''),
            'tva_number': center.get('tva_number', ''),
            'license_number': center.get('license_number', ''),
            'director_name': center.get('director_name', ''),
        }
    
    def get_center_name(self) -> str:
        """Récupère le nom du centre"""
        return self._config.get('center', {}).get('name', 'Auto-École Manager')
    
    def get_center_address(self) -> str:
        """Récupère l'adresse complète du centre"""
        center = self._config.get('center', {})
        address_parts = []
        
        if center.get('address'):
            address_parts.append(center['address'])
        if center.get('city') or center.get('postal_code'):
            city_line = []
            if center.get('postal_code'):
                city_line.append(center['postal_code'])
            if center.get('city'):
                city_line.append(center['city'])
            address_parts.append(' '.join(city_line))
        
        return '\n'.join(address_parts) if address_parts else ''
    
    def get_center_contact(self) -> str:
        """Récupère les informations de contact du centre"""
        center = self._config.get('center', {})
        contact_parts = []
        
        if center.get('phone'):
            contact_parts.append(f"Tél: {center['phone']}")
        if center.get('email'):
            contact_parts.append(f"Email: {center['email']}")
        if center.get('website'):
            contact_parts.append(f"Web: {center['website']}")
        
        return ' | '.join(contact_parts) if contact_parts else ''
    
    def get_center_legal_info(self) -> Dict[str, str]:
        """Récupère les informations légales du centre"""
        center = self._config.get('center', {})
        return {
            'siret': center.get('siret', ''),
            'tva_number': center.get('tva_number', ''),
            'license_number': center.get('license_number', ''),
            'director_name': center.get('director_name', ''),
        }
    
    def get_logo_path(self) -> Optional[str]:
        """Récupère le chemin du logo du centre"""
        logo = self._config.get('pdf', {}).get('company_logo')
        if logo and Path(logo).exists():
            return logo
        return None
    
    def get_export_path(self) -> str:
        """Récupère le chemin du dossier exports depuis config"""
        return self._config.get('paths', {}).get('exports', 'exports')
    
    def get_backup_path(self) -> str:
        """Récupère le chemin du dossier backups depuis config"""
        return self._config.get('paths', {}).get('backups', 'backups')
    
    def get_app_info(self) -> Dict[str, str]:
        """Récupère les informations de l'application"""
        app = self._config.get('app', {})
        return {
            'name': app.get('name', 'Auto-École Manager'),
            'version': app.get('version', '1.0.0'),
            'language': app.get('language', 'fr'),
        }
    
    def format_center_header(self) -> str:
        """
        Formate un en-tête complet pour les rapports
        
        Returns:
            String contenant l'en-tête formaté (nom, adresse, contact)
        """
        center = self.get_center_info()
        lines = []
        
        # Nom du centre (en gras si possible)
        if center['name']:
            lines.append(center['name'].upper())
        
        # Adresse
        if center['address']:
            lines.append(center['address'])
        
        # Ville + Code postal
        city_line = []
        if center['postal_code']:
            city_line.append(center['postal_code'])
        if center['city']:
            city_line.append(center['city'])
        if city_line:
            lines.append(' '.join(city_line))
        
        # Séparateur
        if lines:
            lines.append('')  # Ligne vide
        
        # Contact
        contact_parts = []
        if center['phone']:
            contact_parts.append(f"📞 {center['phone']}")
        if center['email']:
            contact_parts.append(f"📧 {center['email']}")
        if contact_parts:
            lines.append(' | '.join(contact_parts))
        
        # Infos légales
        legal_parts = []
        if center['license_number']:
            legal_parts.append(f"Agrément: {center['license_number']}")
        if center['siret']:
            legal_parts.append(f"SIRET/ICE: {center['siret']}")
        if legal_parts:
            lines.append(' | '.join(legal_parts))
        
        return '\n'.join(lines)
    
    def format_center_footer(self) -> str:
        """
        Formate un pied de page pour les rapports
        
        Returns:
            String contenant le pied de page formaté
        """
        center = self.get_center_info()
        parts = []
        
        if center['website']:
            parts.append(center['website'])
        if center['email']:
            parts.append(center['email'])
        if center['phone']:
            parts.append(center['phone'])
        
        return ' | '.join(parts) if parts else ''


# Instance globale (singleton)
def get_config_manager() -> ConfigManager:
    """Récupère l'instance globale du ConfigManager"""
    return ConfigManager()
