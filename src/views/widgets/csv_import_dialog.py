"""
CSV Import Dialog with validation and progress reporting
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QDialog, QProgressBar, QTextEdit, QFileDialog, QMessageBox,
    QHeaderView, QGroupBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor
import csv
from datetime import datetime
from pathlib import Path

from src.controllers.student_controller import StudentController
from src.models import StudentStatus


class CSVImportWorker(QThread):
    """Worker thread for importing CSV data"""
    progress = Signal(int, int, str)  # current, total, message
    finished = Signal(dict)  # results dictionary
    error = Signal(str)  # error message
    
    def __init__(self, file_path, preview_mode=False):
        super().__init__()
        self.file_path = file_path
        self.preview_mode = preview_mode
        self.should_stop = False
    
    def stop(self):
        """Stop the import process"""
        self.should_stop = True
    
    def run(self):
        """Import CSV file with validation"""
        results = {
            'total': 0,
            'success': 0,
            'errors': 0,
            'skipped': 0,
            'error_details': []
        }
        
        try:
            with open(self.file_path, 'r', encoding='utf-8-sig') as file:
                # Skip comment lines (starting with #)
                lines = [line for line in file if not line.strip().startswith('#')]
                # Read CSV
                csv_reader = csv.DictReader(lines)
                rows = list(csv_reader)
                results['total'] = len(rows)
                
                for idx, row in enumerate(rows):
                    if self.should_stop:
                        break
                    
                    # Emit progress
                    self.progress.emit(idx + 1, results['total'], 
                                      f"Traitement ligne {idx + 1}/{results['total']}")
                    
                    # Validate and process row
                    try:
                        validation_result = self.validate_row(row, idx + 1)
                        
                        if not validation_result['valid']:
                            results['errors'] += 1
                            results['error_details'].append({
                                'row': idx + 1,
                                'data': row,
                                'errors': validation_result['errors']
                            })
                            continue
                        
                        # If preview mode, just validate
                        if self.preview_mode:
                            results['success'] += 1
                            continue
                        
                        # Create student
                        student_data = self.prepare_student_data(row)
                        StudentController.create_student(student_data)
                        results['success'] += 1
                        
                    except Exception as e:
                        results['errors'] += 1
                        results['error_details'].append({
                            'row': idx + 1,
                            'data': row,
                            'errors': [f"Erreur d'importation: {str(e)}"]
                        })
            
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(f"Erreur lors de la lecture du fichier: {str(e)}")
    
    def validate_row(self, row, row_num):
        """Validate a CSV row"""
        errors = []
        
        # Required fields
        required_fields = ['full_name', 'cin', 'phone']
        for field in required_fields:
            if not row.get(field, '').strip():
                errors.append(f"Champ requis manquant: {field}")
        
        # Validate CIN format (8 characters)
        cin = row.get('cin', '').strip()
        if cin and len(cin) != 8:
            errors.append(f"CIN invalide (doit être 8 caractères): {cin}")
        
        # Validate phone format (accept both 0XXXXXXXXX and +212 XXX-XXXXXX)
        phone = row.get('phone', '').strip()
        if phone:
            phone_clean = phone.replace(' ', '').replace('-', '').replace('+', '')
            # Accept Moroccan format: +212XXXXXXXXX or 0XXXXXXXXX
            if phone_clean.startswith('212'):
                phone_clean = '0' + phone_clean[3:]  # Convert +212 to 0
            if not (phone_clean.isdigit() and len(phone_clean) == 10 and phone_clean.startswith('0')):
                errors.append(f"Téléphone invalide (format: 0XXXXXXXXX ou +212 XXX-XXXXXX): {phone}")
        
        # Validate email format
        email = row.get('email', '').strip()
        if email and '@' not in email:
            errors.append(f"Email invalide: {email}")
        
        # Validate license type
        license_type = row.get('license_type', '').strip()
        if license_type and license_type not in ['A', 'B', 'C', 'D', 'E']:
            errors.append(f"Type de permis invalide (A, B, C, D, E): {license_type}")
        
        # Validate status (accept both English and French status values)
        status = row.get('status', '').strip().lower()
        # Map French status to English StudentStatus enum values
        status_mapping = {
            'actif': 'ACTIVE',
            'active': 'ACTIVE',
            'en_attente': 'PENDING',
            'pending': 'PENDING',
            'suspendu': 'SUSPENDED',
            'suspended': 'SUSPENDED',
            'diplome': 'GRADUATED',
            'graduated': 'GRADUATED',
            'abandonne': 'ABANDONED',
            'abandoned': 'ABANDONED'
        }
        if status and status not in status_mapping:
            errors.append(f"Statut invalide: {status}")
        
        # Validate numeric fields
        numeric_fields = {
            'hours_planned': (1, 100),
            'hours_completed': (0, 100),
            'theoretical_exam_attempts': (0, 10),
            'practical_exam_attempts': (0, 10),
            'total_due': (0, 999999),
            'total_paid': (0, 999999)
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            value = row.get(field, '').strip()
            if value:
                try:
                    num_value = float(value)
                    if num_value < min_val or num_value > max_val:
                        errors.append(f"{field} hors limites ({min_val}-{max_val}): {value}")
                except ValueError:
                    errors.append(f"{field} n'est pas un nombre valide: {value}")
        
        # Validate date
        dob = row.get('date_of_birth', '').strip()
        if dob:
            try:
                date_obj = datetime.strptime(dob, '%Y-%m-%d')
                # Check age (must be at least 16)
                age = (datetime.now() - date_obj).days / 365.25
                if age < 16 or age > 100:
                    errors.append(f"Âge invalide (16-100 ans): {dob}")
            except ValueError:
                errors.append(f"Date de naissance invalide (format: YYYY-MM-DD): {dob}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def prepare_student_data(self, row):
        """Prepare student data dictionary from CSV row"""
        data = {
            'full_name': row.get('full_name', '').strip(),
            'cin': row.get('cin', '').strip(),
            'phone': row.get('phone', '').strip(),
            'email': row.get('email', '').strip() or None,
            'address': row.get('address', '').strip() or None,
            'license_type': row.get('license_type', 'B').strip() or 'B',
        }
        
        # Parse date of birth
        dob = row.get('date_of_birth', '').strip()
        if dob:
            try:
                data['date_of_birth'] = datetime.strptime(dob, '%Y-%m-%d').date()
            except ValueError:
                data['date_of_birth'] = None
        
        # Parse status (accept both English and French)
        status_map = {
            'actif': StudentStatus.ACTIVE,
            'active': StudentStatus.ACTIVE,
            'en_attente': StudentStatus.PENDING,
            'pending': StudentStatus.PENDING,
            'suspendu': StudentStatus.SUSPENDED,
            'suspended': StudentStatus.SUSPENDED,
            'diplome': StudentStatus.GRADUATED,
            'graduated': StudentStatus.GRADUATED,
            'abandonne': StudentStatus.ABANDONED,
            'abandoned': StudentStatus.ABANDONED
        }
        status_str = row.get('status', 'actif').strip().lower()
        data['status'] = status_map.get(status_str, StudentStatus.ACTIVE)
        
        # Parse numeric fields with defaults
        data['hours_planned'] = int(row.get('hours_planned', '20') or '20')
        data['hours_completed'] = int(row.get('hours_completed', '0') or '0')
        data['theoretical_exam_attempts'] = int(row.get('theoretical_exam_attempts', '0') or '0')
        data['practical_exam_attempts'] = int(row.get('practical_exam_attempts', '0') or '0')
        data['total_due'] = float(row.get('total_due', '0') or '0')
        
        # Notes
        data['notes'] = row.get('notes', '').strip() or None
        
        return data


class CSVImportDialog(QDialog):
    """
    CSV Import Dialog with:
    - File selection
    - Preview mode with validation
    - Progress bar during import
    - Detailed import report
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = None
        self.worker = None
        
        self.setWindowTitle("Importer des Élèves depuis CSV")
        self.setMinimumSize(800, 600)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("📥 Importation CSV des Élèves")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "Sélectionnez un fichier CSV contenant les informations des élèves.\n"
            "Le fichier doit contenir les colonnes suivantes:\n"
            "• full_name (requis), cin (requis), phone (requis)\n"
            "• date_of_birth, email, address, license_type\n"
            "• status, hours_planned, hours_completed\n"
            "• theoretical_exam_attempts, practical_exam_attempts\n"
            "• total_due, total_paid, notes"
        )
        instructions.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 15px;
                border-radius: 8px;
                color: #34495e;
                font-size: 13px;
            }
        """)
        layout.addWidget(instructions)
        
        # File selection
        file_group = QGroupBox("1️⃣ Sélection du Fichier")
        file_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        file_layout = QHBoxLayout()
        
        self.file_label = QLabel("Aucun fichier sélectionné")
        self.file_label.setStyleSheet("color: #7f8c8d; font-weight: normal;")
        
        select_file_btn = QPushButton("📁 Parcourir...")
        select_file_btn.clicked.connect(self.select_file)
        select_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        file_layout.addWidget(self.file_label, stretch=1)
        file_layout.addWidget(select_file_btn)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Preview/Validation section
        preview_group = QGroupBox("2️⃣ Aperçu et Validation")
        preview_group.setStyleSheet(file_group.styleSheet())
        preview_layout = QVBoxLayout()
        
        preview_btn_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("👁️ Prévisualiser")
        self.preview_btn.setEnabled(False)
        self.preview_btn.clicked.connect(self.preview_file)
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        
        preview_btn_layout.addStretch()
        preview_btn_layout.addWidget(self.preview_btn)
        preview_layout.addLayout(preview_btn_layout)
        
        # Validation results
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        self.validation_text.setMaximumHeight(150)
        self.validation_text.setPlaceholderText("Les résultats de validation apparaîtront ici...")
        self.validation_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-family: Consolas, monospace;
                font-size: 12px;
            }
        """)
        preview_layout.addWidget(self.validation_text)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Import section
        import_group = QGroupBox("3️⃣ Importation")
        import_group.setStyleSheet(file_group.styleSheet())
        import_layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 3px;
            }
        """)
        import_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        import_layout.addWidget(self.progress_label)
        
        import_group.setLayout(import_layout)
        layout.addWidget(import_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("❌ Annuler")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 30px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        self.import_btn = QPushButton("⬇️ Importer")
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self.start_import)
        self.import_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 30px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.import_btn)
        
        layout.addLayout(btn_layout)
    
    def select_file(self):
        """Select CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un fichier CSV",
            "",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            self.file_path = file_path
            self.file_label.setText(Path(file_path).name)
            self.file_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.preview_btn.setEnabled(True)
            self.validation_text.clear()
            self.progress_bar.setValue(0)
            self.progress_label.setText("")
    
    def preview_file(self):
        """Preview and validate CSV file"""
        if not self.file_path:
            return
        
        self.preview_btn.setEnabled(False)
        self.import_btn.setEnabled(False)
        self.validation_text.clear()
        self.validation_text.append("🔍 Validation en cours...")
        
        # Start worker thread for preview
        self.worker = CSVImportWorker(self.file_path, preview_mode=True)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.preview_finished)
        self.worker.error.connect(self.handle_error)
        self.worker.start()
    
    def start_import(self):
        """Start the import process"""
        if not self.file_path:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir importer ces élèves?\n"
            "Cette action créera de nouveaux enregistrements dans la base de données.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.preview_btn.setEnabled(False)
        self.import_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        
        # Start worker thread for import
        self.worker = CSVImportWorker(self.file_path, preview_mode=False)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.import_finished)
        self.worker.error.connect(self.handle_error)
        self.worker.start()
    
    def update_progress(self, current, total, message):
        """Update progress bar"""
        progress_percent = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(progress_percent)
        self.progress_label.setText(message)
    
    def preview_finished(self, results):
        """Handle preview completion"""
        self.preview_btn.setEnabled(True)
        
        # Display validation results
        self.validation_text.clear()
        
        if results['errors'] == 0:
            self.validation_text.append("✅ VALIDATION RÉUSSIE!\n")
            self.validation_text.append(f"📊 Résumé:")
            self.validation_text.append(f"  • Total lignes: {results['total']}")
            self.validation_text.append(f"  • Valides: {results['success']}")
            self.validation_text.append(f"  • Erreurs: {results['errors']}")
            self.validation_text.append(f"\n✅ Tous les enregistrements sont valides. Prêt à importer!")
            self.import_btn.setEnabled(True)
        else:
            self.validation_text.append("⚠️ ERREURS DE VALIDATION DÉTECTÉES\n")
            self.validation_text.append(f"📊 Résumé:")
            self.validation_text.append(f"  • Total lignes: {results['total']}")
            self.validation_text.append(f"  • Valides: {results['success']}")
            self.validation_text.append(f"  • Erreurs: {results['errors']}\n")
            self.validation_text.append("❌ Erreurs détaillées:\n")
            
            for error_detail in results['error_details'][:10]:  # Show first 10 errors
                self.validation_text.append(f"Ligne {error_detail['row']}:")
                for error in error_detail['errors']:
                    self.validation_text.append(f"  • {error}")
                self.validation_text.append("")
            
            if len(results['error_details']) > 10:
                self.validation_text.append(f"... et {len(results['error_details']) - 10} autres erreurs")
            
            self.import_btn.setEnabled(False)
        
        self.progress_bar.setValue(100)
        self.progress_label.setText("Validation terminée")
    
    def import_finished(self, results):
        """Handle import completion"""
        self.cancel_btn.setEnabled(True)
        
        # Show results dialog
        msg_text = f"✅ IMPORTATION TERMINÉE!\n\n"
        msg_text += f"📊 Résultats:\n"
        msg_text += f"  • Total lignes traitées: {results['total']}\n"
        msg_text += f"  • Succès: {results['success']}\n"
        msg_text += f"  • Erreurs: {results['errors']}\n"
        
        if results['errors'] > 0:
            msg_text += f"\n⚠️ {results['errors']} enregistrement(s) n'ont pas pu être importés.\n"
            msg_text += "Voir les détails dans le rapport ci-dessous."
            
            # Show error details in validation text
            self.validation_text.clear()
            self.validation_text.append("❌ Erreurs d'importation:\n")
            for error_detail in results['error_details']:
                self.validation_text.append(f"Ligne {error_detail['row']}:")
                for error in error_detail['errors']:
                    self.validation_text.append(f"  • {error}")
                self.validation_text.append("")
        
        QMessageBox.information(self, "Importation Terminée", msg_text)
        
        if results['success'] > 0:
            self.accept()  # Close dialog and reload students
    
    def handle_error(self, error_message):
        """Handle import error"""
        QMessageBox.critical(self, "Erreur", error_message)
        self.preview_btn.setEnabled(True)
        self.import_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
