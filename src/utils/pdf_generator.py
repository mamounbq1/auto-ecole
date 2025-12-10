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
from src.utils.config_manager import get_config_manager

logger = get_logger()


class PDFGenerator:
    """Générateur de PDF professionnel"""
    
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self.config = get_config_manager()
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
    
    def _create_center_header(self, story: list, doc_title: str = ""):
        """
        Crée un en-tête professionnel avec les informations du centre
        
        Args:
            story: Liste pour ajouter les éléments
            doc_title: Titre du document (ex: "REÇU DE PAIEMENT", "CONTRAT")
        """
        center = self.config.get_center_info()
        
        # Logo si disponible
        logo_path = self.config.get_logo_path()
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=3*cm, height=3*cm, kind='proportional')
                story.append(logo)
                story.append(Spacer(1, 0.3*cm))
            except:
                pass  # Si le logo ne charge pas, on continue
        
        # Nom du centre en grand
        center_name = Paragraph(
            f"<b>{center.get('name', 'Auto-École Manager').upper()}</b>",
            self.styles['CustomTitle']
        )
        story.append(center_name)
        
        # Adresse et contact
        contact_lines = []
        if center.get('address'):
            contact_lines.append(center['address'])
        
        city_parts = []
        if center.get('postal_code'):
            city_parts.append(center['postal_code'])
        if center.get('city'):
            city_parts.append(center['city'])
        if city_parts:
            contact_lines.append(' '.join(city_parts))
        
        contact_parts = []
        if center.get('phone'):
            contact_parts.append(f"Tél: {center['phone']}")
        if center.get('email'):
            contact_parts.append(f"Email: {center['email']}")
        if center.get('website'):
            contact_parts.append(f"Web: {center['website']}")
        
        if contact_parts:
            contact_lines.append(' | '.join(contact_parts))
        
        # Infos légales
        legal_parts = []
        if center.get('license_number'):
            legal_parts.append(f"Agrément N° {center['license_number']}")
        if center.get('siret'):
            legal_parts.append(f"SIRET/ICE: {center['siret']}")
        if center.get('tva_number'):
            legal_parts.append(f"TVA: {center['tva_number']}")
        
        if legal_parts:
            contact_lines.append(' | '.join(legal_parts))
        
        # Afficher toutes les lignes de contact
        if contact_lines:
            contact_style = ParagraphStyle(
                name='ContactInfo',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#555555'),
                alignment=TA_CENTER,
                leading=12
            )
            for line in contact_lines:
                story.append(Paragraph(line, contact_style))
        
        # Ligne de séparation
        from reportlab.platypus import HRFlowable
        story.append(Spacer(1, 0.3*cm))
        story.append(HRFlowable(
            width="100%",
            thickness=2,
            color=colors.HexColor('#3498db'),
            spaceAfter=10,
            spaceBefore=5
        ))
        
        # Titre du document si fourni
        if doc_title:
            doc_title_para = Paragraph(
                f"<b>{doc_title}</b>",
                self.styles['CustomSubtitle']
            )
            story.append(doc_title_para)
        
        story.append(Spacer(1, 0.5*cm))
    
    def _create_center_footer(self, canvas_obj, doc):
        """
        Crée un pied de page avec les informations du centre
        
        Args:
            canvas_obj: Canvas ReportLab
            doc: Document
        """
        center = self.config.get_center_info()
        canvas_obj.saveState()
        
        # Ligne de séparation
        canvas_obj.setStrokeColor(colors.HexColor('#cccccc'))
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(2*cm, 2*cm, A4[0]-2*cm, 2*cm)
        
        # Texte du pied de page
        footer_parts = []
        if center.get('name'):
            footer_parts.append(center['name'])
        if center.get('phone'):
            footer_parts.append(center['phone'])
        if center.get('email'):
            footer_parts.append(center['email'])
        
        footer_text = ' | '.join(footer_parts) if footer_parts else "Auto-École Manager"
        
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.HexColor('#666666'))
        canvas_obj.drawCentredString(A4[0]/2, 1.5*cm, footer_text)
        
        # Numéro de page
        page_num = f"Page {doc.page}"
        canvas_obj.drawRightString(A4[0]-2*cm, 1.5*cm, page_num)
        
        canvas_obj.restoreState()
        
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
            
            # En-tête professionnel avec infos du centre
            self._create_center_header(story, "REÇU DE PAIEMENT")
            
            story.append(Spacer(1, 0.5*cm))
            
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
            
            doc = SimpleDocTemplate(filepath, pagesize=A4,
                                   rightMargin=2*cm, leftMargin=2*cm,
                                   topMargin=2*cm, bottomMargin=2*cm)
            story = []
            
            # En-tête professionnel avec infos du centre
            self._create_center_header(story, "CONTRAT D'INSCRIPTION")
            
            story.append(Spacer(1, 0.5*cm))
            
            # Contenu du contrat (simplifié)
            contract_text = f"""
            <para alignment="justify">
            <b>Entre les soussignés :</b><br/><br/>
            
            <b>{self.config.get_center_name()}</b>, ci-après dénommée "l'établissement",<br/>
            Agrément N° {self.config.get_center_info().get('license_number', 'N/A')}<br/>
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
            
            doc = SimpleDocTemplate(filepath, pagesize=A4,
                                   rightMargin=2*cm, leftMargin=2*cm,
                                   topMargin=2*cm, bottomMargin=2*cm)
            story = []
            
            # En-tête professionnel avec infos du centre
            self._create_center_header(story, "CONVOCATION D'EXAMEN")
            
            story.append(Spacer(1, 0.5*cm))
            
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
    
    def generate_professional_receipt(self, receipt_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Générer un reçu de paiement PDF professionnel style GenSpark
        
        Args:
            receipt_data: Dictionnaire avec les données du reçu
                - receipt_number: Numéro du reçu
                - date: Date du paiement
                - student_name: Nom de l'élève
                - student_cin: CIN de l'élève
                - student_phone: Téléphone de l'élève
                - amount: Montant payé
                - payment_method: Méthode de paiement
                - description: Description
                - validated_by: Validé par
        
        Returns:
            Tuple (success, filepath_or_error)
        """
        try:
            # Nom du fichier
            receipt_num = receipt_data.get('receipt_number', 'UNKNOWN')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recu_{receipt_num}_{timestamp}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Créer le document PDF
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            story = []
            
            # === EN-TÊTE PROFESSIONNEL ===
            self._create_center_header(story, "")
            
            # Ligne de séparation
            story.append(Spacer(1, 0.5*cm))
            line_data = [['_' * 100]]
            line_table = Table(line_data, colWidths=[16*cm])
            line_table.setStyle(TableStyle([
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#667eea')),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            story.append(line_table)
            story.append(Spacer(1, 0.5*cm))
            
            # Titre du document
            title = Paragraph(
                "<b>REÇU DE PAIEMENT</b>",
                ParagraphStyle(
                    name='ReceiptTitle',
                    parent=self.styles['CustomTitle'],
                    fontSize=22,
                    textColor=colors.HexColor('#667eea'),
                    spaceAfter=20
                )
            )
            story.append(title)
            
            # === MÉTADONNÉES (N° Reçu et Date) ===
            meta_data = [
                ['N° REÇU', receipt_data.get('receipt_number', 'N/A')],
                ['DATE', receipt_data.get('date', 'N/A')]
            ]
            meta_table = Table(meta_data, colWidths=[8*cm, 8*cm])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#7f8c8d')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2c3e50')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 0.8*cm))
            
            # === SECTION ÉLÈVE ===
            section_title = Paragraph(
                "<b>👤 INFORMATIONS ÉLÈVE</b>",
                self.styles['SectionHeader']
            )
            story.append(section_title)
            
            student_data = [
                ['Nom Complet', receipt_data.get('student_name', 'N/A')],
                ['CIN', receipt_data.get('student_cin', 'N/A')],
                ['Téléphone', receipt_data.get('student_phone', 'N/A')]
            ]
            student_table = Table(student_data, colWidths=[5*cm, 11*cm])
            student_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#555555')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2c3e50')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#dee2e6')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ]))
            story.append(student_table)
            story.append(Spacer(1, 0.8*cm))
            
            # === MONTANT (BOÎTE VERTE EN ÉVIDENCE) ===
            amount = float(receipt_data.get('amount', 0))
            amount_formatted = f"{amount:,.2f}".replace(',', ' ')
            
            amount_data = [[
                Paragraph(
                    f"<para align=center><font size=14 color='white'><b>MONTANT PAYÉ</b></font><br/>"
                    f"<font size=32 color='white'><b>{amount_formatted} DH</b></font></para>",
                    self.styles['Normal']
                )
            ]]
            amount_table = Table(amount_data, colWidths=[16*cm])
            amount_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#27ae60')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 20),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
                ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#229954')),
            ]))
            story.append(amount_table)
            story.append(Spacer(1, 0.8*cm))
            
            # === DÉTAILS DU PAIEMENT ===
            details_title = Paragraph(
                "<b>💳 DÉTAILS DU PAIEMENT</b>",
                self.styles['SectionHeader']
            )
            story.append(details_title)
            
            payment_method = receipt_data.get('payment_method', 'N/A').replace('_', ' ').title()
            description = receipt_data.get('description', 'Paiement formation')
            validated_by = receipt_data.get('validated_by', 'Administration')
            
            details_data = [
                ['Mode de paiement', payment_method],
                ['Description', description],
                ['Validé par', validated_by]
            ]
            details_table = Table(details_data, colWidths=[5*cm, 11*cm])
            details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#555555')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2c3e50')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#dee2e6')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ]))
            story.append(details_table)
            story.append(Spacer(1, 1.5*cm))
            
            # === SIGNATURES ===
            signature_data = [
                ['Signature de l\'élève', 'Cachet de l\'auto-école'],
                ['', ''],
                ['', ''],
                ['Lu et approuvé', 'Signature et cachet']
            ]
            signature_table = Table(signature_data, colWidths=[8*cm, 8*cm], rowHeights=[0.5*cm, 2*cm, 0.3*cm, 0.5*cm])
            signature_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 3), (-1, 3), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 3), (-1, 3), 9),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#7f8c8d')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                ('VALIGN', (0, 3), (-1, 3), 'TOP'),
                ('LINEABOVE', (0, 3), (-1, 3), 1, colors.HexColor('#2c3e50')),
            ]))
            story.append(signature_table)
            story.append(Spacer(1, 1*cm))
            
            # === PIED DE PAGE ===
            footer_text = Paragraph(
                f"<para align=center>"
                f"<font size=9 color='#7f8c8d'><b>Merci pour votre confiance !</b><br/>"
                f"Ce reçu est valable sans signature ni cachet<br/>"
                f"<font size=8>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</font></font>"
                f"</para>",
                self.styles['Normal']
            )
            story.append(footer_text)
            
            # Générer le PDF
            doc.build(story)
            
            logger.info(f"Reçu PDF professionnel généré : {filepath}")
            return True, filepath
            
        except Exception as e:
            error_msg = f"Erreur lors de la génération du reçu PDF : {str(e)}"
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
