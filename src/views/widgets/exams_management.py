"""
Module: Gestion des examens
Version: 1.0.0 - Créé le 2025-12-08

Description:
    Interface moderne de gestion des examens avec:
    - Tableau avec tous les examens
    - Recherche et filtres avancés
    - Dialogue d'ajout/édition complet
    - Export CSV
    - Actions rapides (modifier, résultat, supprimer)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDateEdit, QTextEdit, QSpinBox, QCheckBox,
    QGroupBox, QFrame, QTimeEdit
)
from PySide6.QtCore import Qt, QDate, QTime, Signal
from PySide6.QtGui import QFont, QColor
from datetime import datetime, date

from src.controllers.exam_controller import ExamController
from src.controllers.student_controller import StudentController
from src.models import ExamType, ExamResult, get_session, Exam
from src.utils import export_to_csv


class ExamDialog(QDialog):
    """Dialogue moderne d'ajout/édition d'examen"""
    
    saved = Signal()
    
    def __init__(self, exam=None, parent=None):
        super().__init__(parent)
        self.exam = exam
        self.setWindowTitle("✏️ Modifier Examen" if exam else "➕ Nouvel Examen")
        self.setMinimumSize(700, 700)
        self.setup_ui()
        
        if exam:
            self.load_exam_data()
    
    def setup_ui(self):
        """Configuration de l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Scroll pour les grands formulaires
        from PySide6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)
        
        # === GROUPE 1: Informations de base ===
        info_group = self.create_group("📝 Informations Générales")
        info_layout = QFormLayout()
        
        # Sélection élève
        self.student_combo = QComboBox()
        self.student_combo.setPlaceholderText("Sélectionner un élève")
        students = StudentController.get_all_students()
        for student in students:
            self.student_combo.addItem(f"{student.full_name} - {student.cin}", student.id)
        self.student_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
            }
        """)
        
        # Type d'examen
        self.exam_type = QComboBox()
        self.exam_type.addItem("📖 Théorique", ExamType.THEORETICAL)
        self.exam_type.addItem("🚗 Pratique", ExamType.PRACTICAL)
        self.exam_type.currentIndexChanged.connect(self.on_type_changed)
        
        # Date et heure
        self.scheduled_date = QDateEdit()
        self.scheduled_date.setCalendarPopup(True)
        self.scheduled_date.setDate(QDate.currentDate())
        
        self.scheduled_time = QTimeEdit()
        self.scheduled_time.setTime(QTime(9, 0))
        self.scheduled_time.setDisplayFormat("HH:mm")
        
        # Centre et lieu
        self.exam_center = QLineEdit()
        self.exam_center.setPlaceholderText("Ex: Centre d'examen provincial")
        
        self.location = QLineEdit()
        self.location.setPlaceholderText("Ex: Salle 12, Avenue Mohammed V")
        
        # Tentative
        self.attempt_number = QSpinBox()
        self.attempt_number.setMinimum(1)
        self.attempt_number.setMaximum(10)
        self.attempt_number.setValue(1)
        
        # Type examen
        self.is_official = QCheckBox("Examen officiel")
        self.is_official.setChecked(True)
        
        info_layout.addRow("Élève*:", self.student_combo)
        info_layout.addRow("Type d'Examen*:", self.exam_type)
        info_layout.addRow("Date Prévue*:", self.scheduled_date)
        info_layout.addRow("Heure:", self.scheduled_time)
        info_layout.addRow("Centre d'Examen:", self.exam_center)
        info_layout.addRow("Lieu:", self.location)
        info_layout.addRow("N° Tentative:", self.attempt_number)
        info_layout.addRow("", self.is_official)
        
        info_group.setLayout(info_layout)
        container_layout.addWidget(info_group)
        
        # === GROUPE 2: Examen Théorique ===
        self.theory_group = self.create_group("📖 Examen Théorique")
        theory_layout = QFormLayout()
        
        self.theory_score = QSpinBox()
        self.theory_score.setMinimum(0)
        self.theory_score.setMaximum(100)
        self.theory_score.setSpecialValueText("Non défini")
        
        self.theory_max_score = QSpinBox()
        self.theory_max_score.setMinimum(1)
        self.theory_max_score.setMaximum(100)
        self.theory_max_score.setValue(40)
        
        self.theory_passing_score = QSpinBox()
        self.theory_passing_score.setMinimum(1)
        self.theory_passing_score.setMaximum(100)
        self.theory_passing_score.setValue(35)
        
        theory_layout.addRow("Score Obtenu:", self.theory_score)
        theory_layout.addRow("Score Maximum:", self.theory_max_score)
        theory_layout.addRow("Score de Passage:", self.theory_passing_score)
        
        self.theory_group.setLayout(theory_layout)
        container_layout.addWidget(self.theory_group)
        
        # === GROUPE 3: Examen Pratique ===
        self.practical_group = self.create_group("🚗 Examen Pratique")
        practical_layout = QFormLayout()
        
        self.practical_score = QSpinBox()
        self.practical_score.setMinimum(0)
        self.practical_score.setMaximum(100)
        self.practical_score.setSpecialValueText("Non défini")
        
        self.examiner_name = QLineEdit()
        self.examiner_name.setPlaceholderText("Nom de l'examinateur")
        
        self.vehicle_plate = QLineEdit()
        self.vehicle_plate.setPlaceholderText("Ex: 12345-A-67")
        
        practical_layout.addRow("Score/Évaluation:", self.practical_score)
        practical_layout.addRow("Examinateur:", self.examiner_name)
        practical_layout.addRow("Véhicule (Plaque):", self.vehicle_plate)
        
        self.practical_group.setLayout(practical_layout)
        container_layout.addWidget(self.practical_group)
        
        # === GROUPE 4: Résultat ===
        result_group = self.create_group("📊 Résultat et Statut")
        result_layout = QFormLayout()
        
        self.result = QComboBox()
        self.result.addItem("⏳ En Attente", ExamResult.PENDING)
        self.result.addItem("✅ Réussi", ExamResult.PASSED)
        self.result.addItem("❌ Échoué", ExamResult.FAILED)
        self.result.addItem("👻 Absent", ExamResult.ABSENT)
        
        self.completion_date = QDateEdit()
        self.completion_date.setCalendarPopup(True)
        self.completion_date.setDate(QDate.currentDate())
        
        result_layout.addRow("Résultat:", self.result)
        result_layout.addRow("Date de Passage:", self.completion_date)
        
        result_group.setLayout(result_layout)
        container_layout.addWidget(result_group)
        
        # === GROUPE 5: Convocation et Paiement ===
        admin_group = self.create_group("📄 Administration")
        admin_layout = QFormLayout()
        
        self.summons_number = QLineEdit()
        self.summons_number.setPlaceholderText("Généré automatiquement")
        self.summons_number.setReadOnly(True)
        
        self.registration_fee = QSpinBox()
        self.registration_fee.setMinimum(0)
        self.registration_fee.setMaximum(99999)
        self.registration_fee.setSuffix(" DH")
        self.registration_fee.setValue(200)
        
        self.is_paid = QCheckBox("Frais payés")
        
        admin_layout.addRow("N° Convocation:", self.summons_number)
        admin_layout.addRow("Frais d'Inscription:", self.registration_fee)
        admin_layout.addRow("", self.is_paid)
        
        admin_group.setLayout(admin_layout)
        container_layout.addWidget(admin_group)
        
        # === Notes ===
        notes_group = self.create_group("📝 Notes et Remarques")
        notes_layout = QVBoxLayout()
        
        notes_layout.addWidget(QLabel("Remarques de l'examinateur:"))
        self.examiner_notes = QTextEdit()
        self.examiner_notes.setMaximumHeight(60)
        self.examiner_notes.setPlaceholderText("Observations de l'examinateur...")
        notes_layout.addWidget(self.examiner_notes)
        
        notes_layout.addWidget(QLabel("Erreurs commises:"))
        self.errors_made = QTextEdit()
        self.errors_made.setMaximumHeight(60)
        self.errors_made.setPlaceholderText("Liste des erreurs...")
        notes_layout.addWidget(self.errors_made)
        
        notes_layout.addWidget(QLabel("Notes générales:"))
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(60)
        self.notes.setPlaceholderText("Notes supplémentaires...")
        notes_layout.addWidget(self.notes)
        
        notes_group.setLayout(notes_layout)
        container_layout.addWidget(notes_group)
        
        container_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # === Boutons ===
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                padding: 12px 30px;
                border-radius: 8px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
        """)
        
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.clicked.connect(self.save_exam)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                padding: 12px 30px;
                border-radius: 8px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        # Afficher/masquer les sections selon le type
        self.on_type_changed()
    
    def create_group(self, title):
        """Créer un groupe stylisé"""
        group = QGroupBox(title)
        group.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2196F3;
            }
        """)
        return group
    
    def on_type_changed(self):
        """Gérer le changement de type d'examen"""
        is_theoretical = self.exam_type.currentData() == ExamType.THEORETICAL
        self.theory_group.setVisible(is_theoretical)
        self.practical_group.setVisible(not is_theoretical)
    
    def load_exam_data(self):
        """Charger les données de l'examen à éditer"""
        if not self.exam:
            return
        
        # Élève
        for i in range(self.student_combo.count()):
            if self.student_combo.itemData(i) == self.exam.student_id:
                self.student_combo.setCurrentIndex(i)
                break
        
        # Type
        for i in range(self.exam_type.count()):
            if self.exam_type.itemData(i) == self.exam.exam_type:
                self.exam_type.setCurrentIndex(i)
                break
        
        # Date et heure
        self.scheduled_date.setDate(QDate(
            self.exam.scheduled_date.year,
            self.exam.scheduled_date.month,
            self.exam.scheduled_date.day
        ))
        
        if self.exam.scheduled_time:
            try:
                h, m = map(int, self.exam.scheduled_time.split(':'))
                self.scheduled_time.setTime(QTime(h, m))
            except:
                pass
        
        # Informations
        self.exam_center.setText(self.exam.exam_center or "")
        self.location.setText(self.exam.location or "")
        self.attempt_number.setValue(self.exam.attempt_number or 1)
        self.is_official.setChecked(self.exam.is_official)
        
        # Théorique
        if self.exam.theory_score is not None:
            self.theory_score.setValue(self.exam.theory_score)
        self.theory_max_score.setValue(self.exam.theory_max_score or 40)
        self.theory_passing_score.setValue(self.exam.theory_passing_score or 35)
        
        # Pratique
        if self.exam.practical_score is not None:
            self.practical_score.setValue(self.exam.practical_score)
        self.examiner_name.setText(self.exam.examiner_name or "")
        self.vehicle_plate.setText(self.exam.vehicle_plate or "")
        
        # Résultat
        for i in range(self.result.count()):
            if self.result.itemData(i) == self.exam.result:
                self.result.setCurrentIndex(i)
                break
        
        if self.exam.completion_date:
            self.completion_date.setDate(QDate(
                self.exam.completion_date.year,
                self.exam.completion_date.month,
                self.exam.completion_date.day
            ))
        
        # Administration
        self.summons_number.setText(self.exam.summons_number or "")
        self.registration_fee.setValue(self.exam.registration_fee or 200)
        self.is_paid.setChecked(self.exam.is_paid)
        
        # Notes
        self.examiner_notes.setPlainText(self.exam.examiner_notes or "")
        self.errors_made.setPlainText(self.exam.errors_made or "")
        self.notes.setPlainText(self.exam.notes or "")
    
    def save_exam(self):
        """Enregistrer l'examen"""
        # Validation
        if self.student_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un élève")
            return
        
        try:
            session = get_session()
            
            if self.exam:
                # Mise à jour
                exam = session.query(Exam).filter_by(id=self.exam.id).first()
                if not exam:
                    QMessageBox.critical(self, "Erreur", "Examen introuvable")
                    return
            else:
                # Création
                exam = Exam(
                    student_id=self.student_combo.currentData(),
                    exam_type=self.exam_type.currentData(),
                    scheduled_date=self.scheduled_date.date().toPython()
                )
            
            # Remplir les données
            exam.student_id = self.student_combo.currentData()
            exam.exam_type = self.exam_type.currentData()
            exam.scheduled_date = self.scheduled_date.date().toPython()
            exam.scheduled_time = self.scheduled_time.time().toString("HH:mm")
            exam.exam_center = self.exam_center.text().strip() or None
            exam.location = self.location.text().strip() or None
            exam.attempt_number = self.attempt_number.value()
            exam.is_official = self.is_official.isChecked()
            
            # Théorique
            if exam.exam_type == ExamType.THEORETICAL:
                exam.theory_score = self.theory_score.value() if self.theory_score.value() > 0 else None
                exam.theory_max_score = self.theory_max_score.value()
                exam.theory_passing_score = self.theory_passing_score.value()
            else:
                exam.theory_score = None
            
            # Pratique
            if exam.exam_type == ExamType.PRACTICAL:
                exam.practical_score = self.practical_score.value() if self.practical_score.value() > 0 else None
                exam.examiner_name = self.examiner_name.text().strip() or None
                exam.vehicle_plate = self.vehicle_plate.text().strip() or None
            else:
                exam.practical_score = None
                exam.examiner_name = None
                exam.vehicle_plate = None
            
            # Résultat
            exam.result = self.result.currentData()
            if exam.result != ExamResult.PENDING:
                exam.completion_date = self.completion_date.date().toPython()
            
            # Administration
            exam.registration_fee = self.registration_fee.value()
            exam.is_paid = self.is_paid.isChecked()
            
            # Notes
            exam.examiner_notes = self.examiner_notes.toPlainText().strip() or None
            exam.errors_made = self.errors_made.toPlainText().strip() or None
            exam.notes = self.notes.toPlainText().strip() or None
            
            # Générer numéro de convocation si nécessaire
            if not exam.summons_number and not self.exam:
                session.add(exam)
                session.flush()
                exam.summons_number = exam.generate_summons_number()
            
            if not self.exam:
                session.add(exam)
            
            session.commit()
            
            QMessageBox.information(
                self,
                "Succès",
                f"Examen {'modifié' if self.exam else 'ajouté'} avec succès"
            )
            
            self.saved.emit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement: {str(e)}")


class ExamsManagement(QWidget):
    """Widget de gestion des examens avec tableau et actions"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_exams()
    
    def setup_ui(self):
        """Configuration de l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        header = QHBoxLayout()
        
        title = QLabel("📝 GESTION DES EXAMENS")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #1a1a1a;")
        header.addWidget(title)
        
        header.addStretch()
        
        # Bouton ajouter
        add_btn = QPushButton("➕ Nouvel Examen")
        add_btn.clicked.connect(self.add_exam)
        add_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        header.addWidget(add_btn)
        
        layout.addLayout(header)
        
        # Barre de recherche et filtres
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par élève, convocation...")
        self.search_input.textChanged.connect(self.filter_table)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 11pt;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        search_layout.addWidget(self.search_input, 2)
        
        # Filtre type
        self.type_filter = QComboBox()
        self.type_filter.addItem("Tous les types", None)
        self.type_filter.addItem("📖 Théorique", ExamType.THEORETICAL)
        self.type_filter.addItem("🚗 Pratique", ExamType.PRACTICAL)
        self.type_filter.currentIndexChanged.connect(self.filter_table)
        self.type_filter.setStyleSheet("""
            QComboBox {
                padding: 10px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 11pt;
                background: white;
                min-width: 150px;
            }
        """)
        search_layout.addWidget(self.type_filter)
        
        # Filtre résultat
        self.result_filter = QComboBox()
        self.result_filter.addItem("Tous les résultats", None)
        self.result_filter.addItem("✅ Réussi", ExamResult.PASSED)
        self.result_filter.addItem("❌ Échoué", ExamResult.FAILED)
        self.result_filter.addItem("⏳ En Attente", ExamResult.PENDING)
        self.result_filter.addItem("👻 Absent", ExamResult.ABSENT)
        self.result_filter.currentIndexChanged.connect(self.filter_table)
        self.result_filter.setStyleSheet("""
            QComboBox {
                padding: 10px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 11pt;
                background: white;
                min-width: 150px;
            }
        """)
        search_layout.addWidget(self.result_filter)
        
        # Bouton export
        export_btn = QPushButton("📥 Export CSV")
        export_btn.clicked.connect(self.export_exams)
        export_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)
        search_layout.addWidget(export_btn)
        
        # Bouton rafraîchir
        refresh_btn = QPushButton("🔄")
        refresh_btn.clicked.connect(self.load_exams)
        refresh_btn.setFixedSize(45, 45)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                border-radius: 8px;
                font-size: 14pt;
                border: none;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
        """)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Date", "Élève", "Type", "Résultat", "Score",
            "Tentative", "Centre", "Payé", "Convocation", "Actions"
        ])
        
        # Style du tableau
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                gridline-color: #f0f0f0;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background: #E3F2FD;
                color: #1976D2;
            }
            QHeaderView::section {
                background: #f5f7fa;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                font-weight: bold;
                color: #333;
            }
        """)
        
        self.table.horizontalHeader().setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        # Colonnes redimensionnables
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(9, 150)
        
        layout.addWidget(self.table)
        
        # Compteur
        self.count_label = QLabel()
        self.count_label.setFont(QFont("Segoe UI", 10))
        self.count_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.count_label)
    
    def load_exams(self):
        """Charger tous les examens"""
        self.all_exams = ExamController.get_all_exams()
        self.filter_table()
    
    def filter_table(self):
        """Filtrer et afficher les examens"""
        search_text = self.search_input.text().lower()
        type_filter = self.type_filter.currentData()
        result_filter = self.result_filter.currentData()
        
        # Filtrer les examens
        filtered = self.all_exams
        
        if type_filter:
            filtered = [e for e in filtered if e.exam_type == type_filter]
        
        if result_filter:
            filtered = [e for e in filtered if e.result == result_filter]
        
        if search_text:
            session = get_session()
            filtered_with_search = []
            for exam in filtered:
                student = exam.student
                if student and search_text in student.full_name.lower():
                    filtered_with_search.append(exam)
                elif exam.summons_number and search_text in exam.summons_number.lower():
                    filtered_with_search.append(exam)
            filtered = filtered_with_search
        
        # Remplir le tableau
        self.table.setRowCount(len(filtered))
        
        session = get_session()
        for row, exam in enumerate(filtered):
            student = exam.student
            
            # Date
            date_item = QTableWidgetItem(exam.scheduled_date.strftime('%d/%m/%Y'))
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, date_item)
            
            # Élève
            student_name = student.full_name if student else "Inconnu"
            self.table.setItem(row, 1, QTableWidgetItem(student_name))
            
            # Type
            type_icon = "📖" if exam.exam_type == ExamType.THEORETICAL else "🚗"
            type_item = QTableWidgetItem(type_icon)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, type_item)
            
            # Résultat
            result_map = {
                ExamResult.PASSED: ("✅ Réussi", QColor("#4CAF50")),
                ExamResult.FAILED: ("❌ Échoué", QColor("#F44336")),
                ExamResult.PENDING: ("⏳ En Attente", QColor("#FFC107")),
                ExamResult.ABSENT: ("👻 Absent", QColor("#FF9800"))
            }
            result_text, result_color = result_map.get(exam.result, ("?", QColor("#999")))
            result_item = QTableWidgetItem(result_text)
            result_item.setForeground(result_color)
            result_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, result_item)
            
            # Score
            score_text = ""
            if exam.exam_type == ExamType.THEORETICAL and exam.theory_score is not None:
                score_text = f"{exam.theory_score}/{exam.theory_max_score}"
            elif exam.exam_type == ExamType.PRACTICAL and exam.practical_score is not None:
                score_text = f"{exam.practical_score}/100"
            
            score_item = QTableWidgetItem(score_text)
            score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, score_item)
            
            # Tentative
            attempt_item = QTableWidgetItem(f"#{exam.attempt_number}")
            attempt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 5, attempt_item)
            
            # Centre
            self.table.setItem(row, 6, QTableWidgetItem(exam.exam_center or "-"))
            
            # Payé
            paid_item = QTableWidgetItem("✅" if exam.is_paid else "❌")
            paid_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 7, paid_item)
            
            # Convocation
            summons_item = QTableWidgetItem(exam.summons_number or "-")
            summons_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 8, summons_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(5)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(30, 30)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #2196F3;
                    color: white;
                    border-radius: 5px;
                    font-size: 12pt;
                    border: none;
                }
                QPushButton:hover {
                    background: #1976D2;
                }
            """)
            edit_btn.clicked.connect(lambda checked, e=exam: self.edit_exam(e))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedSize(30, 30)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: #F44336;
                    color: white;
                    border-radius: 5px;
                    font-size: 12pt;
                    border: none;
                }
                QPushButton:hover {
                    background: #D32F2F;
                }
            """)
            delete_btn.clicked.connect(lambda checked, e=exam: self.delete_exam(e))
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 9, actions_widget)
        
        # Mettre à jour le compteur
        total = len(self.all_exams)
        showing = len(filtered)
        self.count_label.setText(f"Affichage de {showing} examen(s) sur {total} au total")
    
    def add_exam(self):
        """Ajouter un nouvel examen"""
        dialog = ExamDialog(parent=self)
        dialog.saved.connect(self.load_exams)
        dialog.exec()
    
    def edit_exam(self, exam):
        """Modifier un examen"""
        dialog = ExamDialog(exam=exam, parent=self)
        dialog.saved.connect(self.load_exams)
        dialog.exec()
    
    def delete_exam(self, exam):
        """Supprimer un examen"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer cet examen ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                session = get_session()
                e = session.query(Exam).filter_by(id=exam.id).first()
                if e:
                    session.delete(e)
                    session.commit()
                    QMessageBox.information(self, "Succès", "Examen supprimé avec succès")
                    self.load_exams()
            except Exception as ex:
                session.rollback()
                QMessageBox.critical(self, "Erreur", f"Erreur: {str(ex)}")
    
    def export_exams(self):
        """Exporter les examens en CSV"""
        if not self.all_exams:
            QMessageBox.warning(self, "Avertissement", "Aucun examen à exporter")
            return
        
        session = get_session()
        data = []
        for exam in self.all_exams:
            student = exam.student
            data.append({
                'Date': exam.scheduled_date.strftime('%d/%m/%Y'),
                'Élève': student.full_name if student else 'Inconnu',
                'CIN': student.cin if student else '',
                'Type': 'Théorique' if exam.exam_type == ExamType.THEORETICAL else 'Pratique',
                'Résultat': exam.result.value,
                'Score': exam.theory_score or exam.practical_score or '',
                'Tentative': exam.attempt_number,
                'Centre': exam.exam_center or '',
                'Lieu': exam.location or '',
                'Examinateur': exam.examiner_name or '',
                'Convocation': exam.summons_number or '',
                'Frais': exam.registration_fee,
                'Payé': 'Oui' if exam.is_paid else 'Non',
                'Officiel': 'Oui' if exam.is_official else 'Non'
            })
        
        filename = f"examens_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        try:
            export_to_csv(data, filename)
            QMessageBox.information(
                self,
                "Succès",
                f"Export réussi!\nFichier: {filename}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export: {str(e)}")
