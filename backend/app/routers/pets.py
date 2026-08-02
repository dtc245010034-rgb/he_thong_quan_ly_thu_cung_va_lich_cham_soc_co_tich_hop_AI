"""Route quản lý thú cưng."""
from flask import Blueprint, redirect, render_template, request, url_for

from backend.app.auth.decorators import current_user, require_role
from backend.app.extensions import db
from backend.app.models import UserRole
from backend.app.services import owner_service, pet_service
from backend.app.services.errors import DuLieuKhongHopLe

pets_bp = Blueprint('pets', __name__, url_prefix='/thu-cung')

_QUAN_LY = (UserRole.ADMIN, UserRole.RECEPTIONIST)
_MOI_VAI_TRO = tuple(UserRole)


@pets_bp.route('')
@require_role(*_MOI_VAI_TRO)
def danh_sach_thu_cung():
    """Danh sách thú cưng. Service tự lọc theo quyền."""
    tu_khoa = request.args.get('tu_khoa', '').strip() or None
    ds = pet_service.danh_sach(current_user(), tu_khoa=tu_khoa)
    return render_template('pets/list.html', danh_sach=ds, tu_khoa=tu_khoa)


@pets_bp.route('/<int:pet_id>')
@require_role(*_MOI_VAI_TRO)
def chi_tiet_thu_cung(pet_id):
    """Chi tiết một thú cưng."""
    pet = pet_service.lay_theo_id(pet_id, current_user())
    return render_template('pets/detail.html', pet=pet)


@pets_bp.route('/them', methods=['GET', 'POST'])
@require_role(*_QUAN_LY)
def them_thu_cung():
    """Tạo hồ sơ thú cưng mới."""
    nguoi_dung = current_user()
    if request.method == 'GET':
        return render_template('pets/form.html', pet=None,
                               chu_nuoi=owner_service.danh_sach(nguoi_dung))

    du_lieu = _doc_bieu_mau(request.form)
    try:
        pet = pet_service.tao(du_lieu, nguoi_dung)
        db.session.commit()
    except DuLieuKhongHopLe as e:
        db.session.rollback()
        return render_template('pets/form.html', pet=None, error=str(e),
                               form=request.form,
                               chu_nuoi=owner_service.danh_sach(nguoi_dung)), 200

    return redirect(url_for('pets.chi_tiet_thu_cung', pet_id=pet.id))


@pets_bp.route('/<int:pet_id>/sua', methods=['GET', 'POST'])
@require_role(*_QUAN_LY)
def sua_thu_cung(pet_id):
    """Cập nhật hồ sơ thú cưng."""
    nguoi_dung = current_user()
    if request.method == 'GET':
        pet = pet_service.lay_theo_id(pet_id, nguoi_dung)
        return render_template('pets/form.html', pet=pet,
                               chu_nuoi=owner_service.danh_sach(nguoi_dung))

    du_lieu = _doc_bieu_mau(request.form)
    try:
        pet_service.cap_nhat(pet_id, du_lieu, nguoi_dung)
        db.session.commit()
    except DuLieuKhongHopLe as e:
        db.session.rollback()
        pet = pet_service.lay_theo_id(pet_id, nguoi_dung)
        return render_template('pets/form.html', pet=pet, error=str(e),
                               form=request.form,
                               chu_nuoi=owner_service.danh_sach(nguoi_dung)), 200

    return redirect(url_for('pets.chi_tiet_thu_cung', pet_id=pet_id))


@pets_bp.route('/<int:pet_id>/xoa', methods=['POST'])
@require_role(*_QUAN_LY)
def xoa_thu_cung(pet_id):
    """Xóa mềm hồ sơ thú cưng."""
    pet_service.xoa_mem(pet_id, current_user())
    db.session.commit()
    return redirect(url_for('pets.danh_sach_thu_cung'))


def _doc_bieu_mau(form):
    """Chuyển dữ liệu biểu mẫu sang kiểu Python đúng.

    Biểu mẫu HTML gửi mọi thứ dưới dạng chuỗi, kể cả ngày và số. Chuyển ở
    đây để tầng service nhận đúng kiểu và không phải biết gì về HTTP.
    """
    from datetime import date
    from decimal import Decimal, InvalidOperation

    du_lieu = dict(form)

    if du_lieu.get('owner_id'):
        du_lieu['owner_id'] = int(du_lieu['owner_id'])

    ngay_sinh = du_lieu.get('birth_date')
    du_lieu['birth_date'] = date.fromisoformat(ngay_sinh) if ngay_sinh else None

    can_nang = du_lieu.get('weight')
    if can_nang:
        try:
            du_lieu['weight'] = Decimal(can_nang)
        except InvalidOperation:
            raise DuLieuKhongHopLe('Cân nặng phải là số')
    else:
        du_lieu['weight'] = None

    return du_lieu
