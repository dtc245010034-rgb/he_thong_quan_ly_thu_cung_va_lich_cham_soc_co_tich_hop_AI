"""Route nhắc lịch tiêm phòng."""
from datetime import date

from flask import Blueprint, redirect, render_template, request, url_for

from backend.app.auth.decorators import current_user, require_role
from backend.app.extensions import db
from backend.app.models import UserRole
from backend.app.services import pet_service, vaccination_service
from backend.app.services.errors import DuLieuKhongHopLe

vaccinations_bp = Blueprint('vaccinations', __name__, url_prefix='/tiem-phong')

_QUAN_LY = (UserRole.ADMIN, UserRole.RECEPTIONIST)
_XEM_DUOC = tuple(UserRole)


@vaccinations_bp.route('')
@require_role(*_XEM_DUOC)
def danh_sach_nhac_tiem():
    """Danh sách mũi tiêm sắp đến hạn hoặc đã quá hạn."""
    nguoi_dung = current_user()
    hom_nay = date.today()
    ds = vaccination_service.danh_sach_sap_den_han(nguoi_dung, hom_nay=hom_nay)

    # Tính trạng thái ở tầng route để template không phải gọi service.
    dong = [{'lich': lich,
             'trang_thai': vaccination_service.tinh_trang_thai(lich, hom_nay)}
            for lich in ds]
    return render_template('vaccinations/list.html', dong=dong,
                           hom_nay=hom_nay)


@vaccinations_bp.route('/thu-cung/<int:pet_id>')
@require_role(*_XEM_DUOC)
def theo_thu_cung(pet_id):
    """Toàn bộ lịch tiêm của một thú cưng."""
    nguoi_dung = current_user()
    hom_nay = date.today()
    pet = pet_service.lay_theo_id(pet_id, nguoi_dung)
    ds = vaccination_service.danh_sach_theo_thu_cung(pet_id, nguoi_dung)

    dong = [{'lich': lich,
             'trang_thai': vaccination_service.tinh_trang_thai(lich, hom_nay)}
            for lich in ds]
    return render_template('vaccinations/list.html', dong=dong, pet=pet,
                           hom_nay=hom_nay)


@vaccinations_bp.route('/them', methods=['GET', 'POST'])
@require_role(*_QUAN_LY)
def them_lich_tiem():
    """Thêm mũi tiêm cần theo dõi."""
    nguoi_dung = current_user()

    if request.method == 'GET':
        return render_template('vaccinations/form.html',
                               thu_cung=pet_service.danh_sach(nguoi_dung))

    try:
        vaccination_service.tao(_doc_bieu_mau(request.form), nguoi_dung)
        db.session.commit()
    except DuLieuKhongHopLe as e:
        db.session.rollback()
        return render_template('vaccinations/form.html',
                               thu_cung=pet_service.danh_sach(nguoi_dung),
                               error=str(e), form=request.form), 200

    return redirect(url_for('vaccinations.danh_sach_nhac_tiem'))


@vaccinations_bp.route('/<int:vaccination_id>/da-tiem', methods=['POST'])
@require_role(*_QUAN_LY)
def danh_dau_da_tiem(vaccination_id):
    """Đánh dấu đã tiêm và sinh lịch kỳ tiếp theo."""
    vaccination_service.danh_dau_da_tiem(vaccination_id, current_user(),
                                         ngay_tiem=date.today())
    db.session.commit()
    return redirect(url_for('vaccinations.danh_sach_nhac_tiem'))


def _doc_bieu_mau(form):
    """Chuyển dữ liệu biểu mẫu sang kiểu Python đúng."""
    lan_cuoi = form.get('last_date')
    den_han = form.get('next_due_date')
    return {
        'pet_id': int(form['pet_id']) if form.get('pet_id') else None,
        'vaccine_name': form.get('vaccine_name', ''),
        'last_date': date.fromisoformat(lan_cuoi) if lan_cuoi else None,
        'next_due_date': date.fromisoformat(den_han) if den_han else None,
    }
