"""
Script to verify all imports work correctly (without GUI)
"""

import sys
from pathlib import Path

print("="*80)
print("🔍 CHECKING IMPORTS - Auto-École Manager")
print("="*80)

errors = []
warnings = []

# Test 1: Core models
print("\n1. Testing core models...")
try:
    from src.models import (
        Base, get_engine, get_session, init_db,
        User, UserRole,
        Student, StudentStatus,
        Instructor,
        Vehicle, VehicleStatus,
        Session, SessionType, SessionStatus,
        Payment, PaymentMethod,
        Exam, ExamType, ExamResult
    )
    print("   ✅ All models imported successfully")
except Exception as e:
    errors.append(f"Models import error: {e}")
    print(f"   ❌ Error: {e}")

# Test 2: Controllers
print("\n2. Testing controllers...")
try:
    from src.controllers import (
        StudentController,
        InstructorController,
        VehicleController,
        SessionController,
        PaymentController,
        ExamController
    )
    print("   ✅ All controllers imported successfully")
except Exception as e:
    errors.append(f"Controllers import error: {e}")
    print(f"   ❌ Error: {e}")

# Test 3: Utils
print("\n3. Testing utilities...")
try:
    from src.utils import (
        get_logger,
        login, logout, get_current_user,
        create_backup, list_backups,
        export_to_csv
    )
    print("   ✅ All utilities imported successfully")
except Exception as e:
    errors.append(f"Utils import error: {e}")
    print(f"   ❌ Error: {e}")

# Test 4: PDF Generator
print("\n4. Testing PDF generator...")
try:
    from src.utils.pdf_generator import PDFGenerator
    print("   ✅ PDF generator imported successfully")
except Exception as e:
    errors.append(f"PDF generator import error: {e}")
    print(f"   ❌ Error: {e}")

# Test 5: Notification Manager
print("\n5. Testing notification manager...")
try:
    from src.utils import NotificationManager, get_notification_manager
    print("   ✅ Notification manager imported successfully")
except Exception as e:
    errors.append(f"Notification manager import error: {e}")
    print(f"   ❌ Error: {e}")

# Test 6: Database session
print("\n6. Testing database session...")
try:
    from src.models import get_session
    session = get_session()
    session.close()
    print("   ✅ Database session created successfully")
except Exception as e:
    errors.append(f"Database session error: {e}")
    print(f"   ❌ Error: {e}")

# Test 7: Controllers functionality
print("\n7. Testing controllers functionality...")
try:
    students = StudentController.get_all_students()
    instructors = InstructorController.get_all_instructors()
    vehicles = VehicleController.get_all_vehicles()
    exams = ExamController.get_all_exams()
    print(f"   ✅ Controllers functional:")
    print(f"      - Students: {len(students)}")
    print(f"      - Instructors: {len(instructors)}")
    print(f"      - Vehicles: {len(vehicles)}")
    print(f"      - Exams: {len(exams)}")
except Exception as e:
    errors.append(f"Controllers functionality error: {e}")
    print(f"   ❌ Error: {e}")

# GUI imports (will fail in headless environment)
print("\n8. Testing GUI imports (may fail in headless mode)...")
try:
    # Don't actually import to avoid Qt errors
    import importlib.util
    import ast
    
    # Check if files exist
    gui_files = [
        'src/views/login_window.py',
        'src/views/main_window.py',
        'src/views/widgets/dashboard_advanced.py',
        'src/views/widgets/students_enhanced.py',
        'src/views/widgets/payments_enhanced.py',
        'src/views/widgets/planning_enhanced.py',
        'src/views/widgets/instructors_widget.py',
        'src/views/widgets/vehicles_widget.py',
        'src/views/widgets/exams_widget.py',
    ]
    
    missing_files = []
    import_issues = []
    
    for file_path in gui_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            # Check for common import issues
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check for non-existent imports
                if 'from src.database import' in content:
                    import_issues.append(f"{file_path}: uses 'src.database' (should be 'src.models')")
                if 'LicenseType' in content and 'LICENSE_TYPES' not in content:
                    import_issues.append(f"{file_path}: imports LicenseType (doesn't exist)")
                if 'PaymentCategory' in content and 'PAYMENT_CATEGORIES' not in content:
                    import_issues.append(f"{file_path}: imports PaymentCategory (doesn't exist)")
                if 'ExamStatus' in content:
                    import_issues.append(f"{file_path}: imports ExamStatus (should be ExamResult)")
                if 'ExamType.THEORY ' in content or 'ExamType.THEORY)' in content:
                    import_issues.append(f"{file_path}: uses ExamType.THEORY (should be ExamType.THEORETICAL)")
    
    if missing_files:
        errors.append(f"Missing GUI files: {missing_files}")
        print(f"   ❌ Missing files: {missing_files}")
    elif import_issues:
        errors.append(f"Import issues found: {import_issues}")
        print(f"   ❌ Import issues:")
        for issue in import_issues:
            print(f"      - {issue}")
    else:
        print(f"   ✅ All GUI files present ({len(gui_files)} files)")
        print(f"   ✅ No obvious import issues detected")
        warnings.append("GUI imports not fully tested (requires display)")
        
except Exception as e:
    warnings.append(f"GUI check error: {e}")
    print(f"   ⚠️  Warning: {e}")

# Summary
print("\n" + "="*80)
print("📊 SUMMARY")
print("="*80)

if not errors:
    print("✅ All critical imports working!")
    print(f"✨ Backend is fully functional")
else:
    print(f"❌ Found {len(errors)} error(s):")
    for error in errors:
        print(f"   - {error}")

if warnings:
    print(f"\n⚠️  {len(warnings)} warning(s):")
    for warning in warnings:
        print(f"   - {warning}")

print("\n" + "="*80)

# Exit code
sys.exit(0 if not errors else 1)
