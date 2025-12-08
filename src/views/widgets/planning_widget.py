"""Widget Planning - Version simplifiée"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCalendarWidget, QTextEdit
from PySide6.QtCore import Qt
from src.controllers import SessionController
from datetime import date

class PlanningWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("📅 Planning des Sessions", styleSheet="font-size: 20px; font-weight: bold;"))
        
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.show_sessions_for_date)
        layout.addWidget(self.calendar)
        
        self.sessions_display = QTextEdit()
        self.sessions_display.setReadOnly(True)
        self.sessions_display.setMaximumHeight(200)
        layout.addWidget(self.sessions_display)
        
        self.show_sessions_for_date(date.today())
        
    def show_sessions_for_date(self, selected_date):
        sessions = SessionController.get_sessions_by_date_range(selected_date, selected_date)
        
        text = f"<h3>Sessions du {selected_date.strftime('%d/%m/%Y')}</h3>"
        if sessions:
            for s in sessions:
                student_name = s.student.full_name if s.student else "N/A"
                instructor_name = s.instructor.full_name if s.instructor else "N/A"
                text += f"<p>🕐 <b>{s.start_datetime.strftime('%H:%M')}</b> - {student_name} avec {instructor_name}</p>"
        else:
            text += "<p><i>Aucune session programmée</i></p>"
        
        self.sessions_display.setHtml(text)
    
    def refresh(self):
        self.show_sessions_for_date(self.calendar.selectedDate().toPython())
