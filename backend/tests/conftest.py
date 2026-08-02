"""Fixture dùng chung cho toàn bộ test.

CSDL nằm trong bộ nhớ và được dựng lại cho mỗi test, nên các test không
ảnh hưởng lẫn nhau và không đụng tới file pet_care.db thật.
"""
import pytest

from backend.app.extensions import db as _db
from backend.app.main import create_app


@pytest.fixture
def app():
    """Ứng dụng ở chế độ test, CSDL sạch cho mỗi test."""
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def session(app):
    """Phiên làm việc với CSDL."""
    return _db.session


@pytest.fixture
def client(app):
    """Client giả lập trình duyệt, dùng cho test route."""
    return app.test_client()
