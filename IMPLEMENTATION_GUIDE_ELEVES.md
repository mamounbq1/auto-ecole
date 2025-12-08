# 🚀 GUIDE D'IMPLÉMENTATION - MODULE ÉLÈVES

**Date**: 2025-12-08  
**Phases**: 1, 2 et 3 (Toutes les 15 améliorations)  
**Fichier cible**: `src/views/widgets/students_enhanced.py`

---

## 📋 TABLE DES MATIÈRES

1. [Modifications à Apporter](#modifications-à-apporter)
2. [Phase 1: Fonctionnalités Critiques](#phase-1-fonctionnalités-critiques)
3. [Phase 2: Améliorations Moyennes](#phase-2-améliorations-moyennes)
4. [Phase 3: Améliorations Mineures](#phase-3-améliorations-mineures)
5. [Tests et Validation](#tests-et-validation)

---

## 🔧 MODIFICATIONS À APPORTER

### Fichiers Affectés
- ✅ `src/views/widgets/students_enhanced.py` (principal)
- ✅ Créer: `data/photos/` (dossier pour photos)
- ✅ Créer: `templates/students_import_template.csv` (template CSV)

### Imports Supplémentaires Nécessaires

Ajouter en haut du fichier `students_enhanced.py`:

```python
import os
import re
from datetime import date
from PySide6.QtGui import QPixmap, QShortcut, QKeySequence
from PySide6.QtWidgets import QProgressDialog
```

---

## 🔴 PHASE 1: FONCTIONNALITÉS CRITIQUES (2 jours)

### ✅ Amélioration #1: Vue Détaillée Complète (4h)

**Objectif**: Remplacer le `QMessageBox` simple par un dialogue riche avec 6 onglets

**Code à ajouter**: Nouvelle classe `StudentDetailViewDialog`

```python
class StudentDetailViewDialog(QDialog):
    """Vue détaillée complète d'un élève avec tous ses détails"""
    
    def __init__(self, student, parent=None):
        super().__init__(parent)
        self.student = student
        self.setWindowTitle(f"Détails: {student.full_name}")
        self.setMinimumSize(950, 750)
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface complète"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # En-tête avec photo et stats
        header = self.create_header()
        layout.addWidget(header)
        
        # Onglets détaillés
        tabs = QTabWidget()
        tabs.addTab(self.create_info_tab(), "📋 Informations")
        tabs.addTab(self.create_training_tab(), "🎓 Formation")
        tabs.addTab(self.create_sessions_tab(), "🚗 Séances")
        tabs.addTab(self.create_payments_tab(), "💰 Paiements")
        tabs.addTab(self.create_exams_tab(), "📝 Examens")
        tabs.addTab(self.create_notes_tab(), "📄 Notes")
        
        layout.addWidget(tabs)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        edit_btn = QPushButton("✏️ Modifier")
        edit_btn.clicked.connect(self.edit_student)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        close_btn = QPushButton("❌ Fermer")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def create_header(self):
        """Créer l'en-tête avec photo et infos principales"""
        widget = QGroupBox()
        layout = QHBoxLayout(widget)
        layout.setSpacing(20)
        
        # Photo de profil
        photo_label = QLabel()
        photo_label.setFixedSize(130, 130)
        photo_label.setAlignment(Qt.AlignCenter)
        
        if self.student.photo_path and os.path.exists(self.student.photo_path):
            pixmap = QPixmap(self.student.photo_path)
            photo_label.setPixmap(
                pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            photo_label.setStyleSheet("""
                border: 4px solid #3498db;
                border-radius: 65px;
                background: white;
                padding: 5px;
            """)
        else:
            photo_label.setText("👤")
            photo_label.setStyleSheet("""
                font-size: 70px;
                border: 4px dashed #bdc3c7;
                border-radius: 65px;
                background: #ecf0f1;
            """)
        
        layout.addWidget(photo_label)
        
        # Informations principales
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        
        # Nom
        name_label = QLabel(self.student.full_name)
        name_label.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #2c3e50;
        """)
        info_layout.addWidget(name_label)
        
        # CIN
        cin_label = QLabel(f"CIN: {self.student.cin}")
        cin_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        info_layout.addWidget(cin_label)
        
        # Téléphone
        phone_label = QLabel(f"📞 {self.student.phone}")
        phone_label.setStyleSheet("font-size: 14px; color: #34495e;")
        info_layout.addWidget(phone_label)
        
        # Âge
        age_label = QLabel(f"🎂 {self.student.age} ans")
        age_label.setStyleSheet("font-size: 14px; color: #34495e;")
        info_layout.addWidget(age_label)
        
        # Badge de statut
        status_badge = QLabel(self.student.status.value.upper())
        status_badge.setAlignment(Qt.AlignCenter)
        status_badge.setFixedWidth(150)
        status_badge.setStyleSheet(self._get_status_style(self.student.status))
        info_layout.addWidget(status_badge)
        
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        # Statistiques rapides
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(10)
        
        stats_layout.addWidget(self._create_stat_card(
            "Progression", 
            f"{self.student.completion_rate:.1f}%",
            "#3498db"
        ))
        
        balance_color = "#e74c3c" if self.student.balance < 0 else "#27ae60"
        stats_layout.addWidget(self._create_stat_card(
            "Solde", 
            f"{self.student.balance:,.2f} DH",
            balance_color
        ))
        
        stats_layout.addWidget(self._create_stat_card(
            "Séances", 
            str(len(self.student.sessions)),
            "#9b59b6"
        ))
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        widget.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        return widget
    
    def _get_status_style(self, status):
        """Style du badge selon le statut"""
        colors = {
            StudentStatus.ACTIVE: "#27ae60",
            StudentStatus.PENDING: "#f39c12",
            StudentStatus.SUSPENDED: "#e74c3c",
            StudentStatus.GRADUATED: "#3498db",
            StudentStatus.ABANDONED: "#95a5a6"
        }
        color = colors.get(status, "#95a5a6")
        return f"""
            background-color: {color};
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 15px;
        """
    
    def _create_stat_card(self, title, value, color):
        """Créer une carte de statistique"""
        card = QGroupBox()
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: #7f8c8d; font-size: 12px;")
        title_label.setAlignment(Qt.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: bold;
            color: {color};
        """)
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        card.setStyleSheet("""
            QGroupBox {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        return card
    
    def create_info_tab(self):
        """Onglet Informations complètes"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Style pour les labels
        label_style = "font-weight: bold; font-size: 13px; color: #2c3e50;"
        value_style = "font-size: 13px; color: #34495e; padding: 8px; background: #f8f9fa; border-radius: 5px;"
        
        def create_value_label(text):
            label = QLabel(text or "N/A")
            label.setStyleSheet(value_style)
            return label
        
        # Informations personnelles
        layout.addRow(QLabel("👤 INFORMATIONS PERSONNELLES"))
        layout.addRow("Nom complet:", create_value_label(self.student.full_name))
        layout.addRow("CIN:", create_value_label(self.student.cin))
        
        birth_str = self.student.date_of_birth.strftime("%d/%m/%Y") if self.student.date_of_birth else "N/A"
        layout.addRow("Date de naissance:", create_value_label(f"{birth_str} ({self.student.age} ans)"))
        
        layout.addRow("Téléphone:", create_value_label(self.student.phone))
        layout.addRow("Email:", create_value_label(self.student.email))
        layout.addRow("Adresse:", create_value_label(self.student.address))
        
        # Informations formation
        layout.addRow(QLabel(""))  # Separator
        layout.addRow(QLabel("🎓 FORMATION"))
        layout.addRow("Type de permis:", create_value_label(self.student.license_type or "B"))
        layout.addRow("Statut:", create_value_label(self.student.status.value.capitalize()))
        
        reg_date = self.student.registration_date.strftime("%d/%m/%Y") if self.student.registration_date else "N/A"
        layout.addRow("Date d'inscription:", create_value_label(reg_date))
        
        # Contact d'urgence
        if self.student.emergency_contact_name or self.student.emergency_contact_phone:
            layout.addRow(QLabel(""))  # Separator
            layout.addRow(QLabel("🚨 CONTACT D'URGENCE"))
            layout.addRow("Nom:", create_value_label(self.student.emergency_contact_name))
            layout.addRow("Téléphone:", create_value_label(self.student.emergency_contact_phone))
        
        return widget
    
    def create_training_tab(self):
        """Onglet Formation avec progression"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Carte de progression
        progress_card = QGroupBox("📊 Progression de la Formation")
        progress_layout = QVBoxLayout(progress_card)
        
        # Heures de conduite
        hours_label = QLabel(f"Heures de Conduite: {self.student.hours_completed}/{self.student.hours_planned}")
        hours_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        progress_layout.addWidget(hours_label)
        
        # Barre de progression (simulée avec QLabel)
        progress_bar_widget = QWidget()
        progress_bar_widget.setFixedHeight(30)
        progress_percent = min(100, self.student.completion_rate)
        progress_bar_widget.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db,
                    stop:{progress_percent/100} #3498db,
                    stop:{progress_percent/100} #ecf0f1,
                    stop:1 #ecf0f1);
                border-radius: 15px;
                border: 2px solid #bdc3c7;
            }}
        """)
        progress_layout.addWidget(progress_bar_widget)
        
        progress_percent_label = QLabel(f"{progress_percent:.1f}% complété")
        progress_percent_label.setAlignment(Qt.AlignCenter)
        progress_percent_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        progress_layout.addWidget(progress_percent_label)
        
        layout.addWidget(progress_card)
        
        # Statistiques examens
        exams_card = QGroupBox("📝 Examens")
        exams_layout = QGridLayout(exams_card)
        
        # Théorie
        theory_widget = self._create_exam_stat_widget(
            "Théorie",
            self.student.theoretical_exam_attempts,
            self.student.theoretical_exam_passed
        )
        exams_layout.addWidget(theory_widget, 0, 0)
        
        # Pratique
        practical_widget = self._create_exam_stat_widget(
            "Pratique",
            self.student.practical_exam_attempts,
            self.student.practical_exam_passed
        )
        exams_layout.addWidget(practical_widget, 0, 1)
        
        layout.addWidget(exams_card)
        
        layout.addStretch()
        
        return widget
    
    def _create_exam_stat_widget(self, title, attempts, passed):
        """Créer un widget de statistique d'examen"""
        widget = QGroupBox(title)
        layout = QVBoxLayout(widget)
        
        attempts_label = QLabel(f"Tentatives: {attempts}")
        attempts_label.setStyleSheet("font-size: 14px; color: #34495e;")
        layout.addWidget(attempts_label)
        
        passed_label = QLabel(f"Réussi: {passed}")
        color = "#27ae60" if passed > 0 else "#e74c3c"
        passed_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {color};")
        layout.addWidget(passed_label)
        
        widget.setStyleSheet("""
            QGroupBox {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                font-weight: bold;
            }
        """)
        
        return widget
    
    def create_sessions_tab(self):
        """Onglet Séances de conduite"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Statistiques séances
        stats_layout = QHBoxLayout()
        
        total = len(self.student.sessions)
        completed = len([s for s in self.student.sessions if hasattr(s, 'status') and s.status == 'realise'])
        upcoming = len([s for s in self.student.sessions if hasattr(s, 'status') and s.status in ['prevu', 'confirme']])
        
        stats_layout.addWidget(self._create_stat_card("Total", str(total), "#3498db"))
        stats_layout.addWidget(self._create_stat_card("Réalisées", str(completed), "#27ae60"))
        stats_layout.addWidget(self._create_stat_card("À venir", str(upcoming), "#f39c12"))
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # Tableau des séances
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Date", "Type", "Moniteur", "Véhicule", "Durée", "Statut"])
        
        table.setRowCount(len(self.student.sessions))
        for row, session in enumerate(self.student.sessions):
            # Date
            date_str = session.start_datetime.strftime("%d/%m/%Y %H:%M") if hasattr(session, 'start_datetime') else "N/A"
            table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # Type
            session_type = getattr(session, 'session_type', 'N/A')
            table.setItem(row, 1, QTableWidgetItem(session_type))
            
            # Moniteur
            instructor = getattr(session.instructor, 'full_name', 'N/A') if hasattr(session, 'instructor') and session.instructor else "N/A"
            table.setItem(row, 2, QTableWidgetItem(instructor))
            
            # Véhicule
            vehicle = getattr(session.vehicle, 'registration', 'N/A') if hasattr(session, 'vehicle') and session.vehicle else "N/A"
            table.setItem(row, 3, QTableWidgetItem(vehicle))
            
            # Durée
            duration = f"{getattr(session, 'duration_minutes', 0)} min"
            table.setItem(row, 4, QTableWidgetItem(duration))
            
            # Statut
            status = getattr(session, 'status', 'N/A')
            status_item = QTableWidgetItem(status)
            if status == 'realise':
                status_item.setForeground(QColor("#27ae60"))
            elif status in ['prevu', 'confirme']:
                status_item.setForeground(QColor("#3498db"))
            table.setItem(row, 5, status_item)
        
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(table)
        
        return widget
    
    def create_payments_tab(self):
        """Onglet Paiements"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Résumé financier
        summary = QGroupBox("💰 Résumé Financier")
        summary_layout = QGridLayout(summary)
        
        # Total dû
        due_label = QLabel(f"{self.student.total_due:,.2f} DH")
        due_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #e74c3c;")
        summary_layout.addWidget(QLabel("Total Dû:"), 0, 0)
        summary_layout.addWidget(due_label, 0, 1)
        
        # Total payé
        paid_label = QLabel(f"{self.student.total_paid:,.2f} DH")
        paid_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #27ae60;")
        summary_layout.addWidget(QLabel("Total Payé:"), 1, 0)
        summary_layout.addWidget(paid_label, 1, 1)
        
        # Solde
        balance_label = QLabel(f"{self.student.balance:,.2f} DH")
        balance_color = "#e74c3c" if self.student.balance < 0 else "#27ae60"
        balance_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {balance_color};")
        summary_layout.addWidget(QLabel("Solde:"), 2, 0)
        summary_layout.addWidget(balance_label, 2, 1)
        
        summary.setStyleSheet("""
            QGroupBox {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 20px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(summary)
        
        # Tableau des paiements
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Date", "Montant", "Catégorie", "Méthode", "Reçu"])
        
        table.setRowCount(len(self.student.payments))
        for row, payment in enumerate(self.student.payments):
            # Date
            date_str = payment.payment_date.strftime("%d/%m/%Y") if hasattr(payment, 'payment_date') else "N/A"
            table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # Montant
            amount_item = QTableWidgetItem(f"{payment.amount:,.2f} DH")
            amount_item.setForeground(QColor("#27ae60"))
            table.setItem(row, 1, amount_item)
            
            # Catégorie
            table.setItem(row, 2, QTableWidgetItem(getattr(payment, 'category', 'N/A')))
            
            # Méthode
            method = getattr(payment.payment_method, 'value', 'N/A') if hasattr(payment, 'payment_method') else 'N/A'
            table.setItem(row, 3, QTableWidgetItem(method))
            
            # Reçu
            receipt = getattr(payment, 'receipt_number', 'N/A') or 'N/A'
            table.setItem(row, 4, QTableWidgetItem(receipt))
        
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #27ae60;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(table)
        
        return widget
    
    def create_exams_tab(self):
        """Onglet Examens"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Message si pas d'examens
        if not self.student.exams:
            no_exams_label = QLabel("Aucun examen enregistré pour cet élève.")
            no_exams_label.setAlignment(Qt.AlignCenter)
            no_exams_label.setStyleSheet("""
                font-size: 16px;
                color: #7f8c8d;
                padding: 50px;
            """)
            layout.addWidget(no_exams_label)
            return widget
        
        # Tableau des examens
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Date", "Type", "Résultat", "Note", "Remarques"])
        
        table.setRowCount(len(self.student.exams))
        for row, exam in enumerate(self.student.exams):
            # Date
            date_str = exam.exam_date.strftime("%d/%m/%Y") if hasattr(exam, 'exam_date') else "N/A"
            table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # Type
            exam_type = getattr(exam, 'exam_type', 'N/A')
            table.setItem(row, 1, QTableWidgetItem(exam_type))
            
            # Résultat
            result = "✅ RÉUSSI" if getattr(exam, 'passed', False) else "❌ ÉCHOUÉ"
            result_item = QTableWidgetItem(result)
            result_item.setForeground(QColor("#27ae60" if exam.passed else "#e74c3c"))
            table.setItem(row, 2, result_item)
            
            # Note
            score = getattr(exam, 'score', 'N/A')
            table.setItem(row, 3, QTableWidgetItem(str(score)))
            
            # Remarques
            notes = getattr(exam, 'notes', '') or ''
            table.setItem(row, 4, QTableWidgetItem(notes))
        
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #e74c3c;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(table)
        
        return widget
    
    def create_notes_tab(self):
        """Onglet Notes et remarques"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        notes_label = QLabel("📝 Notes et Remarques")
        notes_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(notes_label)
        
        notes_text = QTextEdit()
        notes_text.setPlainText(self.student.notes or "Aucune note disponible.")
        notes_text.setReadOnly(True)
        notes_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        layout.addWidget(notes_text)
        
        return widget
    
    def edit_student(self):
        """Ouvrir le dialogue de modification"""
        from src.views.widgets.students_enhanced import StudentDetailDialog
        dialog = StudentDetailDialog(self.student, self.parent())
        if dialog.exec():
            # Recharger les données
            self.student = StudentController.get_student_by_id(self.student.id)
            self.close()
            # Rouvrir avec nouvelles données
            new_dialog = StudentDetailViewDialog(self.student, self.parent())
            new_dialog.exec()
```

**Modification dans `StudentsEnhancedWidget.view_student()`**:

Remplacer:
```python
def view_student(self, student):
    """Voir les détails d'un élève"""
    # TODO: Créer une vue détaillée (historique, sessions, paiements)
    QMessageBox.information(self, "Détail Élève", 
                           f"Nom: {student.full_name}\n"
                           f"CIN: {student.cin}\n"
                           f"Téléphone: {student.phone}\n"
                           f"Statut: {student.status.value}\n"
                           f"Heures: {student.hours_completed}/{student.hours_planned}\n"
                           f"Solde: {student.balance:,.2f} DH")
```

Par:
```python
def view_student(self, student):
    """Voir les détails complets d'un élève"""
    dialog = StudentDetailViewDialog(student, self)
    dialog.exec()
```

---

### ✅ Amélioration #2: Gestion Photos de Profil (2h)

**Objectif**: Permettre l'upload, preview et suppression de photos

**Modifications dans `StudentDetailDialog.__init__()`**:

Ajouter:
```python
self.photo_path = None  # Pour stocker le chemin de la photo
```

**Ajouter dans `StudentDetailDialog.setup_ui()`** (avant les onglets):

```python
# Widget photo de profil
photo_widget = self.create_photo_widget()
layout.addWidget(photo_widget)
```

**Nouvelle méthode à ajouter dans `StudentDetailDialog`**:

```python
def create_photo_widget(self):
    """Widget pour gérer la photo de profil"""
    widget = QGroupBox("📷 Photo de Profil")
    layout = QVBoxLayout(widget)
    
    # Zone d'affichage
    self.photo_display = QLabel()
    self.photo_display.setFixedSize(160, 160)
    self.photo_display.setAlignment(Qt.AlignCenter)
    self.photo_display.setStyleSheet("""
        border: 3px dashed #3498db;
        border-radius: 80px;
        background-color: #ecf0f1;
    """)
    
    # Charger photo existante
    if self.student and self.student.photo_path and os.path.exists(self.student.photo_path):
        pixmap = QPixmap(self.student.photo_path)
        self.photo_display.setPixmap(
            pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        self.photo_display.setStyleSheet("""
            border: 3px solid #27ae60;
            border-radius: 80px;
        """)
        self.photo_path = self.student.photo_path
    else:
        self.photo_display.setText("👤\n\nPas de photo")
        self.photo_display.setStyleSheet("""
            border: 3px dashed #bdc3c7;
            border-radius: 80px;
            background-color: #ecf0f1;
            font-size: 50px;
            color: #95a5a6;
        """)
    
    layout.addWidget(self.photo_display, alignment=Qt.AlignCenter)
    
    # Boutons
    btn_layout = QHBoxLayout()
    
    upload_btn = QPushButton("📷 Choisir")
    upload_btn.clicked.connect(self.upload_photo)
    upload_btn.setStyleSheet("""
        QPushButton {
            background-color: #3498db;
            color: white;
            padding: 8px 15px;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
    """)
    upload_btn.setCursor(Qt.PointingHandCursor)
    
    remove_btn = QPushButton("🗑️")
    remove_btn.clicked.connect(self.remove_photo)
    remove_btn.setToolTip("Supprimer la photo")
    remove_btn.setFixedWidth(40)
    remove_btn.setStyleSheet("""
        QPushButton {
            background-color: #e74c3c;
            color: white;
            padding: 8px;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #c0392b;
        }
    """)
    remove_btn.setCursor(Qt.PointingHandCursor)
    
    btn_layout.addWidget(upload_btn)
    btn_layout.addWidget(remove_btn)
    
    layout.addLayout(btn_layout)
    
    widget.setStyleSheet("""
        QGroupBox {
            background-color: white;
            border: 2px solid #ecf0f1;
            border-radius: 10px;
            padding: 15px;
            font-weight: bold;
        }
    """)
    
    return widget

def upload_photo(self):
    """Upload d'une photo de profil"""
    filename, _ = QFileDialog.getOpenFileName(
        self,
        "Sélectionner une photo",
        "",
        "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
    )
    
    if not filename:
        return
    
    try:
        # Créer le dossier photos s'il n'existe pas
        photos_dir = "data/photos"
        os.makedirs(photos_dir, exist_ok=True)
        
        # Générer nom de fichier unique
        student_id = self.student.id if self.student else "new"
        timestamp = int(datetime.now().timestamp())
        ext = os.path.splitext(filename)[1]
        new_filename = f"{photos_dir}/student_{student_id}_{timestamp}{ext}"
        
        # Charger et redimensionner l'image
        pixmap = QPixmap(filename)
        if pixmap.isNull():
            QMessageBox.critical(self, "Erreur", "Format d'image non valide")
            return
        
        # Redimensionner à 300x300 max
        pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Sauvegarder
        if pixmap.save(new_filename):
            # Mettre à jour l'affichage
            self.photo_display.setPixmap(
                pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            self.photo_display.setStyleSheet("""
                border: 3px solid #27ae60;
                border-radius: 80px;
            """)
            
            # Stocker le chemin
            self.photo_path = new_filename
            
            QMessageBox.information(self, "Succès", "Photo ajoutée avec succès !")
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de la sauvegarde de l'image")
    
    except Exception as e:
        QMessageBox.critical(self, "Erreur", f"Erreur lors de l'upload:\n{str(e)}")

def remove_photo(self):
    """Supprimer la photo de profil"""
    reply = QMessageBox.question(
        self,
        "Confirmation",
        "Voulez-vous supprimer la photo de profil ?",
        QMessageBox.Yes | QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        self.photo_display.clear()
        self.photo_display.setText("👤\n\nPas de photo")
        self.photo_display.setStyleSheet("""
            border: 3px dashed #bdc3c7;
            border-radius: 80px;
            background-color: #ecf0f1;
            font-size: 50px;
            color: #95a5a6;
        """)
        self.photo_path = None
        QMessageBox.information(self, "Succès", "Photo supprimée")
```

**Modifier `StudentDetailDialog.save_student()`** pour inclure `photo_path`:

Ajouter dans le dictionnaire `data`:
```python
data = {
    # ... champs existants ...
    'photo_path': self.photo_path,  # ✅ NOUVEAU
}
```

---

Ce guide est très long. Voulez-vous que je :

1. **Continue avec toutes les améliorations** (fichier de 3000+ lignes)
2. **Crée un script Python qui applique automatiquement les modifications**
3. **Crée juste les fichiers de code prêts à copier-coller**

Quelle option préférez-vous ? 🚀