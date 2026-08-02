"""Bốn bảng hệ thống: log AI, log thao tác, cấu hình ứng dụng, thông báo.

Cả bốn đều là bảng thêm so với mục 6.1 đặc tả, nhưng không bảng nào là
chức năng mới — mỗi bảng phục vụ một yêu cầu đã có sẵn ở phần khác của
đặc tả mà mục 6.1 chưa cấp bảng để lưu.
"""
from datetime import datetime

from backend.app.extensions import db


class AiInteractionLog(db.Model):
    """Log KỸ THUẬT của mọi lần gọi AI, kể cả lần lỗi.

    latency_ms và was_flagged phục vụ xử lý lỗi mục 8.4 và số liệu báo cáo
    KT3. Bảng này không lưu thông tin thanh toán và chỉ quản lý được xem
    (yêu cầu riêng tư mục 9).
    """

    __tablename__ = 'ai_interaction_logs'

    id = db.Column(db.Integer, primary_key=True)
    feature_type = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=True)
    prompt_input = db.Column(db.Text)
    ai_response = db.Column(db.Text)
    model_used = db.Column(db.String(64))
    latency_ms = db.Column(db.Integer)
    was_flagged = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user = db.relationship('User')
    pet = db.relationship('Pet')


class ActivityLog(db.Model):
    """Log NGHIỆP VỤ: ai làm gì, lúc nào, trên bản ghi nào.

    Mục 4 đặc tả yêu cầu log tạo/hủy lịch VÀ thanh toán. Bảng
    appointment_history chỉ phủ được lịch hẹn nên cần bảng dùng chung này.
    """

    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    actor_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(64), nullable=False)
    entity_type = db.Column(db.String(32))
    entity_id = db.Column(db.Integer)
    detail = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    actor = db.relationship('User')


class AppSetting(db.Model):
    """Cấu hình sửa được lúc chạy, dạng khóa-giá trị.

    Chứa ai_enabled và ai_model để quản lý bật/tắt và đổi model mà không
    phải khởi động lại ứng dụng (mục 3.1 đặc tả).

    KHÓA API KHÔNG BAO GIỜ LƯU Ở ĐÂY — chỉ đọc từ biến môi trường (mục 9).
    """

    __tablename__ = 'app_settings'

    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.String(255))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now,
                           onupdate=datetime.now)

    updated_by_user = db.relationship('User')


class Notification(db.Model):
    """Tin nhắn nhắc lịch đã sinh — dữ liệu NGHIỆP VỤ, không phải log.

    Chủ nuôi xem được các tin này ở cổng tự phục vụ, nên không thể dùng
    ai_interaction_logs (log kỹ thuật) làm chỗ chứa.

    Khóa duy nhất (pet_id, reminder_type, due_date) là thứ chặn job chạy
    hằng ngày gửi lặp một tin mỗi ngày cho cùng một lịch hẹn.
    """

    __tablename__ = 'notifications'
    __table_args__ = (
        db.UniqueConstraint('pet_id', 'reminder_type', 'due_date',
                            name='uq_nhac_lich_khong_trung'),
    )

    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=False)
    reminder_type = db.Column(db.String(32), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    channel = db.Column(db.String(16), nullable=False)
    message = db.Column(db.Text, nullable=False)
    urgency = db.Column(db.String(16), nullable=False)
    status = db.Column(db.String(16), nullable=False, default='da_tao')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    pet = db.relationship('Pet')
    owner = db.relationship('Owner')
