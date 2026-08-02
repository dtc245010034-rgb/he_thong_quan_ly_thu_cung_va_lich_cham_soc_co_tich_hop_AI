"""Gom toàn bộ model để import một chỗ.

Việc import ở đây cũng để SQLAlchemy biết đủ bảng khi gọi create_all().
"""
from backend.app.models.owner import Owner
from backend.app.models.pet import Pet
from backend.app.models.user import User, UserRole

__all__ = ['Owner', 'Pet', 'User', 'UserRole']
