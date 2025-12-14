#!/usr/bin/env python3
"""
Application de génération de licences Auto-École Manager
Interface graphique pour le vendeur uniquement
"""

import sys
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QSpinBox, QMessageBox,
    QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.license_manager import get_license_manager


class LicenseGeneratorWindow(QMainWindow):
    """Fenêtre de génération de licences"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔐 Générateur de Licences - Auto-École Manager")
        self.setMinimumSize(700, 600)
        
        # Charger l'icône si disponible
        icon_path = Path(__file__).parent / "assets" / "app_icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configuration de l'interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Titre
        title = QLabel("🔐 Générateur de Licences")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Outil réservé au vendeur - Confidentiel")
        subtitle.setStyleSheet("color: #e74c3c; font-size: 12px; font-weight: bold;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Groupe informations client
        info_group = QGroupBox("📋 Informations du Client")
        info_group.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout = QFormLayout()
        
        self.hardware_id_input = QLineEdit()
        self.hardware_id_input.setPlaceholderText("ABC123-DEF456-789012")
        self.hardware_id_input.setFont(QFont("Courier New", 10))
        info_layout.addRow("Hardware ID :", self.hardware_id_input)
        
        self.client_name_input = QLineEdit()
        self.client_name_input.setPlaceholderText("Auto-École Rabat (optionnel)")
        info_layout.addRow("Nom du client :", self.client_name_input)
        
        self.duration_input = QSpinBox()
        self.duration_input.setMinimum(1)
        self.duration_input.setMaximum(36500)
        self.duration_input.setValue(365)
        self.duration_input.setSuffix(" jours")
        info_layout.addRow("Durée :", self.duration_input)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Bouton génération
        generate_btn = QPushButton("🔑 Générer la Licence")
        generate_btn.setFont(QFont("Arial", 14, QFont.Bold))
        generate_btn.setMinimumHeight(50)
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        generate_btn.clicked.connect(self.generate_license)
        layout.addWidget(generate_btn)
        
        # Groupe résultat
        result_group = QGroupBox("🔐 Clé de Licence Générée")
        result_group.setFont(QFont("Arial", 12, QFont.Bold))
        result_layout = QVBoxLayout()
        
        self.license_output = QTextEdit()
        self.license_output.setReadOnly(True)
        self.license_output.setFont(QFont("Courier New", 10))
        self.license_output.setPlaceholderText("La clé de licence apparaîtra ici...")
        self.license_output.setMinimumHeight(150)
        result_layout.addWidget(self.license_output)
        
        # Boutons action
        btn_layout = QHBoxLayout()
        
        copy_btn = QPushButton("📋 Copier")
        copy_btn.clicked.connect(self.copy_license)
        copy_btn.setMinimumHeight(40)
        btn_layout.addWidget(copy_btn)
        
        clear_btn = QPushButton("🗑️ Effacer")
        clear_btn.clicked.connect(self.clear_fields)
        clear_btn.setMinimumHeight(40)
        btn_layout.addWidget(clear_btn)
        
        result_layout.addLayout(btn_layout)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        # Info supplémentaire
        info_label = QLabel(
            "💡 <b>Instructions :</b><br>"
            "1. Le client vous envoie son Hardware ID depuis l'application<br>"
            "2. Entrez le Hardware ID ci-dessus<br>"
            "3. Choisissez la durée (365j = 1 an)<br>"
            "4. Cliquez sur 'Générer la Licence'<br>"
            "5. Copiez et envoyez la clé au client"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("background-color: #eaf2f8; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)
    
    def generate_license(self):
        """Générer une licence"""
        hardware_id = self.hardware_id_input.text().strip()
        
        if not hardware_id:
            QMessageBox.warning(self, "Erreur", "Le Hardware ID est obligatoire")
            return
        
        client_name = self.client_name_input.text().strip()
        duration = self.duration_input.value()
        
        try:
            # Générer la licence
            license_manager = get_license_manager()
            license_key = license_manager.generate_license(hardware_id, duration, client_name)
            
            # Afficher la clé
            output_text = (
                f"✅ Licence générée avec succès !\n\n"
                f"📋 Hardware ID : {hardware_id}\n"
                f"👤 Client : {client_name or 'Non spécifié'}\n"
                f"⏱️ Durée : {duration} jours\n"
                f"📅 Expire le : {(datetime.now().date() + __import__('datetime').timedelta(days=duration)).strftime('%d/%m/%Y')}\n\n"
                f"🔑 CLÉ DE LICENCE :\n"
                f"{'-' * 60}\n"
                f"{license_key}\n"
                f"{'-' * 60}\n\n"
                f"📧 À envoyer au client par email/WhatsApp"
            )
            
            self.license_output.setText(output_text)
            
            # Sauvegarder dans un fichier
            license_dir = Path(__file__).parent / "licenses_generated"
            license_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = license_dir / f"license_{hardware_id[:8]}_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(output_text)
                f.write(f"\n\nFichier généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")
            
            QMessageBox.information(
                self, 
                "Succès", 
                f"Licence générée avec succès !\n\n"
                f"Clé copiée dans le presse-papier.\n"
                f"Fichier sauvegardé : {filename.name}"
            )
            
            # Copier automatiquement
            self.copy_license()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération :\n{str(e)}")
    
    def copy_license(self):
        """Copier la licence dans le presse-papier"""
        text = self.license_output.toPlainText()
        if not text or "apparaîtra ici" in text:
            QMessageBox.warning(self, "Erreur", "Aucune licence à copier")
            return
        
        # Extraire seulement la clé
        lines = text.split('\n')
        key_started = False
        key_lines = []
        
        for line in lines:
            if '🔑 CLÉ DE LICENCE' in line:
                key_started = True
                continue
            if key_started:
                if line.startswith('-'):
                    if key_lines:  # Deuxième ligne de tirets = fin
                        break
                    continue
                if line.strip():
                    key_lines.append(line.strip())
        
        license_key = '\n'.join(key_lines)
        
        if license_key:
            QApplication.clipboard().setText(license_key)
            QMessageBox.information(self, "Succès", "Clé de licence copiée dans le presse-papier !")
    
    def clear_fields(self):
        """Effacer tous les champs"""
        self.hardware_id_input.clear()
        self.client_name_input.clear()
        self.duration_input.setValue(365)
        self.license_output.clear()


def main():
    """Fonction principale"""
    app = QApplication(sys.argv)
    app.setApplicationName("Générateur de Licences - Auto-École Manager")
    
    # Style
    app.setStyle("Fusion")
    
    window = LicenseGeneratorWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
