"""
Générateur de documents automatiques (contrats, attestations)
Phase 3 - Génération Automatique de Documents
"""

from datetime import datetime, date
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
import os

from src.utils import get_logger
from src.utils.config_manager import ConfigManager

logger = get_logger()


class DocumentGenerator:
    """Générateur de documents PDF personnalisés"""
    
    def __init__(self):
        """Initialiser le générateur"""
        self.config = ConfigManager()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurer les styles personnalisés"""
        # Titre principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Sous-titre
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#3498db'),
            spaceAfter=20,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Corps de texte justifié
        self.styles.add(ParagraphStyle(
            name='Justified',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
    
    def _add_header(self, elements: list):
        """Ajouter l'en-tête avec logo et infos du centre"""
        # Logo (si disponible)
        logo_path = self.config.get_logo_path()
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=3*cm, height=3*cm)
                elements.append(logo)
                elements.append(Spacer(1, 0.3*cm))
            except Exception as e:
                logger.warning(f"Erreur lors du chargement du logo : {e}")
        
        # Infos du centre
        center_name = self.config.get_center_name()
        center_address = self.config.get_center_address()
        center_contact = self.config.get_center_contact()
        
        if center_name:
            elements.append(Paragraph(center_name, self.styles['CustomTitle']))
        
        if center_address or center_contact:
            info_text = []
            if center_address:
                info_text.append(center_address)
            if center_contact:
                info_text.append(center_contact)
            
            info = Paragraph('<br/>'.join(info_text), ParagraphStyle(
                name='CenterInfo',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=20
            ))
            elements.append(info)
        
        elements.append(Spacer(1, 1*cm))
    
    def _add_footer(self, canvas, doc):
        """Ajouter le pied de page"""
        canvas.saveState()
        
        # Infos légales du centre
        legal_info = self.config.get_center_legal_info()
        if legal_info:
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(colors.grey)
            
            # Centrer le texte
            text_width = canvas.stringWidth(legal_info, 'Helvetica', 8)
            x = (A4[0] - text_width) / 2
            canvas.drawString(x, 2*cm, legal_info)
        
        # Numéro de page
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(A4[0] - 2*cm, 2*cm, text)
        
        canvas.restoreState()
    
    def generate_registration_contract(
        self,
        output_path: str,
        student_data: Dict[str, Any],
        contract_data: Dict[str, Any]
    ) -> bool:
        """
        Générer un contrat d'inscription
        
        Args:
            output_path: Chemin du fichier PDF à créer
            student_data: Données de l'élève
            contract_data: Données du contrat (prix, durée, etc.)
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4,
                                   topMargin=2*cm, bottomMargin=3*cm,
                                   leftMargin=2*cm, rightMargin=2*cm)
            
            elements = []
            
            # En-tête
            self._add_header(elements)
            
            # Titre
            elements.append(Paragraph("CONTRAT D'INSCRIPTION", self.styles['CustomTitle']))
            elements.append(Spacer(1, 0.5*cm))
            
            # Numéro de contrat et date
            contract_number = contract_data.get('contract_number', 'N/A')
            contract_date = contract_data.get('date', date.today()).strftime('%d/%m/%Y')
            
            info_table = Table([
                ['N° Contrat:', contract_number, 'Date:', contract_date]
            ], colWidths=[3*cm, 5*cm, 2*cm, 3*cm])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (2, 0), (2, 0), colors.HexColor('#3498db')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 0.8*cm))
            
            # Partie 1: Informations de l'élève
            elements.append(Paragraph("1. INFORMATIONS DE L'ÉLÈVE", self.styles['CustomSubtitle']))
            
            student_info = [
                ['Nom complet:', student_data.get('full_name', 'N/A')],
                ['CIN:', student_data.get('cin', 'N/A')],
                ['Date de naissance:', student_data.get('date_of_birth', 'N/A')],
                ['Adresse:', student_data.get('address', 'N/A')],
                ['Téléphone:', student_data.get('phone', 'N/A')],
                ['Email:', student_data.get('email', 'N/A')],
            ]
            
            student_table = Table(student_info, colWidths=[5*cm, 12*cm])
            student_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(student_table)
            elements.append(Spacer(1, 0.8*cm))
            
            # Partie 2: Détails de la formation
            elements.append(Paragraph("2. DÉTAILS DE LA FORMATION", self.styles['CustomSubtitle']))
            
            license_type = contract_data.get('license_type', 'B')
            hours_planned = contract_data.get('hours_planned', 20)
            total_price = contract_data.get('total_price', 0)
            
            formation_text = f"""
            La formation comprend l'apprentissage du permis de conduire de catégorie <b>{license_type}</b>.
            <br/><br/>
            <b>Nombre d'heures de conduite prévues :</b> {hours_planned} heures
            <br/>
            <b>Montant total de la formation :</b> {total_price:,.2f} DH
            """
            
            elements.append(Paragraph(formation_text, self.styles['Justified']))
            elements.append(Spacer(1, 0.8*cm))
            
            # Partie 3: Conditions de paiement
            elements.append(Paragraph("3. CONDITIONS DE PAIEMENT", self.styles['CustomSubtitle']))
            
            payment_text = f"""
            Le montant total de la formation s'élève à <b>{total_price:,.2f} DH</b>.
            <br/><br/>
            Les modalités de paiement sont les suivantes :
            <br/>
            • Acompte à l'inscription : {contract_data.get('deposit', 0):,.2f} DH
            <br/>
            • Solde restant : {total_price - contract_data.get('deposit', 0):,.2f} DH
            <br/><br/>
            Les paiements peuvent être effectués en espèces, par chèque, carte bancaire ou virement.
            """
            
            elements.append(Paragraph(payment_text, self.styles['Justified']))
            elements.append(Spacer(1, 0.8*cm))
            
            # Partie 4: Obligations des parties
            elements.append(Paragraph("4. OBLIGATIONS DES PARTIES", self.styles['CustomSubtitle']))
            
            obligations_text = """
            <b>L'auto-école s'engage à :</b>
            <br/>
            • Dispenser une formation théorique et pratique de qualité
            <br/>
            • Mettre à disposition des moniteurs qualifiés et des véhicules en bon état
            <br/>
            • Accompagner l'élève jusqu'à l'obtention du permis de conduire
            <br/><br/>
            <b>L'élève s'engage à :</b>
            <br/>
            • Assister régulièrement aux cours théoriques et pratiques
            <br/>
            • Respecter les horaires convenus
            <br/>
            • S'acquitter des paiements selon les modalités prévues
            <br/>
            • Respecter le règlement intérieur de l'auto-école
            """
            
            elements.append(Paragraph(obligations_text, self.styles['Justified']))
            elements.append(Spacer(1, 1*cm))
            
            # Signatures
            elements.append(Paragraph("5. SIGNATURES", self.styles['CustomSubtitle']))
            elements.append(Spacer(1, 0.5*cm))
            
            signature_data = [
                ['Fait à ___________________', 'Le ___________________'],
                ['', ''],
                ['Signature de l\'élève', 'Signature de l\'auto-école'],
            ]
            
            signature_table = Table(signature_data, colWidths=[8.5*cm, 8.5*cm])
            signature_table.setStyle(TableStyle([
                ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 2), (-1, 2), 30),
            ]))
            elements.append(signature_table)
            
            # Générer le PDF
            doc.build(elements, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
            
            logger.info(f"Contrat d'inscription généré : {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du contrat : {e}")
            return False
    
    def generate_training_certificate(
        self,
        output_path: str,
        student_data: Dict[str, Any],
        training_data: Dict[str, Any]
    ) -> bool:
        """
        Générer une attestation de formation
        
        Args:
            output_path: Chemin du fichier PDF à créer
            student_data: Données de l'élève
            training_data: Données de la formation (heures, dates, etc.)
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4,
                                   topMargin=2*cm, bottomMargin=3*cm,
                                   leftMargin=2*cm, rightMargin=2*cm)
            
            elements = []
            
            # En-tête
            self._add_header(elements)
            
            # Titre
            elements.append(Paragraph("ATTESTATION DE FORMATION", self.styles['CustomTitle']))
            elements.append(Spacer(1, 1*cm))
            
            # Numéro d'attestation
            certificate_number = training_data.get('certificate_number', 'ATT-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
            elements.append(Paragraph(f"N° {certificate_number}", ParagraphStyle(
                name='CertNumber',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.grey,
                alignment=TA_RIGHT
            )))
            elements.append(Spacer(1, 1*cm))
            
            # Corps de l'attestation
            center_name = self.config.get_center_name() or "L'Auto-École"
            student_name = student_data.get('full_name', 'N/A')
            cin = student_data.get('cin', 'N/A')
            license_type = training_data.get('license_type', 'B')
            hours_completed = training_data.get('hours_completed', 0)
            start_date = training_data.get('start_date', date.today()).strftime('%d/%m/%Y')
            end_date = training_data.get('end_date', date.today()).strftime('%d/%m/%Y')
            
            attestation_text = f"""
            <para alignment="justify" spaceBefore="20" spaceAfter="20">
            {center_name} atteste que :
            </para>
            
            <para alignment="center" spaceBefore="30" spaceAfter="30">
            <b><font size="14">{student_name}</font></b>
            <br/>
            CIN : {cin}
            </para>
            
            <para alignment="justify" spaceBefore="20" spaceAfter="20">
            a suivi et complété avec succès la formation au permis de conduire de catégorie <b>{license_type}</b>
            auprès de notre établissement.
            </para>
            
            <para alignment="justify" spaceBefore="20" spaceAfter="20">
            Cette formation s'est déroulée du <b>{start_date}</b> au <b>{end_date}</b> et a comporté
            <b>{hours_completed} heures</b> de conduite pratique ainsi que la préparation théorique complète
            au code de la route.
            </para>
            
            <para alignment="justify" spaceBefore="20" spaceAfter="20">
            Cette attestation est délivrée pour servir et valoir ce que de droit.
            </para>
            """
            
            elements.append(Paragraph(attestation_text, self.styles['Justified']))
            elements.append(Spacer(1, 2*cm))
            
            # Date et signature
            today = date.today().strftime('%d/%m/%Y')
            elements.append(Paragraph(f"Fait à _________________, le {today}", ParagraphStyle(
                name='DateLocation',
                parent=self.styles['Normal'],
                fontSize=11,
                alignment=TA_RIGHT
            )))
            elements.append(Spacer(1, 2*cm))
            
            elements.append(Paragraph("Le Directeur de l'Auto-École", ParagraphStyle(
                name='SignatureTitle',
                parent=self.styles['Normal'],
                fontSize=11,
                fontName='Helvetica-Bold',
                alignment=TA_RIGHT
            )))
            
            # Générer le PDF
            doc.build(elements, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
            
            logger.info(f"Attestation de formation générée : {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'attestation : {e}")
            return False
