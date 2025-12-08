"""
Utilitaires pour l'application Auto-École
"""

from .auth import AuthManager, login, logout, get_current_user, require_role
from .backup import BackupManager, create_backup, restore_backup, list_backups
from .export import ExportManager, export_to_csv, export_to_pdf, import_from_csv, get_export_manager
from .logger import setup_logger, get_logger
from .pdf_generator import PDFGenerator, get_pdf_generator
from .notifications import NotificationManager, get_notification_manager
from .config_manager import ConfigManager, get_config_manager

__all__ = [
    # Auth
    'AuthManager',
    'login',
    'logout',
    'get_current_user',
    'require_role',
    # Backup
    'BackupManager',
    'create_backup',
    'restore_backup',
    'list_backups',
    # Export
    'ExportManager',
    'export_to_csv',
    'export_to_pdf',
    'import_from_csv',
    'get_export_manager',
    # PDF
    'PDFGenerator',
    'get_pdf_generator',
    # Notifications
    'NotificationManager',
    'get_notification_manager',
    # Config Manager
    'ConfigManager',
    'get_config_manager',
    # Logger
    'setup_logger',
    'get_logger',
]
