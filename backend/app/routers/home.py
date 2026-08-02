"""Trang chủ, hiển thị nội dung khác nhau theo vai trò.

Mỗi vai trò cần thấy ngay việc của mình khi vừa đăng nhập: lễ tân cần lịch
hôm nay và danh sách tiêm sắp đến hạn để chủ động gọi khách, nhân viên cần
lịch của chính mình, chủ nuôi cần thú cưng nhà mình.
"""
from datetime import date, datetime, time

from flask import Blueprint, render_template

from backend.app.auth.decorators import current_user, require_role
from backend.app.extensions import db
from backend.app.models import (Appointment, AppointmentStatus, Owner, Pet,
                                Service, UserRole)
from backend.app.services import (appointment_service, pet_service,
                                  vaccination_service)

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
@require_role(*tuple(UserRole))
def trang_chu():
    """Bảng điều khiển theo vai trò."""
    nguoi_dung = current_user()
    hom_nay = date.today()
    dau_ngay = datetime.combine(hom_nay, time.min)
    cuoi_ngay = datetime.combine(hom_nay, time.max)

    ngu_canh = {'hom_nay': hom_nay}

    if nguoi_dung.role == UserRole.ADMIN:
        ngu_canh['so_lieu'] = {
            'chu_nuoi': _dem(db.select(db.func.count(Owner.id))
                             .where(Owner.is_deleted.is_(False))),
            'thu_cung': _dem(db.select(db.func.count(Pet.id))
                             .where(Pet.is_deleted.is_(False))),
            'dich_vu': _dem(db.select(db.func.count(Service.id))
                            .where(Service.is_active.is_(True))),
            'lich_hom_nay': _dem(
                db.select(db.func.count(Appointment.id))
                .where(Appointment.scheduled_at.between(dau_ngay, cuoi_ngay),
                       Appointment.status != AppointmentStatus.CANCELLED)),
        }

    if nguoi_dung.role in (UserRole.ADMIN, UserRole.RECEPTIONIST,
                           UserRole.STAFF):
        ngu_canh['lich_hom_nay'] = appointment_service.danh_sach(
            nguoi_dung, tu_ngay=dau_ngay, den_ngay=cuoi_ngay)

    if nguoi_dung.role in (UserRole.ADMIN, UserRole.RECEPTIONIST):
        ngu_canh['nhac_tiem'] = vaccination_service.danh_sach_sap_den_han(
            nguoi_dung, hom_nay=hom_nay)

    if nguoi_dung.role == UserRole.OWNER:
        ngu_canh['thu_cung'] = pet_service.danh_sach(nguoi_dung)
        ngu_canh['lich_sap_toi'] = appointment_service.danh_sach(
            nguoi_dung, tu_ngay=dau_ngay)
        ngu_canh['nhac_tiem'] = vaccination_service.danh_sach_sap_den_han(
            nguoi_dung, hom_nay=hom_nay)

    return render_template('home.html', **ngu_canh)


def _dem(truy_van):
    """Chạy một truy vấn đếm và trả về số nguyên."""
    return db.session.execute(truy_van).scalar_one()
