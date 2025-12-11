"""
Gestionnaire de Licences pour Auto-École
Système de protection et d'activation de licence
"""

import os
import json
import hashlib
import platform
import subprocess
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from cryptography.fernet import Fernet
import base64

from src.utils import get_logger

logger = get_logger()


class LicenseManager:
    """Gestionnaire de licences avec protection Hardware ID"""
    
    def __init__(self, license_file: str = "config/license.dat"):
        self.license_file = license_file
        self.config_dir = os.path.dirname(license_file)
        
        # Créer le répertoire config si nécessaire
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)
        
        # Clé de chiffrement (à garder secrète en production)
        self._encryption_key = self._get_encryption_key()
        self.cipher = Fernet(self._encryption_key)
    
    def _get_encryption_key(self) -> bytes:
        """Génère une clé de chiffrement basée sur un salt secret"""
        # IMPORTANT : En production, utilisez une clé plus sécurisée
        secret_salt = b"AutoEcole_Secret_Key_2024_V1"
        return base64.urlsafe_b64encode(hashlib.sha256(secret_salt).digest())
    
    def get_hardware_id(self) -> str:
        """
        Récupère l'identifiant unique de la machine
        Combine plusieurs éléments pour plus de sécurité
        """
        try:
            # Récupérer des identifiants système
            system_info = []
            
            # 1. Nom de la machine
            system_info.append(platform.node())
            
            # 2. Système d'exploitation
            system_info.append(platform.system())
            system_info.append(platform.release())
            
            # 3. Architecture processeur
            system_info.append(platform.machine())
            
            # 4. UUID de la machine (Windows/Linux)
            try:
                if platform.system() == "Windows":
                    output = subprocess.check_output("wmic csproduct get uuid", shell=True)
                    uuid = output.decode().split('\n')[1].strip()
                    system_info.append(uuid)
                elif platform.system() == "Linux":
                    with open('/etc/machine-id', 'r') as f:
                        system_info.append(f.read().strip())
                elif platform.system() == "Darwin":  # macOS
                    output = subprocess.check_output("ioreg -rd1 -c IOPlatformExpertDevice", shell=True)
                    uuid = output.decode().split('"IOPlatformUUID" = "')[1].split('"')[0]
                    system_info.append(uuid)
            except:
                pass
            
            # Créer un hash unique
            combined = "|".join(system_info)
            hardware_id = hashlib.sha256(combined.encode()).hexdigest()[:16].upper()
            
            logger.info(f"Hardware ID généré: {hardware_id}")
            return hardware_id
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du Hardware ID: {e}")
            # Fallback: utiliser un ID basique
            return hashlib.md5(platform.node().encode()).hexdigest()[:16].upper()
    
    def generate_license_key(self, 
                            company_name: str,
                            duration_days: int = 365,
                            hardware_id: Optional[str] = None) -> str:
        """
        Génère une clé de licence unique
        
        Args:
            company_name: Nom de l'auto-école
            duration_days: Durée de validité en jours
            hardware_id: ID matériel (si None, utilise celui de la machine actuelle)
        
        Returns:
            Clé de licence chiffrée
        """
        if hardware_id is None:
            hardware_id = self.get_hardware_id()
        
        # Données de la licence
        expiry_date = (datetime.now() + timedelta(days=duration_days)).strftime('%Y-%m-%d')
        
        license_data = {
            'company': company_name,
            'hardware_id': hardware_id,
            'expiry_date': expiry_date,
            'issued_date': datetime.now().strftime('%Y-%m-%d'),
            'version': '1.0'
        }
        
        # Chiffrer les données
        json_data = json.dumps(license_data)
        encrypted = self.cipher.encrypt(json_data.encode())
        
        # Encoder en base64 pour une clé lisible
        license_key = base64.b64encode(encrypted).decode()
        
        # Formater la clé (groupes de 5 caractères)
        formatted_key = '-'.join([license_key[i:i+5] for i in range(0, len(license_key), 5)])
        
        logger.info(f"Licence générée pour {company_name}, valide jusqu'au {expiry_date}")
        return formatted_key
    
    def validate_license_key(self, license_key: str) -> Tuple[bool, str]:
        """
        Valide une clé de licence
        
        Args:
            license_key: Clé de licence à valider
        
        Returns:
            (is_valid, message)
        """
        try:
            # Nettoyer la clé (supprimer les tirets et espaces)
            clean_key = license_key.replace('-', '').replace(' ', '')
            
            # Décoder
            encrypted_data = base64.b64decode(clean_key)
            decrypted_data = self.cipher.decrypt(encrypted_data)
            license_data = json.loads(decrypted_data.decode())
            
            # Vérifier le Hardware ID
            current_hardware_id = self.get_hardware_id()
            if license_data['hardware_id'] != current_hardware_id:
                logger.warning(f"Hardware ID mismatch: {current_hardware_id} != {license_data['hardware_id']}")
                return False, "⚠️ Cette licence n'est pas valide pour cet ordinateur"
            
            # Vérifier la date d'expiration
            expiry_date = datetime.strptime(license_data['expiry_date'], '%Y-%m-%d')
            if datetime.now() > expiry_date:
                return False, f"❌ Licence expirée le {license_data['expiry_date']}"
            
            # Licence valide
            days_remaining = (expiry_date - datetime.now()).days
            logger.info(f"Licence valide pour {license_data['company']}, {days_remaining} jours restants")
            return True, f"✅ Licence valide pour {license_data['company']} ({days_remaining} jours restants)"
            
        except Exception as e:
            logger.error(f"Erreur validation licence: {e}")
            return False, "❌ Clé de licence invalide"
    
    def activate_license(self, license_key: str) -> Tuple[bool, str]:
        """
        Active une licence sur cette machine
        
        Args:
            license_key: Clé de licence
        
        Returns:
            (success, message)
        """
        # Valider la clé
        is_valid, message = self.validate_license_key(license_key)
        
        if not is_valid:
            return False, message
        
        # Sauvegarder la licence
        try:
            # Nettoyer la clé
            clean_key = license_key.replace('-', '').replace(' ', '')
            
            # Décrypter pour récupérer les infos
            encrypted_data = base64.b64decode(clean_key)
            decrypted_data = self.cipher.decrypt(encrypted_data)
            license_data = json.loads(decrypted_data.decode())
            
            # Ajouter la date d'activation
            license_data['activation_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Sauvegarder dans le fichier
            with open(self.license_file, 'w') as f:
                json.dump(license_data, f, indent=4)
            
            logger.info(f"Licence activée avec succès pour {license_data['company']}")
            return True, f"✅ Licence activée avec succès!\nAuto-École: {license_data['company']}\nValide jusqu'au: {license_data['expiry_date']}"
            
        except Exception as e:
            logger.error(f"Erreur activation licence: {e}")
            return False, "❌ Erreur lors de l'activation de la licence"
    
    def is_licensed(self) -> bool:
        """Vérifie si l'application est sous licence valide"""
        try:
            if not os.path.exists(self.license_file):
                return False
            
            with open(self.license_file, 'r') as f:
                license_data = json.load(f)
            
            # Vérifier Hardware ID
            current_hardware_id = self.get_hardware_id()
            if license_data.get('hardware_id') != current_hardware_id:
                logger.warning("Hardware ID ne correspond pas")
                return False
            
            # Vérifier expiration
            expiry_date = datetime.strptime(license_data['expiry_date'], '%Y-%m-%d')
            if datetime.now() > expiry_date:
                logger.warning("Licence expirée")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur vérification licence: {e}")
            return False
    
    def get_license_info(self) -> Optional[Dict]:
        """Récupère les informations de la licence active"""
        try:
            if not os.path.exists(self.license_file):
                return None
            
            with open(self.license_file, 'r') as f:
                license_data = json.load(f)
            
            # Calculer les jours restants
            expiry_date = datetime.strptime(license_data['expiry_date'], '%Y-%m-%d')
            days_remaining = (expiry_date - datetime.now()).days
            
            license_data['days_remaining'] = days_remaining
            license_data['status'] = 'active' if self.is_licensed() else 'expired'
            
            return license_data
            
        except Exception as e:
            logger.error(f"Erreur récupération info licence: {e}")
            return None
    
    def deactivate_license(self) -> bool:
        """Désactive la licence actuelle"""
        try:
            if os.path.exists(self.license_file):
                os.remove(self.license_file)
                logger.info("Licence désactivée")
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur désactivation licence: {e}")
            return False


# Instance globale
_license_manager = None

def get_license_manager() -> LicenseManager:
    """Récupère l'instance du gestionnaire de licences"""
    global _license_manager
    if _license_manager is None:
        _license_manager = LicenseManager()
    return _license_manager
