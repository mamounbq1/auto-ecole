"""
Gestionnaire d'export de données (CSV, PDF)
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .logger import get_logger
from .config_manager import get_config_manager

logger = get_logger()


class ExportManager:
    """Gestionnaire d'export de données"""
    
    def __init__(self, export_dir: str = "exports"):
        """
        Initialiser le gestionnaire d'export
        
        Args:
            export_dir: Répertoire des exports
        """
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
        self.config = get_config_manager()
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str, 
                      fieldnames: Optional[List[str]] = None) -> tuple[bool, str]:
        """
        Exporter des données vers un fichier CSV
        
        Args:
            data: Liste de dictionnaires à exporter
            filename: Nom du fichier (sans extension)
            fieldnames: Liste des champs à exporter (None = tous)
        
        Returns:
            Tuple (success, filepath_or_error)
        """
        try:
            if not data:
                return False, "Aucune donnée à exporter"
            
            # Générer le nom de fichier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"{filename}_{timestamp}.csv"
            filepath = os.path.join(self.export_dir, csv_filename)
            
            # Déterminer les champs
            if fieldnames is None:
                fieldnames = list(data[0].keys())
            
            # Écrire le CSV avec en-tête du centre
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                # En-tête avec informations du centre
                center = self.config.get_center_info()
                csvfile.write(f"# {center.get('name', 'Auto-École Manager')}\n")
                if center.get('address'):
                    csvfile.write(f"# {center['address']}\n")
                if center.get('phone') or center.get('email'):
                    contact_parts = []
                    if center.get('phone'):
                        contact_parts.append(f"Tél: {center['phone']}")
                    if center.get('email'):
                        contact_parts.append(f"Email: {center['email']}")
                    csvfile.write(f"# {' | '.join(contact_parts)}\n")
                csvfile.write(f"# Exporté le {datetime.now().strftime('%d/%m/%Y à %H:%M')}\n")
                csvfile.write("#\n")
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"Export CSV créé : {filepath} ({len(data)} lignes)")
            return True, filepath
            
        except Exception as e:
            error_msg = f"Erreur lors de l'export CSV : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def import_from_csv(self, filepath: str, 
                       required_fields: Optional[List[str]] = None) -> tuple[bool, List[Dict[str, Any]], str]:
        """
        Importer des données depuis un fichier CSV
        
        Args:
            filepath: Chemin vers le fichier CSV
            required_fields: Champs obligatoires
        
        Returns:
            Tuple (success, data, message)
        """
        try:
            if not os.path.exists(filepath):
                return False, [], "Fichier introuvable"
            
            data = []
            with open(filepath, 'r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Vérifier les champs requis
                if required_fields:
                    missing_fields = set(required_fields) - set(reader.fieldnames or [])
                    if missing_fields:
                        return False, [], f"Champs manquants : {', '.join(missing_fields)}"
                
                # Lire les données
                for row in reader:
                    data.append(row)
            
            logger.info(f"Import CSV réussi : {filepath} ({len(data)} lignes)")
            return True, data, f"{len(data)} lignes importées"
            
        except Exception as e:
            error_msg = f"Erreur lors de l'import CSV : {str(e)}"
            logger.error(error_msg)
            return False, [], error_msg
    
    def export_to_pdf(self, content: str, filename: str, 
                     title: Optional[str] = None) -> tuple[bool, str]:
        """
        Exporter du contenu vers un fichier PDF (version simplifiée)
        
        Args:
            content: Contenu à exporter (texte ou HTML)
            filename: Nom du fichier (sans extension)
            title: Titre du document
        
        Returns:
            Tuple (success, filepath_or_error)
        """
        try:
            # Version simplifiée : créer un fichier HTML qui peut être imprimé en PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"{filename}_{timestamp}.html"
            filepath = os.path.join(self.export_dir, html_filename)
            
            # Template HTML simple
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title or filename}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 0.9em;
            color: #777;
        }}
    </style>
</head>
<body>
    <h1>{title or filename}</h1>
    {content}
    <div class="footer">
        <p>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
    </div>
</body>
</html>
            """
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Export HTML créé : {filepath}")
            return True, filepath
            
        except Exception as e:
            error_msg = f"Erreur lors de l'export PDF : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def generate_receipt_html(self, receipt_data: Dict[str, Any]) -> str:
        """
        Générer le HTML d'un reçu de paiement
        
        Args:
            receipt_data: Données du reçu
        
        Returns:
            Contenu HTML du reçu
        """
        html = f"""
        <div style="max-width: 800px; margin: 0 auto; border: 2px solid #333; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: #2c3e50;">AUTO-ÉCOLE</h2>
                <h3 style="color: #3498db;">REÇU DE PAIEMENT</h3>
            </div>
            
            <div style="margin: 20px 0;">
                <p><strong>N° Reçu :</strong> {receipt_data.get('receipt_number', 'N/A')}</p>
                <p><strong>Date :</strong> {receipt_data.get('date', 'N/A')}</p>
            </div>
            
            <div style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #3498db;">
                <h4>Informations Élève</h4>
                <p><strong>Nom :</strong> {receipt_data.get('student_name', 'N/A')}</p>
                <p><strong>CIN :</strong> {receipt_data.get('student_cin', 'N/A')}</p>
                <p><strong>Téléphone :</strong> {receipt_data.get('student_phone', 'N/A')}</p>
            </div>
            
            <div style="margin: 20px 0;">
                <h4>Détails du Paiement</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Montant :</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">
                            <strong style="font-size: 1.2em; color: #27ae60;">
                                {receipt_data.get('amount', 0)} DH
                            </strong>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Mode de paiement :</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{receipt_data.get('payment_method', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Description :</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{receipt_data.get('description', 'N/A')}</td>
                    </tr>
                </table>
            </div>
            
            <div style="margin: 30px 0; text-align: right;">
                <p><strong>Validé par :</strong> {receipt_data.get('validated_by', 'N/A')}</p>
                <p style="margin-top: 50px;">_____________________</p>
                <p>Signature et cachet</p>
            </div>
        </div>
        """
        return html


# Fonctions globales
_default_export_manager = None


def get_export_manager() -> ExportManager:
    """Obtenir l'instance du gestionnaire d'export"""
    global _default_export_manager
    if _default_export_manager is None:
        _default_export_manager = ExportManager()
    return _default_export_manager


def export_to_csv(data: List[Dict[str, Any]], filename: str,
                  fieldnames: Optional[List[str]] = None) -> tuple[bool, str]:
    """Exporter vers CSV"""
    return get_export_manager().export_to_csv(data, filename, fieldnames)


def export_to_pdf(content: str, filename: str, title: Optional[str] = None) -> tuple[bool, str]:
    """Exporter vers PDF/HTML"""
    return get_export_manager().export_to_pdf(content, filename, title)


def import_from_csv(filepath: str, required_fields: Optional[List[str]] = None) -> tuple[bool, List[Dict[str, Any]], str]:
    """Importer depuis CSV"""
    return get_export_manager().import_from_csv(filepath, required_fields)
