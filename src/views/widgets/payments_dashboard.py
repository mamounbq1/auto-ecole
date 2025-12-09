"""
Payments Dashboard Widget - Tableau de bord financier
Module de statistiques et visualisation des paiements
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGroupBox, QGridLayout, QProgressBar, QComboBox, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datetime import datetime, timedelta, date
from typing import Dict, List

from src.controllers.payment_controller import PaymentController
from src.controllers.student_controller import StudentController
from src.models import PaymentMethod
from src.views.widgets.common_widgets import create_center_header_widget


class PaymentsDashboard(QWidget):
    """Dashboard financier avec statistiques des paiements"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_period = "all"  # day, week, month, year, all
        self.setup_ui()
        self.load_all_stats()
    
    def setup_ui(self):
        """Configurer l'interface"""
        # Layout principal avec scroll
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #27ae60;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #229954;
            }
        """)
        
        # Widget de contenu
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # En-tête du centre (compact)
        center_header = create_center_header_widget(compact=True)
        content_layout.addWidget(center_header)
        
        # Header
        header = self.create_header()
        content_layout.addWidget(header)
        
        # Cartes statistiques principales (4 cartes)
        stats_grid = self.create_main_stats()
        content_layout.addWidget(stats_grid)
        
        # Détails (2 colonnes)
        details = self.create_details_section()
        content_layout.addWidget(details)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
    
    def create_header(self) -> QFrame:
        """Créer l'en-tête"""
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #229954);
                border-radius: 8px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Titre
        title = QLabel("💰 Tableau de Bord Financier")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Sélecteur période
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Aujourd'hui", "Cette semaine", "Ce mois", "Cette année", "Tous les paiements"])
        self.period_combo.setCurrentIndex(4)  # Par défaut: Tous les paiements
        self.period_combo.currentIndexChanged.connect(self.on_period_changed)
        self.period_combo.setFixedHeight(35)
        self.period_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: #2c3e50;
                padding: 5px 15px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 150px;
            }
        """)
        layout.addWidget(self.period_combo)
        
        return header
    
    def create_main_stats(self) -> QWidget:
        """Créer les cartes statistiques principales"""
        container = QWidget()
        layout = QGridLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 4 cartes vides (seront remplies dans load_all_stats)
        self.card_revenue = self.create_stat_card("💵 CHIFFRE D'AFFAIRES", "0 DH", "#27ae60")
        self.card_payments = self.create_stat_card("📝 NOMBRE PAIEMENTS", "0", "#3498db")
        self.card_avg = self.create_stat_card("📊 MONTANT MOYEN", "0 DH", "#9b59b6")
        self.card_pending = self.create_stat_card("⏳ EN ATTENTE", "0 DH", "#f39c12")
        
        layout.addWidget(self.card_revenue, 0, 0)
        layout.addWidget(self.card_payments, 0, 1)
        layout.addWidget(self.card_avg, 1, 0)
        layout.addWidget(self.card_pending, 1, 1)
        
        return container
    
    def create_stat_card(self, title: str, value: str, color: str) -> QFrame:
        """Créer une carte statistique"""
        card = QFrame()
        card.setFixedHeight(100)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid #ecf0f1;
                border-left: 6px solid {color};
                border-radius: 8px;
            }}
            QFrame:hover {{
                border: 2px solid {color};
                border-left: 6px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        
        # Titre
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(9)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(title_label)
        
        # Valeur
        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        layout.addStretch()
        
        return card
    
    def create_details_section(self) -> QWidget:
        """Créer la section détails (2 colonnes)"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Colonne gauche
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Répartition par méthode
        self.methods_group = self.create_group("💳 Répartition par Méthode")
        left_layout.addWidget(self.methods_group)
        
        # Répartition par catégorie
        self.categories_group = self.create_group("📚 Répartition par Catégorie")
        left_layout.addWidget(self.categories_group)
        
        left_layout.addStretch()
        layout.addWidget(left)
        
        # Colonne droite
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setSpacing(15)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Top élèves payeurs
        self.top_students_group = self.create_group("🏆 Top Élèves Payeurs")
        right_layout.addWidget(self.top_students_group)
        
        # Statistiques supplémentaires
        self.extra_stats_group = self.create_group("📈 Statistiques")
        right_layout.addWidget(self.extra_stats_group)
        
        right_layout.addStretch()
        layout.addWidget(right)
        
        return container
    
    def create_group(self, title: str) -> QGroupBox:
        """Créer un groupe avec titre"""
        group = QGroupBox(title)
        group.setMinimumHeight(200)
        group.setMaximumHeight(300)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        return group
    
    def update_card_value(self, card: QFrame, new_value: str):
        """Mettre à jour la valeur d'une carte"""
        value_label = card.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(new_value)
    
    def load_all_stats(self):
        """Charger toutes les statistiques (EXCLUT paiements annulés)"""
        start_date, end_date = self.get_date_range()
        
        # Récupérer tous les paiements
        all_payments = PaymentController.get_all_payments()
        
        # Filtrer par période ET exclure annulés
        payments = [
            p for p in all_payments
            if p.payment_date and start_date <= p.payment_date <= end_date
            and not p.is_cancelled  # IMPORTANT: Exclure annulés
        ]
        
        # Calculs principaux (convertir Decimal en float)
        total_revenue = sum(float(p.amount) for p in payments)
        total_payments = len(payments)
        avg_payment = total_revenue / total_payments if total_payments > 0 else 0
        
        # Paiements en attente (non validés ET non annulés)
        pending_payments = [p for p in payments if not p.is_validated and not p.is_cancelled]
        pending_amount = sum(float(p.amount) for p in pending_payments)
        
        # Mettre à jour les cartes
        self.update_card_value(self.card_revenue, f"{total_revenue:,.2f} DH")
        self.update_card_value(self.card_payments, str(total_payments))
        self.update_card_value(self.card_avg, f"{avg_payment:,.2f} DH")
        self.update_card_value(self.card_pending, f"{pending_amount:,.2f} DH")
        
        # Charger détails
        self.load_methods_distribution(payments)
        self.load_categories_distribution(payments)
        self.load_top_students(payments)
        self.load_extra_stats(payments, start_date, end_date)
    
    def load_methods_distribution(self, payments: List):
        """Charger répartition par méthode de paiement"""
        layout = self.methods_group.layout()
        
        # Nettoyer
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Compter par méthode
        methods_count = {}
        methods_amount = {}
        total = len(payments)
        
        for p in payments:
            method = p.payment_method.value
            methods_count[method] = methods_count.get(method, 0) + 1
            methods_amount[method] = methods_amount.get(method, 0) + float(p.amount)
        
        # Mapping noms français
        method_labels = {
            'especes': '💵 Espèces',
            'carte_bancaire': '💳 Carte',
            'cheque': '📝 Chèque',
            'virement': '🏦 Virement',
            'mobile_money': '📱 Mobile Money'
        }
        
        # Afficher avec barres
        for method, count in sorted(methods_count.items(), key=lambda x: x[1], reverse=True):
            pct = int((count / total * 100)) if total > 0 else 0
            amount = methods_amount[method]
            
            label = QLabel(f"{method_labels.get(method, method)}: {count} ({amount:,.0f} DH)")
            label.setStyleSheet("color: #2c3e50; font-size: 11px;")
            layout.addWidget(label)
            
            bar = QProgressBar()
            bar.setValue(pct)
            bar.setFixedHeight(20)
            bar.setFormat(f"{pct}%")
            bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    background-color: #f5f5f5;
                    text-align: center;
                    color: #2c3e50;
                    font-weight: bold;
                    font-size: 10px;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #27ae60, stop:1 #229954);
                    border-radius: 3px;
                }
            """)
            layout.addWidget(bar)
        
        if not methods_count:
            no_data = QLabel("Aucun paiement")
            no_data.setStyleSheet("color: #95a5a6; font-style: italic;")
            layout.addWidget(no_data)
    
    def load_categories_distribution(self, payments: List):
        """Charger répartition par catégorie"""
        layout = self.categories_group.layout()
        
        # Nettoyer
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Compter par catégorie
        categories_amount = {}
        total_amount = sum(float(p.amount) for p in payments)
        
        for p in payments:
            cat = p.category or 'autre'
            categories_amount[cat] = categories_amount.get(cat, 0) + float(p.amount)
        
        # Mapping noms français
        category_labels = {
            'inscription': '📋 Inscription',
            'conduite': '🚗 Conduite',
            'examen_theorique': '📚 Examen Théorique',
            'examen_pratique': '🎯 Examen Pratique',
            'materiel_pedagogique': '📖 Matériel',
            'autre': '📦 Autre'
        }
        
        # Top 5 catégories
        for cat, amount in sorted(categories_amount.items(), key=lambda x: x[1], reverse=True)[:5]:
            pct = int((amount / total_amount * 100)) if total_amount > 0 else 0
            
            label = QLabel(f"{category_labels.get(cat, cat)}: {amount:,.0f} DH")
            label.setStyleSheet("color: #2c3e50; font-size: 11px;")
            layout.addWidget(label)
            
            bar = QProgressBar()
            bar.setValue(pct)
            bar.setFixedHeight(20)
            bar.setFormat(f"{pct}%")
            bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    background-color: #f5f5f5;
                    text-align: center;
                    color: #2c3e50;
                    font-weight: bold;
                    font-size: 10px;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #3498db, stop:1 #2980b9);
                    border-radius: 3px;
                }
            """)
            layout.addWidget(bar)
        
        if not categories_amount:
            no_data = QLabel("Aucune catégorie")
            no_data.setStyleSheet("color: #95a5a6; font-style: italic;")
            layout.addWidget(no_data)
    
    def load_top_students(self, payments: List):
        """Charger top élèves payeurs"""
        layout = self.top_students_group.layout()
        
        # Nettoyer
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Compter par élève
        student_amounts = {}
        for p in payments:
            student_amounts[p.student_id] = student_amounts.get(p.student_id, 0) + float(p.amount)
        
        # Récupérer infos élèves
        all_students = {s.id: s for s in StudentController.get_all_students()}
        
        # Top 5
        for i, (student_id, amount) in enumerate(sorted(student_amounts.items(), key=lambda x: x[1], reverse=True)[:5]):
            student = all_students.get(student_id)
            if not student:
                continue
            
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(0, 2, 0, 2)
            row.setSpacing(8)
            
            rank = QLabel(f"{i+1}.")
            rank.setFixedWidth(20)
            rank.setStyleSheet("color: #f39c12; font-weight: bold;")
            row.addWidget(rank)
            
            name = QLabel(student.full_name[:22])
            name.setStyleSheet("color: #2c3e50; font-size: 11px;")
            row.addWidget(name, stretch=1)
            
            amount_label = QLabel(f"{amount:,.0f} DH")
            amount_label.setFixedWidth(80)
            amount_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amount_label.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 11px;")
            row.addWidget(amount_label)
            
            layout.addWidget(row_widget)
        
        if not student_amounts:
            no_data = QLabel("Aucun paiement")
            no_data.setStyleSheet("color: #95a5a6; font-style: italic;")
            layout.addWidget(no_data)
    
    def load_extra_stats(self, payments: List, start_date: date, end_date: date):
        """Charger statistiques supplémentaires"""
        layout = self.extra_stats_group.layout()
        
        # Nettoyer
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        total_amount = sum(float(p.amount) for p in payments)
        total_count = len(payments)
        
        # Taux de validation (parmi les non annulés)
        validated = len([p for p in payments if p.is_validated and not p.is_cancelled])
        validation_rate = int((validated / total_count * 100)) if total_count > 0 else 0
        
        val_label = QLabel(f"Taux de Validation: {validation_rate}%")
        val_label.setStyleSheet("color: #2c3e50; font-size: 12px;")
        layout.addWidget(val_label)
        
        val_bar = QProgressBar()
        val_bar.setValue(validation_rate)
        val_bar.setFixedHeight(20)
        val_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #f5f5f5;
                text-align: center;
                color: #2c3e50;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #229954);
                border-radius: 3px;
            }
        """)
        layout.addWidget(val_bar)
        
        # Paiements par jour (moyenne)
        days = (end_date - start_date).days + 1
        avg_per_day = total_count / days if days > 0 else 0
        
        avg_day_label = QLabel(f"Moy. Paiements/Jour: {avg_per_day:.1f}")
        avg_day_label.setStyleSheet("color: #2c3e50; font-size: 12px; padding-top: 8px;")
        layout.addWidget(avg_day_label)
        
        # Revenu moyen par jour
        avg_revenue_day = total_amount / days if days > 0 else 0
        
        avg_rev_label = QLabel(f"Moy. Revenu/Jour: {avg_revenue_day:,.0f} DH")
        avg_rev_label.setStyleSheet("color: #2c3e50; font-size: 12px;")
        layout.addWidget(avg_rev_label)
    
    def on_period_changed(self, index: int):
        """Changement de période"""
        period_map = {0: "day", 1: "week", 2: "month", 3: "year", 4: "all"}
        self.current_period = period_map.get(index, "all")
        self.load_all_stats()
    
    def get_date_range(self) -> tuple:
        """Obtenir plage de dates selon période"""
        today = date.today()
        
        if self.current_period == "day":
            return today, today
        elif self.current_period == "week":
            days_since_monday = today.weekday()
            start = today - timedelta(days=days_since_monday)
            end = start + timedelta(days=6)
            return start, end
        elif self.current_period == "month":
            start = today.replace(day=1)
            if today.month == 12:
                end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            return start, end
        elif self.current_period == "year":
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
            return start, end
        else:  # all - Tous les paiements
            # Retourner une plage très large pour inclure tous les paiements
            start = date(2000, 1, 1)  # Début arbitraire très ancien
            end = date(2099, 12, 31)  # Fin arbitraire très future
            return start, end
