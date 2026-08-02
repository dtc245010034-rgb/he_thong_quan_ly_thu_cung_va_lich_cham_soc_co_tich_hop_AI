"""Model lịch hẹn, lịch sử đổi lịch, hồ sơ chăm sóc và lịch tiêm phòng."""
import enum
from datetime import datetime

from backend.app.extensions import db


class AppointmentStatus(enum.Enum):
    """Bốn trạng thái của lịch hẹn.

    KHÔNG có 'rescheduled' (sai khác ⑥ so với mục 3.4 đặc tả). Đổi lịch về
    bản chất là một sự kiện, và mục 3.4 đã yêu cầu lưu nó vào bảng lịch sử.
    Nếu vừa làm trạng thái vừa ghi lịch sử thì một buổi hẹn sinh nhiều dòng,
    mọi báo cáo phải nhớ loại trừ trạng thái này, rất dễ đếm trùng doanh thu.
    """

    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class Appointment(db.Model):
    """Một buổi hẹn dịch vụ.

    ends_at được tính và lưu lúc tạo lịch, không tính lại lúc đọc (sai khác
    ②). Hai lý do: truy vấn chống trùng thành một điều kiện đơn giản không
    cần join sang services; và nếu quản lý sửa duration_minutes sau này thì
    các lịch đã đặt không bị dịch chuyển ngầm.
    """

    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    # Rỗng nếu chưa phân công nhân viên; khi rỗng thì không kiểm tra trùng lịch.
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(
        db.Enum(AppointmentStatus, native_enum=False, validate_strings=True),
        nullable=False,
        default=AppointmentStatus.PENDING,
    )
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    pet = db.relationship('Pet')
    service = db.relationship('Service')
    staff = db.relationship('User', foreign_keys=[staff_id])
    creator = db.relationship('User', foreign_keys=[created_by])
    history = db.relationship('AppointmentHistory', back_populates='appointment')


class AppointmentHistory(db.Model):
    """Lịch sử đổi lịch.

    Bản ghi lịch hẹn được cập nhật tại chỗ, không tạo dòng mới; mỗi lần đổi
    ghi một dòng ở đây. Số lần đổi của một lịch hẹn đếm từ bảng này.
    """

    __tablename__ = 'appointment_history'

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'),
                               nullable=False)
    old_time = db.Column(db.DateTime, nullable=False)
    new_time = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changed_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    appointment = db.relationship('Appointment', back_populates='history')
    changed_by_user = db.relationship('User')


class CareRecord(db.Model):
    """Hồ sơ chăm sóc ghi sau mỗi buổi hẹn hoàn thành.

    record_date và weight_at_visit bắt buộc có: đây là hai trường có cấu trúc
    giúp AI ở KT3 so sánh được xu hướng cân nặng qua các lần khám, thay vì
    chỉ đọc ghi chú rời rạc.
    """

    __tablename__ = 'care_records'

    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    # Rỗng nếu ghi hồ sơ cho lần khám không qua đặt lịch.
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'),
                               nullable=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    record_date = db.Column(db.Date, nullable=False)
    weight_at_visit = db.Column(db.Numeric(6, 2), nullable=False)
    condition_notes = db.Column(db.Text)
    treatment_notes = db.Column(db.Text)
    next_recommendation = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    pet = db.relationship('Pet')
    appointment = db.relationship('Appointment')
    staff = db.relationship('User')


class VaccinationSchedule(db.Model):
    """Lịch tiêm phòng, chỉ ở mức nhắc lịch (mục 3.6 đặc tả).

    KHÔNG có cột status (sai khác ④). Bảng chỉ lưu is_done — trạng thái do
    người dùng gây ra. Hai giá trị "sắp đến hạn" và "quá hạn" phụ thuộc ngày
    hiện tại nên được tính lúc truy vấn từ next_due_date; lưu cứng thì hôm
    sau đã sai.
    """

    __tablename__ = 'vaccination_schedules'

    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    vaccine_name = db.Column(db.String(64), nullable=False)
    last_date = db.Column(db.Date)
    next_due_date = db.Column(db.Date, nullable=False)
    is_done = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    pet = db.relationship('Pet')
