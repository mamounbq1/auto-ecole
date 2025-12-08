"""
Système de notifications Email/SMS avec Twilio et SMTP
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from src.utils import get_logger

logger = get_logger()

# Configuration par défaut (peut être overriden par config.json)
DEFAULT_CONFIG = {
    "email": {
        "enabled": False,
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "",
        "smtp_password": "",
        "from_name": "Auto-École",
        "from_email": ""
    },
    "sms": {
        "enabled": False,
        "twilio_account_sid": "",
        "twilio_auth_token": "",
        "twilio_phone_number": ""
    }
}


class NotificationManager:
    """Gestionnaire de notifications Email et SMS"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialiser le gestionnaire de notifications
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config = self.load_config(config_path)
        self.twilio_client = None
        
        # Initialiser Twilio si configuré
        if self.config["sms"]["enabled"]:
            self.init_twilio()
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Charger la configuration"""
        config = DEFAULT_CONFIG.copy()
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    
                    # Fusionner avec la config par défaut
                    if "notifications" in user_config:
                        notif_config = user_config["notifications"]
                        
                        if "email" in notif_config:
                            config["email"].update(notif_config["email"])
                        
                        if "sms" in notif_config:
                            config["sms"].update(notif_config["sms"])
                
                logger.info("Configuration des notifications chargée")
            except Exception as e:
                logger.error(f"Erreur lors du chargement de la config : {e}")
        
        return config
    
    def init_twilio(self):
        """Initialiser le client Twilio"""
        try:
            from twilio.rest import Client
            
            account_sid = self.config["sms"]["twilio_account_sid"]
            auth_token = self.config["sms"]["twilio_auth_token"]
            
            if account_sid and auth_token:
                self.twilio_client = Client(account_sid, auth_token)
                logger.info("Client Twilio initialisé")
            else:
                logger.warning("Identifiants Twilio manquants")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de Twilio : {e}")
    
    def send_email(self, 
                   to_email: str,
                   subject: str,
                   body: str,
                   html: bool = False,
                   attachments: Optional[List[str]] = None) -> tuple[bool, str]:
        """
        Envoyer un email
        
        Args:
            to_email: Adresse email du destinataire
            subject: Sujet de l'email
            body: Corps du message
            html: Si True, le body est interprété comme HTML
            attachments: Liste des chemins de fichiers à joindre
        
        Returns:
            Tuple (success, message)
        """
        if not self.config["email"]["enabled"]:
            return False, "Les notifications par email ne sont pas activées"
        
        try:
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = f"{self.config['email']['from_name']} <{self.config['email']['from_email']}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
            
            # Corps du message
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Pièces jointes
            if attachments:
                for filepath in attachments:
                    if os.path.exists(filepath):
                        with open(filepath, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(filepath)}'
                            )
                            msg.attach(part)
            
            # Connexion SMTP et envoi
            server = smtplib.SMTP(
                self.config["email"]["smtp_host"],
                self.config["email"]["smtp_port"]
            )
            server.starttls()
            server.login(
                self.config["email"]["smtp_user"],
                self.config["email"]["smtp_password"]
            )
            
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email envoyé à {to_email}")
            return True, "Email envoyé avec succès"
            
        except Exception as e:
            error_msg = f"Erreur lors de l'envoi de l'email : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def send_sms(self, to_phone: str, message: str) -> tuple[bool, str]:
        """
        Envoyer un SMS via Twilio
        
        Args:
            to_phone: Numéro de téléphone (format international, ex: +212600000000)
            message: Message à envoyer (max 160 caractères recommandé)
        
        Returns:
            Tuple (success, message)
        """
        if not self.config["sms"]["enabled"]:
            return False, "Les notifications par SMS ne sont pas activées"
        
        if not self.twilio_client:
            return False, "Client Twilio non initialisé"
        
        try:
            # Vérifier le format du numéro
            if not to_phone.startswith('+'):
                to_phone = f"+{to_phone}"
            
            # Envoyer le SMS
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=self.config["sms"]["twilio_phone_number"],
                to=to_phone
            )
            
            logger.info(f"SMS envoyé à {to_phone}, SID: {message_obj.sid}")
            return True, f"SMS envoyé (ID: {message_obj.sid})"
            
        except Exception as e:
            error_msg = f"Erreur lors de l'envoi du SMS : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def send_payment_receipt_email(self, student_email: str, receipt_data: Dict[str, Any], 
                                   pdf_path: Optional[str] = None) -> tuple[bool, str]:
        """
        Envoyer un reçu de paiement par email
        
        Args:
            student_email: Email de l'élève
            receipt_data: Données du reçu
            pdf_path: Chemin vers le PDF du reçu (optionnel)
        
        Returns:
            Tuple (success, message)
        """
        subject = f"Reçu de paiement #{receipt_data.get('receipt_number', 'N/A')}"
        
        body = f"""
        Bonjour {receipt_data.get('student_name', '')},

        Nous vous confirmons la réception de votre paiement.

        Détails :
        - N° Reçu : {receipt_data.get('receipt_number', 'N/A')}
        - Date : {receipt_data.get('date', 'N/A')}
        - Montant : {receipt_data.get('amount', 0):,.2f} DH
        - Méthode : {receipt_data.get('payment_method', 'N/A')}

        Merci de votre confiance.

        Cordialement,
        Auto-École
        """
        
        attachments = [pdf_path] if pdf_path and os.path.exists(pdf_path) else None
        
        return self.send_email(student_email, subject, body, attachments=attachments)
    
    def send_session_reminder_sms(self, student_phone: str, session_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Envoyer un rappel de session par SMS
        
        Args:
            student_phone: Téléphone de l'élève
            session_data: Données de la session
        
        Returns:
            Tuple (success, message)
        """
        message = (
            f"Rappel: Votre session de conduite est prévue le "
            f"{session_data.get('date', 'N/A')} à {session_data.get('time', 'N/A')}. "
            f"Moniteur: {session_data.get('instructor', 'N/A')}. "
            f"Auto-École"
        )
        
        # Limiter à 160 caractères
        if len(message) > 160:
            message = message[:157] + "..."
        
        return self.send_sms(student_phone, message)
    
    def send_exam_convocation_email(self, student_email: str, exam_data: Dict[str, Any],
                                    pdf_path: Optional[str] = None) -> tuple[bool, str]:
        """
        Envoyer une convocation d'examen par email
        
        Args:
            student_email: Email de l'élève
            exam_data: Données de l'examen
            pdf_path: Chemin vers le PDF de la convocation
        
        Returns:
            Tuple (success, message)
        """
        subject = f"Convocation Examen {exam_data.get('exam_type', 'N/A')}"
        
        body = f"""
        Bonjour {exam_data.get('student_name', '')},

        Vous êtes convoqué(e) à l'examen {exam_data.get('exam_type', 'N/A')}.

        Détails :
        - N° Convocation : {exam_data.get('summons_number', 'N/A')}
        - Date : {exam_data.get('exam_date', 'N/A')}
        - Heure : {exam_data.get('exam_time', 'N/A')}
        - Lieu : {exam_data.get('location', 'N/A')}

        Merci de vous présenter 30 minutes avant l'heure avec :
        • Votre carte d'identité nationale
        • Cette convocation
        • Votre dossier de candidature

        Bonne chance !

        Cordialement,
        Auto-École
        """
        
        attachments = [pdf_path] if pdf_path and os.path.exists(pdf_path) else None
        
        return self.send_email(student_email, subject, body, attachments=attachments)
    
    def send_debt_reminder_sms(self, student_phone: str, student_name: str, 
                               debt_amount: float) -> tuple[bool, str]:
        """
        Envoyer un rappel de dette par SMS
        
        Args:
            student_phone: Téléphone de l'élève
            student_name: Nom de l'élève
            debt_amount: Montant de la dette
        
        Returns:
            Tuple (success, message)
        """
        message = (
            f"Bonjour {student_name}, "
            f"rappel: solde impayé de {debt_amount:,.0f} DH. "
            f"Merci de régulariser. Auto-École"
        )
        
        return self.send_sms(student_phone, message)
    
    def test_email_config(self) -> tuple[bool, str]:
        """
        Tester la configuration email
        
        Returns:
            Tuple (success, message)
        """
        if not self.config["email"]["enabled"]:
            return False, "Email non configuré"
        
        test_email = self.config["email"]["from_email"]
        
        return self.send_email(
            test_email,
            "Test de configuration",
            "Ceci est un email de test pour vérifier la configuration."
        )
    
    def test_sms_config(self, test_phone: str) -> tuple[bool, str]:
        """
        Tester la configuration SMS
        
        Args:
            test_phone: Numéro de test
        
        Returns:
            Tuple (success, message)
        """
        if not self.config["sms"]["enabled"]:
            return False, "SMS non configuré"
        
        return self.send_sms(
            test_phone,
            "Test Auto-École: Configuration SMS fonctionnelle!"
        )


# Instance globale
_notification_manager = None

def get_notification_manager() -> NotificationManager:
    """Obtenir l'instance du gestionnaire de notifications"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager
