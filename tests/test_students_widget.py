#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test du widget Students pour identifier les erreurs"""

import sys
from pathlib import Path

# Configuration encodage Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from src.controllers.student_controller import StudentController
from src.models import StudentStatus

print("="*60)
print("  TEST WIDGET STUDENTS - Verification des donnees")
print("="*60)
print()

try:
    # Test 1: Controller
    print("1. Test StudentController...")
    students = StudentController.get_all_students()
    print(f"   [OK] {len(students)} etudiants recuperes")
    print()
    
    # Test 2: Données des étudiants
    print("2. Test structure des donnees...")
    if students:
        s = students[0]
        print(f"   Etudiant test: {s.full_name}")
        print(f"   - ID: {s.student_id}")
        print(f"   - CIN: {s.cin or 'N/A'}")
        print(f"   - Phone: {s.phone or 'N/A'}")
        print(f"   - License: {s.license_type or 'N/A'} (type: {type(s.license_type).__name__})")
        print(f"   - Status: {s.status} (type: {type(s.status).__name__})")
        
        # Test de conversion status
        if s.status:
            status_val = s.status.value if hasattr(s.status, 'value') else str(s.status)
            print(f"   - Status value: {status_val}")
            print(f"   - Status capitalized: {status_val.capitalize()}")
        
        print(f"   - Hours: {s.hours_completed}/{s.hours_planned}")
        print(f"   - Balance: {s.balance:,.2f} DH")
        print(f"   [OK] Structure correcte")
    print()
    
    # Test 3: Import du widget
    print("3. Test import StudentsEnhancedWidget...")
    try:
        from src.views.widgets.students_enhanced import StudentsEnhancedWidget
        print("   [OK] Widget importe avec succes")
    except Exception as e:
        print(f"   [ERREUR] Import widget: {e}")
        raise
    print()
    
    # Test 4: Création du widget
    print("4. Test creation du widget...")
    app = QApplication(sys.argv)
    
    class FakeUser:
        def __init__(self):
            self.user_id = 1
            self.username = "admin"
            self.role = "Admin"
    
    user = FakeUser()
    
    try:
        widget = StudentsEnhancedWidget(user)
        print("   [OK] Widget cree")
        print(f"   [OK] Table rows: {widget.table.rowCount()}")
        print()
    except Exception as e:
        print(f"   [ERREUR] Creation widget: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    print("="*60)
    print("  TOUS LES TESTS REUSSIS!")
    print("="*60)
    print()
    print("Le module Students peut fonctionner correctement!")
    print()

except Exception as e:
    print()
    print(f"[ERREUR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
