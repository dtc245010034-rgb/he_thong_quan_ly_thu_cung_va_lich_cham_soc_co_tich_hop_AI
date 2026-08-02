"""Model hóa đơn, dòng hóa đơn và thanh toán."""
import enum
from datetime import datetime

from backend.app.extensions import db


class PaymentStatus(enum.Enum):
    """Trạng thái thanh toán của hóa đơn.

    Giá trị này được SUY RA từ tổng các dòng payments, không cho sửa tay
    (ràng buộc mục 5.3). Nếu cho sửa tay thì có thể ghi 'đã thanh toán đủ'
    trong khi chưa thu đồng nào, và số liệu công nợ mất hết ý nghĩa.
    """

    CHUA_THANH_TOAN = 'chua_thanh_toan'
    MOT_PHAN = 'mot_phan'
    DA_THANH_TOAN = 'da_thanh_toan'


class Invoice(db.Model):
    """Hóa đơn của một chủ nuôi.

    KHÔNG có cột appointment_id (sai khác ⑦). Mục 3.7 đặc tả yêu cầu lập
    hóa đơn từ một HOẶC NHIỀU lịch hẹn, nhưng một cột đơn ở đây chỉ diễn đạt
    được quan hệ 1-1. Cột đó nằm ở invoice_items, nơi mỗi dòng truy vết được
    về lịch hẹn sinh ra nó.
    """

    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=False)
    invoice_number = db.Column(db.String(32), unique=True, nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    discount_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_status = db.Column(
        db.Enum(PaymentStatus, native_enum=False, validate_strings=True),
        nullable=False,
        default=PaymentStatus.CHUA_THANH_TOAN,
    )
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    owner = db.relationship('Owner')
    creator = db.relationship('User')
    items = db.relationship('InvoiceItem', back_populates='invoice')
    payments = db.relationship('Payment', back_populates='invoice')


class InvoiceItem(db.Model):
    """Một dòng trên hóa đơn.

    unit_price và line_total được CHÉP CỨNG lúc lập hóa đơn, không tính lại
    lúc đọc (ràng buộc mục 5.3). Nhờ vậy khi quản lý đổi giá dịch vụ, các
    hóa đơn cũ không tự đổi số tiền.

    appointment_id rỗng được, để bán lẻ dịch vụ không qua đặt lịch vẫn ghi
    được. package_id dùng truy vết khi dòng này đến từ một gói combo đã bung
    ra thành các dịch vụ con.
    """

    __tablename__ = 'invoice_items'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'),
                               nullable=True)
    package_id = db.Column(db.Integer, db.ForeignKey('service_packages.id'),
                           nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    line_total = db.Column(db.Numeric(12, 2), nullable=False)

    invoice = db.relationship('Invoice', back_populates='items')
    service = db.relationship('Service')
    appointment = db.relationship('Appointment')
    package = db.relationship('ServicePackage')


class Payment(db.Model):
    """Một lần thu tiền.

    Một hóa đơn có nhiều dòng ở đây để hỗ trợ thanh toán từng phần.
    """

    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    method = db.Column(db.String(32), nullable=False)
    received_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    invoice = db.relationship('Invoice', back_populates='payments')
    received_by_user = db.relationship('User')
