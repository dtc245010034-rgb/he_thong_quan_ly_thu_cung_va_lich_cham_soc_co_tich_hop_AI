"""Cấu hình ứng dụng, đọc từ biến môi trường.

Không hardcode khóa API hay mật khẩu ở đây — yêu cầu bảo mật mục 9 đặc tả.
File .env thật không bao giờ được commit; chỉ commit .env.example.
"""
import os
from datetime import timedelta

from dotenv import load_dotenv

# Nạp backend/.env nếu có. Đường dẫn: config.py -> app/ -> backend/
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))


class Config:
    """Cấu hình dùng khi chạy thật."""

    SECRET_KEY = os.getenv('SECRET_KEY', 'change_me')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///./pet_care.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Phiên đăng nhập phải có hạn — yêu cầu bảo mật mục 4 đặc tả.
    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=int(os.getenv('JWT_EXPIRE_MINUTES', '60'))
    )

    # Ngưỡng nhắc lịch, dùng từ KT3.
    REMINDER_APPOINTMENT_DAYS = int(os.getenv('REMINDER_APPOINTMENT_DAYS', '2'))
    VACCINE_DUE_SOON_DAYS = int(os.getenv('VACCINE_DUE_SOON_DAYS', '7'))


class TestingConfig(Config):
    """Cấu hình khi chạy pytest: CSDL nằm trong bộ nhớ, không đụng file thật."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


CONFIG_MAP = {
    'default': Config,
    'testing': TestingConfig,
}
