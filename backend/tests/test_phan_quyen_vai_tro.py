"""Kiểm thử decorator phân quyền theo vai trò (lớp 1).

Đây MỚI LÀ LỚP MỘT. Lớp hai — lọc theo quyền sở hữu dữ liệu — làm ở KT2-B
khi đã có tầng services/ để đặt bộ lọc vào.
"""
import pytest

from backend.app.auth.password import hash_password
from backend.app.extensions import db
from backend.app.models import User, UserRole


@pytest.fixture
def tao_nguoi_dung(app):
    """Tạo sẵn 4 tài khoản, mỗi vai trò một cái, mật khẩu đều là 'mk'."""
    def _tao():
        with app.app_context():
            for role in UserRole:
                db.session.add(User(username=role.value,
                                    password_hash=hash_password('mk'), role=role))
            db.session.commit()
    return _tao


def dang_nhap(client, username):
    return client.post('/dang-nhap', data={'username': username, 'password': 'mk'})


def test_chua_dang_nhap_bi_chuyen_ve_trang_dang_nhap(client):
    r = client.get('/_thu-nghiem/chi-admin')
    assert r.status_code == 302
    assert '/dang-nhap' in r.headers['Location']


def test_admin_vao_duoc_route_chi_danh_cho_admin(client, tao_nguoi_dung):
    tao_nguoi_dung()
    dang_nhap(client, 'admin')
    r = client.get('/_thu-nghiem/chi-admin')
    assert r.status_code == 200


def test_nhan_vien_goi_route_bao_cao_doanh_thu_bi_403(client, tao_nguoi_dung):
    """Ca kiểm thử bắt buộc ở mục 10 đặc tả."""
    tao_nguoi_dung()
    dang_nhap(client, 'staff')
    r = client.get('/_thu-nghiem/chi-admin')
    assert r.status_code == 403


def test_le_tan_bi_chan_khoi_cau_hinh_ai(client, tao_nguoi_dung):
    """Mục 9 đặc tả: lễ tân không được cấu hình AI."""
    tao_nguoi_dung()
    dang_nhap(client, 'receptionist')
    r = client.get('/_thu-nghiem/chi-admin')
    assert r.status_code == 403


def test_route_cho_nhieu_vai_tro_chap_nhan_ca_hai(client, tao_nguoi_dung):
    tao_nguoi_dung()
    dang_nhap(client, 'receptionist')
    assert client.get('/_thu-nghiem/admin-va-le-tan').status_code == 200
    client.post('/dang-xuat')
    dang_nhap(client, 'admin')
    assert client.get('/_thu-nghiem/admin-va-le-tan').status_code == 200


def test_chu_nuoi_khong_vao_duoc_route_noi_bo(client, tao_nguoi_dung):
    tao_nguoi_dung()
    dang_nhap(client, 'owner')
    assert client.get('/_thu-nghiem/admin-va-le-tan').status_code == 403
