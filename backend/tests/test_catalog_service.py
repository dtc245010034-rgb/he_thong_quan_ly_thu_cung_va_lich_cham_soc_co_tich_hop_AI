"""Kiểm thử service danh mục dịch vụ, gói combo và lịch sử giá."""
from decimal import Decimal

import pytest

from backend.app.models import (ServiceCategory, ServicePriceHistory, User,
                                UserRole)
from backend.app.services import catalog_service
from backend.app.services.errors import DuLieuKhongHopLe, QuyenTruyCapBiTuChoi


@pytest.fixture
def nguoi_dung(session):
    """Một quản lý và một lễ tân."""
    admin = User(username='ad', password_hash='h', role=UserRole.ADMIN)
    le_tan = User(username='lt', password_hash='h', role=UserRole.RECEPTIONIST)
    session.add_all([admin, le_tan])
    session.flush()
    return {'admin': admin, 'le_tan': le_tan}


def _tao_dich_vu_mau(admin, ten='Tắm', gia='150000', phut=45):
    return catalog_service.tao_dich_vu({
        'name': ten,
        'category': ServiceCategory.TAM,
        'price': Decimal(gia),
        'duration_minutes': phut,
    }, admin)


def test_doi_gia_tu_dong_ghi_lich_su(session, nguoi_dung):
    """Yêu cầu mục 3.3: đổi giá phải lưu lịch sử, không sửa đè."""
    admin = nguoi_dung['admin']
    dv = _tao_dich_vu_mau(admin)
    session.flush()

    catalog_service.cap_nhat_dich_vu(dv.id, {'price': Decimal('180000')}, admin)
    session.flush()

    ls = session.query(ServicePriceHistory).filter_by(service_id=dv.id).all()
    assert len(ls) == 1
    assert ls[0].old_price == Decimal('150000')
    assert ls[0].new_price == Decimal('180000')
    assert ls[0].changed_by == admin.id
    assert dv.price == Decimal('180000')


def test_cap_nhat_khong_doi_gia_thi_khong_ghi_lich_su(session, nguoi_dung):
    """Chỉ ghi lịch sử khi giá thực sự đổi, tránh làm bẩn bảng."""
    admin = nguoi_dung['admin']
    dv = _tao_dich_vu_mau(admin)
    session.flush()

    catalog_service.cap_nhat_dich_vu(dv.id, {'name': 'Tắm cơ bản'}, admin)
    session.flush()

    assert session.query(ServicePriceHistory).filter_by(service_id=dv.id).count() == 0
    assert dv.name == 'Tắm cơ bản'


def test_le_tan_khong_duoc_doi_gia(session, nguoi_dung):
    """Mục 3.1: chỉ quản lý được cấu hình dịch vụ và giá."""
    dv = _tao_dich_vu_mau(nguoi_dung['admin'])
    session.flush()

    with pytest.raises(QuyenTruyCapBiTuChoi):
        catalog_service.cap_nhat_dich_vu(dv.id, {'price': Decimal('1')},
                                         nguoi_dung['le_tan'])


def test_le_tan_van_xem_duoc_bang_gia(session, nguoi_dung):
    """Lễ tân cần xem giá để tư vấn khách, chỉ không được sửa."""
    _tao_dich_vu_mau(nguoi_dung['admin'])
    session.flush()

    ds = catalog_service.danh_sach_dich_vu(nguoi_dung['le_tan'])
    assert len(ds) == 1


def test_gia_am_bi_chan(session, nguoi_dung):
    with pytest.raises(DuLieuKhongHopLe):
        catalog_service.tao_dich_vu({
            'name': 'Lỗi', 'category': ServiceCategory.TAM,
            'price': Decimal('-1'), 'duration_minutes': 30,
        }, nguoi_dung['admin'])


def test_tao_goi_lien_ket_dung_cac_dich_vu(session, nguoi_dung):
    admin = nguoi_dung['admin']
    tam = _tao_dich_vu_mau(admin, 'Tắm', '150000')
    cat = _tao_dich_vu_mau(admin, 'Cắt tỉa', '250000', 60)
    session.flush()

    goi = catalog_service.tao_goi(
        {'name': 'Combo sạch đẹp', 'package_price': Decimal('350000')},
        [{'service_id': tam.id, 'quantity': 1},
         {'service_id': cat.id, 'quantity': 1}],
        admin)
    session.flush()

    assert len(goi.items) == 2
    assert goi.package_price == Decimal('350000')


def test_gia_goi_phai_re_hon_tong_gia_le(session, nguoi_dung):
    """Gói combo đắt hơn mua lẻ là vô nghĩa về nghiệp vụ."""
    admin = nguoi_dung['admin']
    tam = _tao_dich_vu_mau(admin, 'Tắm', '150000')
    session.flush()

    with pytest.raises(DuLieuKhongHopLe):
        catalog_service.tao_goi(
            {'name': 'Gói dở', 'package_price': Decimal('999999')},
            [{'service_id': tam.id, 'quantity': 1}],
            admin)
