"""App factory.

Giao diện render phía server bằng Jinja2, nên Flask được trỏ sang thư mục
frontend/ nằm ngoài package Python — theo cấu trúc mục 7.2 đặc tả.
"""
import os

from flask import Flask

from backend.app.config import CONFIG_MAP
from backend.app.extensions import db

# backend/app/main.py -> lùi 3 cấp là thư mục gốc dự án.
_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


def create_app(config_name='default'):
    """Tạo và cấu hình ứng dụng Flask."""
    app = Flask(
        __name__,
        template_folder=os.path.join(_PROJECT_ROOT, 'frontend', 'templates'),
        static_folder=os.path.join(_PROJECT_ROOT, 'frontend', 'static'),
    )
    app.config.from_object(CONFIG_MAP[config_name])

    db.init_app(app)

    # Import để SQLAlchemy biết đủ bảng khi gọi create_all().
    from backend.app import models  # noqa: F401

    from backend.app.auth.routes import auth_bp
    from backend.app.routers.appointments import appointments_bp
    from backend.app.routers.care_records import care_records_bp
    from backend.app.routers.catalog import catalog_bp
    from backend.app.routers.owners import owners_bp
    from backend.app.routers.home import home_bp
    from backend.app.routers.pets import pets_bp
    from backend.app.routers.vaccinations import vaccinations_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(owners_bp)
    app.register_blueprint(pets_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(care_records_bp)
    app.register_blueprint(vaccinations_bp)

    _dang_ky_xu_ly_loi(app)
    _dang_ky_bien_dung_chung(app)

    from backend.app.cli import dang_ky_lenh
    dang_ky_lenh(app)

    if app.config.get('TESTING'):
        _dang_ky_route_thu_nghiem(app)

    return app


def _dang_ky_xu_ly_loi(app):
    """Dịch ngoại lệ nghiệp vụ sang mã HTTP ở một chỗ duy nhất.

    Nhờ vậy từng route không phải tự bắt ngoại lệ, và một route quên bắt
    cũng không trả về lỗi 500 — vốn là cách rò rỉ thông tin hệ thống.
    """
    from flask import render_template

    from backend.app.services.errors import (DuLieuKhongHopLe,
                                             QuyenTruyCapBiTuChoi)

    @app.errorhandler(QuyenTruyCapBiTuChoi)
    def _tu_choi_quyen(e):
        return render_template('errors/403.html', thong_diep=str(e)), 403

    @app.errorhandler(DuLieuKhongHopLe)
    def _du_lieu_sai(e):
        return render_template('errors/404.html', thong_diep=str(e)), 404

    @app.errorhandler(403)
    def _loi_403(e):
        return render_template('errors/403.html', thong_diep=None), 403

    @app.errorhandler(404)
    def _loi_404(e):
        return render_template('errors/404.html', thong_diep=None), 404


def _dang_ky_bien_dung_chung(app):
    """Đưa người dùng hiện tại vào mọi template, để thanh điều hướng hiển thị
    đúng theo vai trò mà không phải truyền thủ công ở từng route."""
    from backend.app.auth.decorators import current_user

    _TEN_VAI_TRO = {
        'admin': 'Quản lý',
        'receptionist': 'Lễ tân',
        'staff': 'Nhân viên',
        'owner': 'Chủ nuôi',
    }

    @app.context_processor
    def _bien_dung_chung():
        nguoi_dung = current_user()
        return {
            'nguoi_dung': nguoi_dung,
            'vai_tro_tieng_viet': (_TEN_VAI_TRO.get(nguoi_dung.role.value)
                                   if nguoi_dung else None),
        }


def _dang_ky_route_thu_nghiem(app):
    """Route dùng riêng cho test decorator phân quyền.

    Chỉ đăng ký khi cờ TESTING bật, nên các route này KHÔNG tồn tại lúc chạy
    thật — không mở thêm bề mặt tấn công.
    """
    from backend.app.auth.decorators import require_role
    from backend.app.models import UserRole

    @app.route('/_thu-nghiem/chi-admin')
    @require_role(UserRole.ADMIN)
    def _thu_nghiem_chi_admin():
        return 'ok'

    @app.route('/_thu-nghiem/admin-va-le-tan')
    @require_role(UserRole.ADMIN, UserRole.RECEPTIONIST)
    def _thu_nghiem_admin_va_le_tan():
        return 'ok'
