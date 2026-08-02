"""Kiểm thử route CRUD chủ nuôi.

Kiểm chứng lại phân quyền lớp 2 qua HTTP thật, không chỉ ở tầng service:
ngoại lệ nghiệp vụ phải được dịch thành đúng mã HTTP.
"""
import pytest

from backend.app.auth.password import hash_password
from backend.app.extensions import db
from backend.app.models import Owner, Pet, User, UserRole


@pytest.fixture
def du_lieu(app):
    """Hai chủ nuôi có tài khoản riêng, một lễ tân, một nhân viên."""
    with app.app_context():
        chu_a = Owner(full_name='Chủ A', phone='0900000001')
        chu_b = Owner(full_name='Chủ B', phone='0900000002')
        db.session.add_all([chu_a, chu_b])
        db.session.flush()

        db.session.add_all([
            User(username='chua', password_hash=hash_password('mk'),
                 role=UserRole.OWNER, owner_id=chu_a.id),
            User(username='letan', password_hash=hash_password('mk'),
                 role=UserRole.RECEPTIONIST),
            User(username='nhanvien', password_hash=hash_password('mk'),
                 role=UserRole.STAFF),
        ])
        db.session.add(Pet(owner_id=chu_a.id, name='Mực', species='chó'))
        db.session.commit()
        return {'chu_a_id': chu_a.id, 'chu_b_id': chu_b.id}


def dang_nhap(client, username):
    return client.post('/dang-nhap',
                       data={'username': username, 'password': 'mk'})


def test_chua_dang_nhap_bi_chuyen_huong(client, du_lieu):
    r = client.get('/chu-nuoi')
    assert r.status_code == 302
    assert '/dang-nhap' in r.headers['Location']


def test_le_tan_xem_duoc_danh_sach(client, du_lieu):
    dang_nhap(client, 'letan')
    r = client.get('/chu-nuoi')
    assert r.status_code == 200
    noi_dung = r.get_data(as_text=True)
    assert 'Chủ A' in noi_dung
    assert 'Chủ B' in noi_dung


def test_nhan_vien_khong_sua_duoc_chu_nuoi(client, du_lieu):
    """Nhân viên không có quyền quản lý hồ sơ chủ nuôi (mục 3.1)."""
    dang_nhap(client, 'nhanvien')
    r = client.get(f"/chu-nuoi/{du_lieu['chu_a_id']}/sua")
    assert r.status_code == 403


def test_chu_nuoi_a_mo_ho_so_nha_b_bi_403(client, du_lieu):
    """LỖ HỔNG PHẢI CHẶN, kiểm chứng qua HTTP thật.

    Vai trò owner hợp lệ nên decorator cho qua; chỉ tầng service mới chặn
    được, và ngoại lệ đó phải thành đúng mã 403 chứ không phải lỗi 500.
    """
    dang_nhap(client, 'chua')
    r = client.get(f"/chu-nuoi/{du_lieu['chu_b_id']}")
    assert r.status_code == 403


def test_chu_nuoi_a_mo_duoc_ho_so_cua_chinh_minh(client, du_lieu):
    dang_nhap(client, 'chua')
    r = client.get(f"/chu-nuoi/{du_lieu['chu_a_id']}")
    assert r.status_code == 200
    assert 'Chủ A' in r.get_data(as_text=True)


def test_tao_chu_nuoi_qua_bieu_mau(client, app, du_lieu):
    dang_nhap(client, 'letan')
    r = client.post('/chu-nuoi/them',
                    data={'full_name': 'Chủ C', 'phone': '0900000003'})

    assert r.status_code == 302
    with app.app_context():
        chu = db.session.execute(
            db.select(Owner).filter_by(phone='0900000003')
        ).scalar_one()
        assert chu.full_name == 'Chủ C'


def test_tao_thieu_so_dien_thoai_bao_loi_tieng_viet(client, du_lieu):
    dang_nhap(client, 'letan')
    r = client.post('/chu-nuoi/them', data={'full_name': 'Chủ D', 'phone': ''})

    assert r.status_code == 200
    assert 'Số điện thoại không được để trống' in r.get_data(as_text=True)
