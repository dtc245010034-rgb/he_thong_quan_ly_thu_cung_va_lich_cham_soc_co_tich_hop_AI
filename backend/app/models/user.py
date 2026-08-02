"""Model tài khoản đăng nhập.

Một bảng users duy nhất cho cả 4 vai trò, kể cả chủ nuôi — nhờ vậy chỉ có
một luồng đăng nhập và một chỗ kiểm tra quyền (thiết kế mục 9, sai khác ①).
"""
import enum
from datetime import datetime

from backend.app.extensions import db


class UserRole(enum.Enum):
    """Bốn vai trò của hệ thống."""

    ADMIN = 'admin'
    RECEPTIONIST = 'receptionist'
    STAFF = 'staff'
    OWNER = 'owner'


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # native_enum=False sinh ràng buộc CHECK trên SQLite, chặn được text tự do.
    role = db.Column(
        db.Enum(UserRole, native_enum=False, validate_strings=True),
        nullable=False,
    )
    full_name = db.Column(db.String(128))
    # Rỗng với nhân viên; trỏ về hồ sơ chủ nuôi với vai trò owner.
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    owner = db.relationship('Owner', back_populates='user_accounts')
