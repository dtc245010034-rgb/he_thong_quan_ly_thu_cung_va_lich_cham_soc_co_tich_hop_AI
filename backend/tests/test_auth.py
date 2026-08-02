"""Kiểm thử hash mật khẩu và luồng đăng nhập, đăng xuất."""
from backend.app.auth.password import hash_password, verify_password
from backend.app.extensions import db
from backend.app.models import User, UserRole


def test_hash_khong_luu_mat_khau_dang_thuong():
    h = hash_password('matkhau123')
    assert h != 'matkhau123'
    assert 'matkhau123' not in h


def test_hai_lan_hash_cung_mat_khau_cho_ket_qua_khac_nhau():
    """bcrypt tự sinh salt ngẫu nhiên -> chống tấn công rainbow table."""
    assert hash_password('matkhau123') != hash_password('matkhau123')


def test_verify_dung_mat_khau():
    assert verify_password('matkhau123', hash_password('matkhau123')) is True


def test_verify_sai_mat_khau():
    assert verify_password('sai', hash_password('matkhau123')) is False


def test_dang_nhap_thanh_cong_tao_phien(client, app):
    with app.app_context():
        db.session.add(User(username='letan', password_hash=hash_password('mk'),
                            role=UserRole.RECEPTIONIST))
        db.session.commit()

    r = client.post('/dang-nhap', data={'username': 'letan', 'password': 'mk'})

    assert r.status_code == 302
    with client.session_transaction() as s:
        assert 'user_id' in s


def test_dang_nhap_sai_mat_khau_bao_loi_tieng_viet(client, app):
    with app.app_context():
        db.session.add(User(username='letan', password_hash=hash_password('mk'),
                            role=UserRole.RECEPTIONIST))
        db.session.commit()

    r = client.post('/dang-nhap', data={'username': 'letan', 'password': 'sai'})

    assert r.status_code == 200
    assert 'Tên đăng nhập hoặc mật khẩu không đúng' in r.get_data(as_text=True)
    with client.session_transaction() as s:
        assert 'user_id' not in s


def test_tai_khoan_bi_khoa_khong_dang_nhap_duoc(client, app):
    """Tài khoản đã khóa bị từ chối, và thông báo phải giống hệt trường hợp sai
    mật khẩu — nếu khác, kẻ tấn công dò được tài khoản nào tồn tại."""
    with app.app_context():
        db.session.add(User(username='nghi', password_hash=hash_password('mk'),
                            role=UserRole.STAFF, is_active=False))
        db.session.commit()

    r = client.post('/dang-nhap', data={'username': 'nghi', 'password': 'mk'})

    assert r.status_code == 200
    assert 'Tên đăng nhập hoặc mật khẩu không đúng' in r.get_data(as_text=True)
    with client.session_transaction() as s:
        assert 'user_id' not in s


def test_dang_xuat_xoa_phien(client, app):
    with app.app_context():
        db.session.add(User(username='letan', password_hash=hash_password('mk'),
                            role=UserRole.RECEPTIONIST))
        db.session.commit()
    client.post('/dang-nhap', data={'username': 'letan', 'password': 'mk'})

    client.post('/dang-xuat')

    with client.session_transaction() as s:
        assert 'user_id' not in s
