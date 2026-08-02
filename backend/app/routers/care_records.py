"""Route hồ sơ chăm sóc."""
from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, redirect, render_template, request, url_for

from backend.app.auth.decorators import current_user, require_role
from backend.app.extensions import db
from backend.app.models import UserRole
from backend.app.services import (appointment_service, care_record_service,
                                  pet_service)
from backend.app.services.errors import DuLieuKhongHopLe

care_records_bp = Blueprint('care_records', __name__)

_GHI_DUOC = (UserRole.ADMIN, UserRole.RECEPTIONIST, UserRole.STAFF)
_XEM_DUOC = tuple(UserRole)


@care_records_bp.route('/thu-cung/<int:pet_id>/ho-so')
@require_role(*_XEM_DUOC)
def danh_sach_ho_so(pet_id):
    """Lịch sử chăm sóc của một thú cưng."""
    nguoi_dung = current_user()
    pet = pet_service.lay_theo_id(pet_id, nguoi_dung)
    ho_so = care_record_service.danh_sach_theo_thu_cung(pet_id, nguoi_dung)
    return render_template('care_records/list.html', pet=pet, ho_so=ho_so)


@care_records_bp.route('/lich-hen/<int:appointment_id>/ho-so',
                       methods=['GET', 'POST'])
@require_role(*_GHI_DUOC)
def ghi_ho_so(appointment_id):
    """Ghi hồ sơ chăm sóc cho một buổi hẹn đã hoàn thành."""
    nguoi_dung = current_user()
    lich = appointment_service.lay_theo_id(appointment_id, nguoi_dung)

    if request.method == 'GET':
        return render_template('care_records/form.html', lich=lich,
                               hom_nay=date.today().isoformat())

    try:
        care_record_service.ghi_ho_so(
            _doc_bieu_mau(request.form, lich), nguoi_dung)
        db.session.commit()
    except DuLieuKhongHopLe as e:
        db.session.rollback()
        return render_template('care_records/form.html', lich=lich,
                               hom_nay=date.today().isoformat(),
                               error=str(e), form=request.form), 200

    return redirect(url_for('care_records.danh_sach_ho_so',
                            pet_id=lich.pet_id))


def _doc_bieu_mau(form, lich):
    """Chuyển dữ liệu biểu mẫu sang kiểu Python đúng."""
    ngay = form.get('record_date')
    can_nang = form.get('weight_at_visit')

    try:
        can_nang_so = Decimal(can_nang) if can_nang else None
    except InvalidOperation:
        raise DuLieuKhongHopLe('Cân nặng phải là số')

    return {
        'pet_id': lich.pet_id,
        'appointment_id': lich.id,
        'record_date': date.fromisoformat(ngay) if ngay else None,
        'weight_at_visit': can_nang_so,
        'condition_notes': form.get('condition_notes'),
        'treatment_notes': form.get('treatment_notes'),
        'next_recommendation': form.get('next_recommendation'),
    }
