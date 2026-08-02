"""Kiểm thử app factory và cấu hình."""
from backend.app.main import create_app


def test_create_app_che_do_test_bat_co_testing():
    """App tạo ở chế độ 'testing' phải bật cờ TESTING."""
    app = create_app('testing')
    assert app.config['TESTING'] is True


def test_che_do_test_dung_csdl_trong_bo_nho():
    """Chế độ test phải dùng SQLite in-memory, không đụng file CSDL thật."""
    app = create_app('testing')
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'


def test_app_tro_dung_thu_muc_frontend():
    """Template và static phải trỏ sang frontend/ theo thiết kế mục 6.3."""
    app = create_app('testing')
    assert app.template_folder.replace('\\', '/').endswith('frontend/templates')
    assert app.static_folder.replace('\\', '/').endswith('frontend/static')


def test_thoi_han_phien_doc_tu_cau_hinh():
    """Phiên đăng nhập phải có hạn, lấy từ JWT_EXPIRE_MINUTES."""
    app = create_app('testing')
    assert app.permanent_session_lifetime.total_seconds() == 60 * 60
