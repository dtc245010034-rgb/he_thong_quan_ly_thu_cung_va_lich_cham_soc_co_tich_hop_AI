"""Gom toàn bộ model để import một chỗ.

Việc import ở đây cũng để SQLAlchemy biết đủ bảng khi gọi create_all().
"""
from backend.app.models.appointment import (Appointment, AppointmentHistory,
                                            AppointmentStatus, CareRecord,
                                            VaccinationSchedule)
from backend.app.models.billing import (Invoice, InvoiceItem, Payment, PaymentStatus)
from backend.app.models.catalog import (PackageItem, Service, ServiceCategory,
                                        ServicePackage, ServicePriceHistory)
from backend.app.models.owner import Owner
from backend.app.models.pet import Pet
from backend.app.models.system import (ActivityLog, AiInteractionLog, AppSetting,
                                       Notification)
from backend.app.models.user import User, UserRole

__all__ = [
    'ActivityLog',
    'AiInteractionLog',
    'AppSetting',
    'Appointment',
    'AppointmentHistory',
    'AppointmentStatus',
    'CareRecord',
    'Invoice',
    'InvoiceItem',
    'Notification',
    'Owner',
    'PackageItem',
    'Payment',
    'PaymentStatus',
    'Pet',
    'Service',
    'ServiceCategory',
    'ServicePackage',
    'ServicePriceHistory',
    'User',
    'UserRole',
    'VaccinationSchedule',
]
