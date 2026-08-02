"""Model thú cưng.

Hai cột ai_summary_cache và ai_summary_cached_at phục vụ chức năng tóm tắt
AI ở KT3: cache có hạn 24 giờ và bị xóa khi có hồ sơ chăm sóc mới, để việc
tải lại màn hình nhiều lần không gọi lại API.
"""
from datetime import datetime

from backend.app.extensions import db


class Pet(db.Model):
    __tablename__ = 'pets'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    species = db.Column(db.String(32), nullable=False)
    breed = db.Column(db.String(64))
    gender = db.Column(db.String(16))
    birth_date = db.Column(db.Date)
    weight = db.Column(db.Numeric(6, 2))
    color = db.Column(db.String(32))
    photo_url = db.Column(db.String(255))
    notes = db.Column(db.Text)
    ai_summary_cache = db.Column(db.Text)
    ai_summary_cached_at = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    deleted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    owner = db.relationship('Owner', back_populates='pets')

    @classmethod
    def query_active(cls):
        """Truy vấn chỉ lấy thú cưng chưa bị xóa mềm (ràng buộc mục 5.3)."""
        return cls.query.filter_by(is_deleted=False)
