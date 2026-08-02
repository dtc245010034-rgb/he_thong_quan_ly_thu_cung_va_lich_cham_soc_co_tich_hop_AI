"""Kiểm thử trang chủ hiển thị theo vai trò."""
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from backend.app.auth.password import hash_password
from backend.app.extensions import db
from backend.app.models import (Owner, Pet, Service, ServiceCategory, User,
                                UserRole)
from backend.app.services import appointment_service


@pytest.fixture
def du_lieu(app):
    """Bốn vai trò, một thú cưng, một lịch hẹn hôm nay."""
    with app.app_context():
        chu = Owner(full_name='Chủ A', phone='0900000001')
        db.session.add(chu)
        db.session.flush()

        nv = User(username='nhanvien', password_hash=hash_password('mk'),
                  role=UserRole.STAFF, full_name='Ngô Văn Khoa')
        le_tan = User(username='letan', password_hash=hash_password('mk'),
                      role=UserRole.RECEPTIONIST)
        db.session.add_all([
            nv, le_tan,
            User(username='admin', password_hash=hash_password('mk'),
                 role=UserRole.ADMIN),
            User(username='chua', password_hash=hash_password('mk'),
                 role=UserRole.OWNER, owner_id=chu.id),
        ])
        dv = Service(name='Tắm', category=ServiceCategory.TAM,
                     price=Decimal('150000'), duration_minutes=45)
        db.session.add(dv)
        db.session.flush()

        pet = Pet(owner_id=chu.id, name='Mực', species='chó')
        db.session.add(pet)
        db.session.flush()

        # Lịch hẹn trong hôm nay, đủ xa để không rơi vào quá khứ.
        appointment_service.dat_lich({
            'pet_id': pet.id, 'service_id': dv.id, 'staff_id': nv.id,
            'scheduled_at': datetime.now() + timedelta(hours=2),
        }, le_tan)
        db.session.commit()
        return {'pet_id': pet.id}


def dang_nhap(client, username):
    return client.post('/dang-nhap',
                       data={'username': username, 'password': 'mk'})


def test_chua_dang_nhap_bi_chuyen_ve_trang_dang_nhap(client, du_lieu):
    r = client.get('/')
    assert r.status_code == 302
    assert '/dang-nhap' in r.headers['Location']


def test_quan_ly_thay_so_lieu_tong_quan(client, du_lieu):
    dang_nhap(client, 'admin')
    r = client.get('/')
    assert r.status_code == 200
    assert 'Tổng quan' in r.get_data(as_text=True)


def test_le_tan_thay_lich_hom_nay_va_nhac_tiem(client, du_lieu):
    dang_nhap(client, 'letan')
    r = client.get('/')
    assert r.status_code == 200
    noi_dung = r.get_data(as_text=True)
    assert 'Lịch hẹn hôm nay' in noi_dung
    assert 'tiêm' in noi_dung.lower()


def test_nhan_vien_thay_lich_cua_minh(client, du_lieu):
    dang_nhap(client, 'nhanvien')
    r = client.get('/')
    assert r.status_code == 200
    noi_dung = r.get_data(as_text=True)
    assert 'Lịch của tôi' in noi_dung
    assert 'Mực' in noi_dung


def test_chu_nuoi_thay_thu_cung_cua_minh(client, du_lieu):
    dang_nhap(client, 'chua')
    r = client.get('/')
    assert r.status_code == 200
    noi_dung = r.get_data(as_text=True)
    assert 'Thú cưng của tôi' in noi_dung
    assert 'Mực' in noi_dung


def test_dang_nhap_xong_vao_duoc_trang_chu(client, du_lieu):
    """Trước Task 9, đăng nhập xong bị chuyển về '/' và nhận 404."""
    r = dang_nhap(client, 'letan')
    assert r.status_code == 302
    assert r.headers['Location'].endswith('/')

    r2 = client.get('/')
    assert r2.status_code == 200
