#!/usr/bin/env python3
"""
Lanceur de l'application Auto-École Manager sans console
Ce fichier .pyw lance l'application sans afficher la console Windows
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire du script au path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Supprimer les warnings matplotlib
os.environ['MPLBACKEND'] = 'Qt5Agg'
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', message='.*FigureCanvasQTAgg.*')

# Lancer l'application
if __name__ == '__main__':
    from src.main_gui import main
    main()
