"""Phân quyền lớp 1: chặn theo vai trò.

ĐÂY MỚI LÀ LỚP MỘT. Vai trò đúng chưa đủ: chủ nuôi A có vai trò 'owner'
hợp lệ nhưng không được xem thú cưng của chủ nuôi B; nhân viên chỉ được
ghi hồ sơ cho lịch hẹn của chính mình.

Việc lọc theo quyền sở hữu dữ liệu nằm ở tầng services/ (làm ở KT2-B),
không làm được bằng decorator vì decorator chỉ biết vai trò, không biết
bản ghi đang được truy cập thuộc về ai.

Thiếu lớp hai thì hệ thống có lỗ hổng dạng đổi tham số trên URL từ
?pet_id=5 thành ?pet_id=6 là xem được hồ sơ nhà khác.
"""
from functools import wraps

from flask import abort, redirect, session, url_for

from backend.app.extensions import db
from backend.app.models import User


def current_user():
    """Trả người dùng của phiên hiện tại, hoặc None nếu chưa đăng nhập."""
    user_id = session.get('user_id')
    if user_id is None:
        return None
    # db.session.get() thay cho Query.get() — API cũ sinh cảnh báo trên
    # SQLAlchemy 2.x.
    return db.session.get(User, user_id)


def require_role(*roles):
    """Chỉ cho phép các vai trò được liệt kê truy cập route.

    Chưa đăng nhập thì chuyển về trang đăng nhập; đã đăng nhập nhưng sai
    vai trò thì trả 403. Phân biệt hai trường hợp này là có chủ đích: người
    chưa đăng nhập cần được dẫn đi đăng nhập, còn người sai quyền thì đăng
    nhập lại cũng không giải quyết được gì.
    """
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = current_user()
            if user is None:
                return redirect(url_for('auth.trang_dang_nhap'))
            if user.role not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapper
    return decorator
