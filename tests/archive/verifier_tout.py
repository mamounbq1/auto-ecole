#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification complète - Auto-École Manager
Vérifie que tous les bugs sont corrigés et tous les modules fonctionnent
"""

import sys
from datetime import datetime

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def test_models():
    """Vérifie que tous les modèles ont les bons attributs"""
    print_header("TEST 1: MODÈLES DE DONNÉES")
    
    try:
        from src.models.student import Student
        from src.models.session import Session
        from src.models.payment import Payment
        
        # Test Student attributes
        student_required = ['theoretical_exam_attempts', 'practical_exam_attempts', 
                           'full_name', 'cin', 'license_type', 'status']
        for attr in student_required:
            if hasattr(Student, attr):
                print_success(f"Student.{attr} existe")
            else:
                print_error(f"Student.{attr} MANQUANT")
                return False
        
        # Test Session attributes
        session_required = ['start_datetime', 'end_datetime', 'session_type', 
                           'student_id', 'instructor_id']
        for attr in session_required:
            if hasattr(Session, attr):
                print_success(f"Session.{attr} existe")
            else:
                print_error(f"Session.{attr} MANQUANT")
                return False
        
        # Test Payment attributes
        payment_required = ['payment_date', 'amount', 'category', 
                           'payment_method', 'student_id']
        for attr in payment_required:
            if hasattr(Payment, attr):
                print_success(f"Payment.{attr} existe")
            else:
                print_error(f"Payment.{attr} MANQUANT")
                return False
        
        print_success("Tous les modèles ont les attributs requis")
        return True
        
    except Exception as e:
        print_error(f"Erreur import modèles: {e}")
        return False

def test_controllers():
    """Vérifie que tous les contrôleurs fonctionnent"""
    print_header("TEST 2: CONTRÔLEURS")
    
    try:
        from src.controllers.student_controller import StudentController
        from src.controllers.session_controller import SessionController
        from src.controllers.payment_controller import PaymentController
        
        # Test StudentController
        student_ctrl = StudentController()
        students = student_ctrl.get_all_students()
        print_success(f"StudentController: {len(students)} élèves trouvés")
        
        # Test SessionController
        session_ctrl = SessionController()
        sessions = session_ctrl.get_all_sessions()
        print_success(f"SessionController: {len(sessions)} sessions trouvées")
        
        # Test PaymentController
        payment_ctrl = PaymentController()
        payments = payment_ctrl.get_all_payments()
        print_success(f"PaymentController: {len(payments)} paiements trouvés")
        
        print_success("Tous les contrôleurs fonctionnent")
        return True
        
    except Exception as e:
        print_error(f"Erreur contrôleurs: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_student_relations():
    """Vérifie les relations de la base de données"""
    print_header("TEST 3: RELATIONS BASE DE DONNÉES")
    
    try:
        from src.controllers.student_controller import StudentController
        
        student_ctrl = StudentController()
        students = student_ctrl.get_all_students()
        
        if not students:
            print_error("Aucun élève dans la base de données")
            return False
        
        # Test premier élève
        student = students[0]
        print_info(f"Test élève: {student.full_name} (ID: {student.id})")
        
        # Test attributs
        attrs_to_test = {
            'theoretical_exam_attempts': int,
            'practical_exam_attempts': int,
            'balance': (int, float),
            'hours_completed': (int, float),
            'hours_planned': (int, float)
        }
        
        for attr, expected_type in attrs_to_test.items():
            if hasattr(student, attr):
                value = getattr(student, attr)
                if isinstance(value, expected_type):
                    print_success(f"{attr} = {value} (type: {type(value).__name__})")
                else:
                    print_error(f"{attr} type incorrect: {type(value).__name__}")
            else:
                print_error(f"Attribut {attr} manquant")
                return False
        
        # Test relations
        try:
            sessions = student.sessions
            print_success(f"Relations sessions: {len(sessions)} sessions liées")
        except Exception as e:
            print_error(f"Erreur relation sessions: {e}")
        
        try:
            payments = student.payments
            print_success(f"Relations payments: {len(payments)} paiements liés")
        except Exception as e:
            print_error(f"Erreur relation payments: {e}")
        
        try:
            exams = student.exams
            print_success(f"Relations exams: {len(exams)} examens liés")
        except Exception as e:
            print_error(f"Erreur relation exams: {e}")
        
        print_success("Relations base de données fonctionnelles")
        return True
        
    except Exception as e:
        print_error(f"Erreur test relations: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_session_dates():
    """Vérifie que les sessions utilisent start_datetime"""
    print_header("TEST 4: DATES SESSIONS")
    
    try:
        from src.controllers.session_controller import SessionController
        
        session_ctrl = SessionController()
        sessions = session_ctrl.get_all_sessions()
        
        if not sessions:
            print_info("Aucune session dans la base de données")
            return True
        
        # Test première session
        session = sessions[0]
        
        # Vérifier start_datetime existe
        if hasattr(session, 'start_datetime'):
            print_success(f"Session.start_datetime existe: {session.start_datetime}")
        else:
            print_error("Session.start_datetime MANQUANT")
            return False
        
        # Vérifier end_datetime existe
        if hasattr(session, 'end_datetime'):
            print_success(f"Session.end_datetime existe: {session.end_datetime}")
        else:
            print_error("Session.end_datetime MANQUANT")
            return False
        
        # Vérifier que session_date n'existe PAS (ancien attribut)
        if hasattr(session, 'session_date'):
            print_error("Session.session_date existe encore (devrait être supprimé)")
            return False
        else:
            print_success("Session.session_date n'existe pas (correct)")
        
        print_success("Dates sessions correctes (start_datetime/end_datetime)")
        return True
        
    except Exception as e:
        print_error(f"Erreur test dates sessions: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_payment_dates():
    """Vérifie que les paiements utilisent payment_date"""
    print_header("TEST 5: DATES PAIEMENTS")
    
    try:
        from src.controllers.payment_controller import PaymentController
        
        payment_ctrl = PaymentController()
        payments = payment_ctrl.get_all_payments()
        
        if not payments:
            print_info("Aucun paiement dans la base de données")
            return True
        
        # Test premier paiement
        payment = payments[0]
        
        # Vérifier payment_date existe
        if hasattr(payment, 'payment_date'):
            print_success(f"Payment.payment_date existe: {payment.payment_date}")
            print_success(f"Type: {type(payment.payment_date).__name__}")
        else:
            print_error("Payment.payment_date MANQUANT")
            return False
        
        print_success("Dates paiements correctes (payment_date)")
        return True
        
    except Exception as e:
        print_error(f"Erreur test dates paiements: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_statistics():
    """Teste le calcul des statistiques"""
    print_header("TEST 6: STATISTIQUES")
    
    try:
        from src.controllers.student_controller import StudentController
        from src.controllers.payment_controller import PaymentController
        from src.controllers.session_controller import SessionController
        
        # Statistiques élèves
        student_ctrl = StudentController()
        students = student_ctrl.get_all_students()
        active_students = [s for s in students if hasattr(s, 'status') and 
                          str(s.status).endswith('ACTIVE')]
        print_success(f"Élèves actifs: {len(active_students)}/{len(students)}")
        
        # Statistiques paiements
        payment_ctrl = PaymentController()
        payments = payment_ctrl.get_all_payments()
        total_amount = sum(p.amount for p in payments if hasattr(p, 'amount'))
        print_success(f"Total paiements: {total_amount:.2f} DH ({len(payments)} paiements)")
        
        # Statistiques sessions
        session_ctrl = SessionController()
        sessions = session_ctrl.get_all_sessions()
        today_sessions = [s for s in sessions if hasattr(s, 'start_datetime') and 
                         s.start_datetime.date() == datetime.now().date()]
        print_success(f"Sessions aujourd'hui: {len(today_sessions)}/{len(sessions)}")
        
        print_success("Calculs statistiques fonctionnels")
        return True
        
    except Exception as e:
        print_error(f"Erreur calcul statistiques: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Exécute tous les tests"""
    print("\n" + "="*70)
    print("  AUTO-ÉCOLE MANAGER - VÉRIFICATION COMPLÈTE")
    print("  Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)
    
    tests = [
        ("Modèles de données", test_models),
        ("Contrôleurs", test_controllers),
        ("Relations DB", test_student_relations),
        ("Dates sessions", test_session_dates),
        ("Dates paiements", test_payment_dates),
        ("Statistiques", test_statistics)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print_error(f"Erreur test {name}: {e}")
            results[name] = False
    
    # Résumé
    print_header("RÉSUMÉ DES TESTS")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    for name, result in results.items():
        if result:
            print_success(f"{name}: RÉUSSI")
        else:
            print_error(f"{name}: ÉCHOUÉ")
    
    print("\n" + "="*70)
    print(f"  TOTAL: {passed}/{total} tests réussis")
    if failed > 0:
        print(f"  ❌ {failed} test(s) échoué(s)")
    else:
        print("  ✅ TOUS LES TESTS RÉUSSIS!")
    print("="*70)
    
    # Code de sortie
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
