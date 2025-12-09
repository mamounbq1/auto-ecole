"""
Contrôleur pour les statistiques avancées
Phase 2 - Statistiques Avancées & Analytics
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, and_, extract, case
from collections import defaultdict

from src.models import (
    Student, StudentStatus,
    Session, SessionStatus,
    Payment, PaymentMethod,
    Exam, ExamType, ExamResult,
    Instructor,
    Vehicle,
    VehicleMaintenance,
    get_session
)
from src.utils import get_logger

logger = get_logger()


class StatisticsController:
    """Contrôleur centralisé pour toutes les statistiques avancées"""
    
    # ========== Statistiques Financières ==========
    
    @staticmethod
    def get_revenue_statistics(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Statistiques complètes sur les revenus
        
        Returns:
            Dict avec total, par méthode, par période, tendances
        """
        try:
            session = get_session()
            
            # Dates par défaut: dernier mois
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Query de base
            query = session.query(Payment).filter(
                and_(
                    Payment.date >= start_date,
                    Payment.date <= end_date
                )
            )
            
            payments = query.all()
            
            if not payments:
                return {
                    'total_revenue': 0.0,
                    'total_payments': 0,
                    'average_payment': 0.0,
                    'by_method': {},
                    'by_day': {},
                    'trend': 'stable'
                }
            
            # Total
            total_revenue = sum(p.amount for p in payments)
            total_payments = len(payments)
            average_payment = total_revenue / total_payments if total_payments > 0 else 0.0
            
            # Par méthode de paiement
            by_method = {}
            for method in PaymentMethod:
                method_payments = [p for p in payments if p.payment_method == method]
                by_method[method.value] = {
                    'count': len(method_payments),
                    'total': sum(p.amount for p in method_payments)
                }
            
            # Par jour
            by_day = {}
            for payment in payments:
                day_key = payment.date.strftime('%Y-%m-%d')
                if day_key not in by_day:
                    by_day[day_key] = {'count': 0, 'total': 0.0}
                by_day[day_key]['count'] += 1
                by_day[day_key]['total'] += payment.amount
            
            # Tendance (comparaison avec période précédente)
            period_days = (end_date - start_date).days
            previous_start = start_date - timedelta(days=period_days)
            previous_end = start_date - timedelta(days=1)
            
            previous_payments = session.query(Payment).filter(
                and_(
                    Payment.date >= previous_start,
                    Payment.date <= previous_end
                )
            ).all()
            
            previous_revenue = sum(p.amount for p in previous_payments)
            
            if previous_revenue > 0:
                change_percent = ((total_revenue - previous_revenue) / previous_revenue) * 100
                if change_percent > 10:
                    trend = f'hausse +{change_percent:.1f}%'
                elif change_percent < -10:
                    trend = f'baisse {change_percent:.1f}%'
                else:
                    trend = 'stable'
            else:
                trend = 'nouveau'
            
            return {
                'total_revenue': total_revenue,
                'total_payments': total_payments,
                'average_payment': average_payment,
                'by_method': by_method,
                'by_day': by_day,
                'previous_period_revenue': previous_revenue,
                'trend': trend,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques de revenus : {e}")
            return {}
    
    @staticmethod
    def get_expenses_statistics(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Statistiques sur les dépenses (maintenances véhicules)
        
        Returns:
            Dict avec total dépenses, par type, par véhicule
        """
        try:
            session = get_session()
            
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Query maintenances terminées dans la période
            maintenances = session.query(VehicleMaintenance).filter(
                and_(
                    VehicleMaintenance.completion_date.isnot(None),
                    VehicleMaintenance.completion_date >= start_date,
                    VehicleMaintenance.completion_date <= end_date
                )
            ).all()
            
            if not maintenances:
                return {
                    'total_expenses': 0.0,
                    'total_maintenances': 0,
                    'average_expense': 0.0,
                    'by_type': {},
                    'by_vehicle': {}
                }
            
            total_expenses = sum(m.total_cost for m in maintenances)
            total_maintenances = len(maintenances)
            average_expense = total_expenses / total_maintenances if total_maintenances > 0 else 0.0
            
            # Par type de maintenance
            by_type = {}
            for maintenance in maintenances:
                m_type = maintenance.maintenance_type.value
                if m_type not in by_type:
                    by_type[m_type] = {'count': 0, 'total': 0.0}
                by_type[m_type]['count'] += 1
                by_type[m_type]['total'] += maintenance.total_cost
            
            # Par véhicule
            by_vehicle = {}
            for maintenance in maintenances:
                vehicle_id = maintenance.vehicle_id
                if vehicle_id not in by_vehicle:
                    by_vehicle[vehicle_id] = {
                        'vehicle_plate': maintenance.vehicle.plate_number if maintenance.vehicle else 'N/A',
                        'count': 0,
                        'total': 0.0
                    }
                by_vehicle[vehicle_id]['count'] += 1
                by_vehicle[vehicle_id]['total'] += maintenance.total_cost
            
            return {
                'total_expenses': total_expenses,
                'total_maintenances': total_maintenances,
                'average_expense': average_expense,
                'by_type': by_type,
                'by_vehicle': by_vehicle,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques de dépenses : {e}")
            return {}
    
    @staticmethod
    def get_profit_statistics(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Statistiques de profit (revenus - dépenses)
        
        Returns:
            Dict avec profit net, marge, évolution
        """
        try:
            revenue_stats = StatisticsController.get_revenue_statistics(start_date, end_date)
            expenses_stats = StatisticsController.get_expenses_statistics(start_date, end_date)
            
            total_revenue = revenue_stats.get('total_revenue', 0.0)
            total_expenses = expenses_stats.get('total_expenses', 0.0)
            net_profit = total_revenue - total_expenses
            profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0.0
            
            return {
                'total_revenue': total_revenue,
                'total_expenses': total_expenses,
                'net_profit': net_profit,
                'profit_margin': profit_margin,
                'period': revenue_stats.get('period', {})
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques de profit : {e}")
            return {}
    
    # ========== Statistiques Élèves ==========
    
    @staticmethod
    def get_student_progression_statistics() -> Dict[str, Any]:
        """
        Statistiques de progression des élèves
        
        Returns:
            Dict avec progression moyenne, taux d'achèvement, distribution
        """
        try:
            session = get_session()
            students = session.query(Student).filter(
                Student.status.in_([StudentStatus.ACTIVE, StudentStatus.GRADUATED])
            ).all()
            
            if not students:
                return {
                    'total_students': 0,
                    'average_progress': 0.0,
                    'completion_rate': 0.0,
                    'by_status': {}
                }
            
            # Progression moyenne
            total_progress = sum(s.completion_rate for s in students)
            average_progress = total_progress / len(students) if students else 0.0
            
            # Taux d'achèvement (élèves qui ont terminé leur formation)
            completed_students = [s for s in students if s.completion_rate >= 100]
            completion_rate = (len(completed_students) / len(students) * 100) if students else 0.0
            
            # Distribution par statut
            by_status = {}
            for status in StudentStatus:
                count = len([s for s in students if s.status == status])
                by_status[status.value] = count
            
            # Distribution par tranche de progression
            progression_ranges = {
                '0-25%': 0,
                '25-50%': 0,
                '50-75%': 0,
                '75-100%': 0,
                '100%+': 0
            }
            
            for student in students:
                rate = student.completion_rate
                if rate < 25:
                    progression_ranges['0-25%'] += 1
                elif rate < 50:
                    progression_ranges['25-50%'] += 1
                elif rate < 75:
                    progression_ranges['50-75%'] += 1
                elif rate < 100:
                    progression_ranges['75-100%'] += 1
                else:
                    progression_ranges['100%+'] += 1
            
            return {
                'total_students': len(students),
                'average_progress': average_progress,
                'completion_rate': completion_rate,
                'completed_students': len(completed_students),
                'by_status': by_status,
                'by_progression_range': progression_ranges
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques de progression : {e}")
            return {}
    
    @staticmethod
    def get_exam_success_rate_statistics() -> Dict[str, Any]:
        """
        Statistiques de taux de réussite aux examens
        
        Returns:
            Dict avec taux de réussite global, par type d'examen
        """
        try:
            session = get_session()
            exams = session.query(Exam).filter(
                Exam.result.in_([ExamResult.PASSED, ExamResult.FAILED])
            ).all()
            
            if not exams:
                return {
                    'total_exams': 0,
                    'success_rate': 0.0,
                    'by_exam_type': {}
                }
            
            # Taux de réussite global
            passed_exams = [e for e in exams if e.result == ExamResult.PASSED]
            success_rate = (len(passed_exams) / len(exams) * 100) if exams else 0.0
            
            # Par type d'examen
            by_exam_type = {}
            for exam_type in ExamType:
                type_exams = [e for e in exams if e.exam_type == exam_type]
                type_passed = [e for e in type_exams if e.result == ExamResult.PASSED]
                
                by_exam_type[exam_type.value] = {
                    'total': len(type_exams),
                    'passed': len(type_passed),
                    'failed': len(type_exams) - len(type_passed),
                    'success_rate': (len(type_passed) / len(type_exams) * 100) if type_exams else 0.0
                }
            
            # Moyenne des scores (théorique uniquement)
            theory_exams = [e for e in exams if e.exam_type == ExamType.THEORY and e.theory_score is not None]
            average_theory_score = (
                sum(e.theory_score for e in theory_exams) / len(theory_exams)
            ) if theory_exams else 0.0
            
            return {
                'total_exams': len(exams),
                'passed_exams': len(passed_exams),
                'success_rate': success_rate,
                'by_exam_type': by_exam_type,
                'average_theory_score': average_theory_score
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques de réussite aux examens : {e}")
            return {}
    
    # ========== Statistiques Véhicules ==========
    
    @staticmethod
    def get_vehicle_utilization_statistics(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Statistiques d'utilisation des véhicules
        
        Returns:
            Dict avec heures d'utilisation, sessions, coûts par véhicule
        """
        try:
            session_db = get_session()
            
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Sessions dans la période
            sessions = session_db.query(Session).filter(
                and_(
                    Session.start_datetime >= datetime.combine(start_date, datetime.min.time()),
                    Session.start_datetime <= datetime.combine(end_date, datetime.max.time()),
                    Session.status == SessionStatus.COMPLETED,
                    Session.vehicle_id.isnot(None)
                )
            ).all()
            
            # Stats par véhicule
            by_vehicle = {}
            for session_obj in sessions:
                vehicle_id = session_obj.vehicle_id
                if vehicle_id not in by_vehicle:
                    by_vehicle[vehicle_id] = {
                        'vehicle_plate': session_obj.vehicle.plate_number if session_obj.vehicle else 'N/A',
                        'total_sessions': 0,
                        'total_hours': 0.0,
                        'total_km': 0.0
                    }
                
                by_vehicle[vehicle_id]['total_sessions'] += 1
                if session_obj.duration_hours:
                    by_vehicle[vehicle_id]['total_hours'] += session_obj.duration_hours
                if session_obj.distance_km:
                    by_vehicle[vehicle_id]['total_km'] += session_obj.distance_km
            
            # Coûts de maintenance par véhicule dans la période
            maintenances = session_db.query(VehicleMaintenance).filter(
                and_(
                    VehicleMaintenance.completion_date.isnot(None),
                    VehicleMaintenance.completion_date >= start_date,
                    VehicleMaintenance.completion_date <= end_date
                )
            ).all()
            
            for maintenance in maintenances:
                vehicle_id = maintenance.vehicle_id
                if vehicle_id in by_vehicle:
                    if 'maintenance_cost' not in by_vehicle[vehicle_id]:
                        by_vehicle[vehicle_id]['maintenance_cost'] = 0.0
                    by_vehicle[vehicle_id]['maintenance_cost'] += maintenance.total_cost
            
            return {
                'total_sessions': len(sessions),
                'by_vehicle': by_vehicle,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques d'utilisation des véhicules : {e}")
            return {}
    
    # ========== Statistiques Moniteurs ==========
    
    @staticmethod
    def get_instructor_performance_statistics(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Statistiques de performance des moniteurs
        
        Returns:
            Dict avec heures enseignées, élèves formés, taux de réussite par moniteur
        """
        try:
            session_db = get_session()
            
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Sessions terminées dans la période
            sessions = session_db.query(Session).filter(
                and_(
                    Session.start_datetime >= datetime.combine(start_date, datetime.min.time()),
                    Session.start_datetime <= datetime.combine(end_date, datetime.max.time()),
                    Session.status == SessionStatus.COMPLETED,
                    Session.instructor_id.isnot(None)
                )
            ).all()
            
            # Stats par moniteur
            by_instructor = {}
            for session_obj in sessions:
                instructor_id = session_obj.instructor_id
                if instructor_id not in by_instructor:
                    by_instructor[instructor_id] = {
                        'instructor_name': session_obj.instructor.full_name if session_obj.instructor else 'N/A',
                        'total_sessions': 0,
                        'total_hours': 0.0,
                        'unique_students': set()
                    }
                
                by_instructor[instructor_id]['total_sessions'] += 1
                if session_obj.duration_hours:
                    by_instructor[instructor_id]['total_hours'] += session_obj.duration_hours
                if session_obj.student_id:
                    by_instructor[instructor_id]['unique_students'].add(session_obj.student_id)
            
            # Convertir sets en counts
            for instructor_id in by_instructor:
                by_instructor[instructor_id]['unique_students'] = len(by_instructor[instructor_id]['unique_students'])
            
            return {
                'total_sessions': len(sessions),
                'by_instructor': by_instructor,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques de performance des moniteurs : {e}")
            return {}
    
    # ========== Dashboard Global ==========
    
    @staticmethod
    def get_global_dashboard_statistics(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Statistiques globales pour le dashboard principal
        
        Returns:
            Dict avec toutes les statistiques principales
        """
        try:
            return {
                'financial': {
                    'revenue': StatisticsController.get_revenue_statistics(start_date, end_date),
                    'expenses': StatisticsController.get_expenses_statistics(start_date, end_date),
                    'profit': StatisticsController.get_profit_statistics(start_date, end_date)
                },
                'students': {
                    'progression': StatisticsController.get_student_progression_statistics(),
                    'exams': StatisticsController.get_exam_success_rate_statistics()
                },
                'vehicles': StatisticsController.get_vehicle_utilization_statistics(start_date, end_date),
                'instructors': StatisticsController.get_instructor_performance_statistics(start_date, end_date),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des statistiques globales : {e}")
            return {}
