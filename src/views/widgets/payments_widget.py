"""Widget Paiements - Version simplifiée"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from src.controllers import StudentController

class PaymentsWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("💰 Gestion des Paiements", styleSheet="font-size: 20px; font-weight: bold;"))
        
        # Afficher les élèves avec dette
        debt_students = StudentController.get_students_with_debt()
        
        info = QTextEdit()
        info.setReadOnly(True)
        
        text = f"<h3>⚠️ Élèves en dette ({len(debt_students)})</h3>"
        for student in debt_students[:20]:
            debt = abs(student.balance)
            text += f"<p><b>{student.full_name}</b> ({student.cin}): <span style='color:red;'>{debt:,.0f} DH</span></p>"
        
        info.setHtml(text)
        layout.addWidget(info)
    
    def refresh(self):
        pass
