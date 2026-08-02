"""Model danh mục dịch vụ, gói dịch vụ và lịch sử giá.

Có hai cơ chế độc lập cùng bảo vệ tính đúng đắn của hóa đơn cũ:
service_price_history trả lời "giá đã từng là bao nhiêu và ai đổi", còn
invoice_items chép cứng đơn giá để "hóa đơn đã phát hành không đổi số".
"""
import enum
from datetime import datetime

from backend.app.extensions import db


class ServiceCategory(enum.Enum):
    """Bốn danh mục dịch vụ theo mục 3.3 đặc tả."""

    TAM = 'tam'
    SPA = 'spa'
    GROOMING = 'grooming'
    KHAC = 'khac'


class Service(db.Model):
    """Một dịch vụ lẻ trong bảng giá."""

    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    category = db.Column(
        db.Enum(ServiceCategory, native_enum=False, validate_strings=True),
        nullable=False,
    )
    price = db.Column(db.Numeric(12, 2), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    price_history = db.relationship('ServicePriceHistory', back_populates='service')


class ServicePackage(db.Model):
    """Gói combo gồm nhiều dịch vụ với giá ưu đãi."""

    __tablename__ = 'service_packages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    package_price = db.Column(db.Numeric(12, 2), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    items = db.relationship('PackageItem', back_populates='package')


class PackageItem(db.Model):
    """Bảng nối n-n giữa gói dịch vụ và dịch vụ."""

    __tablename__ = 'package_items'

    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('service_packages.id'),
                           nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    package = db.relationship('ServicePackage', back_populates='items')
    service = db.relationship('Service')


class ServicePriceHistory(db.Model):
    """Lịch sử thay đổi giá dịch vụ.

    Mục 3.3 đặc tả yêu cầu lưu lịch sử thay vì sửa đè giá cũ. Không có bảng
    này thì giá cũ mất vĩnh viễn và không truy được ai đã đổi.
    """

    __tablename__ = 'service_price_history'

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    old_price = db.Column(db.Numeric(12, 2), nullable=False)
    new_price = db.Column(db.Numeric(12, 2), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changed_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    service = db.relationship('Service', back_populates='price_history')
    changed_by_user = db.relationship('User')
