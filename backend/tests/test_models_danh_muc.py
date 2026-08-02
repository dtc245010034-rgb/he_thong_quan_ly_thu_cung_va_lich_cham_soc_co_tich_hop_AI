"""Kiểm thử model danh mục dịch vụ, gói dịch vụ và lịch sử giá."""
from decimal import Decimal

import pytest
from sqlalchemy.exc import StatementError

from backend.app.models import (PackageItem, Service, ServiceCategory,
                                ServicePackage, ServicePriceHistory, User, UserRole)


def test_tao_dich_vu(session):
    """Dịch vụ mới mặc định đang hoạt động."""
    dv = Service(name='Tắm cơ bản', category=ServiceCategory.TAM,
                 price=Decimal('150000'), duration_minutes=45)
    session.add(dv)
    session.flush()
    assert dv.is_active is True


def test_danh_muc_khong_hop_le_bi_chan(session):
    """category phải là enum kiểm soát, không nhận text tự do."""
    dv = Service(name='X', category='matxa', price=Decimal('1'), duration_minutes=1)
    session.add(dv)
    with pytest.raises(StatementError):
        session.flush()


def test_goi_dich_vu_lien_ket_nhieu_dich_vu(session):
    """Gói combo nối n-n với dịch vụ qua package_items, và phải rẻ hơn mua lẻ."""
    tam = Service(name='Tắm', category=ServiceCategory.TAM,
                  price=Decimal('150000'), duration_minutes=45)
    cat = Service(name='Cắt tỉa', category=ServiceCategory.GROOMING,
                  price=Decimal('250000'), duration_minutes=60)
    session.add_all([tam, cat])
    session.flush()

    goi = ServicePackage(name='Combo sạch đẹp', package_price=Decimal('350000'))
    session.add(goi)
    session.flush()
    session.add_all([
        PackageItem(package_id=goi.id, service_id=tam.id, quantity=1),
        PackageItem(package_id=goi.id, service_id=cat.id, quantity=1),
    ])
    session.flush()

    assert len(goi.items) == 2
    assert sum(i.service.price * i.quantity for i in goi.items) == Decimal('400000')
    assert goi.package_price < Decimal('400000')


def test_lich_su_gia_ghi_nhan_nguoi_doi(session):
    """Đổi giá phải lưu lịch sử, không sửa đè (yêu cầu mục 3.3 đặc tả)."""
    admin = User(username='ad', password_hash='h', role=UserRole.ADMIN)
    dv = Service(name='Tắm', category=ServiceCategory.TAM,
                 price=Decimal('150000'), duration_minutes=45)
    session.add_all([admin, dv])
    session.flush()

    ls = ServicePriceHistory(service_id=dv.id, old_price=Decimal('150000'),
                             new_price=Decimal('180000'), changed_by=admin.id)
    session.add(ls)
    session.flush()

    assert dv.price_history[0].old_price == Decimal('150000')
    assert dv.price_history[0].changed_by_user.username == 'ad'
