"""Kiểm thử route lịch hẹn.

Kiểm chứng qua HTTP thật rằng ngoại lệ nghiệp vụ thành đúng mã HTTP, và
thông báo trùng lịch hiển thị được cho người dùng.
"""
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from backend.app.auth.password import hash_password
from backend.app.extensions import db
from backend.app.models import (Appointment, AppointmentStatus, Owner, Pet,
                                Service, ServiceCategory, User, UserRole)

GIO_9H = datetime(2027, 9, 1, 9, 0)


@pytest.fixture
def du_lieu(app):
    with app.app_context():
        chu = Owner(full_name='Chủ A', phone='0900000001')
        db.session.add(chu)
        db.session.flush()

        nv = User(username='nhanvien', password_hash=hash_password('mk'),
                  role=UserRole.STAFF)
        db.session.add_all([
            nv,
            User(username='letan', password_hash=hash_password('mk'),
                 role=UserRole.RECEPTIONIST),
            User(username='chua', password_hash=hash_password('mk'),
                 role=UserRole.OWNER, owner_id=chu.id),
        ])
        dv = Service(name='Tắm', category=ServiceCategory.TAM,
                     price=Decimal('150000'), duration_minutes=45)
        db.session.add(dv)
        db.session.flush()

        pet = Pet(owner_id=chu.id, name='Mực', species='chó')
        db.session.add(pet)
        db.session.commit()
        return {'pet_id': pet.id, 'service_id': dv.id, 'staff_id': nv.id}


def dang_nhap(client, username):
    return client.post('/dang-nhap',
                       data={'username': username, 'password': 'mk'})


def _dat_qua_route(client, du_lieu, gio):
    return client.post('/lich-hen/dat', data={
        'pet_id': du_lieu['pet_id'],
        'service_id': du_lieu['service_id'],
        'staff_id': du_lieu['staff_id'],
        'scheduled_at': gio.strftime('%Y-%m-%dT%H:%M'),
    })


def test_chua_dang_nhap_bi_chuyen_huong(client, du_lieu):
    r = client.get('/lich-hen')
    assert r.status_code == 302


def test_le_tan_dat_lich_qua_bieu_mau(client, app, du_lieu):
    dang_nhap(client, 'letan')
    r = _dat_qua_route(client, du_lieu, GIO_9H)

    assert r.status_code == 302
    with app.app_context():
        lich = db.session.execute(db.select(Appointment)).scalar_one()
        assert lich.scheduled_at == GIO_9H
        assert lich.ends_at == GIO_9H + timedelta(minutes=45)


def test_dat_trung_lich_hien_thong_bao_neu_ro_nhan_vien(client, du_lieu):
    """Thông báo trùng phải hiển thị được cho lễ tân, không phải lỗi 500."""
    dang_nhap(client, 'letan')
    _dat_qua_route(client, du_lieu, GIO_9H)

    r = _dat_qua_route(client, du_lieu, GIO_9H + timedelta(minutes=30))

    assert r.status_code == 200
    noi_dung = r.get_data(as_text=True)
    assert 'nhanvien' in noi_dung
    assert '09:00' in noi_dung


def test_nhan_vien_khong_dat_duoc_lich(client, du_lieu):
    """Mục 3.4: đặt lịch là việc của lễ tân."""
    dang_nhap(client, 'nhanvien')
    assert client.get('/lich-hen/dat').status_code == 403


def test_chu_nuoi_khong_dat_duoc_lich(client, du_lieu):
    dang_nhap(client, 'chua')
    assert client.get('/lich-hen/dat').status_code == 403


def test_huy_lich_khong_chon_ly_do_hien_loi(client, app, du_lieu):
    """Ca mục 10 kiểm chứng qua HTTP: thiếu lý do thì hiện lỗi, không hủy."""
    dang_nhap(client, 'letan')
    _dat_qua_route(client, du_lieu, GIO_9H)
    with app.app_context():
        lich_id = db.session.execute(db.select(Appointment)).scalar_one().id

    r = client.post(f'/lich-hen/{lich_id}/huy', data={'ly_do': ''})

    assert r.status_code == 200
    assert 'lý do' in r.get_data(as_text=True).lower()
    with app.app_context():
        lich = db.session.get(Appointment, lich_id)
        assert lich.status == AppointmentStatus.PENDING


def test_huy_lich_co_ly_do_thanh_cong(client, app, du_lieu):
    dang_nhap(client, 'letan')
    _dat_qua_route(client, du_lieu, GIO_9H)
    with app.app_context():
        lich_id = db.session.execute(db.select(Appointment)).scalar_one().id

    r = client.post(f'/lich-hen/{lich_id}/huy',
                    data={'ly_do': 'thu_cung_om', 'mo_ta': ''})

    assert r.status_code == 302
    with app.app_context():
        assert db.session.get(Appointment, lich_id).status == \
            AppointmentStatus.CANCELLED


def test_doi_lich_qua_bieu_mau_ghi_lich_su(client, app, du_lieu):
    dang_nhap(client, 'letan')
    _dat_qua_route(client, du_lieu, GIO_9H)
    with app.app_context():
        lich_id = db.session.execute(db.select(Appointment)).scalar_one().id

    gio_moi = GIO_9H + timedelta(days=1)
    r = client.post(f'/lich-hen/{lich_id}/doi', data={
        'scheduled_at': gio_moi.strftime('%Y-%m-%dT%H:%M'),
        'ly_do': 'khach_yeu_cau',
    })

    assert r.status_code == 302
    with app.app_context():
        lich = db.session.get(Appointment, lich_id)
        assert lich.scheduled_at == gio_moi
        assert len(lich.history) == 1


def test_nhan_vien_chi_thay_lich_cua_minh(client, app, du_lieu):
    """Ma trận quyền mục 4.2, kiểm chứng qua HTTP."""
    dang_nhap(client, 'letan')
    _dat_qua_route(client, du_lieu, GIO_9H)
    client.post('/dang-xuat')

    dang_nhap(client, 'nhanvien')
    r = client.get('/lich-hen')
    assert r.status_code == 200
    assert 'Mực' in r.get_data(as_text=True)
