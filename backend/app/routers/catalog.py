"""Route danh mục dịch vụ và gói combo.

Toàn bộ route sửa đổi yêu cầu vai trò quản lý. Route xem thì mở cho các vai
trò khác vì lễ tân cần bảng giá để tư vấn khách.
"""
from decimal import Decimal, InvalidOperation

from flask import Blueprint, redirect, render_template, request, url_for

from backend.app.auth.decorators import current_user, require_role
from backend.app.extensions import db
from backend.app.models import ServiceCategory, UserRole
from backend.app.services import catalog_service
from backend.app.services.errors import DuLieuKhongHopLe

catalog_bp = Blueprint('catalog', __name__, url_prefix='/dich-vu')

_QUAN_LY = (UserRole.ADMIN,)
_XEM_DUOC = (UserRole.ADMIN, UserRole.RECEPTIONIST, UserRole.STAFF)


@catalog_bp.route('')
@require_role(*_XEM_DUOC)
def danh_sach_dich_vu():
    """Bảng giá dịch vụ."""
    nguoi_dung = current_user()
    return render_template(
        'catalog/services.html',
        danh_sach=catalog_service.danh_sach_dich_vu(nguoi_dung,
                                                    chi_dang_hoat_dong=False),
    )


@catalog_bp.route('/them', methods=['GET', 'POST'])
@require_role(*_QUAN_LY)
def them_dich_vu():
    """Thêm dịch vụ mới vào bảng giá."""
    if request.method == 'GET':
        return render_template('catalog/service_form.html', dich_vu=None,
                               danh_muc=list(ServiceCategory))

    try:
        catalog_service.tao_dich_vu(_doc_bieu_mau(request.form), current_user())
        db.session.commit()
    except DuLieuKhongHopLe as e:
        db.session.rollback()
        return render_template('catalog/service_form.html', dich_vu=None,
                               danh_muc=list(ServiceCategory), error=str(e),
                               form=request.form), 200

    return redirect(url_for('catalog.danh_sach_dich_vu'))


@catalog_bp.route('/<int:service_id>/sua', methods=['GET', 'POST'])
@require_role(*_QUAN_LY)
def sua_dich_vu(service_id):
    """Sửa dịch vụ. Đổi giá sẽ tự ghi vào lịch sử giá."""
    nguoi_dung = current_user()
    if request.method == 'GET':
        dv = catalog_service.lay_dich_vu(service_id, nguoi_dung)
        return render_template('catalog/service_form.html', dich_vu=dv,
                               danh_muc=list(ServiceCategory))

    try:
        catalog_service.cap_nhat_dich_vu(service_id, _doc_bieu_mau(request.form),
                                         nguoi_dung)
        db.session.commit()
    except DuLieuKhongHopLe as e:
        db.session.rollback()
        dv = catalog_service.lay_dich_vu(service_id, nguoi_dung)
        return render_template('catalog/service_form.html', dich_vu=dv,
                               danh_muc=list(ServiceCategory), error=str(e),
                               form=request.form), 200

    return redirect(url_for('catalog.danh_sach_dich_vu'))


@catalog_bp.route('/goi')
@require_role(*_XEM_DUOC)
def danh_sach_goi():
    """Danh sách gói combo."""
    nguoi_dung = current_user()
    return render_template(
        'catalog/packages.html',
        danh_sach=catalog_service.danh_sach_goi(nguoi_dung,
                                                chi_dang_hoat_dong=False),
    )


@catalog_bp.route('/goi/them', methods=['GET', 'POST'])
@require_role(*_QUAN_LY)
def them_goi():
    """Tạo gói combo mới."""
    nguoi_dung = current_user()
    dich_vu = catalog_service.danh_sach_dich_vu(nguoi_dung)

    if request.method == 'GET':
        return render_template('catalog/package_form.html', dich_vu=dich_vu)

    # Biểu mẫu gửi service_id[] và quantity[] song song nhau.
    ids = request.form.getlist('service_id')
    so_luong = request.form.getlist('quantity')
    items = [{'service_id': int(sid), 'quantity': int(sl or 1)}
             for sid, sl in zip(ids, so_luong) if sid]

    try:
        gia = request.form.get('package_price') or '0'
        catalog_service.tao_goi(
            {'name': request.form.get('name', ''),
             'description': request.form.get('description'),
             'package_price': Decimal(gia)},
            items, nguoi_dung)
        db.session.commit()
    except (DuLieuKhongHopLe, InvalidOperation) as e:
        db.session.rollback()
        return render_template('catalog/package_form.html', dich_vu=dich_vu,
                               error=str(e), form=request.form), 200

    return redirect(url_for('catalog.danh_sach_goi'))


def _doc_bieu_mau(form):
    """Chuyển dữ liệu biểu mẫu sang kiểu Python đúng.

    Biểu mẫu gửi mọi thứ dưới dạng chuỗi. Đổi kiểu ở tầng route để service
    nhận đúng kiểu và không phải biết gì về HTTP.
    """
    du_lieu = {'name': form.get('name', ''),
               'description': form.get('description')}

    if form.get('category'):
        du_lieu['category'] = ServiceCategory(form['category'])

    try:
        du_lieu['price'] = Decimal(form.get('price') or '0')
    except InvalidOperation:
        raise DuLieuKhongHopLe('Giá dịch vụ phải là số')

    try:
        du_lieu['duration_minutes'] = int(form.get('duration_minutes') or 0)
    except ValueError:
        raise DuLieuKhongHopLe('Thời lượng phải là số nguyên')

    du_lieu['is_active'] = form.get('is_active') == 'on'
    return du_lieu
