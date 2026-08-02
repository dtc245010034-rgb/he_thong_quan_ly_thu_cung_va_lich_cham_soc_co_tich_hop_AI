"""Route quản lý lịch hẹn."""
from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for

from backend.app.auth.decorators import current_user, require_role
from backend.app.extensions import db
from backend.app.models import AppointmentStatus, UserRole
from backend.app.services import (appointment_service, catalog_service,
                                  pet_service)
from backend.app.services.errors import DuLieuKhongHopLe, TrungLichHen

appointments_bp = Blueprint('appointments', __name__, url_prefix='/lich-hen')

_QUAN_LY_LICH = (UserRole.ADMIN, UserRole.RECEPTIONIST)
_MOI_VAI_TRO = tuple(UserRole)
_HOAN_THANH_DUOC = _QUAN_LY_LICH + (UserRole.STAFF,)


@appointments_bp.route('')
@require_role(*_MOI_VAI_TRO)
def danh_sach_lich_hen():
    """Danh sách lịch hẹn kèm bộ lọc. Service tự lọc theo quyền."""
    nguoi_dung = current_user()

    tu_ngay = _doc_ngay(request.args.get('tu_ngay'))
    den_ngay = _doc_ngay(request.args.get('den_ngay'), cuoi_ngay=True)
    trang_thai = (AppointmentStatus(request.args['trang_thai'])
                  if request.args.get('trang_thai') else None)

    ds = appointment_service.danh_sach(nguoi_dung, tu_ngay=tu_ngay,
                                       den_ngay=den_ngay, trang_thai=trang_thai)
    return render_template('appointments/list.html', danh_sach=ds,
                           trang_thai_chon=request.args.get('trang_thai', ''),
                           tu_ngay=request.args.get('tu_ngay', ''),
                           den_ngay=request.args.get('den_ngay', ''),
                           cac_trang_thai=list(AppointmentStatus))


@appointments_bp.route('/dat', methods=['GET', 'POST'])
@require_role(*_QUAN_LY_LICH)
def dat_lich_hen():
    """Đặt lịch hẹn mới."""
    nguoi_dung = current_user()

    if request.method == 'GET':
        return _render_bieu_mau_dat(nguoi_dung)

    try:
        lich = appointment_service.dat_lich(_doc_bieu_mau_dat(request.form),
                                            nguoi_dung)
        db.session.commit()
    except (DuLieuKhongHopLe, TrungLichHen) as e:
        db.session.rollback()
        return _render_bieu_mau_dat(nguoi_dung, error=str(e),
                                    form=request.form), 200

    return redirect(url_for('appointments.chi_tiet_lich_hen',
                            appointment_id=lich.id))


@appointments_bp.route('/<int:appointment_id>')
@require_role(*_MOI_VAI_TRO)
def chi_tiet_lich_hen(appointment_id):
    """Chi tiết lịch hẹn kèm lịch sử đổi lịch."""
    lich = appointment_service.lay_theo_id(appointment_id, current_user())
    return render_template('appointments/detail.html', lich=lich,
                           ly_do_huy=appointment_service.LY_DO_HUY)


@appointments_bp.route('/<int:appointment_id>/doi', methods=['GET', 'POST'])
@require_role(*_QUAN_LY_LICH)
def doi_lich_hen(appointment_id):
    """Đổi lịch sang giờ khác, bắt buộc nhập lý do."""
    nguoi_dung = current_user()
    lich = appointment_service.lay_theo_id(appointment_id, nguoi_dung)

    if request.method == 'GET':
        return render_template('appointments/reschedule.html', lich=lich)

    try:
        appointment_service.doi_lich(
            appointment_id,
            _doc_thoi_gian(request.form.get('scheduled_at')),
            request.form.get('ly_do', ''),
            nguoi_dung)
        db.session.commit()
    except (DuLieuKhongHopLe, TrungLichHen) as e:
        db.session.rollback()
        return render_template('appointments/reschedule.html', lich=lich,
                               error=str(e), form=request.form), 200

    return redirect(url_for('appointments.chi_tiet_lich_hen',
                            appointment_id=appointment_id))


@appointments_bp.route('/<int:appointment_id>/huy', methods=['GET', 'POST'])
@require_role(*_QUAN_LY_LICH)
def huy_lich_hen(appointment_id):
    """Hủy lịch. Lý do bắt buộc, chọn từ danh sách 4 giá trị (mục 3.4)."""
    nguoi_dung = current_user()
    lich = appointment_service.lay_theo_id(appointment_id, nguoi_dung)

    if request.method == 'GET':
        return render_template('appointments/cancel.html', lich=lich,
                               ly_do_huy=appointment_service.LY_DO_HUY)

    try:
        appointment_service.huy_lich(appointment_id,
                                     request.form.get('ly_do', ''),
                                     request.form.get('mo_ta'),
                                     nguoi_dung)
        db.session.commit()
    except DuLieuKhongHopLe as e:
        db.session.rollback()
        return render_template('appointments/cancel.html', lich=lich,
                               ly_do_huy=appointment_service.LY_DO_HUY,
                               error=str(e), form=request.form), 200

    return redirect(url_for('appointments.chi_tiet_lich_hen',
                            appointment_id=appointment_id))


@appointments_bp.route('/<int:appointment_id>/xac-nhan', methods=['POST'])
@require_role(*_QUAN_LY_LICH)
def xac_nhan_lich_hen(appointment_id):
    """Xác nhận lịch hẹn."""
    appointment_service.xac_nhan(appointment_id, current_user())
    db.session.commit()
    return redirect(url_for('appointments.chi_tiet_lich_hen',
                            appointment_id=appointment_id))


@appointments_bp.route('/<int:appointment_id>/hoan-thanh', methods=['POST'])
@require_role(*_HOAN_THANH_DUOC)
def hoan_thanh_lich_hen(appointment_id):
    """Đánh dấu buổi hẹn đã hoàn thành."""
    appointment_service.hoan_thanh(appointment_id, current_user())
    db.session.commit()
    return redirect(url_for('appointments.chi_tiet_lich_hen',
                            appointment_id=appointment_id))


# ----- Hàm phụ trợ -----

def _render_bieu_mau_dat(nguoi_dung, **thong_so):
    """Dựng biểu mẫu đặt lịch kèm danh sách thú cưng, dịch vụ, nhân viên."""
    from backend.app.models import User

    nhan_vien = db.session.execute(
        db.select(User).where(User.role == UserRole.STAFF,
                              User.is_active.is_(True))
    ).scalars().all()

    return render_template(
        'appointments/form.html',
        thu_cung=pet_service.danh_sach(nguoi_dung),
        dich_vu=catalog_service.danh_sach_dich_vu(nguoi_dung),
        nhan_vien=list(nhan_vien),
        **thong_so)


def _doc_bieu_mau_dat(form):
    """Chuyển dữ liệu biểu mẫu đặt lịch sang kiểu Python đúng."""
    return {
        'pet_id': int(form['pet_id']) if form.get('pet_id') else None,
        'service_id': int(form['service_id']) if form.get('service_id') else None,
        # Không phân công nhân viên là hợp lệ — khi đó bỏ qua kiểm tra trùng.
        'staff_id': int(form['staff_id']) if form.get('staff_id') else None,
        'scheduled_at': _doc_thoi_gian(form.get('scheduled_at')),
        'notes': form.get('notes'),
    }


def _doc_thoi_gian(chuoi):
    """Đọc giá trị từ ô input type=datetime-local."""
    if not chuoi:
        raise DuLieuKhongHopLe('Phải chọn thời gian')
    try:
        return datetime.fromisoformat(chuoi)
    except ValueError:
        raise DuLieuKhongHopLe('Thời gian không hợp lệ')


def _doc_ngay(chuoi, cuoi_ngay=False):
    """Đọc ô lọc ngày. cuoi_ngay=True lấy 23:59 để bao trọn ngày đó."""
    if not chuoi:
        return None
    try:
        ngay = datetime.fromisoformat(chuoi)
    except ValueError:
        return None
    return ngay.replace(hour=23, minute=59, second=59) if cuoi_ngay else ngay
