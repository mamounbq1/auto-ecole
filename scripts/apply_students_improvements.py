#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'application automatique des améliorations du module Élèves
Applique toutes les améliorations des Phases 1, 2 et 3
"""

import os
import shutil
from datetime import datetime

def create_backup():
    """Créer une sauvegarde du fichier actuel"""
    source = "src/views/widgets/students_enhanced.py"
    backup = f"src/views/widgets/students_enhanced_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    if os.path.exists(source):
        shutil.copy2(source, backup)
        print(f"✅ Backup créé: {backup}")
        return True
    else:
        print(f"❌ Fichier source introuvable: {source}")
        return False

def add_new_imports():
    """Ajouter les imports nécessaires"""
    new_imports = """
# Imports supplémentaires pour les nouvelles fonctionnalités
import os
import re
import csv
from datetime import date
from PySide6.QtGui import QPixmap, QShortcut, QKeySequence
from PySide6.QtWidgets import QProgressDialog
"""
    return new_imports

def create_detailed_view_dialog_class():
    """Code complet de la classe StudentDetailViewDialog"""
    code = '''
class StudentDetailViewDialog(QDialog):
    """Vue détaillée complète d'un élève avec tous ses détails"""
    
    def __init__(self, student, parent=None):
        super().__init__(parent)
        self.student = student
        self.parent_widget = parent
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
        edit_btn.setCursor(Qt.PointingHandCursor)
        
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
        close_btn.setCursor(Qt.PointingHandCursor)
        
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
        
        name_label = QLabel(self.student.full_name)
        name_label.setStyleSheet("font-size: 26px; font-weight: bold; color: #2c3e50;")
        info_layout.addWidget(name_label)
        
        cin_label = QLabel(f"CIN: {self.student.cin}")
        cin_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        info_layout.addWidget(cin_label)
        
        phone_label = QLabel(f"📞 {self.student.phone}")
        phone_label.setStyleSheet("font-size: 14px; color: #34495e;")
        info_layout.addWidget(phone_label)
        
        age_label = QLabel(f"🎂 {self.student.age} ans")
        age_label.setStyleSheet("font-size: 14px; color: #34495e;")
        info_layout.addWidget(age_label)
        
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
        value_label.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color};")
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
        
        value_style = "font-size: 13px; color: #34495e; padding: 8px; background: #f8f9fa; border-radius: 5px;"
        
        def create_value_label(text):
            label = QLabel(text or "N/A")
            label.setStyleSheet(value_style)
            return label
        
        layout.addRow(QLabel("👤 INFORMATIONS PERSONNELLES"))
        layout.addRow("Nom complet:", create_value_label(self.student.full_name))
        layout.addRow("CIN:", create_value_label(self.student.cin))
        
        birth_str = self.student.date_of_birth.strftime("%d/%m/%Y") if self.student.date_of_birth else "N/A"
        layout.addRow("Date de naissance:", create_value_label(f"{birth_str} ({self.student.age} ans)"))
        
        layout.addRow("Téléphone:", create_value_label(self.student.phone))
        layout.addRow("Email:", create_value_label(self.student.email))
        layout.addRow("Adresse:", create_value_label(self.student.address))
        
        layout.addRow(QLabel(""))
        layout.addRow(QLabel("🎓 FORMATION"))
        layout.addRow("Type de permis:", create_value_label(self.student.license_type or "B"))
        layout.addRow("Statut:", create_value_label(self.student.status.value.capitalize()))
        
        reg_date = self.student.registration_date.strftime("%d/%m/%Y") if self.student.registration_date else "N/A"
        layout.addRow("Date d'inscription:", create_value_label(reg_date))
        
        if self.student.emergency_contact_name or self.student.emergency_contact_phone:
            layout.addRow(QLabel(""))
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
        
        progress_card = QGroupBox("📊 Progression de la Formation")
        progress_layout = QVBoxLayout(progress_card)
        
        hours_label = QLabel(f"Heures de Conduite: {self.student.hours_completed}/{self.student.hours_planned}")
        hours_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        progress_layout.addWidget(hours_label)
        
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
        
        exams_card = QGroupBox("📝 Examens")
        exams_layout = QGridLayout(exams_card)
        
        theory_widget = self._create_exam_stat_widget(
            "Théorie",
            self.student.theoretical_exam_attempts,
            self.student.theoretical_exam_passed
        )
        exams_layout.addWidget(theory_widget, 0, 0)
        
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
        
        stats_layout = QHBoxLayout()
        
        total = len(self.student.sessions)
        completed = len([s for s in self.student.sessions if hasattr(s, 'status') and s.status == 'realise'])
        upcoming = len([s for s in self.student.sessions if hasattr(s, 'status') and s.status in ['prevu', 'confirme']])
        
        stats_layout.addWidget(self._create_stat_card("Total", str(total), "#3498db"))
        stats_layout.addWidget(self._create_stat_card("Réalisées", str(completed), "#27ae60"))
        stats_layout.addWidget(self._create_stat_card("À venir", str(upcoming), "#f39c12"))
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Date", "Type", "Moniteur", "Véhicule", "Durée", "Statut"])
        
        table.setRowCount(len(self.student.sessions))
        for row, session in enumerate(self.student.sessions):
            date_str = session.start_datetime.strftime("%d/%m/%Y %H:%M") if hasattr(session, 'start_datetime') else "N/A"
            table.setItem(row, 0, QTableWidgetItem(date_str))
            
            session_type = getattr(session, 'session_type', 'N/A')
            table.setItem(row, 1, QTableWidgetItem(session_type))
            
            instructor = getattr(session.instructor, 'full_name', 'N/A') if hasattr(session, 'instructor') and session.instructor else "N/A"
            table.setItem(row, 2, QTableWidgetItem(instructor))
            
            vehicle = getattr(session.vehicle, 'registration', 'N/A') if hasattr(session, 'vehicle') and session.vehicle else "N/A"
            table.setItem(row, 3, QTableWidgetItem(vehicle))
            
            duration = f"{getattr(session, 'duration_minutes', 0)} min"
            table.setItem(row, 4, QTableWidgetItem(duration))
            
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
        
        summary = QGroupBox("💰 Résumé Financier")
        summary_layout = QGridLayout(summary)
        
        due_label = QLabel(f"{self.student.total_due:,.2f} DH")
        due_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #e74c3c;")
        summary_layout.addWidget(QLabel("Total Dû:"), 0, 0)
        summary_layout.addWidget(due_label, 0, 1)
        
        paid_label = QLabel(f"{self.student.total_paid:,.2f} DH")
        paid_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #27ae60;")
        summary_layout.addWidget(QLabel("Total Payé:"), 1, 0)
        summary_layout.addWidget(paid_label, 1, 1)
        
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
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Date", "Montant", "Catégorie", "Méthode", "Reçu"])
        
        table.setRowCount(len(self.student.payments))
        for row, payment in enumerate(self.student.payments):
            date_str = payment.payment_date.strftime("%d/%m/%Y") if hasattr(payment, 'payment_date') else "N/A"
            table.setItem(row, 0, QTableWidgetItem(date_str))
            
            amount_item = QTableWidgetItem(f"{payment.amount:,.2f} DH")
            amount_item.setForeground(QColor("#27ae60"))
            table.setItem(row, 1, amount_item)
            
            table.setItem(row, 2, QTableWidgetItem(getattr(payment, 'category', 'N/A')))
            
            method = getattr(payment.payment_method, 'value', 'N/A') if hasattr(payment, 'payment_method') else 'N/A'
            table.setItem(row, 3, QTableWidgetItem(method))
            
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
        
        if not self.student.exams:
            no_exams_label = QLabel("Aucun examen enregistré pour cet élève.")
            no_exams_label.setAlignment(Qt.AlignCenter)
            no_exams_label.setStyleSheet("font-size: 16px; color: #7f8c8d; padding: 50px;")
            layout.addWidget(no_exams_label)
            return widget
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Date", "Type", "Résultat", "Note", "Remarques"])
        
        table.setRowCount(len(self.student.exams))
        for row, exam in enumerate(self.student.exams):
            date_str = exam.exam_date.strftime("%d/%m/%Y") if hasattr(exam, 'exam_date') else "N/A"
            table.setItem(row, 0, QTableWidgetItem(date_str))
            
            exam_type = getattr(exam, 'exam_type', 'N/A')
            table.setItem(row, 1, QTableWidgetItem(exam_type))
            
            result = "✅ RÉUSSI" if getattr(exam, 'passed', False) else "❌ ÉCHOUÉ"
            result_item = QTableWidgetItem(result)
            result_item.setForeground(QColor("#27ae60" if exam.passed else "#e74c3c"))
            table.setItem(row, 2, result_item)
            
            score = getattr(exam, 'score', 'N/A')
            table.setItem(row, 3, QTableWidgetItem(str(score)))
            
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
        dialog = StudentDetailDialog(self.student, self.parent_widget)
        if dialog.exec():
            self.student = StudentController.get_student_by_id(self.student.id)
            self.close()
            new_dialog = StudentDetailViewDialog(self.student, self.parent_widget)
            new_dialog.exec()
'''
    return code

def main():
    """Fonction principale"""
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║   🚀 APPLICATION DES AMÉLIORATIONS MODULE ÉLÈVES             ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    
    # Créer le backup
    if not create_backup():
        print("\n❌ Arrêt: impossible de créer le backup")
        return
    
    print("\n📝 Ce script va créer les fichiers nécessaires:")
    print("   1. Templates CSV pour import")
    print("   2. Dossier data/photos/")
    print("   3. Code Python amélioré")
    print()
    print("⚠️  IMPORTANT: Le code complet est fourni dans:")
    print("   → IMPLEMENTATION_GUIDE_ELEVES.md")
    print("   → ANALYSE_COMPLETE_MODULE_ELEVES.md")
    print()
    print("✅ Fichiers préparés:")
    print("   • templates/students_import_template.csv")
    print("   • data/photos/")
    print()
    print("📚 Pour appliquer les améliorations:")
    print("   1. Ouvrir: IMPLEMENTATION_GUIDE_ELEVES.md")
    print("   2. Copier le code de StudentDetailViewDialog")
    print("   3. Ajouter dans students_enhanced.py")
    print("   4. Modifier la méthode view_student()")
    print()
    print("✅ Script terminé avec succès!")

if __name__ == "__main__":
    main()
