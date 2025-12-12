"""
Modèles de données pour l'application Auto-École
"""

from sqlalchemy.orm import relationship

from .base import Base, get_engine, get_session, init_db
from .user import User, UserRole
from .role import Role, Permission, PermissionType, user_roles, role_permissions
from .student import Student, StudentStatus
from .instructor import Instructor
from .vehicle import Vehicle, VehicleStatus
from .session import Session, SessionType, SessionStatus
from .payment import Payment, PaymentMethod
from .exam import Exam, ExamType, ExamResult
from .maintenance import VehicleMaintenance, MaintenanceType, MaintenanceStatus
from .notification import Notification, NotificationType, NotificationCategory, NotificationStatus, NotificationPriority
from .document import Document, DocumentType, DocumentStatus

# Configurer la relation many-to-many entre User et Role après tous les imports
# Cela évite les imports circulaires
User.roles = relationship("Role", secondary=user_roles, back_populates="users", lazy="joined")

__all__ = [
    # Base
    'Base',
    'get_engine',
    'get_session',
    'init_db',
    # User
    'User',
    'UserRole',
    # Role & Permissions
    'Role',
    'Permission',
    'PermissionType',
    'user_roles',
    'role_permissions',
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
    # Notification
    'Notification',
    'NotificationType',
    'NotificationCategory',
    'NotificationStatus',
    'NotificationPriority',
    # Document
    'Document',
    'DocumentType',
    'DocumentStatus',
]
