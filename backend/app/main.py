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
    app.register_blueprint(auth_bp)

    from backend.app.cli import dang_ky_lenh
    dang_ky_lenh(app)

    if app.config.get('TESTING'):
        _dang_ky_route_thu_nghiem(app)

    return app


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
