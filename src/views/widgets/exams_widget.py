"""
Widget de gestion des examens avec inscriptions et résultats
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDateEdit, QTimeEdit, QTextEdit, QSpinBox, QCheckBox,
    QFileDialog, QGroupBox
)
from PySide6.QtCore import Qt, QDate, QTime
from PySide6.QtGui import QFont, QColor
from datetime import datetime

from src.controllers.exam_controller import ExamController
from src.controllers.student_controller import StudentController
from src.models import ExamType, ExamResult
from src.utils import export_to_csv, get_pdf_generator


class ExamDialog(QDialog):
    """Dialogue de création/édition d'un examen"""
    
    def __init__(self, exam=None, parent=None):
        super().__init__(parent)
        self.exam = exam
        self.setWindowTitle("Détail Examen" if exam else "Nouvel Examen")
        self.setMinimumSize(600, 550)
        self.setup_ui()
        
        if exam:
            self.load_exam_data()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        
        # Informations générales
        general_group = QGroupBox("📝 Informations Générales")
        general_layout = QFormLayout(general_group)
        
        self.student_combo = QComboBox()
        students = StudentController.get_all_students()
        for student in students:
            self.student_combo.addItem(
                f"{student.full_name} (CIN: {student.cin})",
                student.id
            )
        
        self.exam_type = QComboBox()
        for etype in ExamType:
            self.exam_type.addItem(etype.value.capitalize(), etype)
        
        self.scheduled_date = QDateEdit()
        self.scheduled_date.setCalendarPopup(True)
        self.scheduled_date.setDate(QDate.currentDate().addDays(7))
        
        self.scheduled_time = QTimeEdit()
        self.scheduled_time.setTime(QTime(10, 0))
        
        self.location = QLineEdit()
        self.location.setPlaceholderText("Ex: Centre d'Examen - Rabat")
        
        self.exam_center = QLineEdit()
        
        self.attempt_number = QSpinBox()
        self.attempt_number.setMinimum(1)
        self.attempt_number.setValue(1)
        
        self.is_official = QCheckBox("Examen Officiel")
        self.is_official.setChecked(True)
        
        general_layout.addRow("Élève*:", self.student_combo)
        general_layout.addRow("Type d'Examen*:", self.exam_type)
        general_layout.addRow("Date*:", self.scheduled_date)
        general_layout.addRow("Heure:", self.scheduled_time)
        general_layout.addRow("Lieu:", self.location)
        general_layout.addRow("Centre d'Examen:", self.exam_center)
        general_layout.addRow("N° Tentative:", self.attempt_number)
        general_layout.addRow("", self.is_official)
        
        layout.addWidget(general_group)
        
        # Résultat
        result_group = QGroupBox("🎯 Résultat")
        result_layout = QFormLayout(result_group)
        
        self.result = QComboBox()
        for res in ExamResult:
            self.result.addItem(res.value.capitalize(), res)
        
        self.theory_score = QSpinBox()
        self.theory_score.setMinimum(0)
        self.theory_score.setMaximum(40)
        
        self.examiner_name = QLineEdit()
        
        self.registration_fee = QSpinBox()
        self.registration_fee.setMinimum(0)
        self.registration_fee.setMaximum(9999)
        self.registration_fee.setValue(300)
        self.registration_fee.setSuffix(" DH")
        
        self.is_paid = QCheckBox("Payé")
        
        result_layout.addRow("Résultat:", self.result)
        result_layout.addRow("Score Théorique:", self.theory_score)
        result_layout.addRow("Examinateur:", self.examiner_name)
        result_layout.addRow("Frais:", self.registration_fee)
        result_layout.addRow("", self.is_paid)
        
        layout.addWidget(result_group)
        
        # Notes
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(80)
        self.notes.setPlaceholderText("Notes, remarques ou erreurs commises...")
        layout.addWidget(QLabel("📝 Notes:"))
        layout.addWidget(self.notes)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.clicked.connect(self.save_exam)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
        """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def load_exam_data(self):
        """Charger les données de l'examen"""
        if not self.exam:
            return
        
        # Sélectionner l'élève
        for i in range(self.student_combo.count()):
            if self.student_combo.itemData(i) == self.exam.student_id:
                self.student_combo.setCurrentIndex(i)
                break
        
        # Type
        for i in range(self.exam_type.count()):
            if self.exam_type.itemData(i) == self.exam.exam_type:
                self.exam_type.setCurrentIndex(i)
                break
        
        # Date
        if self.exam.scheduled_date:
            self.scheduled_date.setDate(QDate(
                self.exam.scheduled_date.year,
                self.exam.scheduled_date.month,
                self.exam.scheduled_date.day
            ))
        
        # Heure
        if self.exam.scheduled_time:
            try:
                h, m = map(int, self.exam.scheduled_time.split(':'))
                self.scheduled_time.setTime(QTime(h, m))
            except:
                pass
        
        self.location.setText(self.exam.location or "")
        self.exam_center.setText(self.exam.exam_center or "")
        self.attempt_number.setValue(self.exam.attempt_number or 1)
        self.is_official.setChecked(self.exam.is_official)
        
        # Résultat
        for i in range(self.result.count()):
            if self.result.itemData(i) == self.exam.result:
                self.result.setCurrentIndex(i)
                break
        
        self.theory_score.setValue(self.exam.theory_score or 0)
        self.examiner_name.setText(self.exam.examiner_name or "")
        self.registration_fee.setValue(self.exam.registration_fee or 300)
        self.is_paid.setChecked(self.exam.is_paid)
        
        self.notes.setPlainText(self.exam.notes or "")
    
    def save_exam(self):
        """Enregistrer l'examen"""
        data = {
            'student_id': self.student_combo.currentData(),
            'exam_type': self.exam_type.currentData(),
            'scheduled_date': self.scheduled_date.date().toPython(),
            'scheduled_time': self.scheduled_time.time().toString("HH:mm"),
            'location': self.location.text().strip() or None,
            'exam_center': self.exam_center.text().strip() or None,
            'attempt_number': self.attempt_number.value(),
            'is_official': self.is_official.isChecked(),
            'result': self.result.currentData(),
            'theory_score': self.theory_score.value() if self.theory_score.value() > 0 else None,
            'examiner_name': self.examiner_name.text().strip() or None,
            'registration_fee': self.registration_fee.value(),
            'is_paid': self.is_paid.isChecked(),
            'notes': self.notes.toPlainText().strip() or None,
        }
        
        try:
            if self.exam:
                ExamController.update_exam(self.exam.id, data)
                QMessageBox.information(self, "Succès", "Examen mis à jour avec succès")
            else:
                ExamController.create_exam(data)
                QMessageBox.information(self, "Succès", "Examen créé avec succès")
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")


class ExamsWidget(QWidget):
    """Widget de gestion des examens"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.exams = []
        self.setup_ui()
        self.load_exams()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        self.create_header(layout)
        
        # Filtres
        self.create_filters(layout)
        
        # Statistiques
        self.create_stats(layout)
        
        # Tableau
        self.create_table(layout)
    
    def create_header(self, layout):
        """Créer l'en-tête"""
        header_layout = QHBoxLayout()
        
        title = QLabel("📝 Gestion des Examens")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        add_btn = QPushButton("➕ Nouvel Examen")
        add_btn.clicked.connect(self.add_exam)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        add_btn.setCursor(Qt.PointingHandCursor)
        
        export_btn = QPushButton("📤 Exporter CSV")
        export_btn.clicked.connect(self.export_csv)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #1abc9c;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #16a085; }
        """)
        export_btn.setCursor(Qt.PointingHandCursor)
        
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.clicked.connect(self.load_exams)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #8e44ad; }
        """)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        
        header_layout.addWidget(add_btn)
        header_layout.addWidget(export_btn)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
    
    def create_filters(self, layout):
        """Créer les filtres"""
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par nom d'élève...")
        self.search_input.textChanged.connect(self.apply_filters)
        self.search_input.setMinimumHeight(40)
        
        self.type_filter = QComboBox()
        self.type_filter.addItem("📊 Tous les types", None)
        for etype in ExamType:
            self.type_filter.addItem(etype.value.capitalize(), etype)
        self.type_filter.currentIndexChanged.connect(self.apply_filters)
        self.type_filter.setMinimumHeight(40)
        
        self.result_filter = QComboBox()
        self.result_filter.addItem("🎯 Tous les résultats", None)
        for res in ExamResult:
            self.result_filter.addItem(res.value.capitalize(), res)
        self.result_filter.currentIndexChanged.connect(self.apply_filters)
        self.result_filter.setMinimumHeight(40)
        
        filter_layout.addWidget(self.search_input, stretch=2)
        filter_layout.addWidget(self.type_filter, stretch=1)
        filter_layout.addWidget(self.result_filter, stretch=1)
        
        layout.addLayout(filter_layout)
    
    def create_stats(self, layout):
        """Créer les statistiques"""
        stats_layout = QHBoxLayout()
        
        self.total_label = QLabel("Total: 0")
        self.theory_success_label = QLabel("Théorie: 0%")
        self.practical_success_label = QLabel("Pratique: 0%")
        self.pending_label = QLabel("En Attente: 0")
        
        for label in [self.total_label, self.theory_success_label, 
                     self.practical_success_label, self.pending_label]:
            label.setStyleSheet("""
                QLabel {
                    background-color: white;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                    color: #2c3e50;
                    border: 2px solid #ecf0f1;
                }
            """)
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.theory_success_label)
        stats_layout.addWidget(self.practical_success_label)
        stats_layout.addWidget(self.pending_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
    
    def create_table(self, layout):
        """Créer le tableau"""
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Élève", "Type", "Date", "Heure",
            "Tentative", "Résultat", "Payé", "Actions"
        ])
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(400)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.table)
    
    def load_exams(self):
        """Charger tous les examens"""
        self.exams = ExamController.get_all_exams()
        self.update_stats()
        self.populate_table()
    
    def update_stats(self):
        """Mettre à jour les statistiques"""
        total = len(self.exams)
        
        theory_exams = [e for e in self.exams if e.exam_type == ExamType.THEORETICAL]
        theory_passed = len([e for e in theory_exams if e.result == ExamResult.PASSED])
        theory_rate = (theory_passed / len(theory_exams) * 100) if theory_exams else 0
        
        practical_exams = [e for e in self.exams if e.exam_type == ExamType.PRACTICAL]
        practical_passed = len([e for e in practical_exams if e.result == ExamResult.PASSED])
        practical_rate = (practical_passed / len(practical_exams) * 100) if practical_exams else 0
        
        pending = len([e for e in self.exams if e.result == ExamResult.PENDING])
        
        self.total_label.setText(f"Total: {total}")
        self.theory_success_label.setText(f"Théorie: {theory_rate:.1f}%")
        self.practical_success_label.setText(f"Pratique: {practical_rate:.1f}%")
        self.pending_label.setText(f"En Attente: {pending}")
    
    def apply_filters(self):
        """Appliquer les filtres"""
        search_text = self.search_input.text().lower()
        type_filter = self.type_filter.currentData()
        result_filter = self.result_filter.currentData()
        
        filtered = []
        
        for exam in self.exams:
            if search_text and exam.student:
                if search_text not in exam.student.full_name.lower():
                    continue
            
            if type_filter and exam.exam_type != type_filter:
                continue
            
            if result_filter and exam.result != result_filter:
                continue
            
            filtered.append(exam)
        
        self.populate_table(filtered)
    
    def populate_table(self, exams=None):
        """Remplir le tableau"""
        if exams is None:
            exams = self.exams
        
        self.table.setRowCount(0)
        
        for row, exam in enumerate(exams):
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(exam.id)))
            self.table.setItem(row, 1, QTableWidgetItem(exam.student.full_name if exam.student else "N/A"))
            self.table.setItem(row, 2, QTableWidgetItem(exam.exam_type.value.capitalize() if exam.exam_type else "N/A"))
            self.table.setItem(row, 3, QTableWidgetItem(exam.scheduled_date.strftime('%d/%m/%Y') if exam.scheduled_date else ""))
            self.table.setItem(row, 4, QTableWidgetItem(exam.scheduled_time or ""))
            self.table.setItem(row, 5, QTableWidgetItem(str(exam.attempt_number or 1)))
            
            # Résultat
            result_item = QTableWidgetItem(exam.result.value.capitalize() if exam.result else "N/A")
            if exam.result == ExamResult.PASSED:
                result_item.setForeground(QColor("#27ae60"))
            elif exam.result == ExamResult.FAILED:
                result_item.setForeground(QColor("#e74c3c"))
            elif exam.result == ExamResult.PENDING:
                result_item.setForeground(QColor("#f39c12"))
            self.table.setItem(row, 6, result_item)
            
            # Payé
            paid_item = QTableWidgetItem("✅" if exam.is_paid else "❌")
            self.table.setItem(row, 7, paid_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 0, 5, 0)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Modifier")
            edit_btn.clicked.connect(lambda checked, e=exam: self.edit_exam(e))
            edit_btn.setCursor(Qt.PointingHandCursor)
            
            conv_btn = QPushButton("📄")
            conv_btn.setToolTip("Convocation")
            conv_btn.clicked.connect(lambda checked, e=exam: self.generate_convocation(e))
            conv_btn.setCursor(Qt.PointingHandCursor)
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(conv_btn)
            
            self.table.setCellWidget(row, 8, actions_widget)
    
    def add_exam(self):
        """Ajouter un examen"""
        dialog = ExamDialog(parent=self)
        if dialog.exec():
            self.load_exams()
    
    def edit_exam(self, exam):
        """Modifier un examen"""
        dialog = ExamDialog(exam, parent=self)
        if dialog.exec():
            self.load_exams()
    
    def generate_convocation(self, exam):
        """Générer une convocation"""
        try:
            pdf_gen = get_pdf_generator()
            
            exam_data = {
                'summons_number': exam.summons_number or f"CONV-{exam.id}-{datetime.now().strftime('%Y%m%d')}",
                'student_name': exam.student.full_name if exam.student else "N/A",
                'student_cin': exam.student.cin if exam.student else "N/A",
                'exam_type': exam.exam_type.value.capitalize() if exam.exam_type else "N/A",
                'exam_date': exam.scheduled_date.strftime('%d %B %Y') if exam.scheduled_date else "N/A",
                'exam_time': exam.scheduled_time or "N/A",
                'location': exam.location or exam.exam_center or "N/A"
            }
            
            success, result = pdf_gen.generate_summons(exam_data)
            
            if success:
                # Mettre à jour l'examen
                ExamController.update_exam(exam.id, {'summons_generated': True})
                QMessageBox.information(self, "Succès", f"Convocation générée: {result}")
            else:
                QMessageBox.warning(self, "Erreur", result)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def export_csv(self):
        """Exporter en CSV"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exporter les examens",
                f"exports/examens_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if filename:
                success, result = export_to_csv(self.exams, filename, 'exams')
                
                if success:
                    QMessageBox.information(self, "Succès", f"Export réussi: {result}")
                else:
                    QMessageBox.warning(self, "Erreur", result)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
