"""
Générateur de PDF professionnel avec ReportLab
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, Frame, PageTemplate
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas

from src.utils import get_logger

logger = get_logger()


class PDFGenerator:
    """Générateur de PDF professionnel"""
    
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Configurer des styles personnalisés"""
        # Titre principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=26,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=20,
            spaceBefore=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Sous-titre
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#555555'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#3498db'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Body text enhanced
        self.styles.add(ParagraphStyle(
            name='BodyEnhanced',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            leading=16,
            alignment=TA_LEFT
        ))
        
    def generate_receipt(self, payment_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Générer un reçu de paiement professionnel
        
        Args:
            payment_data: Données du paiement
        
        Returns:
            Tuple (success, filepath_or_error)
        """
        try:
            # Nom du fichier
            receipt_number = payment_data.get('receipt_number', 'DRAFT')
            filename = f"recu_{receipt_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Créer le document
            doc = SimpleDocTemplate(filepath, pagesize=A4,
                                   rightMargin=2*cm, leftMargin=2*cm,
                                   topMargin=2*cm, bottomMargin=2*cm)
            
            # Contenu
            story = []
            
            # En-tête avec bordure décorative
            story.append(Spacer(1, 0.5*cm))
            
            # Titre principal avec style professionnel
            title = Paragraph(
                "<font color='#3498db'>🚗</font> AUTO-ÉCOLE",
                self.styles['CustomTitle']
            )
            story.append(title)
            
            # Ligne de séparation
            from reportlab.platypus import HRFlowable
            story.append(HRFlowable(
                width="80%",
                thickness=2,
                color=colors.HexColor('#3498db'),
                spaceAfter=10,
                spaceBefore=5
            ))
            
            subtitle = Paragraph(
                "<b>REÇU DE PAIEMENT</b>",
                self.styles['CustomSubtitle']
            )
            story.append(subtitle)
            
            story.append(Spacer(1, 1*cm))
            
            # Informations du reçu
            info_data = [
                ['N° Reçu:', payment_data.get('receipt_number', 'N/A')],
                ['Date:', payment_data.get('date', datetime.now().strftime('%d/%m/%Y'))],
            ]
            
            info_table = Table(info_data, colWidths=[4*cm, 10*cm])
            info_table.setStyle(TableStyle([
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
                ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(info_table)
            
            story.append(Spacer(1, 0.8*cm))
            
            # Section élève
            section_title = Paragraph("Informations Élève", self.styles['SectionHeader'])
            story.append(section_title)
            
            student_data = [
                ['Nom:', payment_data.get('student_name', 'N/A')],
                ['CIN:', payment_data.get('student_cin', 'N/A')],
                ['Téléphone:', payment_data.get('student_phone', 'N/A')],
            ]
            
            student_table = Table(student_data, colWidths=[4*cm, 10*cm])
            student_table.setStyle(TableStyle([
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
                ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(student_table)
            
            story.append(Spacer(1, 0.8*cm))
            
            # Détails du paiement
            section_title = Paragraph(
                "📋 Détails du Paiement",
                self.styles['SectionHeader']
            )
            story.append(section_title)
            
            amount = payment_data.get('amount', 0)
            payment_details = [
                ['Description', 'Montant'],
                [payment_data.get('description', 'Paiement'), f"{amount:,.2f} DH"],
                ['Mode de paiement', payment_data.get('payment_method', 'N/A')],
            ]
            
            # Ligne totale
            payment_details.append(['MONTANT TOTAL', f"{amount:,.2f} DH"])
            
            payment_table = Table(payment_details, colWidths=[11*cm, 4*cm])
            payment_table.setStyle(TableStyle([
                # En-tête
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                
                # Corps
                ('FONT', (0, 1), (-1, -2), 'Helvetica', 11),
                ('ALIGN', (0, 1), (0, -2), 'LEFT'),
                ('ALIGN', (1, 1), (1, -2), 'RIGHT'),
                ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -2), 1, colors.HexColor('#dee2e6')),
                
                # Ligne total
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#27ae60')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 14),
                ('ALIGN', (0, -1), (0, -1), 'LEFT'),
                ('ALIGN', (1, -1), (1, -1), 'RIGHT'),
                
                # Padding
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ]))
            story.append(payment_table)
            
            story.append(Spacer(1, 2*cm))
            
            # Signature
            sig_data = [
                ['Validé par:', payment_data.get('validated_by', 'N/A')],
                ['', ''],
                ['Signature et cachet:', '_________________________'],
            ]
            
            sig_table = Table(sig_data, colWidths=[5*cm, 9*cm])
            sig_table.setStyle(TableStyle([
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
                ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(sig_table)
            
            # Footer
            story.append(Spacer(1, 1*cm))
            footer_text = f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
            footer = Paragraph(footer_text, ParagraphStyle(
                name='Footer',
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            ))
            story.append(footer)
            
            # Générer le PDF
            doc.build(story)
            
            logger.info(f"Reçu PDF généré : {filepath}")
            return True, filepath
            
        except Exception as e:
            error_msg = f"Erreur lors de la génération du reçu : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def generate_contract(self, student_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Générer un contrat d'inscription
        
        Args:
            student_data: Données de l'élève
        
        Returns:
            Tuple (success, filepath_or_error)
        """
        try:
            filename = f"contrat_{student_data.get('cin', 'DRAFT')}_{datetime.now().strftime('%Y%m%d')}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            
            # Titre
            story.append(Spacer(1, 1*cm))
            title = Paragraph("CONTRAT D'INSCRIPTION", self.styles['CustomTitle'])
            story.append(title)
            
            story.append(Spacer(1, 1*cm))
            
            # Contenu du contrat (simplifié)
            contract_text = f"""
            <para alignment="justify">
            <b>Entre les soussignés :</b><br/><br/>
            
            L'Auto-École, ci-après dénommée "l'établissement",<br/>
            d'une part,<br/><br/>
            
            Et :<br/><br/>
            
            <b>Nom :</b> {student_data.get('full_name', 'N/A')}<br/>
            <b>CIN :</b> {student_data.get('cin', 'N/A')}<br/>
            <b>Date de naissance :</b> {student_data.get('date_of_birth', 'N/A')}<br/>
            <b>Téléphone :</b> {student_data.get('phone', 'N/A')}<br/>
            <b>Adresse :</b> {student_data.get('address', 'N/A')}<br/><br/>
            
            ci-après dénommé "l'élève", d'autre part,<br/><br/>
            
            <b>IL A ÉTÉ CONVENU CE QUI SUIT :</b><br/><br/>
            
            <b>Article 1 : Objet du contrat</b><br/>
            Le présent contrat a pour objet la formation à la conduite automobile 
            en vue de l'obtention du permis de conduire catégorie <b>{student_data.get('license_type', 'B')}</b>.<br/><br/>
            
            <b>Article 2 : Durée de la formation</b><br/>
            La formation comprend {student_data.get('hours_planned', 20)} heures de conduite pratique 
            et la préparation aux examens théorique et pratique.<br/><br/>
            
            <b>Article 3 : Tarif</b><br/>
            Le montant total de la formation s'élève à <b>{student_data.get('total_due', 0):,.0f} DH</b>.<br/><br/>
            
            Fait à __________, le {datetime.now().strftime('%d/%m/%Y')}<br/><br/>
            
            Signatures :<br/>
            L'établissement : _______________      L'élève : _______________
            </para>
            """
            
            contract_para = Paragraph(contract_text, self.styles['BodyText'])
            story.append(contract_para)
            
            doc.build(story)
            
            logger.info(f"Contrat PDF généré : {filepath}")
            return True, filepath
            
        except Exception as e:
            error_msg = f"Erreur lors de la génération du contrat : {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def generate_summons(self, exam_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Générer une convocation d'examen
        
        Args:
            exam_data: Données de l'examen
        
        Returns:
            Tuple (success, filepath_or_error)
        """
        try:
            filename = f"convocation_{exam_data.get('summons_number', 'DRAFT')}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            
            story.append(Spacer(1, 1*cm))
            title = Paragraph("CONVOCATION D'EXAMEN", self.styles['CustomTitle'])
            story.append(title)
            
            story.append(Spacer(1, 1.5*cm))
            
            # Informations
            info_text = f"""
            <para alignment="center" fontSize="14">
            <b>N° Convocation :</b> {exam_data.get('summons_number', 'N/A')}<br/><br/>
            
            <b>{exam_data.get('student_name', 'N/A')}</b><br/>
            CIN : {exam_data.get('student_cin', 'N/A')}<br/><br/>
            
            Vous êtes convoqué(e) à l'examen <b>{exam_data.get('exam_type', 'N/A')}</b><br/><br/>
            
            📅 Date : <b>{exam_data.get('exam_date', 'N/A')}</b><br/>
            🕐 Heure : <b>{exam_data.get('exam_time', 'N/A')}</b><br/>
            📍 Lieu : <b>{exam_data.get('location', 'N/A')}</b><br/><br/>
            
            Merci de vous présenter 30 minutes avant l'heure indiquée avec :<br/>
            • Votre carte d'identité nationale<br/>
            • Cette convocation<br/>
            • Votre dossier de candidature<br/><br/>
            
            Bonne chance !
            </para>
            """
            
            info_para = Paragraph(info_text, self.styles['BodyText'])
            story.append(info_para)
            
            doc.build(story)
            
            logger.info(f"Convocation PDF générée : {filepath}")
            return True, filepath
            
        except Exception as e:
            error_msg = f"Erreur lors de la génération de la convocation : {str(e)}"
            logger.error(error_msg)
            return False, error_msg


# Fonction globale
_pdf_generator = None

def get_pdf_generator() -> PDFGenerator:
    """Obtenir l'instance du générateur PDF"""
    global _pdf_generator
    if _pdf_generator is None:
        _pdf_generator = PDFGenerator()
    return _pdf_generator
