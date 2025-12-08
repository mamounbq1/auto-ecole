"""
Widget Rapports avec graphiques matplotlib
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QScrollArea, QFrame
from PySide6.QtCore import Qt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from src.controllers import StudentController, SessionController
from src.models import StudentStatus
from datetime import datetime, timedelta

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class ReportsWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("📈 Rapports et Statistiques", styleSheet="font-size: 20px; font-weight: bold; color: #2c3e50;"))
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Graphique 1: Distribution des élèves par statut
        self.create_students_chart(content_layout)
        
        # Graphique 2: Sessions par jour (7 derniers jours)
        self.create_sessions_chart(content_layout)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
    def create_students_chart(self, layout):
        """Graphique en camembert des statuts élèves"""
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px;")
        frame_layout = QVBoxLayout(frame)
        
        frame_layout.addWidget(QLabel("Distribution des Élèves par Statut", styleSheet="font-size: 16px; font-weight: bold;"))
        
        canvas = MplCanvas(self, width=6, height=4)
        students = StudentController.get_all_students()
        
        # Compter par statut
        status_counts = {}
        for student in students:
            status = student.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            canvas.axes.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%', startangle=90)
            canvas.axes.set_title('Répartition des élèves')
        
        frame_layout.addWidget(canvas)
        layout.addWidget(frame)
        
    def create_sessions_chart(self, layout):
        """Graphique en barres des sessions"""
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px; margin-top: 20px;")
        frame_layout = QVBoxLayout(frame)
        
        frame_layout.addWidget(QLabel("Sessions des 7 derniers jours", styleSheet="font-size: 16px; font-weight: bold;"))
        
        canvas = MplCanvas(self, width=6, height=4)
        
        # Données pour 7 jours
        days = []
        counts = []
        today = datetime.now().date()
        
        for i in range(7):
            day = today - timedelta(days=6-i)
            sessions = SessionController.get_sessions_by_date_range(day, day)
            days.append(day.strftime('%d/%m'))
            counts.append(len(sessions))
        
        canvas.axes.bar(days, counts, color='#3498db')
        canvas.axes.set_xlabel('Date')
        canvas.axes.set_ylabel('Nombre de sessions')
        canvas.axes.set_title('Activité quotidienne')
        
        frame_layout.addWidget(canvas)
        layout.addWidget(frame)
    
    def refresh(self):
        pass
