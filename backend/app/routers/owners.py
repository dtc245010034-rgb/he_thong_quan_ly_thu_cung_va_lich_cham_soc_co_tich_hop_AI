"""Route quản lý chủ nuôi."""
from flask import (Blueprint, redirect, render_template, request, url_for)

from backend.app.auth.decorators import current_user, require_role
from backend.app.extensions import db
from backend.app.models import UserRole
from backend.app.services import owner_service, pet_service
from backend.app.services.errors import DuLieuKhongHopLe

owners_bp = Blueprint('owners', __name__, url_prefix='/chu-nuoi')

# Vai trò được sửa hồ sơ. Tầng service kiểm tra lại lần nữa — decorator chỉ
# là lớp chặn đầu tiên.
_QUAN_LY = (UserRole.ADMIN, UserRole.RECEPTIONIST)
_MOI_VAI_TRO = tuple(UserRole)


@owners_bp.route('')
@require_role(*_MOI_VAI_TRO)
def danh_sach_chu_nuoi():
    """Danh sách chủ nuôi. Service tự lọc theo quyền của người đang đăng nhập."""
    tu_khoa = request.args.get('tu_khoa', '').strip() or None
    ds = owner_service.danh_sach(current_user(), tu_khoa=tu_khoa)
    return render_template('owners/list.html', danh_sach=ds, tu_khoa=tu_khoa)


@owners_bp.route('/<int:owner_id>')
@require_role(*_MOI_VAI_TRO)
def chi_tiet_chu_nuoi(owner_id):
    """Chi tiết một chủ nuôi kèm danh sách thú cưng của họ."""
    nguoi_dung = current_user()
    chu = owner_service.lay_theo_id(owner_id, nguoi_dung)
    thu_cung = pet_service.danh_sach(nguoi_dung, owner_id=owner_id)
    return render_template('owners/detail.html', chu=chu, thu_cung=thu_cung)


@owners_bp.route('/them', methods=['GET', 'POST'])
@require_role(*_QUAN_LY)
def them_chu_nuoi():
    """Tạo hồ sơ chủ nuôi mới."""
    if request.method == 'GET':
        return render_template('owners/form.html', chu=None)

    try:
        chu = owner_service.tao(dict(request.form), current_user())
        db.session.commit()
    except DuLieuKhongHopLe as e:
        db.session.rollback()
        return render_template('owners/form.html', chu=None, error=str(e),
                               form=request.form), 200

    return redirect(url_for('owners.chi_tiet_chu_nuoi', owner_id=chu.id))


@owners_bp.route('/<int:owner_id>/sua', methods=['GET', 'POST'])
@require_role(*_QUAN_LY)
def sua_chu_nuoi(owner_id):
    """Cập nhật hồ sơ chủ nuôi."""
    nguoi_dung = current_user()
    if request.method == 'GET':
        chu = owner_service.lay_theo_id(owner_id, nguoi_dung)
        return render_template('owners/form.html', chu=chu)

    try:
        owner_service.cap_nhat(owner_id, dict(request.form), nguoi_dung)
        db.session.commit()
    except DuLieuKhongHopLe as e:
        db.session.rollback()
        chu = owner_service.lay_theo_id(owner_id, nguoi_dung)
        return render_template('owners/form.html', chu=chu, error=str(e),
                               form=request.form), 200

    return redirect(url_for('owners.chi_tiet_chu_nuoi', owner_id=owner_id))


@owners_bp.route('/<int:owner_id>/xoa', methods=['POST'])
@require_role(*_QUAN_LY)
def xoa_chu_nuoi(owner_id):
    """Xóa mềm hồ sơ chủ nuôi."""
    owner_service.xoa_mem(owner_id, current_user())
    db.session.commit()
    return redirect(url_for('owners.danh_sach_chu_nuoi'))
