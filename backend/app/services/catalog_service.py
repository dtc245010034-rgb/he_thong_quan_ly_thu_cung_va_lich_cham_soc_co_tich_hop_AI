"""Nghiệp vụ danh mục dịch vụ, gói combo và bảng giá.

Chỉ quản lý được cấu hình dịch vụ và giá (mục 3.1 đặc tả). Các vai trò khác
vẫn xem được bảng giá để tư vấn khách, chỉ không sửa được.
"""
from decimal import Decimal

from backend.app.extensions import db
from backend.app.models import (PackageItem, Service, ServicePackage,
                                ServicePriceHistory, UserRole)
from backend.app.services import activity_log_service
from backend.app.services.errors import DuLieuKhongHopLe, QuyenTruyCapBiTuChoi


def _bat_buoc_quan_ly(current_user):
    """Chỉ vai trò quản lý được thay đổi danh mục và giá."""
    if current_user.role != UserRole.ADMIN:
        raise QuyenTruyCapBiTuChoi(
            'Chỉ quản lý mới được cấu hình dịch vụ và bảng giá'
        )


def danh_sach_dich_vu(current_user, chi_dang_hoat_dong=True):
    """Danh sách dịch vụ. Mọi vai trò đều xem được để tư vấn khách."""
    truy_van = db.select(Service)
    if chi_dang_hoat_dong:
        truy_van = truy_van.where(Service.is_active.is_(True))
    return list(db.session.execute(truy_van.order_by(Service.name))
                .scalars().all())


def lay_dich_vu(service_id, current_user):
    """Lấy một dịch vụ theo id."""
    dv = db.session.get(Service, service_id)
    if dv is None:
        raise DuLieuKhongHopLe('Không tìm thấy dịch vụ này')
    return dv


def tao_dich_vu(du_lieu, current_user):
    """Tạo dịch vụ mới trong bảng giá."""
    _bat_buoc_quan_ly(current_user)
    _kiem_tra_dich_vu(du_lieu, bat_buoc_day_du=True)

    dv = Service(
        name=du_lieu['name'].strip(),
        category=du_lieu['category'],
        price=du_lieu['price'],
        duration_minutes=du_lieu['duration_minutes'],
        description=(du_lieu.get('description') or None),
    )
    db.session.add(dv)
    db.session.flush()

    activity_log_service.ghi(current_user, 'tao_dich_vu', 'services', dv.id,
                             f'Tạo dịch vụ {dv.name}')
    return dv


def cap_nhat_dich_vu(service_id, du_lieu, current_user):
    """Cập nhật dịch vụ.

    Nếu giá thay đổi thì ghi một dòng vào service_price_history — mục 3.3
    đặc tả yêu cầu lưu lịch sử thay vì sửa đè, để truy được giá cũ là bao
    nhiêu và ai đã đổi.
    """
    _bat_buoc_quan_ly(current_user)
    dv = lay_dich_vu(service_id, current_user)
    _kiem_tra_dich_vu(du_lieu, bat_buoc_day_du=False)

    if 'price' in du_lieu:
        gia_moi = du_lieu['price']
        # Chỉ ghi lịch sử khi giá THỰC SỰ đổi. Nếu ghi cả khi giá giữ nguyên
        # thì bảng lịch sử đầy dòng vô nghĩa và mất tác dụng tra cứu.
        if gia_moi != dv.price:
            db.session.add(ServicePriceHistory(
                service_id=dv.id,
                old_price=dv.price,
                new_price=gia_moi,
                changed_by=current_user.id,
            ))
            dv.price = gia_moi

    for truong in ('name', 'description'):
        if truong in du_lieu:
            gia_tri = du_lieu[truong]
            setattr(dv, truong, gia_tri.strip() if gia_tri else None)
    if 'duration_minutes' in du_lieu:
        dv.duration_minutes = du_lieu['duration_minutes']
    if 'category' in du_lieu:
        dv.category = du_lieu['category']
    if 'is_active' in du_lieu:
        dv.is_active = du_lieu['is_active']

    activity_log_service.ghi(current_user, 'sua_dich_vu', 'services', dv.id,
                             f'Cập nhật dịch vụ {dv.name}')
    return dv


def danh_sach_goi(current_user, chi_dang_hoat_dong=True):
    """Danh sách gói dịch vụ combo."""
    truy_van = db.select(ServicePackage)
    if chi_dang_hoat_dong:
        truy_van = truy_van.where(ServicePackage.is_active.is_(True))
    return list(db.session.execute(truy_van.order_by(ServicePackage.name))
                .scalars().all())


def tao_goi(du_lieu, danh_sach_item, current_user):
    """Tạo gói combo gồm nhiều dịch vụ với giá ưu đãi.

    danh_sach_item là list các dict dạng {'service_id': int, 'quantity': int}.
    """
    _bat_buoc_quan_ly(current_user)

    if not (du_lieu.get('name') or '').strip():
        raise DuLieuKhongHopLe('Tên gói dịch vụ không được để trống')
    if not danh_sach_item:
        raise DuLieuKhongHopLe('Gói dịch vụ phải có ít nhất một dịch vụ')

    gia_goi = du_lieu.get('package_price')
    if gia_goi is None or Decimal(gia_goi) <= 0:
        raise DuLieuKhongHopLe('Giá gói phải lớn hơn 0')

    # Gói combo đắt hơn mua lẻ là vô nghĩa về nghiệp vụ — khách không có lý
    # do nào để mua. Chặn ngay ở đây thay vì để lọt vào bảng giá.
    tong_gia_le = Decimal('0')
    for item in danh_sach_item:
        dv = db.session.get(Service, item['service_id'])
        if dv is None:
            raise DuLieuKhongHopLe(
                f"Dịch vụ id {item['service_id']} không tồn tại"
            )
        tong_gia_le += dv.price * item.get('quantity', 1)

    if Decimal(gia_goi) >= tong_gia_le:
        raise DuLieuKhongHopLe(
            f'Giá gói ({gia_goi}) phải nhỏ hơn tổng giá mua lẻ ({tong_gia_le})'
        )

    goi = ServicePackage(
        name=du_lieu['name'].strip(),
        description=(du_lieu.get('description') or None),
        package_price=gia_goi,
    )
    db.session.add(goi)
    db.session.flush()

    for item in danh_sach_item:
        db.session.add(PackageItem(
            package_id=goi.id,
            service_id=item['service_id'],
            quantity=item.get('quantity', 1),
        ))

    activity_log_service.ghi(current_user, 'tao_goi_dich_vu',
                             'service_packages', goi.id,
                             f'Tạo gói {goi.name}')
    return goi


def _kiem_tra_dich_vu(du_lieu, bat_buoc_day_du):
    """Kiểm tra dữ liệu dịch vụ, báo lỗi tiếng Việt nêu rõ trường nào sai."""
    if bat_buoc_day_du or 'name' in du_lieu:
        if not (du_lieu.get('name') or '').strip():
            raise DuLieuKhongHopLe('Tên dịch vụ không được để trống')
    if bat_buoc_day_du or 'price' in du_lieu:
        gia = du_lieu.get('price')
        if gia is None or Decimal(gia) < 0:
            raise DuLieuKhongHopLe('Giá dịch vụ không được âm')
    if bat_buoc_day_du or 'duration_minutes' in du_lieu:
        phut = du_lieu.get('duration_minutes')
        if phut is None or int(phut) <= 0:
            raise DuLieuKhongHopLe('Thời lượng dịch vụ phải lớn hơn 0 phút')
