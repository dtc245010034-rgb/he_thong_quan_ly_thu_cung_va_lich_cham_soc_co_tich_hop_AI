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

    return app
