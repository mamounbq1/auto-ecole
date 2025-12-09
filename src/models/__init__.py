"""
Modèles de données pour l'application Auto-École
"""

from .base import Base, get_engine, get_session, init_db
from .user import User, UserRole
from .student import Student, StudentStatus
from .instructor import Instructor
from .vehicle import Vehicle, VehicleStatus
from .session import Session, SessionType, SessionStatus
from .payment import Payment, PaymentMethod
from .exam import Exam, ExamType, ExamResult
from .maintenance import VehicleMaintenance, MaintenanceType, MaintenanceStatus

__all__ = [
    # Base
    'Base',
    'get_engine',
    'get_session',
    'init_db',
    # User
    'User',
    'UserRole',
    # Student
    'Student',
    'StudentStatus',
    # Instructor
    'Instructor',
    # Vehicle
    'Vehicle',
    'VehicleStatus',
    # Session
    'Session',
    'SessionType',
    'SessionStatus',
    # Payment
    'Payment',
    'PaymentMethod',
    # Exam
    'Exam',
    'ExamType',
    'ExamResult',
    # Maintenance
    'VehicleMaintenance',
    'MaintenanceType',
    'MaintenanceStatus',
]
