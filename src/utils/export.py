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
    
    def __init__(self, export_dir: str = None):
        """
        Initialiser le gestionnaire d'export
        
        Args:
            export_dir: Répertoire des exports (None = utilise config)
        """
        self.config = get_config_manager()
        self.export_dir = export_dir or self.config.get_export_path()
        os.makedirs(self.export_dir, exist_ok=True)
    
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
        Générer le HTML d'un reçu de paiement professionnel
        
        Args:
            receipt_data: Données du reçu
        
        Returns:
            Contenu HTML du reçu
        """
        # Récupérer les informations du centre
        center_info = self.config.get_center_info()
        center_name = center_info.get('name', 'Auto-École')
        center_address = center_info.get('address', '')
        center_phone = center_info.get('phone', '')
        center_email = center_info.get('email', '')
        
        # Formater le montant
        amount = receipt_data.get('amount', 0)
        amount_formatted = f"{float(amount):,.2f}".replace(',', ' ')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .receipt-container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 32px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                }}
                .header p {{
                    margin: 5px 0 0 0;
                    font-size: 14px;
                    opacity: 0.9;
                }}
                .receipt-title {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    border-bottom: 3px solid #667eea;
                }}
                .receipt-title h2 {{
                    margin: 0;
                    color: #2c3e50;
                    font-size: 24px;
                    font-weight: 600;
                }}
                .receipt-meta {{
                    display: flex;
                    justify-content: space-between;
                    padding: 20px 30px;
                    background: #fff;
                    border-bottom: 1px solid #e0e0e0;
                }}
                .receipt-meta div {{
                    text-align: center;
                }}
                .receipt-meta .label {{
                    font-size: 12px;
                    color: #7f8c8d;
                    text-transform: uppercase;
                    margin-bottom: 5px;
                }}
                .receipt-meta .value {{
                    font-size: 16px;
                    color: #2c3e50;
                    font-weight: 600;
                }}
                .content {{
                    padding: 30px;
                }}
                .section {{
                    margin-bottom: 25px;
                }}
                .section-title {{
                    color: #667eea;
                    font-size: 14px;
                    font-weight: 600;
                    text-transform: uppercase;
                    margin-bottom: 15px;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 5px;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                }}
                .info-item {{
                    display: flex;
                    flex-direction: column;
                }}
                .info-label {{
                    font-size: 12px;
                    color: #7f8c8d;
                    margin-bottom: 5px;
                }}
                .info-value {{
                    font-size: 14px;
                    color: #2c3e50;
                    font-weight: 500;
                }}
                .amount-box {{
                    background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
                    color: white;
                    padding: 25px;
                    border-radius: 10px;
                    text-align: center;
                    margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
                }}
                .amount-label {{
                    font-size: 14px;
                    opacity: 0.9;
                    margin-bottom: 10px;
                }}
                .amount-value {{
                    font-size: 42px;
                    font-weight: 700;
                    margin: 0;
                }}
                .payment-details {{
                    background: #fff;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    overflow: hidden;
                }}
                .payment-row {{
                    display: flex;
                    padding: 15px 20px;
                    border-bottom: 1px solid #e0e0e0;
                }}
                .payment-row:last-child {{
                    border-bottom: none;
                }}
                .payment-row .label {{
                    flex: 1;
                    color: #7f8c8d;
                    font-size: 14px;
                }}
                .payment-row .value {{
                    flex: 1;
                    color: #2c3e50;
                    font-weight: 500;
                    text-align: right;
                }}
                .signature-section {{
                    margin-top: 40px;
                    padding-top: 30px;
                    border-top: 2px dashed #e0e0e0;
                    display: flex;
                    justify-content: space-between;
                }}
                .signature-box {{
                    text-align: center;
                    width: 45%;
                }}
                .signature-line {{
                    border-top: 2px solid #2c3e50;
                    margin-top: 60px;
                    padding-top: 10px;
                    font-size: 12px;
                    color: #7f8c8d;
                }}
                .footer {{
                    background: #2c3e50;
                    color: white;
                    text-align: center;
                    padding: 20px;
                    font-size: 12px;
                }}
                .footer p {{
                    margin: 5px 0;
                    opacity: 0.8;
                }}
            </style>
        </head>
        <body>
            <div class="receipt-container">
                <!-- En-tête -->
                <div class="header">
                    <h1>🚗 {center_name}</h1>
                    {f'<p>{center_address}</p>' if center_address else ''}
                    <p>
                        {f'📞 {center_phone}' if center_phone else ''}
                        {f' | 📧 {center_email}' if center_email else ''}
                    </p>
                </div>
                
                <!-- Titre du reçu -->
                <div class="receipt-title">
                    <h2>📄 REÇU DE PAIEMENT</h2>
                </div>
                
                <!-- Métadonnées -->
                <div class="receipt-meta">
                    <div>
                        <div class="label">N° Reçu</div>
                        <div class="value">{receipt_data.get('receipt_number', 'N/A')}</div>
                    </div>
                    <div>
                        <div class="label">Date</div>
                        <div class="value">{receipt_data.get('date', 'N/A')}</div>
                    </div>
                </div>
                
                <!-- Contenu -->
                <div class="content">
                    <!-- Informations Élève -->
                    <div class="section">
                        <div class="section-title">👤 Informations Élève</div>
                        <div class="info-grid">
                            <div class="info-item">
                                <div class="info-label">Nom Complet</div>
                                <div class="info-value">{receipt_data.get('student_name', 'N/A')}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">CIN</div>
                                <div class="info-value">{receipt_data.get('student_cin', 'N/A')}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Téléphone</div>
                                <div class="info-value">{receipt_data.get('student_phone', 'N/A')}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Montant -->
                    <div class="amount-box">
                        <div class="amount-label">MONTANT PAYÉ</div>
                        <p class="amount-value">{amount_formatted} DH</p>
                    </div>
                    
                    <!-- Détails du Paiement -->
                    <div class="section">
                        <div class="section-title">💳 Détails du Paiement</div>
                        <div class="payment-details">
                            <div class="payment-row">
                                <div class="label">Mode de paiement</div>
                                <div class="value">{receipt_data.get('payment_method', 'N/A').replace('_', ' ').title()}</div>
                            </div>
                            <div class="payment-row">
                                <div class="label">Description</div>
                                <div class="value">{receipt_data.get('description', 'Paiement formation')}</div>
                            </div>
                            <div class="payment-row">
                                <div class="label">Validé par</div>
                                <div class="value">{receipt_data.get('validated_by', 'Administration')}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Signatures -->
                    <div class="signature-section">
                        <div class="signature-box">
                            <p style="font-weight: 600; color: #2c3e50;">Signature de l'élève</p>
                            <div class="signature-line">
                                Lu et approuvé
                            </div>
                        </div>
                        <div class="signature-box">
                            <p style="font-weight: 600; color: #2c3e50;">Cachet de l'auto-école</p>
                            <div class="signature-line">
                                Signature et cachet
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Pied de page -->
                <div class="footer">
                    <p><strong>Merci pour votre confiance !</strong></p>
                    <p>Ce reçu est valable sans signature ni cachet</p>
                    <p style="margin-top: 10px; font-size: 10px;">Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
                </div>
            </div>
        </body>
        </html>
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
