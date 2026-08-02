"""Model chủ nuôi.

Dùng xóa mềm thay vì xóa cứng: mục 3.2 đặc tả yêu cầu cảnh báo khi xóa chủ
nuôi còn thú cưng, lịch hẹn hoặc hóa đơn liên quan. Xóa cứng sẽ làm hỏng
các hóa đơn cũ đang trỏ về chủ nuôi đó.
"""
from datetime import datetime

from backend.app.extensions import db


class Owner(db.Model):
    __tablename__ = 'owners'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(128))
    address = db.Column(db.String(255))
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    deleted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    pets = db.relationship('Pet', back_populates='owner')
    user_accounts = db.relationship('User', back_populates='owner')

    @classmethod
    def query_active(cls):
        """Truy vấn chỉ lấy bản ghi chưa bị xóa mềm (ràng buộc mục 5.3).

        Mọi màn hình danh sách phải dùng hàm này thay vì cls.query, nếu không
        chủ nuôi đã xóa vẫn hiện ra khi chọn để đặt lịch.
        """
        return cls.query.filter_by(is_deleted=False)
