"""
Widget de gestion des élèves
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton,
    QLineEdit, QComboBox, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.controllers import StudentController
from src.models import StudentStatus


class StudentsWidget(QWidget):
    """Widget de gestion des élèves"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.students = []
        self.setup_ui()
        self.load_students()
        
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        title = QLabel("👥 Gestion des Élèves")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Boutons d'action
        add_btn = QPushButton("➕ Nouvel Élève")
        add_btn.clicked.connect(self.add_student)
        add_btn.setStyleSheet("background-color: #3498db; color: white; padding: 8px 15px; border-radius: 5px; font-weight: bold;")
        add_btn.setCursor(Qt.PointingHandCursor)
        
        export_btn = QPushButton("📤 Exporter CSV")
        export_btn.clicked.connect(self.export_csv)
        export_btn.setStyleSheet("background-color: #1abc9c; color: white; padding: 8px 15px; border-radius: 5px; font-weight: bold;")
        export_btn.setCursor(Qt.PointingHandCursor)
        
        header_layout.addWidget(add_btn)
        header_layout.addWidget(export_btn)
        
        layout.addLayout(header_layout)
        
        # Barre de recherche et filtres
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par nom, CIN ou téléphone...")
        self.search_input.textChanged.connect(self.search_students)
        self.search_input.setMinimumHeight(35)
        
        self.status_filter = QComboBox()
        self.status_filter.addItem("Tous les statuts", None)
        for status in StudentStatus:
            self.status_filter.addItem(status.value.capitalize(), status)
        self.status_filter.currentIndexChanged.connect(self.filter_students)
        self.status_filter.setMinimumHeight(35)
        
        search_layout.addWidget(self.search_input, stretch=3)
        search_layout.addWidget(self.status_filter, stretch=1)
        
        layout.addLayout(search_layout)
        
        # Tableau des élèves
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom Complet", "CIN", "Téléphone", "Statut", 
            "Heures", "Solde (DH)", "Actions"
        ])
        
        # Configuration du tableau
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        
        # Style du tableau
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.table)
        
        # Statistiques en bas
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(self.stats_label)
        
    def load_students(self):
        """Charger tous les élèves"""
        self.students = StudentController.get_all_students()
        self.display_students(self.students)
        self.update_stats()
        
    def display_students(self, students):
        """Afficher les élèves dans le tableau"""
        self.table.setRowCount(0)
        
        for row, student in enumerate(students):
            self.table.insertRow(row)
            
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(student.id)))
            
            # Nom
            self.table.setItem(row, 1, QTableWidgetItem(student.full_name))
            
            # CIN
            self.table.setItem(row, 2, QTableWidgetItem(student.cin))
            
            # Téléphone
            self.table.setItem(row, 3, QTableWidgetItem(student.phone))
            
            # Statut avec couleur
            status_item = QTableWidgetItem(student.status.value.capitalize())
            if student.status == StudentStatus.ACTIVE:
                status_item.setForeground(Qt.darkGreen)
            elif student.status == StudentStatus.GRADUATED:
                status_item.setForeground(Qt.blue)
            else:
                status_item.setForeground(Qt.gray)
            self.table.setItem(row, 4, status_item)
            
            # Heures
            hours_text = f"{student.hours_completed}/{student.hours_planned}"
            self.table.setItem(row, 5, QTableWidgetItem(hours_text))
            
            # Solde avec couleur
            balance_item = QTableWidgetItem(f"{student.balance:,.0f}")
            if student.balance < 0:
                balance_item.setForeground(Qt.red)
            else:
                balance_item.setForeground(Qt.darkGreen)
            self.table.setItem(row, 6, balance_item)
            
            # Boutons d'action
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 0, 5, 0)
            
            view_btn = QPushButton("👁️")
            view_btn.setToolTip("Voir détails")
            view_btn.clicked.connect(lambda checked, s=student: self.view_student(s))
            view_btn.setCursor(Qt.PointingHandCursor)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Modifier")
            edit_btn.clicked.connect(lambda checked, s=student: self.edit_student(s))
            edit_btn.setCursor(Qt.PointingHandCursor)
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            
            self.table.setCellWidget(row, 7, actions_widget)
        
        # Ajuster les colonnes
        self.table.resizeColumnsToContents()
        
    def search_students(self, query):
        """Rechercher des élèves"""
        if not query:
            self.display_students(self.students)
            return
        
        results = StudentController.search_students(query)
        self.display_students(results)
        
    def filter_students(self, index):
        """Filtrer par statut"""
        status = self.status_filter.itemData(index)
        
        if status is None:
            filtered = self.students
        else:
            filtered = [s for s in self.students if s.status == status]
        
        self.display_students(filtered)
        
    def update_stats(self):
        """Mettre à jour les statistiques"""
        total = len(self.students)
        active = len([s for s in self.students if s.status == StudentStatus.ACTIVE])
        debt = len([s for s in self.students if s.balance < 0])
        
        self.stats_label.setText(
            f"📊 Total: {total} élèves | "
            f"✅ Actifs: {active} | "
            f"⚠️ En dette: {debt}"
        )
        
    def add_student(self):
        """Ajouter un nouvel élève"""
        QMessageBox.information(self, "Ajouter", "Formulaire d'ajout d'élève (à implémenter)")
        
    def view_student(self, student):
        """Voir les détails d'un élève"""
        QMessageBox.information(
            self,
            "Détails de l'élève",
            f"<b>Nom:</b> {student.full_name}<br>"
            f"<b>CIN:</b> {student.cin}<br>"
            f"<b>Téléphone:</b> {student.phone}<br>"
            f"<b>Statut:</b> {student.status.value}<br>"
            f"<b>Heures:</b> {student.hours_completed}/{student.hours_planned}<br>"
            f"<b>Solde:</b> {student.balance:,.0f} DH"
        )
        
    def edit_student(self, student):
        """Modifier un élève"""
        QMessageBox.information(self, "Modifier", f"Édition de {student.full_name} (à implémenter)")
        
    def export_csv(self):
        """Exporter en CSV"""
        success, filepath = StudentController.export_students_to_csv(self.students)
        
        if success:
            QMessageBox.information(self, "Export réussi", f"Fichier créé:\n{filepath}")
        else:
            QMessageBox.critical(self, "Erreur", f"Échec de l'export:\n{filepath}")
        
    def refresh(self):
        """Actualiser la liste"""
        self.load_students()
